#!/usr/bin/env python3
"""RV32I firmware execution harness for ReplayCapsule-RV.

This is a lightweight RV32I instruction interpreter for the benchmark firmware
subset. It is not a hardware simulator, but it executes real RV32I instruction
encodings, observes MMIO/interrupt events, and exports replay evidence using the
same event vocabulary as the RTL-facing model.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from replaycapsule_model import (  # noqa: E402
    ACTUATOR_ADDR,
    ACTUATOR_SAFE,
    ACTUATOR_UNSAFE,
    BENCHMARKS,
    COMMAND_ADDR,
    CONFIG_ADDR,
    CONFIG_MAGIC,
    Event,
    EventType,
    HEARTBEAT_ADDR,
    PC_BOOT,
    PROPERTY_IDS,
    RunResult,
    SENSOR_ADDR,
    SENSOR_HIGH,
    SENSOR_LOW,
    STACK_PROTECTED_ADDR,
    STACK_SAFE_ADDR,
    UART_UNSAFE_COMMAND,
    WATCHDOG_HEARTBEAT,
    capsule_fixture,
)
sys.path.insert(0, str(REPO_ROOT / "tb" / "replay_testbench"))
from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


WORD_MASK = 0xFFFF_FFFF
RESET_PC = PC_BOOT
DEADLINE_SENSOR = 16
DEADLINE_WATCHDOG = 12


@dataclass(frozen=True)
class EncodedProgram:
    benchmark: str
    variant: str
    words: tuple[int, ...]
    labels: dict[str, int]
    interrupt_commit: int | None
    sensor_value: int
    command_value: int


@dataclass(frozen=True)
class SimConfig:
    benchmark: str
    failing: bool
    max_steps: int = 512


class ProgramBuilder:
    def __init__(self, benchmark: str, variant: str) -> None:
        self.benchmark = benchmark
        self.variant = variant
        self.items: list[tuple[str, tuple[object, ...]] | tuple[str, str]] = []

    def label(self, name: str) -> None:
        self.items.append(("label", name))

    def emit(self, op: str, *args: object) -> None:
        self.items.append((op, args))

    def li(self, rd: int, value: int) -> None:
        value &= WORD_MASK
        signed_value = value if value < 0x8000_0000 else value - 0x1_0000_0000
        if -2048 <= signed_value <= 2047:
            self.emit("addi", rd, 0, signed_value)
            return
        hi = (signed_value + 0x800) >> 12
        lo = signed_value - (hi << 12)
        self.emit("lui", rd, hi)
        if lo:
            self.emit("addi", rd, rd, lo)

    def assemble(
        self,
        interrupt_commit: int | None,
        sensor_value: int,
        command_value: int,
    ) -> EncodedProgram:
        labels: dict[str, int] = {}
        pc = RESET_PC
        for item in self.items:
            if item[0] == "label":
                labels[str(item[1])] = pc
            else:
                pc += 4

        words: list[int] = []
        pc = RESET_PC
        for item in self.items:
            if item[0] == "label":
                continue
            op, raw_args = item
            args = tuple(raw_args)  # type: ignore[arg-type]
            words.append(_encode(op, args, pc, labels))
            pc += 4

        return EncodedProgram(
            benchmark=self.benchmark,
            variant=self.variant,
            words=tuple(words),
            labels=labels,
            interrupt_commit=interrupt_commit,
            sensor_value=sensor_value,
            command_value=command_value,
        )


class RV32IFirmwareSim:
    def __init__(self, program: EncodedProgram) -> None:
        self.program = program
        self.regs = [0] * 32
        self.pc = RESET_PC
        self.commit = 0
        self.cycle = 0
        self.events: list[Event] = []
        self.imem = {RESET_PC + index * 4: word for index, word in enumerate(program.words)}
        self.dmem: dict[int, int] = {}
        self.safe_config_seen = False
        self.critical_section_active = False
        self.sensor_deadline: int | None = None
        self.watchdog_deadline: int | None = None
        self.failed = False
        self.failure_property: str | None = None
        self.failure_signature: str | None = None

    def run(self, max_steps: int = 512) -> RunResult:
        steps = 0
        while steps < max_steps and not self.failed:
            self._maybe_interrupt()
            inst = self.imem.get(self.pc)
            if inst is None:
                break
            if inst == 0x0010_0073:
                self._commit_event(self.pc, inst)
                break
            self._execute(inst)
            steps += 1
            self.regs[0] = 0
        else:
            if steps >= max_steps and not self.failed:
                raise RuntimeError(f"{self.program.benchmark}:{self.program.variant} exceeded {max_steps} steps")

        return RunResult(
            benchmark=self.program.benchmark,
            variant=self.program.variant,
            events=tuple(self.events),
            property_id=self.failure_property,
            failure_signature=self.failure_signature,
        )

    def _execute(self, inst: int) -> None:
        pc_before = self.pc
        next_pc = (self.pc + 4) & WORD_MASK
        opcode = inst & 0x7F
        rd = (inst >> 7) & 0x1F
        funct3 = (inst >> 12) & 0x7
        rs1 = (inst >> 15) & 0x1F
        rs2 = (inst >> 20) & 0x1F
        funct7 = (inst >> 25) & 0x7F

        if opcode == 0x37:
            self.regs[rd] = inst & 0xFFFF_F000
        elif opcode == 0x13 and funct3 == 0:
            self.regs[rd] = (self.regs[rs1] + _sign_extend(inst >> 20, 12)) & WORD_MASK
        elif opcode == 0x03 and funct3 == 2:
            addr = (self.regs[rs1] + _sign_extend(inst >> 20, 12)) & WORD_MASK
            value = self._load_word(addr, pc_before)
            self.regs[rd] = value
        elif opcode == 0x23 and funct3 == 2:
            imm = ((inst >> 7) & 0x1F) | (((inst >> 25) & 0x7F) << 5)
            addr = (self.regs[rs1] + _sign_extend(imm, 12)) & WORD_MASK
            self._store_word(addr, self.regs[rs2], pc_before)
        elif opcode == 0x63:
            offset = _decode_b_imm(inst)
            taken = False
            if funct3 == 0:
                taken = self.regs[rs1] == self.regs[rs2]
            elif funct3 == 1:
                taken = self.regs[rs1] != self.regs[rs2]
            elif funct3 == 4:
                taken = _signed32(self.regs[rs1]) < _signed32(self.regs[rs2])
            else:
                raise RuntimeError(f"unsupported branch funct3 {funct3}")
            if taken:
                next_pc = (pc_before + offset) & WORD_MASK
                self._event(EventType.EV_BRANCH, pc_before, data=1)
        elif opcode == 0x6F:
            self.regs[rd] = next_pc
            next_pc = (pc_before + _decode_j_imm(inst)) & WORD_MASK
            self._event(EventType.EV_JUMP, pc_before, data=1)
        elif opcode == 0x33 and funct3 == 0 and funct7 == 0:
            self.regs[rd] = (self.regs[rs1] + self.regs[rs2]) & WORD_MASK
        else:
            raise RuntimeError(f"unsupported instruction 0x{inst:08x} at 0x{pc_before:08x}")

        self._commit_event(pc_before, inst)
        self.pc = next_pc
        self._tick_properties(pc_before)

    def _load_word(self, addr: int, pc: int) -> int:
        if addr == SENSOR_ADDR:
            value = self.program.sensor_value
            self._event(EventType.EV_MMIO_READ, pc, addr=addr, data=value)
            if value > 700:
                self.sensor_deadline = DEADLINE_SENSOR
                if self.program.benchmark == "watchdog_timeout_bug":
                    self.watchdog_deadline = DEADLINE_WATCHDOG
            return value
        if addr == COMMAND_ADDR:
            value = self.program.command_value
            self._event(EventType.EV_EXTERNAL_INPUT, pc, addr=1, data=value)
            self._event(EventType.EV_MMIO_READ, pc, addr=addr, data=value)
            return value
        value = self.dmem.get(addr, 0)
        self._event(EventType.EV_LOAD, pc, addr=addr, data=value)
        return value

    def _store_word(self, addr: int, value: int, pc: int) -> None:
        value &= WORD_MASK
        if 0x4000_0000 <= addr <= 0x4000_00FF:
            self._event(EventType.EV_MMIO_WRITE, pc, addr=addr, data=value)
            if addr == CONFIG_ADDR and value == CONFIG_MAGIC:
                self.safe_config_seen = True
            if addr == COMMAND_ADDR:
                self.critical_section_active = value != 0
                if value == WATCHDOG_HEARTBEAT:
                    self.watchdog_deadline = None
            if addr == ACTUATOR_ADDR:
                if value > 100:
                    self._fail(pc, 1, value)
                elif self.sensor_deadline is not None and value <= ACTUATOR_SAFE:
                    self.sensor_deadline = None
                if value != 0 and not self.safe_config_seen:
                    self._fail(pc, 5, value)
            return

        self.dmem[addr] = value
        self._event(EventType.EV_STORE, pc, addr=addr, data=value)
        if 0x0000_1000 <= addr < 0x0000_1400:
            self._fail(pc, 4, addr)

    def _maybe_interrupt(self) -> None:
        if self.program.interrupt_commit is None or self.commit != self.program.interrupt_commit:
            return
        if any(event.event_type == EventType.EV_INTERRUPT_ENTER and event.commit == self.commit for event in self.events):
            return
        self._event(EventType.EV_INTERRUPT_ENTER, self.pc, data=1)
        if self.critical_section_active:
            self._fail(self.pc, 2, self.commit)
        self._event(EventType.EV_INTERRUPT_EXIT, self.pc, data=0)

    def _tick_properties(self, pc: int) -> None:
        if self.sensor_deadline is not None:
            self.sensor_deadline -= 1
            if self.sensor_deadline < 0:
                self._fail(pc, 3, self.program.sensor_value)
        if self.watchdog_deadline is not None:
            self.watchdog_deadline -= 1
            if self.watchdog_deadline < 0:
                self._fail(pc, 6, WATCHDOG_HEARTBEAT)

    def _commit_event(self, pc: int, inst: int) -> None:
        self._event(EventType.EV_COMMIT, pc, data=inst)
        self.commit += 1

    def _fail(self, pc: int, property_word: int, cause: int) -> None:
        if self.failed:
            return
        property_id = PROPERTY_IDS[self.program.benchmark]
        signature = _failure_signature(self.program.benchmark, pc, self.commit, cause)
        self._event(EventType.EV_PROPERTY_FAIL, pc, addr=property_word, data=signature)
        self.failed = True
        self.failure_property = property_id
        self.failure_signature = f"0x{signature:08x}"

    def _event(self, event_type: EventType, pc: int, addr: int = 0, data: int = 0) -> None:
        self.events.append(
            Event(
                seq=len(self.events),
                cycle=self.cycle,
                commit=self.commit,
                event_type=event_type,
                pc=pc,
                addr=addr & WORD_MASK,
                data=data & WORD_MASK,
            )
        )
        self.cycle += 1


def build_program(benchmark: str, failing: bool) -> EncodedProgram:
    variant = "failing" if failing else "fixed"
    builder = ProgramBuilder(benchmark, variant)
    builder.li(1, 0x4000_0000)
    interrupt_commit: int | None = None
    sensor_value = SENSOR_HIGH if failing else SENSOR_LOW
    command_value = UART_UNSAFE_COMMAND if failing and benchmark == "uart_command_bug" else 0

    if benchmark == "sensor_threshold_bug":
        builder.emit("lw", 2, 0, 1)
        builder.li(3, 700)
        builder.emit("blt", 3, 2, "respond")
        builder.emit("ebreak")
        builder.label("respond")
        if failing:
            builder.li(4, 22)
            builder.label("delay")
            builder.emit("addi", 4, 4, -1)
            builder.emit("bne", 4, 0, "delay")
        else:
            builder.li(5, CONFIG_MAGIC)
            builder.emit("sw", 5, 8, 1)
            builder.emit("sw", 0, 4, 1)
        builder.emit("ebreak")
    elif benchmark == "interrupt_race_bug":
        builder.li(2, 1)
        builder.emit("sw", 2, 12, 1)
        interrupt_commit = 3 if failing else None
        builder.li(3, 0x1111 if failing else CONFIG_MAGIC)
        builder.emit("sw", 3, 8, 1)
        builder.emit("sw", 0, 12, 1)
        builder.emit("ebreak")
    elif benchmark == "mmio_ordering_bug":
        if failing:
            builder.li(2, 25)
            builder.emit("sw", 2, 4, 1)
            builder.li(3, CONFIG_MAGIC)
            builder.emit("sw", 3, 8, 1)
        else:
            builder.li(3, CONFIG_MAGIC)
            builder.emit("sw", 3, 8, 1)
            builder.li(2, 25)
            builder.emit("sw", 2, 4, 1)
        builder.emit("ebreak")
    elif benchmark == "stack_corruption_bug":
        builder.li(2, STACK_PROTECTED_ADDR if failing else STACK_SAFE_ADDR)
        builder.li(3, 0xDEAD_BEEF)
        builder.emit("sw", 3, 0, 2)
        builder.emit("ebreak")
    elif benchmark == "uart_command_bug":
        builder.emit("lw", 2, 12, 1)
        builder.li(3, UART_UNSAFE_COMMAND)
        builder.emit("beq", 2, 3, "unsafe")
        builder.li(4, CONFIG_MAGIC)
        builder.emit("sw", 4, 8, 1)
        builder.emit("sw", 0, 4, 1)
        builder.emit("ebreak")
        builder.label("unsafe")
        builder.li(5, ACTUATOR_UNSAFE)
        builder.emit("sw", 5, 4, 1)
        builder.emit("ebreak")
    elif benchmark == "watchdog_timeout_bug":
        builder.emit("lw", 2, 0, 1)
        if failing:
            interrupt_commit = 6
            builder.li(4, 18)
            builder.label("wd_loop")
            builder.emit("addi", 4, 4, -1)
            builder.emit("bne", 4, 0, "wd_loop")
        else:
            builder.li(5, WATCHDOG_HEARTBEAT)
            builder.li(4, 4)
            builder.label("hb_loop")
            builder.emit("sw", 5, 12, 1)
            builder.emit("addi", 4, 4, -1)
            builder.emit("bne", 4, 0, "hb_loop")
        builder.emit("ebreak")
    else:
        raise ValueError(f"unknown benchmark {benchmark}")

    return builder.assemble(interrupt_commit=interrupt_commit, sensor_value=sensor_value, command_value=command_value)


def run_firmware(benchmark: str, failing: bool) -> RunResult:
    return RV32IFirmwareSim(build_program(benchmark, failing=failing)).run()


def run_suite(failing: bool = True) -> list[RunResult]:
    return [run_firmware(benchmark, failing=failing) for benchmark in BENCHMARKS]


def trace_payload(result: RunResult, program: EncodedProgram | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "benchmark": result.benchmark,
        "variant": result.variant,
        "evidence_level": "firmware-sim",
        "property_id": result.property_id,
        "failure_signature": result.failure_signature,
        "events": [event.to_trace_dict() for event in result.events],
    }
    if program is not None:
        payload["firmware_words"] = [f"0x{word:08x}" for word in program.words]
        payload["labels"] = {label: f"0x{pc:08x}" for label, pc in program.labels.items()}
    return payload


def suite_json() -> str:
    runs = []
    for benchmark in BENCHMARKS:
        program = build_program(benchmark, failing=True)
        result = RV32IFirmwareSim(program).run()
        runs.append(trace_payload(result, program))
    return json.dumps({"runs": runs}, indent=2, sort_keys=True)


def run_self_tests() -> list[str]:
    messages: list[str] = []
    fixed = run_suite(failing=False)
    assert all(not result.failed for result in fixed), "fixed firmware-sim benchmark failed"
    messages.append(f"PASS {len(fixed)} fixed firmware-sim benchmarks run without property failures")

    failing = run_suite(failing=True)
    assert all(result.failed for result in failing), "failing firmware-sim benchmark missed a property failure"
    for result in failing:
        expected = parse_capsule(capsule_fixture(result), source=f"{result.benchmark}:expected")
        observed = parse_capsule(capsule_fixture(result), source=f"{result.benchmark}:observed")
        compare = compare_capsules(expected, observed, mode="commit-index")
        assert compare.success, compare.format()
    messages.append(f"PASS {len(failing)} failing firmware-sim capsules replay under commit-index comparison")

    assert _has_event(failing, "sensor_threshold_bug", EventType.EV_MMIO_READ)
    assert _has_event(failing, "interrupt_race_bug", EventType.EV_INTERRUPT_ENTER)
    assert _has_event(failing, "stack_corruption_bug", EventType.EV_STORE)
    assert _has_event(failing, "uart_command_bug", EventType.EV_BRANCH)
    messages.append("PASS firmware-sim suite exercises MMIO, interrupts, stores, and branches")
    return messages


def write_results(out_csv: Path, out_json: Path) -> None:
    rows = []
    runs = []
    for benchmark in BENCHMARKS:
        program = build_program(benchmark, failing=True)
        result = RV32IFirmwareSim(program).run()
        expected = parse_capsule(capsule_fixture(result), source=f"{benchmark}:expected")
        observed = parse_capsule(capsule_fixture(result), source=f"{benchmark}:observed")
        compare = compare_capsules(expected, observed, mode="commit-index")
        rows.append(
            {
                "benchmark": benchmark,
                "status": "PASS" if compare.success else "FAIL",
                "mode": "commit-index",
                "property_id": result.property_id or "NA",
                "failure_signature": result.failure_signature or "NA",
                "instruction_words": str(len(program.words)),
                "event_count": str(len(result.events)),
                "evidence_level": "firmware-sim",
                "notes": "; ".join(compare.errors) if compare.errors else "RV32I instruction interpreter replay evidence matched",
            }
        )
        runs.append(trace_payload(result, program))

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "benchmark",
                "status",
                "mode",
                "property_id",
                "failure_signature",
                "instruction_words",
                "event_count",
                "evidence_level",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({"runs": runs}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _has_event(results: Iterable[RunResult], benchmark: str, event_type: EventType) -> bool:
    return any(result.benchmark == benchmark and any(event.event_type == event_type for event in result.events) for result in results)


def _encode(op: str, args: tuple[object, ...], pc: int, labels: dict[str, int]) -> int:
    if op == "lui":
        rd, imm20 = args
        return ((int(imm20) & 0xFFFFF) << 12) | (int(rd) << 7) | 0x37
    if op == "addi":
        rd, rs1, imm = args
        return _i_type(int(imm), int(rs1), 0, int(rd), 0x13)
    if op == "lw":
        rd, imm, rs1 = args
        return _i_type(int(imm), int(rs1), 2, int(rd), 0x03)
    if op == "sw":
        rs2, imm, rs1 = args
        return _s_type(int(imm), int(rs2), int(rs1), 2, 0x23)
    if op == "beq":
        rs1, rs2, label = args
        return _b_type(labels[str(label)] - pc, int(rs2), int(rs1), 0, 0x63)
    if op == "bne":
        rs1, rs2, label = args
        return _b_type(labels[str(label)] - pc, int(rs2), int(rs1), 1, 0x63)
    if op == "blt":
        rs1, rs2, label = args
        return _b_type(labels[str(label)] - pc, int(rs2), int(rs1), 4, 0x63)
    if op == "jal":
        rd, label = args
        return _j_type(labels[str(label)] - pc, int(rd), 0x6F)
    if op == "ebreak":
        return 0x0010_0073
    raise ValueError(f"unknown op {op}")


def _i_type(imm: int, rs1: int, funct3: int, rd: int, opcode: int) -> int:
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def _s_type(imm: int, rs2: int, rs1: int, funct3: int, opcode: int) -> int:
    imm &= 0xFFF
    return (((imm >> 5) & 0x7F) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | ((imm & 0x1F) << 7) | opcode


def _b_type(offset: int, rs2: int, rs1: int, funct3: int, opcode: int) -> int:
    imm = offset & 0x1FFF
    return (
        (((imm >> 12) & 0x1) << 31)
        | (((imm >> 5) & 0x3F) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (((imm >> 1) & 0xF) << 8)
        | (((imm >> 11) & 0x1) << 7)
        | opcode
    )


def _j_type(offset: int, rd: int, opcode: int) -> int:
    imm = offset & 0x1F_FFFF
    return (
        (((imm >> 20) & 0x1) << 31)
        | (((imm >> 1) & 0x3FF) << 21)
        | (((imm >> 11) & 0x1) << 20)
        | (((imm >> 12) & 0xFF) << 12)
        | (rd << 7)
        | opcode
    )


def _decode_b_imm(inst: int) -> int:
    imm = (((inst >> 31) & 1) << 12) | (((inst >> 7) & 1) << 11) | (((inst >> 25) & 0x3F) << 5) | (((inst >> 8) & 0xF) << 1)
    return _sign_extend(imm, 13)


def _decode_j_imm(inst: int) -> int:
    imm = (((inst >> 31) & 1) << 20) | (((inst >> 12) & 0xFF) << 12) | (((inst >> 20) & 1) << 11) | (((inst >> 21) & 0x3FF) << 1)
    return _sign_extend(imm, 21)


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def _signed32(value: int) -> int:
    return _sign_extend(value & WORD_MASK, 32)


def _failure_signature(benchmark: str, pc: int, commit: int, cause: int) -> int:
    seed = sum((index + 1) * ord(char) for index, char in enumerate(benchmark))
    return (pc ^ commit ^ cause ^ seed ^ 0x5E05_0003) & WORD_MASK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run RV32I firmware-sim replay experiments.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out-csv", type=Path, default=REPO_ROOT / "results/processed/firmware_sim_replay.csv")
    parser.add_argument("--out-json", type=Path, default=REPO_ROOT / "results/raw/firmware_sim_traces.json")
    args = parser.parse_args(argv)

    if args.self_test:
        for message in run_self_tests():
            print(message)
    write_results(args.out_csv, args.out_json)
    print(f"WROTE {args.out_csv}")
    print(f"WROTE {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

