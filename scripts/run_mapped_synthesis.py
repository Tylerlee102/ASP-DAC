#!/usr/bin/env python3
"""Run real mapped FPGA flows and keep full-core failures visible."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/mapped_synthesis.csv"
OVERHEAD_CSV = REPO_ROOT / "results/processed/mapped_overhead.csv"
RAW_DIR = REPO_ROOT / "results/raw/mapped_synthesis"
OSS = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"

DESIGNS = {
    "replaycapsule_tiny_baseline": (
        "replaycapsule_tiny_baseline_wrapper",
        ("rtl/mapped/replaycapsule_tiny_baseline_wrapper.sv",),
        "tiny",
    ),
    "replaycapsule_recorder_tiny": (
        "replaycapsule_recorder_tiny_wrapper",
        (
            "rtl/event_pkg.sv",
            "rtl/event_tap.sv",
            "rtl/event_classifier.sv",
            "rtl/capsule_buffer.sv",
            "rtl/property_checker.sv",
            "rtl/event_slicer.sv",
            "rtl/hash_signature.sv",
            "rtl/replay_capsule_top.sv",
            "rtl/mapped/replaycapsule_recorder_tiny_wrapper.sv",
        ),
        "tiny",
    ),
    "picorv32": ("picorv32", ("third_party/picorv32/picorv32.v",), "full_core"),
    "replay_capsule_top": (
        "replay_capsule_top",
        (
            "rtl/event_pkg.sv",
            "rtl/event_tap.sv",
            "rtl/event_classifier.sv",
            "rtl/capsule_buffer.sv",
            "rtl/property_checker.sv",
            "rtl/event_slicer.sv",
            "rtl/hash_signature.sv",
            "rtl/replay_capsule_top.sv",
        ),
        "recorder_only",
    ),
    "picorv32_replaycapsule_wrapper": (
        "picorv32_replaycapsule_wrapper",
        (
            "third_party/picorv32/picorv32.v",
            "rtl/event_pkg.sv",
            "rtl/event_tap.sv",
            "rtl/event_classifier.sv",
            "rtl/capsule_buffer.sv",
            "rtl/property_checker.sv",
            "rtl/event_slicer.sv",
            "rtl/hash_signature.sv",
            "rtl/replay_capsule_top.sv",
            "rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
        ),
        "full_core",
    ),
}

FIELDS = ["target", "flow", "design", "lut", "ff", "bram", "dsp", "cells", "area_um2", "fmax_mhz", "wns", "tns", "power_mw", "status", "report_path", "notes"]
OVERHEAD_FIELDS = ["target", "flow", "metric", "baseline", "with_replaycapsule", "delta", "percent_overhead", "notes"]
YOSYS_TIMEOUT_SECONDS = 240
NEXTPNR_TIMEOUT_SECONDS = 180


def main() -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    yosys = _find_tool("yosys")
    rows: list[dict[str, str]] = []
    if not yosys:
        rows.extend(_todo_row("ecp5-85k", "yosys+synth_ecp5+nextpnr-ecp5", design, "missing yosys") for design in _full_core_designs())
        rows.extend(_todo_row("ice40-hx8k", "yosys+synth_ice40+nextpnr-ice40", design, "missing yosys") for design in DESIGNS)
    else:
        rows.extend(_run_ecp5_rows(yosys))
        rows.extend(_run_ice40_rows(yosys))
    _write_rows(rows)
    _write_overhead(rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OVERHEAD_CSV)}")
    return 0


def _run_ice40_rows(yosys: str) -> list[dict[str, str]]:
    nextpnr = _find_tool("nextpnr-ice40")
    flow = "yosys+synth_ice40+nextpnr-ice40"
    target = "ice40-hx8k"
    if not nextpnr:
        return [_todo_row(target, flow, design, "missing nextpnr-ice40") for design in DESIGNS]
    rows = []
    for name, (top, sources, _scope) in DESIGNS.items():
        rows.append(_run_ice40_design(name, top, sources, yosys, nextpnr))
    return rows


def _run_ecp5_rows(yosys: str) -> list[dict[str, str]]:
    nextpnr = _find_tool("nextpnr-ecp5")
    flow = "yosys+synth_ecp5+nextpnr-ecp5"
    target = "ecp5-85k"
    designs = _full_core_designs()
    if not nextpnr:
        return [_todo_row(target, flow, design, "missing nextpnr-ecp5") for design in designs]
    rows = []
    for name in designs:
        top, sources, _scope = DESIGNS[name]
        rows.append(_run_ecp5_design(name, top, sources, yosys, nextpnr))
    return rows


def _full_core_designs() -> tuple[str, ...]:
    return ("picorv32", "replay_capsule_top", "picorv32_replaycapsule_wrapper")


def _run_ice40_design(name: str, top: str, sources: tuple[str, ...], yosys: str, nextpnr: str) -> dict[str, str]:
    json_path = RAW_DIR / f"{name}_ice40.json"
    asc_path = RAW_DIR / f"{name}_ice40.asc"
    yosys_log = RAW_DIR / f"{name}_yosys_ice40.txt"
    nextpnr_log = RAW_DIR / f"{name}_nextpnr_ice40.txt"
    for stale in (json_path, asc_path):
        if stale.exists():
            stale.unlink()
    script = "read_verilog -sv -Irtl -Irtl/mapped " + " ".join(sources) + f"; synth_ice40 -top {top} -json {_rel(json_path)}"
    y = _run_tool([yosys, "-p", script], YOSYS_TIMEOUT_SECONDS)
    yosys_log.write_text(_clean(y.stdout), encoding="utf-8")
    if y.returncode != 0 or not json_path.exists():
        notes = "Yosys synth_ice40 timed out" if y.returncode == 124 else "Yosys synth_ice40 failed"
        return _fail_row("ice40-hx8k", "yosys+synth_ice40+nextpnr-ice40", name, yosys_log, notes)
    n = _run_tool([nextpnr, "--hx8k", "--package", "ct256", "--json", _rel(json_path), "--asc", _rel(asc_path)], NEXTPNR_TIMEOUT_SECONDS)
    nextpnr_log.write_text(_clean(n.stdout), encoding="utf-8")
    if n.returncode != 0 or not asc_path.exists():
        notes = "nextpnr-ice40 place-and-route timed out" if n.returncode == 124 else "nextpnr-ice40 place-and-route failed"
        return _fail_row("ice40-hx8k", "yosys+synth_ice40+nextpnr-ice40", name, nextpnr_log, notes)
    text = yosys_log.read_text(encoding="utf-8") + "\n" + nextpnr_log.read_text(encoding="utf-8")
    return _pass_row("ice40-hx8k", "yosys+synth_ice40+nextpnr-ice40", name, nextpnr_log, _ice40_metrics(text), "real mapped iCE40 place-and-route completed")


def _run_ecp5_design(name: str, top: str, sources: tuple[str, ...], yosys: str, nextpnr: str) -> dict[str, str]:
    json_path = RAW_DIR / f"{name}_ecp5.json"
    config_path = RAW_DIR / f"{name}_ecp5.config"
    yosys_log = RAW_DIR / f"{name}_yosys_ecp5.txt"
    nextpnr_log = RAW_DIR / f"{name}_nextpnr_ecp5.txt"
    for stale in (json_path, config_path):
        if stale.exists():
            stale.unlink()
    script = "read_verilog -sv -Irtl -Irtl/mapped " + " ".join(sources) + f"; synth_ecp5 -top {top} -json {_rel(json_path)}"
    y = _run_tool([yosys, "-p", script], YOSYS_TIMEOUT_SECONDS)
    yosys_log.write_text(_clean(y.stdout), encoding="utf-8")
    if y.returncode != 0 or not json_path.exists():
        notes = "Yosys synth_ecp5 timed out" if y.returncode == 124 else "Yosys synth_ecp5 failed"
        return _fail_row("ecp5-85k", "yosys+synth_ecp5+nextpnr-ecp5", name, yosys_log, notes)
    n = _run_tool(
        [
            nextpnr,
            "--85k",
            "--package",
            "CABGA381",
            "--freq",
            "50",
            "--json",
            _rel(json_path),
            "--textcfg",
            _rel(config_path),
        ],
        NEXTPNR_TIMEOUT_SECONDS,
    )
    nextpnr_log.write_text(_clean(n.stdout), encoding="utf-8")
    if n.returncode != 0 or not config_path.exists():
        notes = "nextpnr-ecp5 place-and-route timed out" if n.returncode == 124 else "nextpnr-ecp5 place-and-route failed"
        return _fail_row("ecp5-85k", "yosys+synth_ecp5+nextpnr-ecp5", name, nextpnr_log, notes)
    text = yosys_log.read_text(encoding="utf-8") + "\n" + nextpnr_log.read_text(encoding="utf-8")
    return _pass_row("ecp5-85k", "yosys+synth_ecp5+nextpnr-ecp5", name, nextpnr_log, _ecp5_metrics(text), "real mapped ECP5 place-and-route completed")


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
    lut = _last_cell_count("LUT4", text) or _last_cell_count("TRELLIS_SLICE", text)
    ff = _last_cell_count("TRELLIS_FF", text) or 0
    bram = _last_cell_count("DP16KD", text)
    dsp = _last_cell_count("MULT18X18D", text)
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


def _pass_row(target: str, flow: str, design: str, report: Path, metrics: dict[str, str], notes: str) -> dict[str, str]:
    return {
        "target": target,
        "flow": flow,
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


def _todo_row(target: str, flow: str, design: str, notes: str) -> dict[str, str]:
    return {
        "target": target,
        "flow": flow,
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


def _fail_row(target: str, flow: str, design: str, report: Path, notes: str) -> dict[str, str]:
    detail = _last_error_line(report)
    return {**_todo_row(target, flow, design, notes + (f": {detail}" if detail else "")), "status": "FAIL", "report_path": _rel(report)}


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_overhead(rows: list[dict[str, str]]) -> None:
    out_rows: list[dict[str, str]] = []
    out_rows.extend(
        _target_overheads(
            rows,
            "ice40-hx8k",
            "yosys+synth_ice40+nextpnr-ice40",
            "replaycapsule_tiny_baseline",
            "replaycapsule_recorder_tiny",
            "scoped tiny-wrapper overhead; not a full-core overhead claim",
        )
    )
    for target, flow in (
        ("ice40-hx8k", "yosys+synth_ice40+nextpnr-ice40"),
        ("ecp5-85k", "yosys+synth_ecp5+nextpnr-ecp5"),
    ):
        out_rows.extend(
            _target_overheads(
                rows,
                target,
                flow,
                "picorv32",
                "picorv32_replaycapsule_wrapper",
                "full-core mapped overhead only if both same-target rows PASS",
            )
        )
    with OVERHEAD_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OVERHEAD_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)


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


def _find_pass(rows: list[dict[str, str]], target: str, flow: str, design: str) -> dict[str, str] | None:
    return next((row for row in rows if row["target"] == target and row["flow"] == flow and row["design"] == design and row["status"] == "PASS"), None)


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
        "notes": notes,
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
    matches = re.findall(rf"^\s+(\d+)\s+{re.escape(cell_name)}\s*$", text, flags=re.MULTILINE)
    return int(matches[-1]) if matches else None


def _last_float(pattern: str, text: str) -> float | None:
    matches = re.findall(pattern, text)
    return float(matches[-1]) if matches else None


def _last_error_line(path: Path) -> str:
    if not path.exists():
        return ""
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip().startswith(("ERROR:", "TIMEOUT"))]
    return lines[-1] if lines else ""


def _clean(text: str) -> str:
    cleaned = text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")
    cleaned = cleaned.replace(str(Path.home()), ".").replace(str(Path.home()).replace("\\", "/"), ".")
    cleaned = re.sub(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+", ".", cleaned)
    return cleaned


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
