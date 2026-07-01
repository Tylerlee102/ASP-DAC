#!/usr/bin/env python3
"""Run focused standalone self-replay smokes for the reusable v2 RTL shell."""

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
BUILD_DIR = REPO_ROOT / ".tools/standalone_self_replay"
RAW_DIR = REPO_ROOT / "results/raw/standalone_self_replay_smokes"
OUT_CSV = REPO_ROOT / "results/processed/standalone_self_replay_smokes.csv"
OUT_MD = REPO_ROOT / "docs/standalone_self_replay_smokes.md"

FIELDS = [
    "benchmark",
    "variant",
    "firmware_image",
    "stimulus_family",
    "recorder_config",
    "recorder_config_select",
    "expected_property",
    "sensor_value",
    "command_value",
    "watchdog_enable",
    "irq_after_command",
    "status",
    "shell",
    "property_id",
    "captured_count",
    "source_sent_count",
    "consumed_count",
    "controller_done",
    "record_irq_entry_count",
    "replay_irq_entry_count",
    "signature",
    "raw_log",
    "notes",
]

SOURCES = (
    "tb/system/tb_picorv32_standalone_self_replay_smoke.sv",
    "third_party/picorv32/picorv32.v",
    "rtl/event_tap.sv",
    "rtl/event_classifier.sv",
    "rtl/capsule_buffer.sv",
    "rtl/property_checker.sv",
    "rtl/event_slicer.sv",
    "rtl/hash_signature.sv",
    "rtl/replay_capsule_top.sv",
    "rtl/replaycapsule_v2/rcv2_payload_hasher.sv",
    "rtl/replaycapsule_v2/rcv2_address_dictionary.sv",
    "rtl/replaycapsule_v2/rcv2_adaptive_window.sv",
    "rtl/replaycapsule_v2/rcv2_event_packer.sv",
    "rtl/replaycapsule_v2/rcv2_event_fifo_bram.sv",
    "rtl/replaycapsule_v2/rcv2_event_stream_fifo.sv",
    "rtl/replaycapsule_v2/rcv2_recorder.sv",
    "rtl/replaycapsule_v2/rcv2_mmio_replay_driver.sv",
    "rtl/replaycapsule_v2/rcv2_irq_replay_driver.sv",
    "rtl/replaycapsule_v2/rcv2_capsule_source.sv",
    "rtl/replaycapsule_v2/rcv2_replay_mode_controller.sv",
    "rtl/replaycapsule_v2/rcv2_replay_consumer.sv",
    "rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
    "rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv",
    "rtl/rv32i_integration/replaycapsule_v2_self_replay_soc.sv",
)

INCLUDE_DIRS = ("rtl", "rtl/replaycapsule_v2", "rtl/rv32i_integration", "third_party/picorv32")


@dataclass(frozen=True)
class Case:
    benchmark: str
    expected_property: int
    sensor_value: int
    command_value: int
    firmware_root: str = "firmware/build"
    firmware_ext: str = "mem"
    stimulus_family: str = "base_model_mem"
    watchdog_enable: int = 0
    irq_after_command: int = 0
    irq_pulse_cycles: int = 24
    max_cycles: int = 900
    mem_variant: str = "failing"


CASES = (
    Case("sensor_threshold_bug", 3, 850, 0),
    Case("interrupt_race_bug", 2, 850, 0, irq_after_command=1, max_cycles=1200),
    Case("mmio_ordering_bug", 5, 850, 0),
    Case("stack_corruption_bug", 4, 850, 0),
    Case("uart_command_bug", 1, 850, 85),
    Case("watchdog_timeout_bug", 6, 850, 0, watchdog_enable=1, max_cycles=1600),
    Case(
        "commanded_actuator_limit_bug",
        1,
        850,
        85,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="expanded_compiler_hex",
        max_cycles=2500,
    ),
    Case(
        "late_config_sequence_bug",
        5,
        850,
        0,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="expanded_compiler_hex",
        max_cycles=2500,
    ),
    Case(
        "sensor_debounce_bug",
        3,
        850,
        0,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="expanded_compiler_hex",
        max_cycles=3000,
    ),
    Case(
        "status_clear_on_read_bug",
        1,
        850,
        85,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="expanded_compiler_hex",
        max_cycles=2500,
    ),
    Case(
        "platform2_status_window_bug",
        1,
        850,
        85,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="expanded_profile2_compiler_hex",
        max_cycles=2500,
    ),
    Case(
        "platform2_config_order_bug",
        5,
        850,
        0,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="expanded_profile2_compiler_hex",
        max_cycles=2500,
    ),
    Case(
        "environmental_controller_bug",
        1,
        650,
        85,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="realistic_control_compiler_hex",
        max_cycles=3000,
    ),
    Case(
        "power_rail_sequencer_bug",
        5,
        850,
        85,
        firmware_root="firmware/build_expanded",
        firmware_ext="hex",
        stimulus_family="realistic_control_compiler_hex",
        max_cycles=3000,
    ),
)

