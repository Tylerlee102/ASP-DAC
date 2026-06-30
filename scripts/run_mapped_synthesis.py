#!/usr/bin/env python3
"""Run real mapped FPGA flows for board-scoped full-core overhead evidence."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import check_mapped_recorder_presence


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/mapped_synthesis.csv"
OVERHEAD_CSV = REPO_ROOT / "results/processed/mapped_overhead.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/full_core_mapped_summary.csv"
RAW_DIR = REPO_ROOT / "results/raw/mapped_synthesis"
OSS = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"
ECP5_LPF = REPO_ROOT / "constraints/ecp5_board.lpf"

FULL_CORE_MEMORY_WORDS = 2048
FULL_CORE_CAPSULE_DEPTH = 16
YOSYS_TIMEOUT_SECONDS = 300
NEXTPNR_TIMEOUT_SECONDS = 240

FIELDS = [
    "target",
    "flow",
    "design",
    "lut",
    "ff",
    "bram",
    "dsp",
    "cells",
    "area_um2",
    "fmax_mhz",
    "wns",
    "tns",
    "power_mw",
    "status",
    "report_path",
    "notes",
]
OVERHEAD_FIELDS = ["target", "flow", "metric", "baseline", "with_replaycapsule", "delta", "percent_overhead", "notes"]
SUMMARY_FIELDS = [
    "status",
    "target",
    "flow",
    "baseline_design",
    "replay_design",
    "baseline_status",
    "replay_status",
    "recorder_presence_status",
    "memory_words",
    "capsule_depth",
    "overhead_claim_allowed",
    "first_blocker",
    "notes",
]


@dataclass(frozen=True)
class Design:
    name: str
    top: str
    sources: tuple[str, ...]
    scope: str


@dataclass(frozen=True)
class Target:
    name: str
    flow: str
    family: str
    suffix: str
    nextpnr_name: str
    nextpnr_args: tuple[str, ...]
    output_ext: str


RTL_COMMON = (
    "rtl/event_pkg.sv",
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
    "rtl/replaycapsule_v2/rcv2_recorder.sv",
    "rtl/replaycapsule_v2/rcv2_mmio_replay_driver.sv",
    "rtl/replaycapsule_v2/rcv2_irq_replay_driver.sv",
    "rtl/replaycapsule_v2/rcv2_replay_consumer.sv",
)

DESIGNS = {
    "full_core_baseline_board": Design(
        "full_core_baseline_board",
        "full_core_baseline_board_top",
        (
            "third_party/picorv32/picorv32.v",
            "rtl/mapped/mapped_memory.sv",
            "rtl/mapped/full_core_baseline_board_top.sv",
        ),
        "full_core_board",
    ),
    "full_core_replaycapsule_board": Design(
        "full_core_replaycapsule_board",
        "full_core_replaycapsule_board_top",
        (
            "third_party/picorv32/picorv32.v",
            *RTL_COMMON,
            "rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
            "rtl/mapped/mapped_memory.sv",
            "rtl/mapped/full_core_replaycapsule_board_top.sv",
        ),
        "full_core_board",
    ),
    "replaycapsule_tiny_baseline": Design(
        "replaycapsule_tiny_baseline",
        "replaycapsule_tiny_baseline_wrapper",
        ("rtl/mapped/replaycapsule_tiny_baseline_wrapper.sv",),
        "tiny",
    ),
    "replaycapsule_recorder_tiny": Design(
        "replaycapsule_recorder_tiny",
        "replaycapsule_recorder_tiny_wrapper",
        (
            *RTL_COMMON,
            "rtl/mapped/replaycapsule_recorder_tiny_wrapper.sv",
        ),
        "tiny",
    ),
}

FULL_CORE_DESIGNS = ("full_core_baseline_board", "full_core_replaycapsule_board")
TINY_DESIGNS = ("replaycapsule_tiny_baseline", "replaycapsule_recorder_tiny")

FULL_CORE_TARGETS = (
    Target(
        "ecp5-85k",
        "yosys+synth_ecp5+nextpnr-ecp5",
        "ecp5",
        "ecp5_85k",
        "nextpnr-ecp5",
        ("--85k", "--package", "CABGA381", "--freq", "50"),
        "config",
    ),
    Target(
        "ecp5-45k",
        "yosys+synth_ecp5+nextpnr-ecp5",
        "ecp5",
        "ecp5_45k",
        "nextpnr-ecp5",
        ("--45k", "--package", "CABGA381", "--freq", "50"),
        "config",
    ),
    Target(
        "ice40-hx8k",
        "yosys+synth_ice40+nextpnr-ice40",
        "ice40",
        "ice40_hx8k",
        "nextpnr-ice40",
        ("--hx8k", "--package", "ct256", "--freq", "50"),
        "asc",
    ),
)

TINY_TARGET = Target(
    "ice40-hx8k",
    "yosys+synth_ice40+nextpnr-ice40",
    "ice40",
    "ice40_hx8k",
    "nextpnr-ice40",
    ("--hx8k", "--package", "ct256", "--freq", "50"),
    "asc",
)


def main() -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    yosys = _find_tool("yosys")
    rows: list[dict[str, str]] = []

    if not yosys:
        for target in FULL_CORE_TARGETS[:2]:
            rows.extend(_todo_row(target, design, "missing yosys") for design in FULL_CORE_DESIGNS)
        rows.extend(_todo_row(TINY_TARGET, design, "missing yosys") for design in TINY_DESIGNS)
    else:
        rows.extend(_run_full_core_targets(yosys))
        rows.extend(_run_tiny_rows(yosys))

    _write_rows(rows)
    overhead_rows = _write_overhead(rows)
    presence_rows = check_mapped_recorder_presence.write_presence_csv(REPO_ROOT)
    _write_summary(rows, presence_rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OVERHEAD_CSV)}")
    print(f"WROTE {_rel(check_mapped_recorder_presence.OUT_CSV)}")
    print(f"WROTE {_rel(SUMMARY_CSV)}")
    _print_full_core_result(rows, overhead_rows, presence_rows)
    return 0


def _run_full_core_targets(yosys: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, target in enumerate(FULL_CORE_TARGETS):
        if target.family == "ice40" and not _ice40_full_core_expected_to_fit(rows):
            rows.extend(_todo_row(target, design, "iCE40 full-core board attempt skipped; larger ECP5 target did not produce fit evidence") for design in FULL_CORE_DESIGNS)
            continue
        nextpnr = _find_tool(target.nextpnr_name)
        if not nextpnr:
            rows.extend(_todo_row(target, design, f"missing {target.nextpnr_name}") for design in FULL_CORE_DESIGNS)
            continue
        for design_name in FULL_CORE_DESIGNS:
            rows.append(_run_design(target, DESIGNS[design_name], yosys, nextpnr))
        if _target_has_full_core_pair(rows, target):
            break
        if index == 0:
            print("ECP5 85K full-core board pair did not both PASS; trying ECP5 45K.")
        elif index == 1:
            print("ECP5 45K full-core board pair did not both PASS; checking whether iCE40 full-core attempt is reasonable.")
    return rows


def _run_tiny_rows(yosys: str) -> list[dict[str, str]]:
    nextpnr = _find_tool(TINY_TARGET.nextpnr_name)
    if not nextpnr:
        return [_todo_row(TINY_TARGET, design, f"missing {TINY_TARGET.nextpnr_name}") for design in TINY_DESIGNS]
    return [_run_design(TINY_TARGET, DESIGNS[design], yosys, nextpnr) for design in TINY_DESIGNS]


def _run_design(target: Target, design: Design, yosys: str, nextpnr: str) -> dict[str, str]:
    json_path = RAW_DIR / f"{design.name}_{target.suffix}.json"
    bitstream_path = RAW_DIR / f"{design.name}_{target.suffix}.{target.output_ext}"
    yosys_log = RAW_DIR / f"{design.name}_yosys_{target.suffix}.txt"
    nextpnr_log = RAW_DIR / f"{design.name}_nextpnr_{target.suffix}.txt"
    for stale in (json_path, bitstream_path):
        if stale.exists():
            stale.unlink()

    script = _yosys_script(target, design, json_path)
    y = _run_tool([yosys, "-p", script], YOSYS_TIMEOUT_SECONDS)
    yosys_log.write_text(_clean(y.stdout), encoding="utf-8")
    if y.returncode != 0 or not json_path.exists():
        notes = f"Yosys {target.family} synthesis timed out" if y.returncode == 124 else f"Yosys {target.family} synthesis failed"
        return _fail_row(target, design.name, yosys_log, notes)
    _sanitize_file(json_path)

    command = [nextpnr, *target.nextpnr_args, "--json", _rel(json_path)]
    if target.family == "ecp5":
        command.extend(["--textcfg", _rel(bitstream_path)])
        if ECP5_LPF.exists():
            command.extend(["--lpf", _rel(ECP5_LPF)])
    else:
        command.extend(["--asc", _rel(bitstream_path)])
    n = _run_tool(command, NEXTPNR_TIMEOUT_SECONDS)
    nextpnr_log.write_text(_clean(n.stdout), encoding="utf-8")
    if n.returncode != 0 or not bitstream_path.exists():
        notes = f"{target.nextpnr_name} place-and-route timed out" if n.returncode == 124 else f"{target.nextpnr_name} place-and-route failed"
        return _fail_row(target, design.name, nextpnr_log, notes)

    text = yosys_log.read_text(encoding="utf-8") + "\n" + nextpnr_log.read_text(encoding="utf-8")
    metrics = _ecp5_metrics(text) if target.family == "ecp5" else _ice40_metrics(text)
    notes = _notes_for_pass(target, design)
    return _pass_row(target, design.name, nextpnr_log, metrics, notes)


def _yosys_script(target: Target, design: Design, json_path: Path) -> str:
    read = "read_verilog -sv -Irtl -Irtl/mapped -Irtl/rv32i_integration -Ithird_party/picorv32 " + " ".join(design.sources)
    if target.family == "ecp5":
        synth = f"synth_ecp5 -top {design.top} -json {_rel(json_path)}"
    else:
        synth = f"synth_ice40 -top {design.top} -json {_rel(json_path)}"
    return f"{read}; {synth}"


def _notes_for_pass(target: Target, design: Design) -> str:
    if design.scope == "full_core_board":
        return (
            f"real mapped {target.name} board-level place-and-route completed; "
            f"memory_words={FULL_CORE_MEMORY_WORDS}; allowed top-level IO only"
        )
    return f"real mapped {target.name} place-and-route completed"


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_overhead(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out_rows: list[dict[str, str]] = []
    out_rows.extend(
        _target_overheads(
            rows,
            TINY_TARGET.name,
            TINY_TARGET.flow,
            "replaycapsule_tiny_baseline",
            "replaycapsule_recorder_tiny",
            "scoped tiny-wrapper overhead; not a full-core overhead claim",
        )
    )
    for target in FULL_CORE_TARGETS:
        out_rows.extend(
            _target_overheads(
                rows,
                target.name,
                target.flow,
                "full_core_baseline_board",
                "full_core_replaycapsule_board",
                "full-core board-level mapped overhead from same-target place-and-route PASS rows",
            )
        )
    with OVERHEAD_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OVERHEAD_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)
    return out_rows


def _target_overheads(
    rows: list[dict[str, str]],
    target: str,
    flow: str,
    baseline_design: str,
    replay_design: str,
    notes: str,
) -> list[dict[str, str]]:
    baseline = _find_pass(rows, target, flow, baseline_design)
    replay = _find_pass(rows, target, flow, replay_design)
    return [_overhead_row(target, flow, baseline_design, baseline, replay_design, replay, metric, notes) for metric in ("lut", "ff", "bram", "fmax_mhz")]


def _write_summary(rows: list[dict[str, str]], presence_rows: list[dict[str, str]]) -> None:
    summary = _full_core_summary_row(rows, presence_rows)
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerow(summary)


def _full_core_summary_row(rows: list[dict[str, str]], presence_rows: list[dict[str, str]]) -> dict[str, str]:
    for target in FULL_CORE_TARGETS:
        baseline = _find_row(rows, target.name, target.flow, "full_core_baseline_board")
        replay = _find_row(rows, target.name, target.flow, "full_core_replaycapsule_board")
        presence = _find_presence(presence_rows, target.name, target.flow)
        if (
            baseline is not None
            and replay is not None
            and baseline.get("status") == "PASS"
            and replay.get("status") == "PASS"
            and presence is not None
            and presence.get("status") == "PASS"
        ):
            return {
                "status": "PASS",
                "target": target.name,
                "flow": target.flow,
                "baseline_design": "full_core_baseline_board",
                "replay_design": "full_core_replaycapsule_board",
                "baseline_status": "PASS",
                "replay_status": "PASS",
                "recorder_presence_status": "PASS",
                "memory_words": str(FULL_CORE_MEMORY_WORDS),
                "capsule_depth": str(FULL_CORE_CAPSULE_DEPTH),
                "overhead_claim_allowed": "yes",
                "first_blocker": "none",
                "notes": "same-target full-core board-level mapped overhead is available",
            }

    blocker = _first_full_core_blocker(rows, presence_rows)
    target = blocker.get("target", FULL_CORE_TARGETS[0].name)
    flow = blocker.get("flow", FULL_CORE_TARGETS[0].flow)
    baseline = _find_row(rows, target, flow, "full_core_baseline_board")
    replay = _find_row(rows, target, flow, "full_core_replaycapsule_board")
    presence = _find_presence(presence_rows, target, flow)
    return {
        "status": "BLOCKED",
        "target": target,
        "flow": flow,
        "baseline_design": "full_core_baseline_board",
        "replay_design": "full_core_replaycapsule_board",
        "baseline_status": baseline.get("status", "MISSING") if baseline else "MISSING",
        "replay_status": replay.get("status", "MISSING") if replay else "MISSING",
        "recorder_presence_status": presence.get("status", "MISSING") if presence else "MISSING",
        "memory_words": str(FULL_CORE_MEMORY_WORDS),
        "capsule_depth": str(FULL_CORE_CAPSULE_DEPTH),
        "overhead_claim_allowed": "no",
        "first_blocker": blocker.get("notes", "same-target full-core board rows did not both PASS"),
        "notes": "full-core mapped overhead remains unavailable",
    }


def _first_full_core_blocker(rows: list[dict[str, str]], presence_rows: list[dict[str, str]]) -> dict[str, str]:
    for target in FULL_CORE_TARGETS:
        for design in FULL_CORE_DESIGNS:
            row = _find_row(rows, target.name, target.flow, design)
            if row is None:
                return {"target": target.name, "flow": target.flow, "notes": f"{design} row missing"}
            if row.get("status") != "PASS":
                return row
        presence = _find_presence(presence_rows, target.name, target.flow)
        if presence is None or presence.get("status") != "PASS":
            return {
                "target": target.name,
                "flow": target.flow,
                "notes": (presence or {}).get("notes", "recorder presence row missing or failed"),
            }
    return {"target": FULL_CORE_TARGETS[0].name, "flow": FULL_CORE_TARGETS[0].flow, "notes": "unknown blocker"}


def _find_presence(rows: list[dict[str, str]], target: str, flow: str) -> dict[str, str] | None:
    return next((row for row in rows if row.get("target") == target and row.get("flow") == flow), None)


def _find_pass(rows: list[dict[str, str]], target: str, flow: str, design: str) -> dict[str, str] | None:
    row = _find_row(rows, target, flow, design)
    return row if row and row.get("status") == "PASS" else None


def _find_row(rows: list[dict[str, str]], target: str, flow: str, design: str) -> dict[str, str] | None:
    return next((row for row in rows if row["target"] == target and row["flow"] == flow and row["design"] == design), None)


def _target_has_full_core_pair(rows: list[dict[str, str]], target: Target) -> bool:
    return all(_find_pass(rows, target.name, target.flow, design) is not None for design in FULL_CORE_DESIGNS)


def _ice40_full_core_expected_to_fit(rows: list[dict[str, str]]) -> bool:
    ecp5_rows = [
        row
        for row in rows
        if row.get("design") in FULL_CORE_DESIGNS
        and row.get("target", "").startswith("ecp5")
        and row.get("status") == "PASS"
    ]
    if len(ecp5_rows) >= 2:
        return all(_safe_float(row.get("lut")) <= 6500 and _safe_float(row.get("ff")) <= 7000 for row in ecp5_rows)
    failed_for_resources = any("no BELs remaining" in row.get("notes", "") for row in rows)
    return not failed_for_resources


def _overhead_row(
    target: str,
    flow: str,
    baseline_design: str,
    baseline: dict[str, str] | None,
    replay_design: str,
    replay: dict[str, str] | None,
    metric: str,
    notes: str,
) -> dict[str, str]:
    if baseline and replay and baseline[metric] != "NA" and replay[metric] != "NA":
        b = float(baseline[metric])
        w = float(replay[metric])
        delta = w - b
        pct = (delta / b * 100.0) if b else 0.0
        return {
            "target": target,
            "flow": flow,
            "metric": f"{baseline_design}_to_{replay_design}_{metric}",
            "baseline": baseline[metric],
            "with_replaycapsule": replay[metric],
            "delta": f"{delta:.2f}",
            "percent_overhead": f"{pct:.2f}",
            "notes": notes,
        }
    return {
        "target": target,
        "flow": flow,
        "metric": f"{baseline_design}_to_{replay_design}_{metric}",
        "baseline": "NA",
        "with_replaycapsule": "NA",
        "delta": "NA",
        "percent_overhead": "NA",
        "notes": notes + "; requires both same-target rows to PASS",
    }


def _pass_row(target: Target, design: str, report: Path, metrics: dict[str, str], notes: str) -> dict[str, str]:
    return {
        "target": target.name,
        "flow": target.flow,
        "design": design,
        "lut": metrics.get("lut", "NA"),
        "ff": metrics.get("ff", "NA"),
        "bram": metrics.get("bram", "NA"),
        "dsp": metrics.get("dsp", "NA"),
        "cells": metrics.get("cells", "NA"),
        "area_um2": "NA",
        "fmax_mhz": metrics.get("fmax_mhz", "NA"),
        "wns": "NA",
        "tns": "NA",
        "power_mw": "NA",
        "status": "PASS",
        "report_path": _rel(report),
        "notes": notes,
    }


def _todo_row(target: Target, design: str, notes: str) -> dict[str, str]:
    return {
        "target": target.name,
        "flow": target.flow,
        "design": design,
        "lut": "NA",
        "ff": "NA",
        "bram": "NA",
        "dsp": "NA",
        "cells": "NA",
        "area_um2": "NA",
        "fmax_mhz": "NA",
        "wns": "NA",
        "tns": "NA",
        "power_mw": "NA",
        "status": "BLOCKED",
        "report_path": "NA",
        "notes": notes,
    }


def _fail_row(target: Target, design: str, report: Path, notes: str) -> dict[str, str]:
    detail = _last_error_line(report)
    return {**_todo_row(target, design, notes + (f": {detail}" if detail else "")), "status": "FAIL", "report_path": _rel(report)}


def _ice40_metrics(text: str) -> dict[str, str]:
    lut = _last_cell_count("SB_LUT4", text)
    ff = sum(value for value in (_last_cell_count(name, text) for name in ("SB_DFF", "SB_DFFE", "SB_DFFR", "SB_DFFS", "SB_DFFER", "SB_DFFES", "SB_DFFSR", "SB_DFFSS", "SB_DFFESS")) if value is not None)
    bram = _last_cell_count("SB_RAM40_4K", text)
    fmax = _last_float(r"Max frequency for clock.*?:\s+([0-9.]+)", text)
    return {
        "lut": str(lut) if lut is not None else "NA",
        "ff": str(ff),
        "bram": str(bram) if bram is not None else "NA",
        "dsp": "0",
        "cells": "NA",
        "fmax_mhz": f"{fmax:.2f}" if fmax is not None else "NA",
    }


def _ecp5_metrics(text: str) -> dict[str, str]:
    lut = _last_int(r"Total LUT4s:\s+(\d+)\s*/", text) or _last_cell_count("LUT4", text) or _last_cell_count("TRELLIS_SLICE", text)
    ff = _last_int(r"TRELLIS_FF:\s+(\d+)\s*/", text) or _last_cell_count("TRELLIS_FF", text) or 0
    bram = _last_int(r"DP16KD:\s+(\d+)\s*/", text) or _last_cell_count("DP16KD", text)
    dsp = _last_int(r"MULT18X18D:\s+(\d+)\s*/", text) or _last_cell_count("MULT18X18D", text)
    fmax = _last_float(r"Max frequency for clock.*?:\s+([0-9.]+)", text)
    cells = _last_float(r"Number of cells:\s+([0-9.]+)", text)
    return {
        "lut": str(lut) if lut is not None else "NA",
        "ff": str(ff),
        "bram": str(bram) if bram is not None else "0",
        "dsp": str(dsp) if dsp is not None else "0",
        "cells": f"{cells:.0f}" if cells is not None else "NA",
        "fmax_mhz": f"{fmax:.2f}" if fmax is not None else "NA",
    }


def _find_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    local = OSS / "bin" / f"{name}.exe"
    return str(local) if local.exists() else None


def _run_tool(command: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, env=_tool_env(), timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        output += f"\nTIMEOUT after {timeout_seconds} seconds\n"
        return subprocess.CompletedProcess(command, 124, output)


def _tool_env() -> dict[str, str]:
    env = dict(os.environ)
    if OSS.exists():
        env["PATH"] = os.pathsep.join([str(OSS / "bin"), str(OSS / "lib"), env.get("PATH", "")])
    return env


def _last_cell_count(cell_name: str, text: str) -> int | None:
    matches = re.findall(rf"^\s+(?:{re.escape(cell_name)}\s+(\d+)|(\d+)\s+{re.escape(cell_name)})\s*$", text, flags=re.MULTILINE)
    if matches:
        last = matches[-1]
        value = last[0] or last[1]
        return int(value)
    matches = re.findall(rf"{re.escape(cell_name)}:\s+(\d+)\s*/", text)
    return int(matches[-1]) if matches else None


def _last_float(pattern: str, text: str) -> float | None:
    matches = re.findall(pattern, text)
    return float(matches[-1]) if matches else None


def _last_int(pattern: str, text: str) -> int | None:
    matches = re.findall(pattern, text)
    return int(matches[-1]) if matches else None


def _last_error_line(path: Path) -> str:
    if not path.exists():
        return ""
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip().startswith(("ERROR:", "TIMEOUT"))]
    return lines[-1] if lines else ""


def _safe_float(value: str | None) -> float:
    try:
        return float(value or "nan")
    except ValueError:
        return float("nan")


def _clean(text: str) -> str:
    cleaned = text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")
    cleaned = cleaned.replace(str(Path.home()), ".").replace(str(Path.home()).replace("\\", "/"), ".")
    cloud_dir = "One" + "Drive"
    cleaned = re.sub(r"\.?[/\\]?" + cloud_dir + r"[/\\]DOCUME~1[/\\]NEWPRO~1[/\\]TOOLS~1[/\\]OSS-CA~1[/\\]OSS-CA~1", ".tools/oss-cad-suite/oss-cad-suite", cleaned)
    cleaned = cleaned.replace(cloud_dir, "WORKSPACE")
    cleaned = re.sub(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+", ".", cleaned)
    return cleaned


def _sanitize_file(path: Path) -> None:
    if not path.exists():
        return
    path.write_text(_clean(path.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _print_full_core_result(rows: list[dict[str, str]], overhead_rows: list[dict[str, str]], presence_rows: list[dict[str, str]]) -> None:
    summary = _full_core_summary_row(rows, presence_rows)
    print(f"FULL_CORE_MAPPED_STATUS {summary['status']}: {summary['first_blocker']}")
    measured = [
        row for row in overhead_rows
        if row["metric"].startswith("full_core_baseline_board_to_full_core_replaycapsule_board")
        and row["percent_overhead"] != "NA"
    ]
    for row in measured:
        print(f"FULL_CORE_OVERHEAD {row['target']} {row['metric']} {row['percent_overhead']}")


if __name__ == "__main__":
    raise SystemExit(main())
