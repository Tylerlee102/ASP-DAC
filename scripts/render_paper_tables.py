#!/usr/bin/env python3
"""Render paper table sources from generated result CSVs."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS_CSV = REPO_ROOT / "results/processed/synthesis.csv"
SYNTHESIS_OVERHEAD_CSV = REPO_ROOT / "results/processed/synthesis_overhead.csv"
OUT_TABLE = REPO_ROOT / "paper/figures/table01_synthesis_resources.md"

SYNTHESIS_ORDER = [
    "picorv32",
    "replay_capsule_top",
    "picorv32_replaycapsule_wrapper",
]

DISPLAY_NAMES = {
    "picorv32": "Baseline PicoRV32",
    "replay_capsule_top": "ReplayCapsule record-side top",
    "picorv32_replaycapsule_wrapper": "PicoRV32 + ReplayCapsule wrapper",
}


def main() -> int:
    synthesis_rows = _ordered_synthesis_rows(_read_rows(SYNTHESIS_CSV))
    overhead_rows = _read_rows(SYNTHESIS_OVERHEAD_CSV)
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.write_text(_render_table(synthesis_rows, overhead_rows), encoding="utf-8")
    print(f"WROTE {OUT_TABLE}")
    return 0


def _render_table(synthesis_rows: list[dict[str, str]], overhead_rows: list[dict[str, str]]) -> str:
    lines = [
        "# Table 1. Synthesis Resource Status",
        "",
        "Generated from `../../results/processed/synthesis.csv` and "
        "`../../results/processed/synthesis_overhead.csv`.",
        "",
        "Generic Yosys cell counts are measured from real local reports. "
        "Mapped FPGA LUT/FF/BRAM/Fmax fields remain `NA` until a mapped flow exists.",
        "",
        "| Design | Tool | Status | Generic cells | LUTs | FFs | BRAMs | Fmax MHz | Notes |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    if synthesis_rows:
        for row in synthesis_rows:
            lines.append(
                "| {design} | {tool} | {status} | {cells} | {luts} | {ffs} | {brams} | {fmax} | {notes} |".format(
                    design=_escape_cell(DISPLAY_NAMES.get(row.get("top", ""), row.get("top", "unknown"))),
                    tool=_escape_cell(row.get("tool", "NA")),
                    status=_escape_cell(row.get("status", "NA")),
                    cells=_escape_cell(row.get("cells", "NA")),
                    luts=_escape_cell(row.get("luts", "NA")),
                    ffs=_escape_cell(row.get("ffs", "NA")),
                    brams=_escape_cell(row.get("brams", "NA")),
                    fmax=_escape_cell(row.get("fmax_mhz", "NA")),
                    notes=_escape_cell(row.get("notes", "")),
                )
            )
    else:
        lines.append("| No synthesis rows | NA | TODO | NA | NA | NA | NA | NA | Missing synthesis CSV |")

    lines.extend(
        [
            "",
            "## Generic Cell-Overhead Context",
            "",
            "| Baseline | Instrumented build | Status | Baseline cells | Instrumented cells | Delta cells | Overhead vs baseline | Record-side cells | Notes |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    if overhead_rows:
        for row in overhead_rows:
            lines.append(
                "| {baseline} | {instrumented} | {status} | {baseline_cells} | {instrumented_cells} | {delta} | {percent} | {record_cells} | {notes} |".format(
                    baseline=_escape_cell(DISPLAY_NAMES.get(row.get("baseline_top", ""), row.get("baseline_top", "unknown"))),
                    instrumented=_escape_cell(
                        DISPLAY_NAMES.get(row.get("instrumented_top", ""), row.get("instrumented_top", "unknown"))
                    ),
                    status=_escape_cell(row.get("status", "NA")),
                    baseline_cells=_escape_cell(row.get("baseline_cells", "NA")),
                    instrumented_cells=_escape_cell(row.get("instrumented_cells", "NA")),
                    delta=_escape_cell(row.get("generic_cell_delta", "NA")),
                    percent=_percent_cell(row.get("generic_cell_overhead_percent", "NA")),
                    record_cells=_escape_cell(row.get("record_side_cells", "NA")),
                    notes=_escape_cell(row.get("notes", "")),
                )
            )
    else:
        lines.append("| No overhead row | NA | TODO | NA | NA | NA | NA | NA | Missing overhead CSV |")
    return "\n".join(lines) + "\n"


def _ordered_synthesis_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_top = {row.get("top", ""): row for row in rows}
    ordered = [by_top[top] for top in SYNTHESIS_ORDER if top in by_top]
    ordered.extend(row for row in rows if row.get("top", "") not in set(SYNTHESIS_ORDER))
    return ordered


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _percent_cell(value: str) -> str:
    escaped = _escape_cell(value)
    return escaped if escaped in {"", "NA", "TODO"} else f"{escaped}%"


if __name__ == "__main__":
    raise SystemExit(main())