CONFIGS = (("core", 0), ("hashed", 1), ("full", 2))
PASS_RE = re.compile(
    r"RC_STANDALONE_SELF_REPLAY_PASS shell=(?P<shell>[A-Za-z0-9_]+) "
    r"property=(?P<property>\d+) "
    r"captured=(?P<captured>\d+) sent=(?P<sent>\d+) consumed=(?P<consumed>\d+) "
    r"controller_done=(?P<controller_done>\d+) "
    r"irq_record=(?P<irq_record>\d+) irq_replay=(?P<irq_replay>\d+) "
    r"signature=(?P<signature>[0-9a-fA-F]+)"
)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    iverilog = _find_tool("iverilog")
    vvp = _find_tool("vvp")
    if not iverilog or not vvp:
        rows = [_blocked_row(case, config, select, "missing iverilog/vvp") for case in CASES for config, select in CONFIGS]
        _write_rows(rows)
        _write_doc(rows)
        print(f"WROTE {_rel(OUT_CSV)}")
        return 1

    simv = BUILD_DIR / "tb_picorv32_standalone_self_replay_smoke.vvp"
    compile_log = RAW_DIR / "compile.txt"
    compile_result = _compile(iverilog, simv)
    compile_log.write_text(_clean(compile_result.stdout) or "compile passed without output\n", encoding="utf-8")
    if compile_result.returncode != 0:
        rows = [_blocked_row(case, config, select, f"compile failed: {_rel(compile_log)}") for case in CASES for config, select in CONFIGS]
        _write_rows(rows)
        _write_doc(rows)
        print(f"WROTE {_rel(OUT_CSV)}")
        return 1

    rows = []
    for case in CASES:
        for config, select in CONFIGS:
            rows.append(_run_case(vvp, simv, case, config, select))
    _write_rows(rows)
    _write_doc(rows)
    bad = [row for row in rows if row["status"] != "PASS"]
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OUT_MD)}")
    print(f"STANDALONE_SELF_REPLAY rows={len(rows)} bad={len(bad)}")
    return 1 if bad else 0


def _compile(iverilog: str, simv: Path) -> subprocess.CompletedProcess[str]:
    cmd = [iverilog, "-g2012"]
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


def _run_case(vvp: str, simv: Path, case: Case, config: str, select: int) -> dict[str, str]:
    raw_log = RAW_DIR / f"{case.benchmark}_{config}.txt"
    memfile = _firmware_image_for_case(case)
    cmd = [
        vvp,
        str(simv),
        f"+MEMFILE={_rel(memfile)}",
        f"+EXPECTED_PROPERTY={case.expected_property}",
        f"+SENSOR_VALUE={case.sensor_value}",
        f"+COMMAND_VALUE={case.command_value}",
        f"+WATCHDOG_ENABLE={case.watchdog_enable}",
        f"+IRQ_AFTER_COMMAND={case.irq_after_command}",
        f"+IRQ_PULSE_CYCLES={case.irq_pulse_cycles}",
        f"+RECORDER_CONFIG_SELECT={select}",
        f"+MAX_CYCLES={case.max_cycles}",
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
        and match.group("captured") == match.group("sent")
        and match.group("captured") == match.group("consumed")
        and match.group("controller_done") == "1"
        and _irq_counts_ok(match, case)
        else "FAIL"
    )
    return {
        "benchmark": case.benchmark,
        "variant": "failing",
        "firmware_image": _rel(memfile),
        "stimulus_family": case.stimulus_family,
        "recorder_config": config,
        "recorder_config_select": str(select),
        "expected_property": str(case.expected_property),
        "sensor_value": str(case.sensor_value),
        "command_value": str(case.command_value),
        "watchdog_enable": str(case.watchdog_enable),
        "irq_after_command": str(case.irq_after_command),
        "status": status,
        "shell": match.group("shell") if match else "NA",
        "property_id": match.group("property") if match else "NA",
        "captured_count": match.group("captured") if match else "NA",
        "source_sent_count": match.group("sent") if match else "NA",
        "consumed_count": match.group("consumed") if match else "NA",
        "controller_done": match.group("controller_done") if match else "NA",
        "record_irq_entry_count": match.group("irq_record") if match else "NA",
        "replay_irq_entry_count": match.group("irq_replay") if match else "NA",
        "signature": match.group("signature") if match else "NA",
        "raw_log": _rel(raw_log),
        "notes": _pass_notes(case) if status == "PASS" else _last_line(text),
    }


