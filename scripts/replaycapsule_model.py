#!/usr/bin/env python3
"""Deterministic ReplayCapsule-RV model-level benchmark generator.

This is not an RTL simulator and it is not a PicoRV32 result. It is an
executable event-boundary model used to exercise replay evidence, baselines,
and ablations while Verilator/PicoRV32/Yosys are unavailable locally.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
import sys
from typing import Callable, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
REPLAY_TB = REPO_ROOT / "tb" / "replay_testbench"
if str(REPLAY_TB) not in sys.path:
    sys.path.insert(0, str(REPLAY_TB))

from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


class EventType(IntEnum):
    EV_COMMIT = 0
    EV_BRANCH = 1
    EV_JUMP = 2
    EV_STORE = 3
    EV_LOAD = 4
    EV_MMIO_READ = 5
    EV_MMIO_WRITE = 6
    EV_INTERRUPT_ENTER = 7
    EV_INTERRUPT_EXIT = 8
    EV_EXTERNAL_INPUT = 9
    EV_PROPERTY_FAIL = 10
    EV_CHECKPOINT_HASH = 11


SENSOR_ADDR = 0x4000_0000
ACTUATOR_ADDR = 0x4000_0004
CONFIG_ADDR = 0x4000_0008
COMMAND_ADDR = 0x4000_000C
STACK_PROTECTED_ADDR = 0x0000_1010
STACK_SAFE_ADDR = 0x0000_1800
HEARTBEAT_ADDR = COMMAND_ADDR

PC_BOOT = 0x0000_0080
PC_SENSOR = 0x0000_0090
PC_CONFIG = 0x0000_00A0
PC_ACTUATOR = 0x0000_00B0
PC_DELAY = 0x0000_00C0
PC_ISR = 0x0000_00D0
PC_STACK = 0x0000_00E0
PC_COMMAND = 0x0000_00F0
PC_WATCHDOG = 0x0000_0100

CONFIG_MAGIC = 0x0000_CAFE
ACTUATOR_SAFE = 0
ACTUATOR_UNSAFE = 250
SENSOR_HIGH = 850
SENSOR_LOW = 300
UART_UNSAFE_COMMAND = 0x55
WATCHDOG_HEARTBEAT = 0xFEED

BENCHMARKS = (
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
)


PROPERTY_IDS = {
    "sensor_threshold_bug": "P3_SENSOR_DEADLINE",
    "interrupt_race_bug": "P2_INTERRUPT_CRITICAL",
    "mmio_ordering_bug": "P5_MMIO_ORDERING",
    "stack_corruption_bug": "P4_STACK_PROTECT",
    "uart_command_bug": "P1_ACTUATOR_LIMIT",
    "watchdog_timeout_bug": "P6_WATCHDOG_TIMEOUT",
}


@dataclass(frozen=True)
class Event:
    seq: int
    cycle: int
    commit: int
    event_type: EventType
    pc: int = 0
    addr: int = 0
    data: int = 0

    def to_trace_dict(self) -> dict[str, int | str]:
        return {
            "seq": self.seq,
            "cycle": self.cycle,
            "commit": self.commit,
            "event_type": self.event_type.name,
            "pc": f"0x{self.pc:08x}",
            "addr": f"0x{self.addr:08x}",
            "data": f"0x{self.data:08x}",
        }


@dataclass(frozen=True)
class RunResult:
    benchmark: str
    variant: str
    events: tuple[Event, ...]
    property_id: str | None
    failure_signature: str | None

    @property
    def failed(self) -> bool:
        return self.property_id is not None


class BenchmarkModel:
    """Small deterministic event model for benchmark-level replay evidence."""

    def __init__(self, benchmark: str) -> None:
        if benchmark not in BENCHMARKS:
            raise ValueError(f"unknown benchmark {benchmark!r}")
        self.benchmark = benchmark
        self._events: list[Event] = []
        self._cycle = 0
        self._commit = 0

    def run(self, failing: bool) -> RunResult:
        self._events = []
        self._cycle = 0
        self._commit = 0
        self._commit_event(PC_BOOT)
        dispatch: dict[str, Callable[[bool], None]] = {
            "sensor_threshold_bug": self._sensor_threshold,
            "interrupt_race_bug": self._interrupt_race,
            "mmio_ordering_bug": self._mmio_ordering,
            "stack_corruption_bug": self._stack_corruption,
            "uart_command_bug": self._uart_command,
            "watchdog_timeout_bug": self._watchdog_timeout,
        }
        dispatch[self.benchmark](failing)
        property_id = self._expected_property() if failing else None
        signature = None
        if failing:
            fail_event = next(event for event in reversed(self._events) if event.event_type == EventType.EV_PROPERTY_FAIL)
            signature = f"0x{fail_event.data:08x}"
        return RunResult(
            benchmark=self.benchmark,
            variant="failing" if failing else "fixed",
            events=tuple(self._events),
            property_id=property_id,
            failure_signature=signature,
        )

    def _sensor_threshold(self, failing: bool) -> None:
        sensor_value = SENSOR_HIGH if failing else SENSOR_LOW
        self._mmio(EventType.EV_MMIO_READ, PC_SENSOR, SENSOR_ADDR, sensor_value)
        if failing:
            for _ in range(17):
                if self._commit == 4:
                    self._interrupt_pair(PC_DELAY)
                self._commit_event(PC_DELAY)
            self._fail(PC_DELAY, 3, sensor_value)
        else:
            self._mmio(EventType.EV_MMIO_WRITE, PC_CONFIG, CONFIG_ADDR, CONFIG_MAGIC)
            self._mmio(EventType.EV_MMIO_WRITE, PC_ACTUATOR, ACTUATOR_ADDR, ACTUATOR_SAFE)

    def _interrupt_race(self, failing: bool) -> None:
        self._mmio(EventType.EV_MMIO_WRITE, PC_COMMAND, COMMAND_ADDR, 1)
        self._mmio(EventType.EV_MMIO_WRITE, PC_CONFIG, CONFIG_ADDR, 0x1111)
        if failing:
            self._interrupt_pair(PC_ISR)
            self._fail(PC_ISR, 2, 0x1111)
        else:
            self._mmio(EventType.EV_MMIO_WRITE, PC_CONFIG, CONFIG_ADDR, CONFIG_MAGIC)
            self._mmio(EventType.EV_MMIO_WRITE, PC_ACTUATOR, ACTUATOR_ADDR, ACTUATOR_SAFE)
            self._mmio(EventType.EV_MMIO_WRITE, PC_COMMAND, COMMAND_ADDR, 0)

    def _mmio_ordering(self, failing: bool) -> None:
        if failing:
            self._mmio(EventType.EV_MMIO_WRITE, PC_ACTUATOR, ACTUATOR_ADDR, 25)
            self._fail(PC_ACTUATOR, 5, 25)
            self._mmio(EventType.EV_MMIO_WRITE, PC_CONFIG, CONFIG_ADDR, CONFIG_MAGIC)
        else:
            self._mmio(EventType.EV_MMIO_WRITE, PC_CONFIG, CONFIG_ADDR, CONFIG_MAGIC)
            self._mmio(EventType.EV_MMIO_WRITE, PC_ACTUATOR, ACTUATOR_ADDR, 25)

    def _stack_corruption(self, failing: bool) -> None:
        self._mmio(EventType.EV_MMIO_WRITE, PC_CONFIG, CONFIG_ADDR, CONFIG_MAGIC)
        if failing:
            self._store(PC_STACK, STACK_PROTECTED_ADDR, 0xDEAD_BEEF)
            self._fail(PC_STACK, 4, STACK_PROTECTED_ADDR)
        else:
            self._store(PC_STACK, STACK_SAFE_ADDR, 0xDEAD_BEEF)

    def _uart_command(self, failing: bool) -> None:
        command = UART_UNSAFE_COMMAND if failing else 0
        self._input(PC_COMMAND, input_id=1, value=command)
        self._mmio(EventType.EV_MMIO_READ, PC_COMMAND, COMMAND_ADDR, command)
        self._branch(PC_COMMAND, taken=failing)
        if failing:
            self._mmio(EventType.EV_MMIO_WRITE, PC_ACTUATOR, ACTUATOR_ADDR, ACTUATOR_UNSAFE)
            self._fail(PC_ACTUATOR, 1, ACTUATOR_UNSAFE)
        else:
            self._mmio(EventType.EV_MMIO_WRITE, PC_CONFIG, CONFIG_ADDR, CONFIG_MAGIC)
            self._mmio(EventType.EV_MMIO_WRITE, PC_ACTUATOR, ACTUATOR_ADDR, ACTUATOR_SAFE)

    def _watchdog_timeout(self, failing: bool) -> None:
        self._mmio(EventType.EV_MMIO_READ, PC_SENSOR, SENSOR_ADDR, SENSOR_HIGH)
        if failing:
            for _ in range(20):
                if self._commit == 6:
                    self._interrupt_pair(PC_ISR)
                self._commit_event(PC_WATCHDOG)
            self._fail(PC_WATCHDOG, 6, WATCHDOG_HEARTBEAT)
        else:
            for _ in range(4):
                self._mmio(EventType.EV_MMIO_WRITE, PC_WATCHDOG, HEARTBEAT_ADDR, WATCHDOG_HEARTBEAT)
                self._commit_event(PC_WATCHDOG)

    def _expected_property(self) -> str:
        return PROPERTY_IDS[self.benchmark]

    def _commit_event(self, pc: int) -> None:
        self._event(EventType.EV_COMMIT, pc, data=0x0000_0013)
        self._commit += 1

    def _branch(self, pc: int, taken: bool) -> None:
        if taken:
            self._event(EventType.EV_BRANCH, pc, data=1)
        self._commit_event(pc)

    def _store(self, pc: int, addr: int, data: int) -> None:
        self._event(EventType.EV_STORE, pc, addr=addr, data=data)
        self._commit_event(pc)

    def _mmio(self, event_type: EventType, pc: int, addr: int, data: int) -> None:
        self._event(event_type, pc, addr=addr, data=data)
        self._commit_event(pc)

    def _input(self, pc: int, input_id: int, value: int) -> None:
        self._event(EventType.EV_EXTERNAL_INPUT, pc, addr=input_id, data=value)

    def _interrupt_pair(self, pc: int) -> None:
        self._event(EventType.EV_INTERRUPT_ENTER, pc, data=1)
        self._event(EventType.EV_INTERRUPT_EXIT, pc, data=0)

    def _fail(self, pc: int, property_word: int, cause: int) -> None:
        signature = _failure_signature(self.benchmark, pc, self._commit, cause)
        self._event(EventType.EV_PROPERTY_FAIL, pc, addr=property_word, data=signature)

    def _event(self, event_type: EventType, pc: int, addr: int = 0, data: int = 0) -> None:
        self._events.append(
            Event(
                seq=len(self._events),
                cycle=self._cycle,
                commit=self._commit,
                event_type=event_type,
                pc=pc,
                addr=addr,
                data=data & 0xFFFF_FFFF,
            )
        )
        self._cycle += 1


def _failure_signature(benchmark: str, pc: int, commit: int, cause: int) -> int:
    seed = sum((index + 1) * ord(char) for index, char in enumerate(benchmark))
    return (pc ^ commit ^ cause ^ seed ^ 0x5E05_0003) & 0xFFFF_FFFF


def run_benchmark(benchmark: str, failing: bool = True) -> RunResult:
    return BenchmarkModel(benchmark).run(failing=failing)


def run_suite(failing: bool = True) -> list[RunResult]:
    return [run_benchmark(benchmark, failing=failing) for benchmark in BENCHMARKS]


def capsule_fixture(result: RunResult, omit: set[str] | None = None) -> str:
    """Render replay evidence in the text format consumed by replay_driver."""

    omitted = omit or set()
    lines: list[str] = [f"benchmark {result.benchmark}", f"variant {result.variant}"]
    if result.property_id:
        lines.append(f"property_id {result.property_id}")
    if result.failure_signature:
        lines.append(f"failure_signature {result.failure_signature}")

    for event in result.events:
        if event.event_type == EventType.EV_PROPERTY_FAIL:
            if "pc" not in omitted:
                lines.append(f"pc cycle={event.cycle} commit={event.commit} pc=0x{event.pc:08x}")
        elif event.event_type == EventType.EV_BRANCH and "branch" not in omitted:
            lines.append(f"branch cycle={event.cycle} commit={event.commit} pc=0x{event.pc:08x} value=0x{event.data:x}")
        elif event.event_type == EventType.EV_STORE and "store" not in omitted:
            lines.append(
                "store "
                f"cycle={event.cycle} commit={event.commit} pc=0x{event.pc:08x} "
                f"addr=0x{event.addr:08x} value=0x{event.data:08x}"
            )
        elif event.event_type == EventType.EV_MMIO_READ:
            if "mmio_read" not in omitted:
                value = "0x0" if "mmio_value" in omitted else f"0x{event.data:08x}"
                lines.append(
                    "mmio "
                    f"cycle={event.cycle} commit={event.commit} direction=read "
                    f"addr=0x{event.addr:08x} value={value}"
                )
        elif event.event_type == EventType.EV_MMIO_WRITE and "mmio_write" not in omitted:
            lines.append(
                "mmio "
                f"cycle={event.cycle} commit={event.commit} direction=write "
                f"addr=0x{event.addr:08x} value=0x{event.data:08x}"
            )
        elif event.event_type == EventType.EV_EXTERNAL_INPUT and "external_input" not in omitted:
            value = "0x0" if "external_input_value" in omitted else f"0x{event.data:08x}"
            lines.append(
                "input "
                f"cycle={event.cycle} commit={event.commit} input_id=input{event.addr} value={value}"
            )
        elif event.event_type in (EventType.EV_INTERRUPT_ENTER, EventType.EV_INTERRUPT_EXIT):
            if "interrupt_timing" not in omitted:
                state = "taken" if event.event_type == EventType.EV_INTERRUPT_ENTER else "return"
                lines.append(f"interrupt cycle={event.cycle} commit={event.commit} irq=timer0 state={state}")
    return "\n".join(lines) + "\n"


def trace_payload(result: RunResult) -> dict[str, object]:
    return {
        "benchmark": result.benchmark,
        "variant": result.variant,
        "property_id": result.property_id,
        "failure_signature": result.failure_signature,
        "events": [event.to_trace_dict() for event in result.events],
    }


def trace_json(result: RunResult) -> str:
    return json.dumps(trace_payload(result), indent=2, sort_keys=True)


def suite_json(results: list[RunResult]) -> str:
    return json.dumps({"runs": [trace_payload(result) for result in results]}, indent=2, sort_keys=True)


def run_self_tests() -> list[str]:
    messages: list[str] = []

    fixed_runs = run_suite(failing=False)
    assert all(not result.failed for result in fixed_runs), "a fixed benchmark unexpectedly failed"
    assert any(event.event_type == EventType.EV_MMIO_READ for result in fixed_runs for event in result.events)
    assert any(event.event_type == EventType.EV_MMIO_WRITE for result in fixed_runs for event in result.events)
    messages.append(f"PASS {len(fixed_runs)} fixed benchmark models run without property failures")

    failing_runs = run_suite(failing=True)
    assert len(failing_runs) == len(BENCHMARKS)
    for result in failing_runs:
        assert result.failed, f"{result.benchmark} did not emit property failure"
        assert _monotonic(event.seq for event in result.events), f"{result.benchmark} seq not monotonic"
        assert _monotonic(event.cycle for event in result.events), f"{result.benchmark} cycle not monotonic"
        expected = parse_capsule(capsule_fixture(result), source=f"{result.benchmark}:expected")
        observed = parse_capsule(capsule_fixture(result), source=f"{result.benchmark}:observed")
        compare = compare_capsules(expected, observed, mode="commit-index")
        assert compare.success, compare.format()
    messages.append(f"PASS {len(failing_runs)} failing benchmark capsules replay under commit-index comparison")

    sensor = run_benchmark("sensor_threshold_bug", failing=True)
    _assert_ablation_detected(sensor, {"mmio_value"}, "MMIO-read-value")
    messages.append("PASS MMIO-read-value ablation is detected")

    irq = run_benchmark("interrupt_race_bug", failing=True)
    _assert_ablation_detected(irq, {"interrupt_timing"}, "interrupt-timing")
    messages.append("PASS interrupt-timing ablation is detected")

    stack = run_benchmark("stack_corruption_bug", failing=True)
    _assert_ablation_detected(stack, {"store"}, "store-event")
    messages.append("PASS store-event ablation is detected")

    uart = run_benchmark("uart_command_bug", failing=True)
    _assert_ablation_detected(uart, {"external_input_value"}, "external-input-value")
    _assert_ablation_detected(uart, {"branch"}, "branch-event")
    messages.append("PASS UART external-input and branch ablations are detected")

    return messages


def _assert_ablation_detected(result: RunResult, omitted: set[str], label: str) -> None:
    expected = parse_capsule(capsule_fixture(result), source=f"{result.benchmark}:expected")
    observed = parse_capsule(capsule_fixture(result, omit=omitted), source=f"{result.benchmark}:ablation")
    compare = compare_capsules(expected, observed, mode="commit-index")
    assert not compare.success, f"{label} ablation should fail replay comparison for {result.benchmark}"


def _monotonic(values: Iterable[int]) -> bool:
    previous: int | None = None
    for value in values:
        if previous is not None and value < previous:
            return False
        previous = value
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the ReplayCapsule-RV model-level benchmark suite.")
    parser.add_argument("--self-test", action="store_true", help="run deterministic suite assertions")
    parser.add_argument("--dump-json", type=Path, help="write a failing trace JSON artifact")
    parser.add_argument("--dump-suite-json", type=Path, help="write all failing benchmark traces as JSON")
    parser.add_argument("--benchmark", choices=BENCHMARKS, default="sensor_threshold_bug")
    args = parser.parse_args(argv)

    if args.self_test:
        for message in run_self_tests():
            print(message)

    if args.dump_json:
        result = run_benchmark(args.benchmark, failing=True)
        args.dump_json.parent.mkdir(parents=True, exist_ok=True)
        args.dump_json.write_text(trace_json(result) + "\n", encoding="utf-8")
        print(f"WROTE {args.dump_json}")

    if args.dump_suite_json:
        results = run_suite(failing=True)
        args.dump_suite_json.parent.mkdir(parents=True, exist_ok=True)
        args.dump_suite_json.write_text(suite_json(results) + "\n", encoding="utf-8")
        print(f"WROTE {args.dump_suite_json}")

    if not args.self_test and not args.dump_json and not args.dump_suite_json:
        parser.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

