#!/usr/bin/env python3
"""Run focused FemtoRV32 ReplayCapsule capture/replay smokes."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OSS_CAD_SUITE = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"
BUILD_DIR = REPO_ROOT / ".tools/second_core_replay_smokes"
RAW_DIR = REPO_ROOT / "results/raw/second_core_replay_smokes"
OUT_CSV = REPO_ROOT / "results/processed/second_core_replay_smokes.csv"
OUT_MD = REPO_ROOT / "docs/second_core_replay_smokes.md"

FIELDS = [
    "benchmark",
    "variant",
    "capture_profile",
    "capture_mode",
    "expected_property",
    "sensor_value",
    "command_value",
    "watchdog_enable",
    "irq_after_command",
    "replay_packet_index",
    "status",
    "property_id",
    "capsule_count",
    "signature",
    "replay_sensor",
    "replay_command",
    "sensor_packet",
    "command_packet",
    "checker_consumed",
    "mmio_driver_hits",
    "raw_log",
    "notes",
]

SOURCES = (
    "tb/system/tb_femtorv32_wrapper_smoke.sv",
    "third_party/femtorv32/femtorv32_quark.v",
    "rtl/event_tap.sv",
    "rtl/event_classifier.sv",
    "rtl/capsule_buffer.sv",
    "rtl/property_checker.sv",
    "rtl/event_slicer.sv",
    "rtl/hash_signature.sv",
    "rtl/replay_capsule_top.sv",
    "rtl/replaycapsule_v1/rcv1_capsule_replay_checker.sv",
    "rtl/replaycapsule_v1/rcv1_mmio_replay_driver.sv",
    "rtl/rv32i_integration/femtorv32_replaycapsule_wrapper.sv",
)

INCLUDE_DIRS = ("rtl", "rtl/replaycapsule_v1", "rtl/rv32i_integration", "third_party/femtorv32")


@dataclass(frozen=True)
class Case:
    benchmark: str
    expected_property: int
    sensor_value: int
    command_value: int
    replay_packet_index: int
    variant: str = "failing"
    mem_variant: str = "failing"
    build_root: str = "firmware/build"
    watchdog_enable: int = 0
    irq_after_command: int = 0
    irq_pulse_cycles: int = 24
    max_cycles: int = 1200


@dataclass(frozen=True)
class CaptureProfile:
    name: str
    mode: int
    notes: str


CASES = (
    Case("sensor_threshold_bug", 3, 850, 0, 1),
    Case(
        "interrupt_race_bug",
        2,
        850,
        0,
        1,
        variant="fixed_with_wrapper_irq",
        mem_variant="fixed",
        irq_after_command=1,
        max_cycles=900,
    ),
    Case("mmio_ordering_bug", 5, 850, 0, 1),
    Case("stack_corruption_bug", 4, 850, 0, 1),
    Case("uart_command_bug", 1, 850, 85, 2),
    Case("watchdog_timeout_bug", 6, 850, 0, 1, watchdog_enable=1, max_cycles=1600),
    Case("commanded_actuator_limit_bug", 1, 850, 85, 1, build_root="firmware/build_expanded"),
    Case("late_config_sequence_bug", 5, 850, 0, 1, build_root="firmware/build_expanded"),
    Case("sensor_debounce_bug", 3, 850, 0, 1, build_root="firmware/build_expanded", max_cycles=1400),
    Case("status_clear_on_read_bug", 1, 850, 85, 1, build_root="firmware/build_expanded"),
    Case("platform2_status_window_bug", 1, 850, 85, 1, build_root="firmware/build_expanded"),
    Case("platform2_config_order_bug", 5, 850, 0, 1, build_root="firmware/build_expanded"),
    Case("environmental_controller_bug", 1, 650, 85, 1, build_root="firmware/build_expanded", max_cycles=1400),
    Case("power_rail_sequencer_bug", 5, 850, 85, 1, build_root="firmware/build_expanded", max_cycles=1400),
)

CAPTURE_PROFILES = (
    CaptureProfile("capture_all", 0, "v1 diagnostic capture-all profile"),
    CaptureProfile("mmio_interrupt", 1, "v1 replay-critical MMIO/interrupt/input/property capture profile"),
    CaptureProfile("property_aware", 2, "v1 property-aware nondeterministic/window capture profile"),
    CaptureProfile("replaycapsule_default", 3, "v1 ReplayCapsule default property-relevant capture profile"),
)

PASS_RE = re.compile(
    r"RC_FEMTO_REPLAY_SMOKE_PASS property=(?P<property>\d+) "
    r"count=(?P<count>\d+) signature=(?P<signature>[0-9a-fA-F]+) "
    r"replay_sensor=(?P<replay_sensor>-?\d+) "
    r"replay_command=(?P<replay_command>-?\d+) "
    r"capture_mode=(?P<capture_mode>\d+) "
    r"sensor_packet=(?P<sensor_packet>\d+) "
    r"command_packet=(?P<command_packet>\d+) "
    r"checker_consumed=(?P<checker_consumed>\d+) "
    r"mmio_driver_hits=(?P<mmio_driver_hits>\d+)"
)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    iverilog = _find_tool("iverilog")
    vvp = _find_tool("vvp")
    if not iverilog or not vvp:
        rows = [_blocked_row(case, profile, "missing iverilog/vvp") for case in CASES for profile in CAPTURE_PROFILES]
        _write_rows(rows)
        _write_doc(rows)
        print(f"WROTE {_rel(OUT_CSV)}")
        return 1

    simv = BUILD_DIR / "tb_femtorv32_wrapper_smoke.vvp"
    compile_log = RAW_DIR / "compile.txt"
    compile_result = _compile(iverilog, simv)
    compile_log.write_text(_clean(compile_result.stdout) or "compile passed without output\n", encoding="utf-8")
    if compile_result.returncode != 0:
        rows = [_blocked_row(case, profile, f"compile failed: {_rel(compile_log)}") for case in CASES for profile in CAPTURE_PROFILES]
        _write_rows(rows)
        _write_doc(rows)
        print(f"WROTE {_rel(OUT_CSV)}")
        return 1

    rows = [_run_case(vvp, simv, case, profile) for case in CASES for profile in CAPTURE_PROFILES]
    _write_rows(rows)
    _write_doc(rows)
    bad = [row for row in rows if row["status"] != "PASS"]
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OUT_MD)}")
    print(f"SECOND_CORE_REPLAY_SMOKES rows={len(rows)} bad={len(bad)}")
    return 1 if bad else 0


def _compile(iverilog: str, simv: Path) -> subprocess.CompletedProcess[str]:
    cmd = [iverilog, "-g2012", "-DBENCH"]
    for include_dir in INCLUDE_DIRS:
        cmd.extend(["-I", include_dir])
    cmd.extend(["-o", str(simv), *SOURCES])
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=_tool_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _run_case(vvp: str, simv: Path, case: Case, profile: CaptureProfile) -> dict[str, str]:
    raw_log = RAW_DIR / f"{case.benchmark}_{profile.name}.txt"
    memfile = f"{case.build_root}/{case.benchmark}/{case.mem_variant}.hex"
    cmd = [
        vvp,
        str(simv),
        f"+MEMFILE={memfile}",
        f"+EXPECTED_PROPERTY={case.expected_property}",
        f"+SENSOR_VALUE={case.sensor_value}",
        f"+COMMAND_VALUE={case.command_value}",
        f"+WATCHDOG_ENABLE={case.watchdog_enable}",
        f"+IRQ_AFTER_COMMAND={case.irq_after_command}",
        f"+IRQ_PULSE_CYCLES={case.irq_pulse_cycles}",
        f"+CAPTURE_MODE={profile.mode}",
        f"+MAX_CYCLES={case.max_cycles}",
        "+REPLAY_FROM_CAPTURE=1",
        f"+REPLAY_PACKET_INDEX={case.replay_packet_index}",
    ]
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=_tool_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    text = _clean(completed.stdout)
    raw_log.write_text(text, encoding="utf-8")
    match = PASS_RE.search(text)
    status = (
        "PASS"
        if completed.returncode == 0
        and match
        and int(match.group("property")) == case.expected_property
        and int(match.group("capture_mode")) == profile.mode
        and match.group("checker_consumed") == match.group("count")
        else "FAIL"
    )
    return {
        "benchmark": case.benchmark,
        "variant": case.variant,
        "capture_profile": profile.name,
        "capture_mode": str(profile.mode),
        "expected_property": str(case.expected_property),
        "sensor_value": str(case.sensor_value),
        "command_value": str(case.command_value),
        "watchdog_enable": str(case.watchdog_enable),
        "irq_after_command": str(case.irq_after_command),
        "replay_packet_index": str(case.replay_packet_index),
        "status": status,
        "property_id": match.group("property") if match else "NA",
        "capsule_count": match.group("count") if match else "NA",
        "signature": match.group("signature") if match else "NA",
        "replay_sensor": match.group("replay_sensor") if match else "NA",
        "replay_command": match.group("replay_command") if match else "NA",
        "sensor_packet": match.group("sensor_packet") if match else "NA",
        "command_packet": match.group("command_packet") if match else "NA",
        "checker_consumed": match.group("checker_consumed") if match else "NA",
        "mmio_driver_hits": match.group("mmio_driver_hits") if match else "NA",
        "raw_log": _rel(raw_log),
        "notes": (
            f"{profile.notes}; FemtoRV32 wrapper captured a property-fail capsule, reset, loaded captured packets into the scoped v1 RTL MMIO replay driver for replay reads, and the v1 RTL replay checker consumed the matching replay capsule stream"
            if status == "PASS"
            else _last_line(text)
        ),
    }


def _blocked_row(case: Case, profile: CaptureProfile, notes: str) -> dict[str, str]:
    return {
        "benchmark": case.benchmark,
        "variant": case.variant,
        "capture_profile": profile.name,
        "capture_mode": str(profile.mode),
        "expected_property": str(case.expected_property),
        "sensor_value": str(case.sensor_value),
        "command_value": str(case.command_value),
        "watchdog_enable": str(case.watchdog_enable),
        "irq_after_command": str(case.irq_after_command),
        "replay_packet_index": str(case.replay_packet_index),
        "status": "BLOCKED",
        "property_id": "NA",
        "capsule_count": "NA",
        "signature": "NA",
        "replay_sensor": "NA",
        "replay_command": "NA",
        "sensor_packet": "NA",
        "command_packet": "NA",
        "checker_consumed": "NA",
        "mmio_driver_hits": "NA",
        "raw_log": "",
        "notes": notes,
    }


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_doc(rows: list[dict[str, str]]) -> None:
    pass_rows = sum(1 for row in rows if row["status"] == "PASS")
    benchmarks = sorted({row["benchmark"] for row in rows})
    profiles = sorted({row["capture_profile"] for row in rows})
    lines = [
        "# Second-Core Replay Smokes",
        "",
        f"Status: `{pass_rows}/{len(rows)}` rows PASS.",
        "",
        "These focused Icarus rows run compiler-built firmware on the FemtoRV32 ReplayCapsule wrapper, capture a property-fail capsule, reset the wrapped core, load captured packets into a scoped v1 RTL MMIO replay driver for replay reads, and require the replay property, signature, and v1 RTL replay-checker-consumed capsule packets to match.",
        "",
        f"- Benchmarks covered: `{len(benchmarks)}` ({', '.join(benchmarks)})",
        f"- v1 capture profiles covered: `{len(profiles)}` ({', '.join(profiles)})",
        "",
        "| Benchmark | Capture profile | Status | Property | Capsule count | Checker consumed | MMIO driver hits | Signature | Replay sensor | Replay command |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['benchmark']}` | `{row['capture_profile']}` | `{row['status']}` | {row['property_id']} | "
            f"{row['capsule_count']} | {row['checker_consumed']} | {row['mmio_driver_hits']} | `{row['signature']}` | {row['replay_sensor']} | {row['replay_command']} |"
        )
    lines.extend(
        [
            "",
            "Allowed from this evidence:",
            "",
            f"- FemtoRV32 ReplayCapsule capture/replay smokes pass for {len(benchmarks)} base and expanded benchmark families across {len(profiles)} v1 capture profiles, including wrapper-level interrupt-boundary, profile2-MMIO, realistic-control, stack, command-limit, and watchdog cases.",
            "- A scoped v1 RTL MMIO replay driver stores captured 168-bit packets and supplies replay MMIO-read values during the FemtoRV32 replay phase.",
            "- The replay packet comparison is consumed by a reusable v1 RTL checker for the 168-bit capsule format used by the FemtoRV32 wrapper.",
            "- The second-core wrapper can reproduce captured property/signature/capsule evidence after reset for this focused set.",
            "",
            "Do not claim from this evidence:",
            "",
            "- A seeded v2 second-core ReplayCapsule evaluation.",
            "- Full v2 replay-consumer stimulus that drives FemtoRV32 core-facing MMIO/IRQ inputs.",
            "- True CPU interrupt/ISR replay on FemtoRV32; the vendored Quark core has no external interrupt/CSR machinery.",
            "- Cross-core equivalence, broad platform portability, mapped FPGA, or ASIC evidence for FemtoRV32.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _find_tool(name: str) -> str | None:
    system_tool = shutil.which(name)
    if system_tool:
        return system_tool
    local = OSS_CAD_SUITE / "bin" / f"{name}.exe"
    if local.exists():
        return str(local)
    return None


def _tool_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(OSS_CAD_SUITE / "bin"), str(OSS_CAD_SUITE / "lib"), env.get("PATH", "")])
    return env


def _clean(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + ("\n" if text else "")


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "no simulator output"


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