def _blocked_row(case: Case, config: str, select: int, notes: str) -> dict[str, str]:
    return {
        "benchmark": case.benchmark,
        "variant": "failing",
        "firmware_image": "NA",
        "stimulus_family": case.stimulus_family,
        "recorder_config": config,
        "recorder_config_select": str(select),
        "expected_property": str(case.expected_property),
        "sensor_value": str(case.sensor_value),
        "command_value": str(case.command_value),
        "watchdog_enable": str(case.watchdog_enable),
        "irq_after_command": str(case.irq_after_command),
        "status": "BLOCKED",
        "shell": "NA",
        "property_id": "NA",
        "captured_count": "NA",
        "source_sent_count": "NA",
        "consumed_count": "NA",
        "controller_done": "NA",
        "record_irq_entry_count": "NA",
        "replay_irq_entry_count": "NA",
        "signature": "NA",
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
    families = sorted({row["stimulus_family"] for row in rows})
    lines = [
        "# Standalone Self-Replay Smokes",
        "",
        f"Status: `{pass_rows}/{len(rows)}` rows PASS.",
        "",
        "These focused Icarus rows instantiate the reusable v2 RTL self-replay SoC shell outside the Verilator top. Each row records a PicoRV32 v2 firmware failure through the shell's internal instruction memory, MMIO, IRQ, watchdog, replay-mode controller, and captured capsule source, resets the core, launches captured-store replay, and checks that the replay source and consumer consume the same captured replay-critical word count. IRQ rows additionally require matching nonzero PicoRV32 interrupt-handler entry counts in record and replay phases.",
        "",
        f"- Benchmarks covered: `{len(benchmarks)}` ({', '.join(benchmarks)})",
        f"- Stimulus image families: `{', '.join(families)}`",
        "",
        "| Benchmark | Config | Family | Status | Shell | Property | Captured | Sent | Consumed | Done | IRQ record | IRQ replay | Signature |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['benchmark']}` | `{row['recorder_config']}` | `{row['stimulus_family']}` | `{row['status']}` | `{row['shell']}` | "
            f"{row['property_id']} | {row['captured_count']} | {row['source_sent_count']} | {row['consumed_count']} | {row['controller_done']} | "
            f"{row['record_irq_entry_count']} | {row['replay_irq_entry_count']} | `{row['signature']}` |"
        )
    lines.extend(
        [
            "",
            "Allowed from this evidence:",
            "",
            "- The reusable RTL self-replay SoC shell works outside the Verilator top for the base model-backed benchmark families and expanded compiler-built benchmark families across core, hashed, and full v2 recorder configs.",
            "- The shell contains the focused instruction-memory, MMIO, IRQ, watchdog, replay-mode-controller, and captured-source path used by these rows.",
            "- The captured-store replay path can preserve replay-critical words across a reset and feed the RTL consumer without host-preloaded capsule words.",
            "- IRQ-triggered rows prove PicoRV32 interrupt-handler entry through nonzero, matching record/replay EOI counts.",
            "",
            "Do not claim from this evidence:",
            "",
            "- A board/silicon replay engine.",
            "- Arbitrary peripheral coverage beyond the focused memory/MMIO/IRQ/watchdog shell used by these rows.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _firmware_image_for_case(case: Case) -> Path:
    source = REPO_ROOT / case.firmware_root / case.benchmark / f"{case.mem_variant}.{case.firmware_ext}"
    if case.firmware_ext == "mem":
        return source
    if case.firmware_ext != "hex":
        raise ValueError(f"unsupported firmware image extension {case.firmware_ext!r}")
    out_dir = BUILD_DIR / "converted_mem"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{case.benchmark}_{case.mem_variant}.mem"
    _convert_reset_hex_to_mem(source, dest)
    return dest


def _convert_reset_hex_to_mem(source: Path, dest: Path) -> None:
    lines: list[str] = []
    for raw in source.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^@([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s*$", raw.strip())
        if not match:
            continue
        addr = int(match.group(1), 16)
        if addr < 0x80:
            continue
        if (addr - 0x80) % 4 != 0:
            raise ValueError(f"{_rel(source)} contains non-word-aligned address 0x{addr:08x}")
        index = (addr - 0x80) // 4
        lines.append(f"@{index:08x} {match.group(2)}")
    if not lines:
        raise ValueError(f"{_rel(source)} contains no reset-relative words")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _irq_counts_ok(match: re.Match[str], case: Case) -> bool:
    record = int(match.group("irq_record"))
    replay = int(match.group("irq_replay"))
    if case.irq_after_command:
        return record > 0 and replay > 0 and record == replay
    return True


def _pass_notes(case: Case) -> str:
    base = (
        "reusable RTL self-replay SoC shell captured replay-critical words, streamed them "
        "from the source after reset, and the replay consumer consumed the same count"
    )
    if case.irq_after_command:
        return base + "; nonzero matching record/replay PicoRV32 interrupt-handler entry counts were observed"
    return base


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
    return text.replace(str(REPO_ROOT), "<repo>").replace("\\", "/")


def _last_line(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "no output"


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
