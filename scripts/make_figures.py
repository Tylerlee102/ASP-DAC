#!/usr/bin/env python3
"""Generate SVG figures from measured/TODO result CSVs."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_FIGURES = REPO_ROOT / "results" / "figures"
PAPER_FIGURES = REPO_ROOT / "paper" / "figures"
TRACE_CSV = REPO_ROOT / "results" / "processed" / "trace_sizes.csv"
ABLATION_CSV = REPO_ROOT / "results" / "processed" / "ablations.csv"
SYNTH_CSV = REPO_ROOT / "results" / "processed" / "synthesis.csv"


def main() -> int:
    RESULTS_FIGURES.mkdir(parents=True, exist_ok=True)
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    figures = {
        "architecture_overview.svg": _architecture_svg(),
        "replay_flow.svg": _replay_flow_svg(),
        "baseline_trace_sizes.svg": _baseline_trace_sizes_svg(_read_rows(TRACE_CSV)),
        "ablation_heatmap.svg": _ablation_heatmap_svg(_read_rows(ABLATION_CSV)),
        "synthesis_status.svg": _synthesis_status_svg(_read_rows(SYNTH_CSV)),
        "trace_size_status.svg": _trace_status_svg(_read_rows(TRACE_CSV)),
    }
    for name, svg in figures.items():
        (RESULTS_FIGURES / name).write_text(svg, encoding="utf-8")
        (PAPER_FIGURES / name).write_text(svg, encoding="utf-8")
    print(f"WROTE {len(figures)} SVG figures to {RESULTS_FIGURES} and {PAPER_FIGURES}")
    return 0


def _architecture_svg() -> str:
    boxes = [
        (30, 80, 150, 54, "RV32I core"),
        (230, 40, 150, 54, "event_tap"),
        (430, 40, 150, 54, "classifier"),
        (630, 40, 150, 54, "capsule_buffer"),
        (230, 140, 150, 54, "property_checker"),
        (430, 140, 150, 54, "event_slicer"),
        (630, 140, 150, 54, "hash_signature"),
        (430, 240, 150, 54, "replay_control"),
        (630, 240, 150, 54, "MMIO/IRQ inject"),
    ]
    arrows = [
        (180, 107, 230, 67),
        (380, 67, 430, 67),
        (580, 67, 630, 67),
        (180, 107, 230, 167),
        (380, 167, 430, 167),
        (580, 167, 630, 167),
        (705, 94, 505, 240),
        (580, 267, 630, 267),
    ]
    return _diagram("ReplayCapsule-RV RTL Architecture", boxes, arrows, 820, 340)


def _replay_flow_svg() -> str:
    boxes = [
        (30, 80, 150, 58, "Record run"),
        (220, 80, 150, 58, "Property fail"),
        (410, 80, 150, 58, "Freeze capsule"),
        (600, 80, 150, 58, "Commit-index replay"),
        (790, 80, 150, 58, "Compare signature"),
    ]
    arrows = [(180, 109, 220, 109), (370, 109, 410, 109), (560, 109, 600, 109), (750, 109, 790, 109)]
    return _diagram("Deterministic Replay Methodology", boxes, arrows, 980, 220)


def _baseline_trace_sizes_svg(rows: list[dict[str, str]]) -> str:
    measured = [
        row for row in rows
        if row.get("baseline")
        in {
            "full_instruction_trace",
            "full_commit_trace",
            "interrupt_mmio_trace",
            "snapshot_on_failure",
            "property_aware_replaycapsule_rv",
        }
        and row.get("status") == "MEASURED"
        and row.get("evidence_level") in {"firmware-sim", "model"}
    ]
    if not measured:
        return _text_svg("Baseline Trace Sizes", ["No measured trace-size rows yet."])
    if any(row.get("evidence_level") == "firmware-sim" for row in measured):
        measured = [row for row in measured if row.get("evidence_level") == "firmware-sim"]
    labels = sorted({row["benchmark"] for row in measured})
    baselines = [
        "full_instruction_trace",
        "full_commit_trace",
        "interrupt_mmio_trace",
        "snapshot_on_failure",
        "property_aware_replaycapsule_rv",
    ]
    max_bytes = max(int(row["bytes"]) for row in measured if row["bytes"].isdigit())
    width = 1280
    height = 90 + len(labels) * 78
    parts = [_svg_open(width, height), _title("Baseline Trace Sizes (firmware-sim bytes)", width)]
    y = 70
    colors = {
        "full_instruction_trace": "#b7a7ff",
        "full_commit_trace": "#8fb3ff",
        "interrupt_mmio_trace": "#ffcc66",
        "snapshot_on_failure": "#f7a6a6",
        "property_aware_replaycapsule_rv": "#7bd88f",
    }
    for benchmark in labels:
        parts.append(_text(24, y + 16, benchmark, size=13))
        x = 220
        for baseline in baselines:
            row = next((item for item in measured if item["benchmark"] == benchmark and item["baseline"] == baseline), None)
            value = int(row["bytes"]) if row and row["bytes"].isdigit() else 0
            bar_w = int((value / max_bytes) * 130) if max_bytes else 0
            parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="16" fill="{colors[baseline]}"/>')
            parts.append(_text(x, y + 36, f"{_short_baseline(baseline)} {value}B", size=11))
            x += 205
        y += 78
    parts.append(_svg_close())
    return "\n".join(parts)


def _ablation_heatmap_svg(rows: list[dict[str, str]]) -> str:
    measured = [row for row in rows if row.get("status") == "MEASURED"]
    if not measured:
        return _text_svg("Ablation Heatmap", ["No measured ablation rows yet."])
    benchmarks = sorted({row["benchmark"] for row in measured})
    ablations = sorted({row["ablation"] for row in measured})
    cell_w = 114
    cell_h = 32
    left = 190
    top = 96
    width = left + len(ablations) * cell_w + 30
    height = top + len(benchmarks) * cell_h + 70
    parts = [_svg_open(width, height), _title("Ablation Outcome Heatmap (model-level)", width)]
    parts.append(_text(24, 58, "red = removing event breaks replay; green = no mismatch in this benchmark", size=12))
    for col, ablation in enumerate(ablations):
        parts.append(_rotated_text(left + col * cell_w + 18, top - 10, _short_ablation(ablation), size=10))
    for row_idx, benchmark in enumerate(benchmarks):
        y = top + row_idx * cell_h
        parts.append(_text(24, y + 21, benchmark, size=12))
        for col, ablation in enumerate(ablations):
            match = next(item for item in measured if item["benchmark"] == benchmark and item["ablation"] == ablation)
            breaks_replay = match["replay_success"] == "False"
            color = "#f06a6a" if breaks_replay else "#8bdc8b"
            label = "breaks" if breaks_replay else "ok"
            x = left + col * cell_w
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 4}" height="{cell_h - 4}" fill="{color}" stroke="#ffffff"/>')
            parts.append(_text(x + 10, y + 20, label, size=10))
    parts.append(_svg_close())
    return "\n".join(parts)


def _synthesis_status_svg(rows: list[dict[str, str]]) -> str:
    if not rows:
        return _text_svg("Synthesis Status", ["No synthesis rows yet."])
    lines = ["Synthesis/resource status"]
    for row in rows:
        lines.append(
            f"{row.get('top', 'top')} ({row.get('tool', 'tool')}): {row.get('status', 'NA')} cells={row.get('cells', 'NA')} "
            f"LUT={row.get('luts', 'NA')} FF={row.get('ffs', 'NA')} Fmax={row.get('fmax_mhz', 'NA')}"
        )
        lines.append(row.get("notes", ""))
    return _text_svg("Synthesis Status", lines)


def _trace_status_svg(rows: list[dict[str, str]]) -> str:
    if not rows:
        return _text_svg("Trace Size Status", ["No measured trace-size data yet."])
    measured = sum(1 for row in rows if row.get("status") == "MEASURED")
    todo = sum(1 for row in rows if row.get("status") == "TODO")
    passes = sum(1 for row in rows if row.get("replay_success") == "True")
    rtl_smoke = sum(1 for row in rows if row.get("evidence_level") == "rtl-smoke")
    lines = [
        f"measured trace-size rows: {measured}",
        f"TODO rows: {todo}",
        f"replay-success rows: {passes}",
        f"RTL-smoke packet-size rows: {rtl_smoke}",
        "Full benchmark-wide RTL trace/replay rows remain TODO; generic Yosys synthesis is tracked separately.",
    ]
    return _text_svg("Trace Size Status", lines)


def _diagram(title: str, boxes: list[tuple[int, int, int, int, str]], arrows: list[tuple[int, int, int, int]], width: int, height: int) -> str:
    parts = [_svg_open(width, height), _title(title, width)]
    parts.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#555"/></marker></defs>')
    for x1, y1, x2, y2 in arrows:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="2" marker-end="url(#arrow)"/>')
    for x, y, w, h, label in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#f8fbff" stroke="#4b6f9f" stroke-width="1.5"/>')
        parts.append(_text(x + w / 2, y + h / 2 + 5, label, anchor="middle", size=13))
    parts.append(_svg_close())
    return "\n".join(parts)


def _text_svg(title: str, lines: list[str]) -> str:
    width = 980
    height = 64 + 26 * len(lines)
    parts = [_svg_open(width, height), _title(title, width)]
    y = 62
    for line in lines:
        parts.append(_text(28, y, line, size=13))
        y += 26
    parts.append(_svg_close())
    return "\n".join(parts)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _svg_open(width: int, height: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n<rect width="{width}" height="{height}" fill="#ffffff"/>'


def _svg_close() -> str:
    return "</svg>"


def _title(value: str, width: int) -> str:
    return _text(width / 2, 30, value, anchor="middle", size=18, weight="700")


def _text(x: float, y: float, value: str, anchor: str = "start", size: int = 12, weight: str = "400") -> str:
    return (
        f'<text x="{x:.0f}" y="{y:.0f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#1f2933">{_escape(value)}</text>'
    )


def _rotated_text(x: float, y: float, value: str, size: int = 10) -> str:
    return (
        f'<text x="{x:.0f}" y="{y:.0f}" transform="rotate(-35 {x:.0f} {y:.0f})" '
        f'font-family="Arial, sans-serif" font-size="{size}" fill="#1f2933">{_escape(value)}</text>'
    )


def _short_baseline(value: str) -> str:
    return {
        "full_instruction_trace": "instr",
        "full_commit_trace": "commit",
        "interrupt_mmio_trace": "irq+mmio",
        "snapshot_on_failure": "snapshot",
        "property_aware_replaycapsule_rv": "capsule",
    }.get(value, value)


def _short_ablation(value: str) -> str:
    return value.replace("remove_", "").replace("_events", "").replace("_values", "").replace("_", " ")


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    raise SystemExit(main())
