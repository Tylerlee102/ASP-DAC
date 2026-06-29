#!/usr/bin/env python3
"""Generate SVG figures from measured/TODO result CSVs."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

try:
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
except Exception:  # pragma: no cover - optional local rendering helper
    canvas = None
    colors = None


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_FIGURES = REPO_ROOT / "results" / "figures"
PAPER_FIGURES = REPO_ROOT / "paper" / "figures"
TRACE_CSV = REPO_ROOT / "results" / "processed" / "trace_sizes.csv"
ABLATION_CSV = REPO_ROOT / "results" / "processed" / "ablations.csv"
SYNTH_CSV = REPO_ROOT / "results" / "processed" / "synthesis.csv"
RTL_CLASSES_CSV = REPO_ROOT / "results" / "processed" / "rtl_capsule_event_classes.csv"
RANDOMIZED_IRQ_CSV = REPO_ROOT / "results" / "processed" / "randomized_interrupt_campaign.csv"
FULL_RTL_REPLAY_CSV = REPO_ROOT / "results" / "processed" / "full_rtl_replay.csv"
FULL_RTL_NEGATIVE_CSV = REPO_ROOT / "results" / "processed" / "full_rtl_replay_negative.csv"
RUNTIME_OVERHEAD_SUMMARY_CSV = REPO_ROOT / "results" / "processed" / "runtime_overhead_summary.csv"
MAPPED_OVERHEAD_CSV = REPO_ROOT / "results" / "processed" / "mapped_overhead.csv"


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
        "rtl_capsule_event_classes.svg": _rtl_capsule_event_classes_svg(_read_rows(RTL_CLASSES_CSV)),
        "randomized_interrupt_campaign.svg": _randomized_interrupt_campaign_svg(_read_rows(RANDOMIZED_IRQ_CSV)),
        "replay_success_summary.svg": _replay_success_summary_svg(_read_rows(FULL_RTL_REPLAY_CSV), _read_rows(FULL_RTL_NEGATIVE_CSV)),
        "runtime_overhead_summary.svg": _runtime_overhead_summary_svg(_read_rows(RUNTIME_OVERHEAD_SUMMARY_CSV)),
        "mapped_overhead_summary.svg": _mapped_overhead_summary_svg(_read_rows(MAPPED_OVERHEAD_CSV)),
    }
    for name, svg in figures.items():
        (RESULTS_FIGURES / name).write_text(svg, encoding="utf-8")
        (PAPER_FIGURES / name).write_text(svg, encoding="utf-8")
    _write_core_pdf_figures()
    print(f"WROTE {len(figures)} SVG figures to {RESULTS_FIGURES} and {PAPER_FIGURES}")
    return 0


def _architecture_svg() -> str:
    boxes, arrows, width, height = _architecture_diagram()
    return _diagram("ReplayCapsule-RV RTL Architecture", boxes, arrows, width, height)


def _replay_flow_svg() -> str:
    boxes, arrows, width, height = _replay_flow_diagram()
    return _diagram("Deterministic Replay Methodology", boxes, arrows, width, height)


def _architecture_diagram() -> tuple[list[tuple[int, int, int, int, str]], list[tuple[int, int, int, int]], int, int]:
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
    return boxes, arrows, 820, 340


def _replay_flow_diagram() -> tuple[list[tuple[int, int, int, int, str]], list[tuple[int, int, int, int]], int, int]:
    boxes = [
        (30, 80, 150, 58, "Record run"),
        (220, 80, 150, 58, "Property fail"),
        (410, 80, 150, 58, "Freeze capsule"),
        (600, 80, 150, 58, "Commit-index replay"),
        (790, 80, 150, 58, "Compare signature"),
    ]
    arrows = [(180, 109, 220, 109), (370, 109, 410, 109), (560, 109, 600, 109), (750, 109, 790, 109)]
    return boxes, arrows, 980, 220


def _write_core_pdf_figures() -> None:
    if canvas is None or colors is None:
        return
    specs = [
        ("architecture_overview.pdf", "ReplayCapsule-RV RTL Architecture", *_architecture_diagram()),
        ("replay_flow.pdf", "Deterministic Replay Methodology", *_replay_flow_diagram()),
    ]
    for name, title, boxes, arrows, width, height in specs:
        for directory in (RESULTS_FIGURES, PAPER_FIGURES):
            _write_pdf_diagram(directory / name, title, boxes, arrows, width, height)


def _write_pdf_diagram(
    path: Path,
    title: str,
    boxes: Iterable[tuple[int, int, int, int, str]],
    arrows: Iterable[tuple[int, int, int, int]],
    width: int,
    height: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=(width, height))
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#1f2933"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 30, title)
    c.setStrokeColor(colors.HexColor("#555555"))
    c.setLineWidth(2)
    for x1, y1, x2, y2 in arrows:
        _pdf_arrow(c, x1, height - y1, x2, height - y2)
    for x, y, w, h, label in boxes:
        yy = height - y - h
        c.setFillColor(colors.HexColor("#f8fbff"))
        c.setStrokeColor(colors.HexColor("#4b6f9f"))
        c.roundRect(x, yy, w, h, 6, stroke=1, fill=1)
        c.setFillColor(colors.HexColor("#1f2933"))
        c.setFont("Helvetica", 13)
        c.drawCentredString(x + w / 2, yy + h / 2 - 4, label)
    c.showPage()
    c.save()


def _pdf_arrow(c: canvas.Canvas, x1: int, y1: int, x2: int, y2: int) -> None:
    c.line(x1, y1, x2, y2)
    # Short arrowhead good enough for manuscript figures.
    dx = x2 - x1
    dy = y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1.0)
    ux = dx / length
    uy = dy / length
    size = 8
    left = (x2 - size * ux - size * uy / 2, y2 - size * uy + size * ux / 2)
    right = (x2 - size * ux + size * uy / 2, y2 - size * uy - size * ux / 2)
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(*left)
    path.lineTo(*right)
    path.close()
    c.setFillColor(colors.HexColor("#555555"))
    c.drawPath(path, stroke=0, fill=1)


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


def _rtl_capsule_event_classes_svg(rows: list[dict[str, str]]) -> str:
    measured = [row for row in rows if row.get("status") == "PASS"]
    if not measured:
        return _text_svg("RTL Capsule Event Classes", ["No passing RTL-smoke capsule class rows yet."])
    max_packets = max(_int(row.get("rtl_packet_count")) for row in measured) or 1
    width = 1240
    height = 88 + len(measured) * 36
    parts = [_svg_open(width, height), _title("RTL-Smoke Capsule Event Classes", width)]
    parts.append(_text(24, 58, "gray = total exported packets; green = replay-relevant packets; labels show class counts", size=12))
    y = 86
    for row in measured:
        label = f"{row.get('benchmark')} {row.get('variant')}"
        total = _int(row.get("rtl_packet_count"))
        relevant = _int(row.get("replay_relevant_packet_count"))
        total_w = int((total / max_packets) * 260)
        relevant_w = int((relevant / max_packets) * 260)
        x = 260
        parts.append(_text(24, y + 17, label, size=11))
        parts.append(f'<rect x="{x}" y="{y}" width="{total_w}" height="12" fill="#d8dee9"/>')
        parts.append(f'<rect x="{x}" y="{y + 14}" width="{relevant_w}" height="12" fill="#7bd88f"/>')
        mix = (
            f"pkt {total}, rel {relevant}, br {row.get('branch')}, mmio "
            f"{_int(row.get('mmio_read')) + _int(row.get('mmio_write'))}, irq "
            f"{_int(row.get('interrupt_enter')) + _int(row.get('interrupt_exit'))}, "
            f"store {row.get('store')}, fail {row.get('property_fail')}"
        )
        parts.append(_text(x + 286, y + 20, mix, size=11))
        y += 36
    parts.append(_svg_close())
    return "\n".join(parts)


def _randomized_interrupt_campaign_svg(rows: list[dict[str, str]]) -> str:
    measured = [row for row in rows if row.get("status") == "PASS"]
    if not measured:
        return _text_svg("Randomized Interrupt Campaign", ["No passing seeded interrupt rows yet."])
    max_count = max(_int(row.get("capsule_count_run1")) for row in measured) or 1
    width = 1120
    height = 88 + len(measured) * 34
    parts = [_svg_open(width, height), _title("Seeded RTL-Smoke Interrupt Campaign", width)]
    parts.append(_text(24, 58, "Each seed ran twice; bars show frozen capsule packet count from run 1 after digest match.", size=12))
    colors = {"irq_after_command": "#8fb3ff", "fixed_irq_window": "#ffcc66"}
    y = 86
    for row in measured:
        count = _int(row.get("capsule_count_run1"))
        bar_w = int((count / max_count) * 300)
        family = row.get("family", "family")
        label = f"seed {row.get('seed')} {family}"
        x = 270
        parts.append(_text(24, y + 16, label, size=11))
        parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="16" fill="{colors.get(family, "#b7a7ff")}"/>')
        window = "after-command" if family == "irq_after_command" else f"{row.get('irq_start_cycle')}-{row.get('irq_end_cycle')}"
        parts.append(_text(x + bar_w + 12, y + 13, f"{count} packets, window {window}, property {row.get('property_run1')}", size=11))
        y += 34
    parts.append(_svg_close())
    return "\n".join(parts)


def _replay_success_summary_svg(replay_rows: list[dict[str, str]], negative_rows: list[dict[str, str]]) -> str:
    total = len(replay_rows)
    passes = sum(
        1 for row in replay_rows
        if row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
    )
    rejects = sum(1 for row in negative_rows if row.get("actual_result") == "REJECT")
    accepts = sum(1 for row in negative_rows if row.get("actual_result") == "ACCEPT")
    na_rows = sum(1 for row in negative_rows if row.get("actual_result") == "NA")
    lines = [
        f"Full RTL replay PASS rows: {passes}/{total}",
        f"Replay-critical corruptions rejected: {rejects}",
        f"Unexpected accepts: {accepts}",
        f"Not-applicable corruption rows: {na_rows}",
        "Source: full_rtl_replay.csv and full_rtl_replay_negative.csv",
    ]
    return _text_svg("Replay Success Summary", lines)


def _runtime_overhead_summary_svg(rows: list[dict[str, str]]) -> str:
    if not rows:
        return _text_svg("Runtime Overhead Summary", ["No runtime-overhead summary rows yet."])
    width = 980
    height = 250
    parts = [_svg_open(width, height), _title("Runtime Overhead Summary", width)]
    wanted = [
        ("recorder_present_disabled_vs_baseline_no_recorder", "cycle_overhead_pct", "#8fb3ff"),
        ("recorder_enabled_vs_baseline_no_recorder", "cycle_overhead_pct", "#7bd88f"),
        ("recorder_enabled_vs_baseline_no_recorder", "sim_wall_time_overhead_pct", "#ffcc66"),
    ]
    values = []
    for config, metric, color in wanted:
        row = next((item for item in rows if item.get("config") == config and item.get("metric") == metric), {})
        values.append((config, metric, _float(row.get("median")), row.get("n", "NA"), color))
    max_abs = max(abs(value[2]) for value in values) or 1.0
    x0 = 300
    y = 78
    for config, metric, value, n, color in values:
        bar_w = int((abs(value) / max_abs) * 360)
        label = f"{config.replace('_', ' ')} / {metric.replace('_', ' ')}"
        parts.append(_text(24, y + 18, label, size=11))
        parts.append(f'<rect x="{x0}" y="{y}" width="{bar_w}" height="18" fill="{color}"/>')
        parts.append(_text(x0 + bar_w + 12, y + 15, f"median {value:.2f}% n={n}", size=11))
        y += 45
    parts.append(_text(24, height - 24, "Simulator wall-clock rows are reported separately from cycle/commit counts.", size=11))
    parts.append(_svg_close())
    return "\n".join(parts)


def _mapped_overhead_summary_svg(rows: list[dict[str, str]]) -> str:
    full_core = [row for row in rows if row.get("target") == "ecp5-85k" and row.get("metric", "").startswith("full_core_baseline")]
    if not full_core:
        return _text_svg("Mapped Overhead Summary", ["No same-target full-core mapped overhead rows yet."])
    width = 980
    height = 270
    parts = [_svg_open(width, height), _title("Full-Core ECP5 Mapped Overhead", width)]
    colors = {"lut": "#8fb3ff", "ff": "#7bd88f", "bram": "#d8dee9", "fmax": "#ffcc66"}
    labels = [
        ("LUT", "full_core_baseline_board_to_full_core_replaycapsule_board_lut", "percent_overhead", "lut"),
        ("FF", "full_core_baseline_board_to_full_core_replaycapsule_board_ff", "percent_overhead", "ff"),
        ("BRAM", "full_core_baseline_board_to_full_core_replaycapsule_board_bram", "percent_overhead", "bram"),
        ("Fmax delta", "full_core_baseline_board_to_full_core_replaycapsule_board_fmax_mhz", "percent_overhead", "fmax"),
    ]
    values = []
    for label, metric, field, color_key in labels:
        row = next((item for item in full_core if item.get("metric") == metric), {})
        values.append((label, _float(row.get(field)), color_key))
    max_abs = max(abs(value[1]) for value in values) or 1.0
    x0 = 220
    y = 78
    for label, value, color_key in values:
        bar_w = int((abs(value) / max_abs) * 420)
        parts.append(_text(44, y + 17, label, size=12))
        parts.append(f'<rect x="{x0}" y="{y}" width="{bar_w}" height="18" fill="{colors[color_key]}"/>')
        parts.append(_text(x0 + bar_w + 12, y + 15, f"{value:.2f}%", size=12))
        y += 42
    parts.append(_text(24, height - 24, "Source: mapped_overhead.csv; same target ecp5-85k, yosys+synth_ecp5+nextpnr-ecp5.", size=11))
    parts.append(_svg_close())
    return "\n".join(parts)


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


def _int(value: str | None) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0


def _float(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


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
