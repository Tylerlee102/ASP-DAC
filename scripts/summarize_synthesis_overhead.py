#!/usr/bin/env python3
"""Summarize measured generic synthesis overhead without inventing FPGA metrics."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS_CSV = REPO_ROOT / "results/processed/synthesis.csv"
OUT_CSV = REPO_ROOT / "results/processed/synthesis_overhead.csv"

BASELINE_TOP = "picorv32"
INSTRUMENTED_TOP = "picorv32_replaycapsule_wrapper"
RECORDER_TOP = "replay_capsule_top"

FIELDNAMES = [
    "tool",
    "baseline_top",
    "instrumented_top",
    "status",
    "baseline_cells",
    "instrumented_cells",
    "generic_cell_delta",
    "generic_cell_overhead_percent",
    "record_side_top",
    "record_side_cells",
    "luts",
    "ffs",
    "brams",
    "fmax_mhz",
    "notes",
]


def main() -> int:
    rows = _read_rows(SYNTHESIS_CSV)
    summary = _summarize(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(summary)
    print(f"WROTE {OUT_CSV}")
    return 0


def _summarize(rows: list[dict[str, str]]) -> dict[str, str]:
    baseline = _row_for(rows, BASELINE_TOP)
    instrumented = _row_for(rows, INSTRUMENTED_TOP)
    recorder = _row_for(rows, RECORDER_TOP)
    baseline_cells = _measured_cells(baseline)
    instrumented_cells = _measured_cells(instrumented)
    recorder_cells = _measured_cells(recorder)
    tool = _tool_name(baseline, instrumented, recorder)

    if baseline_cells is None or instrumented_cells is None:
        return {
            "tool": tool,
            "baseline_top": BASELINE_TOP,
            "instrumented_top": INSTRUMENTED_TOP,
            "status": "TODO",
            "baseline_cells": "NA",
            "instrumented_cells": "NA",
            "generic_cell_delta": "NA",
            "generic_cell_overhead_percent": "NA",
            "record_side_top": RECORDER_TOP,
            "record_side_cells": str(recorder_cells) if recorder_cells is not None else "NA",
            "luts": "NA",
            "ffs": "NA",
            "brams": "NA",
            "fmax_mhz": "NA",
            "notes": "Missing measured generic cells for baseline or instrumented top",
        }

    delta = instrumented_cells - baseline_cells
    overhead_percent = (delta / baseline_cells) * 100 if baseline_cells else 0.0
    return {
        "tool": tool,
        "baseline_top": BASELINE_TOP,
        "instrumented_top": INSTRUMENTED_TOP,
        "status": "MEASURED",
        "baseline_cells": str(baseline_cells),
        "instrumented_cells": str(instrumented_cells),
        "generic_cell_delta": str(delta),
        "generic_cell_overhead_percent": f"{overhead_percent:.2f}",
        "record_side_top": RECORDER_TOP,
        "record_side_cells": str(recorder_cells) if recorder_cells is not None else "NA",
        "luts": "NA",
        "ffs": "NA",
        "brams": "NA",
        "fmax_mhz": "NA",
        "notes": "Generic Yosys cell-count context only; mapped FPGA overhead requires LUT/FF/BRAM/Fmax reports",
    }


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _row_for(rows: list[dict[str, str]], top: str) -> dict[str, str] | None:
    return next((row for row in rows if row.get("top") == top), None)


def _measured_cells(row: dict[str, str] | None) -> int | None:
    if not row or row.get("status") != "MEASURED":
        return None
    try:
        return int(row.get("cells", ""))
    except ValueError:
        return None


def _tool_name(*rows: dict[str, str] | None) -> str:
    tools = sorted({row.get("tool", "") for row in rows if row and row.get("tool")})
    return "+".join(tools) if tools else "yosys"


if __name__ == "__main__":
    raise SystemExit(main())
