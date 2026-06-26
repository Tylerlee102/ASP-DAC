#!/usr/bin/env python3
"""Attempt a real mapped FPGA flow; never label generic synthesis as mapped."""

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
        (
            "rtl/mapped/replaycapsule_tiny_baseline_wrapper.sv",
        ),
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
    ),
    "picorv32": ("picorv32", ("third_party/picorv32/picorv32.v",)),
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
    ),
}

FIELDS = ["target", "flow", "design", "lut", "ff", "bram", "dsp", "cells", "area_um2", "fmax_mhz", "wns", "tns", "power_mw", "status", "report_path", "notes"]
OVERHEAD_FIELDS = ["target", "flow", "metric", "baseline", "with_replaycapsule", "delta", "percent_overhead", "notes"]
YOSYS_TIMEOUT_SECONDS = 180
NEXTPNR_TIMEOUT_SECONDS = 120


def main() -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    yosys = _find_tool("yosys")
    nextpnr = _find_tool("nextpnr-ice40")
    if not yosys or not nextpnr:
        missing = ", ".join(name for name, tool in (("yosys", yosys), ("nextpnr-ice40", nextpnr)) if not tool)
        rows = [_todo_row(design, f"missing {missing}") for design in DESIGNS]
        _write_rows(rows)
        _write_overhead(rows)
        print(f"WROTE {_rel(OUT_CSV)}")
        print(f"WROTE {_rel(OVERHEAD_CSV)}")
        return 0

    rows = [_run_design(name, top, sources, yosys, nextpnr) for name, (top, sources) in DESIGNS.items()]
    _write_rows(rows)
    _write_overhead(rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OVERHEAD_CSV)}")
    return 0


def _run_design(name: str, top: str, sources: tuple[str, ...], yosys: str, nextpnr: str) -> dict[str, str]:
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
        return _fail_row(name, yosys_log, notes)
    n = _run_tool(
        [nextpnr, "--hx8k", "--package", "ct256", "--json", _rel(json_path), "--asc", _rel(asc_path)],
        NEXTPNR_TIMEOUT_SECONDS,
    )
    nextpnr_log.write_text(_clean(n.stdout), encoding="utf-8")
    if n.returncode != 0 or not asc_path.exists():
        notes = "nextpnr-ice40 place-and-route timed out" if n.returncode == 124 else "nextpnr-ice40 place-and-route failed"
        return _fail_row(name, nextpnr_log, notes)

    text = yosys_log.read_text(encoding="utf-8") + "\n" + nextpnr_log.read_text(encoding="utf-8")
    lut = _last_cell_count("SB_LUT4", text)
    ff = sum(
        value
        for value in (
            _last_cell_count("SB_DFF", text),
            _last_cell_count("SB_DFFE", text),
            _last_cell_count("SB_DFFR", text),
            _last_cell_count("SB_DFFS", text),
            _last_cell_count("SB_DFFER", text),
            _last_cell_count("SB_DFFES", text),
            _last_cell_count("SB_DFFSR", text),
            _last_cell_count("SB_DFFSS", text),
            _last_cell_count("SB_DFFESS", text),
        )
        if value is not None
    )
    bram = _last_cell_count("SB_RAM40_4K", text)
    fmax = _last_float(r"Max frequency for clock.*?:\s+([0-9.]+)", text)
    return {
        "target": "ice40-hx8k",
        "flow": "yosys+synth_ice40+nextpnr-ice40",
        "design": name,
        "lut": str(lut) if lut is not None else "NA",
        "ff": str(ff),
        "bram": str(bram) if bram is not None else "NA",
        "dsp": "0",
        "cells": "NA",
        "area_um2": "NA",
        "fmax_mhz": f"{fmax:.2f}" if fmax is not None else "NA",
        "wns": "NA",
        "tns": "NA",
        "power_mw": "NA",
        "status": "PASS",
        "report_path": _rel(nextpnr_log),
        "notes": "real mapped iCE40 place-and-route completed",
    }


def _todo_row(design: str, notes: str) -> dict[str, str]:
    return {
        "target": "ice40-hx8k",
        "flow": "yosys+synth_ice40+nextpnr-ice40",
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


def _fail_row(design: str, report: Path, notes: str) -> dict[str, str]:
    detail = _last_error_line(report)
    return {**_todo_row(design, notes + (f": {detail}" if detail else "")), "status": "FAIL", "report_path": _rel(report)}


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_overhead(rows: list[dict[str, str]]) -> None:
    tiny_baseline = next((row for row in rows if row["design"] == "replaycapsule_tiny_baseline" and row["status"] == "PASS"), None)
    tiny_recorder = next((row for row in rows if row["design"] == "replaycapsule_recorder_tiny" and row["status"] == "PASS"), None)
    baseline = next((row for row in rows if row["design"] == "picorv32" and row["status"] == "PASS"), None)
    wrapped = next((row for row in rows if row["design"] == "picorv32_replaycapsule_wrapper" and row["status"] == "PASS"), None)
    out_rows: list[dict[str, str]] = []
    for metric in ("lut", "ff", "bram", "fmax_mhz"):
        out_rows.append(
            _overhead_row(
                "replaycapsule_tiny_baseline",
                tiny_baseline,
                "replaycapsule_recorder_tiny",
                tiny_recorder,
                metric,
                "scoped tiny-wrapper overhead; not a full-core overhead claim",
            )
        )
    for metric in ("lut", "ff", "bram", "fmax_mhz"):
        out_rows.append(
            _overhead_row(
                "picorv32",
                baseline,
                "picorv32_replaycapsule_wrapper",
                wrapped,
                metric,
                "requires full-core mapped_synthesis.csv PASS rows",
            )
        )
    with OVERHEAD_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OVERHEAD_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)


def _overhead_row(
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
            "target": "ice40-hx8k",
            "flow": "yosys+synth_ice40+nextpnr-ice40",
            "metric": f"{baseline_design}_to_{replay_design}_{metric}",
            "baseline": baseline[metric],
            "with_replaycapsule": replay[metric],
            "delta": f"{delta:.2f}",
            "percent_overhead": f"{pct:.2f}",
            "notes": notes,
        }
    return {
        "target": "ice40-hx8k",
        "flow": "yosys+synth_ice40+nextpnr-ice40",
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
        return subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env=_tool_env(),
            timeout=timeout_seconds,
        )
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
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip().startswith(("ERROR:", "TIMEOUT"))
    ]
    return lines[-1] if lines else ""


def _clean(text: str) -> str:
    cleaned = text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")
    short_docs = "DOCUME" + "~1"
    short_project = "NEWPRO" + "~1"
    return re.sub(rf"[A-Za-z]:\\Users\\[^\\]+\\OneDrive\\{short_docs}\\{short_project}", ".", cleaned)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
