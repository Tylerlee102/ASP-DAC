#!/usr/bin/env python3
"""Parse available synthesis reports into CSV without inventing missing data."""

from __future__ import annotations

import csv
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "results/raw"
OUT_CSV = REPO_ROOT / "results/processed/synthesis.csv"


def main() -> int:
    reports = sorted(RAW_DIR.glob("yosys_*.txt"))
    rows = [parse_report(path) for path in reports] if reports else [_todo("unknown", "missing synthesis reports")]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tool", "top", "status", "cells", "luts", "ffs", "brams", "fmax_mhz", "notes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {OUT_CSV}")
    return 0


def parse_report(path: Path) -> dict[str, str]:
    top = _top_from_path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    explicit_top = _first_str(r"TOP:\s+(\S+)", text)
    if explicit_top:
        top = explicit_top
    if "STATUS: TODO" in text:
        return _todo(top, "yosys not available")
    cells = _first_int(r"Number of cells:\s+(\d+)", text)
    return {
        "tool": "yosys",
        "top": top,
        "status": "MEASURED" if cells is not None else "TODO",
        "cells": str(cells) if cells is not None else "NA",
        "luts": "NA",
        "ffs": "NA",
        "brams": "NA",
        "fmax_mhz": "NA",
        "notes": "Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow",
    }


def _todo(top: str, notes: str) -> dict[str, str]:
    return {
        "tool": "yosys",
        "top": top,
        "status": "TODO",
        "cells": "NA",
        "luts": "NA",
        "ffs": "NA",
        "brams": "NA",
        "fmax_mhz": "NA",
        "notes": notes,
    }


def _top_from_path(path: Path) -> str:
    stem = path.stem
    return stem[6:] if stem.startswith("yosys_") else stem


def _first_int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def _first_str(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1) if match else None


if __name__ == "__main__":
    raise SystemExit(main())

