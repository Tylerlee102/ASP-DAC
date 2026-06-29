#!/usr/bin/env python3
"""Generate compact v2 paper tables and status figures from processed CSVs."""

from __future__ import annotations

from pathlib import Path
from statistics import median

from topconf_eval_common import REPO_ROOT, read_csv


TABLE_DIR = REPO_ROOT / "paper/tables"
FIG_DIR = REPO_ROOT / "paper/figures"


def main() -> int:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    _write_table_replay_consumer_tests()
    _write_table_buffer_sensitivity_v2()
    _write_table_capsule_baselines_v2()
    _write_table_runtime_scaling_v2()
    _write_table_mapped_scaling_v2()
    _write_limitations_table()
    _write_figures()
    print("WROTE v2 paper tables and figures")
    return 0


def _write_table_replay_consumer_tests() -> None:
    rows = read_csv(REPO_ROOT / "results/processed/replay_consumer_tests.csv")
    passed = sum(1 for row in rows if row.get("passed") == "true")
    total = len(rows)
    _write_tex(
        TABLE_DIR / "table_replay_consumer_tests.tex",
        [
            r"\begin{tabular}{lrr}",
            r"\toprule",
            r"Scope & Passed & Total \\",
            r"\midrule",
            f"Replay-consume RTL tests & {passed} & {total} " + r"\\",
            r"\bottomrule",
            r"\end{tabular}",
        ],
    )


def _write_table_buffer_sensitivity_v2() -> None:
    rows = []
    v1_depths = {"256", "1024", "4096", "16384"}
    rows.extend(
        {
            "architecture": "v1",
            "recorder_config": "full",
            "buffer_depth": row.get("buffer_depth", "NA"),
            "overflow_rate_pct": row.get("overflow_rate_pct", "NA"),
            "replay_success_rate_pct": row.get("replay_success_rate_pct", "NA"),
        }
        for row in read_csv(REPO_ROOT / "results/processed/buffer_sensitivity_summary.csv")
        if row.get("workload_scale") == "stress" and row.get("buffer_depth") in v1_depths
    )
    v2_depths = {"64", "256", "2048"}
    measured_buffer = _preferred_csv("buffer_sensitivity_v2_measured_summary.csv", "buffer_sensitivity_v2_summary.csv")
    rows.extend(
        row
        for row in measured_buffer
        if row.get("workload_scale") == "stress"
        and row.get("recorder_config") in {"core", "full"}
        and row.get("buffer_depth") in v2_depths
    )
    rows.sort(key=lambda row: (_esc(row.get("architecture", "NA")), _esc(row.get("recorder_config", "NA")), int(row.get("buffer_depth", "0"))))
    lines = [r"\begin{tabular}{llrrr}", r"\toprule", r"Arch & Config & Depth & Overflow \% & Replay success \% \\", r"\midrule"]
    for row in rows:
        lines.append(
            f"{_esc(row['architecture'])} & {_esc(row['recorder_config'])} & {row['buffer_depth']} & "
            f"{_esc(row.get('overflow_rate_pct', 'NA'))} & {_esc(row.get('replay_success_rate_pct', 'NA'))} " + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write_tex(TABLE_DIR / "table_buffer_sensitivity_v2.tex", lines)


def _write_table_capsule_baselines_v2() -> None:
    rows = [
        row
        for row in _preferred_csv("capsule_baseline_summary_v2_measured.csv", "capsule_baseline_summary_v2.csv")
        if row.get("workload_scale") == "stress"
        and row.get("baseline") in {"full_instruction_trace", "full_commit_trace", "v1_replaycapsule_full", "v1_full", "v2_core", "v2_hashed", "v2_full"}
    ]
    lines = [r"\begin{tabular}{llrrr}", r"\toprule", r"Baseline & Config & Median bytes & Pass & N \\", r"\midrule"]
    for row in rows:
        lines.append(
            f"{_esc(row['baseline'])} & {_esc(row['recorder_config'])} & {row['median_bytes']} & "
            f"{_esc(row.get('pass_count', 'NA'))} & {row['n']} " + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write_tex(TABLE_DIR / "table_capsule_baselines_v2.tex", lines)


def _write_table_runtime_scaling_v2() -> None:
    rows = _preferred_csv("runtime_scaling_v2_measured.csv", "runtime_scaling.csv")
    configs = [
        "v2_recorder_present_disabled",
        "v2_recorder_enabled_core",
        "v2_recorder_enabled_hashed",
        "v2_recorder_enabled_full",
    ]
    lines = [r"\begin{tabular}{lrrr}", r"\toprule", r"Config & Cycle overhead & Commit overhead & Wall overhead \\", r"\midrule"]
    for config in configs:
        subset = [row for row in rows if row.get("config") == config and row.get("status", "MEASURED") == "MEASURED"]
        lines.append(
            f"{_esc(config)} & {_median_field(subset, 'cycle_overhead_pct')} & "
            f"{_median_field(subset, 'commit_overhead_pct')} & {_median_field(subset, 'sim_wall_time_overhead_pct')} " + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write_tex(TABLE_DIR / "table_runtime_scaling_v2.tex", lines)


def _write_table_mapped_scaling_v2() -> None:
    consumer = read_csv(REPO_ROOT / "results/processed/replay_consumer_mapped.csv")
    mapped = consumer[0] if consumer else {}
    full_core_rows = [
        row
        for row in _preferred_csv("mapped_scaling_v2_measured.csv", "mapped_scaling_v2.csv")
        if row.get("status") == "PASS"
    ]
    lines = [
        r"\begin{tabular}{lrrrrl}",
        r"\toprule",
        r"Design & LUT & FF & BRAM & Fmax MHz & Scope \\",
        r"\midrule",
        f"v2 replay consumer & {_esc(mapped.get('lut', 'NA'))} & {_esc(mapped.get('ff', 'NA'))} & {_esc(mapped.get('bram', 'NA'))} & {_esc(mapped.get('fmax_mhz', 'NA'))} & standalone prototype " + r"\\",
    ]
    for row in full_core_rows:
        scope = "baseline full-core mapping" if row.get("architecture") == "baseline" else "full-core recorder mapping"
        lines.append(
            f"{_esc(row.get('design', 'NA'))} & {_esc(row.get('lut', 'NA'))} & {_esc(row.get('ff', 'NA'))} & "
            f"{_esc(row.get('bram', 'NA'))} & {_esc(row.get('fmax_mhz', 'NA'))} & {scope} " + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    _write_tex(TABLE_DIR / "table_mapped_scaling_v2.tex", lines)


def _write_limitations_table() -> None:
    _write_tex(
        TABLE_DIR / "table_limitations.tex",
        [
            r"\begin{tabular}{lp{0.58\linewidth}}",
            r"\toprule",
            r"Topic & Current scope \\",
            r"\midrule",
            r"Core scope & Single-hart RV32I only \\",
            r"Replay consume & v2 synthesizable prototype; autonomous full-core consume not integrated \\",
            r"v2 workload replay & Measured full-core host-driven record/replay rows \\",
            r"Mapped overhead & v1 and representative v2 full-core ECP5 rows measured \\",
            r"ASIC/power & Not measured \\",
            r"\bottomrule",
            r"\end{tabular}",
        ],
    )


def _write_figures() -> None:
    summaries = {
        "fig_workload_scaling_v2.pdf": _workload_lines(),
        "fig_capsule_scaling_v2.pdf": _capsule_lines(),
        "fig_buffer_sensitivity_v2.pdf": _buffer_lines(),
        "fig_runtime_scaling_v2.pdf": _runtime_lines(),
        "fig_mapped_overhead_v2.pdf": _mapped_lines(),
        "fig_recorder_config_tradeoff_v2.pdf": _recorder_config_lines(),
        "fig_replay_consumer_controller.pdf": _consumer_lines(),
    }
    for name, lines in summaries.items():
        _write_pdf(FIG_DIR / name, lines)


def _workload_lines() -> list[str]:
    rows = _preferred_csv("workload_scaling_v2_measured_summary.csv", "workload_scaling_v2_summary.csv")
    v2_pass = sum(_int(row.get("pass_count")) for row in rows if row.get("architecture") == "v2")
    v2_total = sum(_int(row.get("n")) for row in rows if row.get("architecture") == "v2")
    blocked = sum(_int(row.get("blocked_count")) for row in rows if row.get("architecture") == "v2")
    return ["Workload scaling v2", f"Measured v2 PASS rows: {v2_pass}/{v2_total}", f"Blocked rows: {blocked}", "Scope: host-driven full-core record/replay."]


def _capsule_lines() -> list[str]:
    rows = _preferred_csv("capsule_baseline_summary_v2_measured.csv", "capsule_baseline_summary_v2.csv")
    stress = {row["baseline"]: row["median_bytes"] for row in rows if row.get("workload_scale") == "stress"}
    return ["Capsule scaling v2", f"v1 full median stress bytes: {stress.get('v1_full', stress.get('v1_replaycapsule_full', 'NA'))}", f"v2 core measured median stress bytes: {stress.get('v2_core', 'NA')}", "Rows preserve measured/estimated labels in CSV."]


def _buffer_lines() -> list[str]:
    rows = _preferred_csv("buffer_sensitivity_v2_measured_summary.csv", "buffer_sensitivity_v2_summary.csv")
    core = [row for row in rows if row.get("recorder_config") == "core" and row.get("workload_scale") == "stress" and row.get("buffer_depth") == "256"]
    return ["Buffer sensitivity v2", f"v2 core stress overflow at depth 256: {core[0]['overflow_rate_pct'] if core else 'NA'}%", f"Replay success at depth 256: {core[0]['replay_success_rate_pct'] if core else 'NA'}%"]


def _runtime_lines() -> list[str]:
    rows = _preferred_csv("runtime_scaling_v2_measured.csv", "runtime_scaling.csv")
    core = [row for row in rows if row.get("config") == "v2_recorder_enabled_core" and row.get("status", "MEASURED") == "MEASURED"]
    full = [row for row in rows if row.get("config") == "v2_recorder_enabled_full" and row.get("status", "MEASURED") == "MEASURED"]
    return [
        "Runtime scaling v2",
        f"Core median cycle overhead: {_median_field(core, 'cycle_overhead_pct')}%",
        f"Full median wall overhead: {_median_field(full, 'sim_wall_time_overhead_pct')}%",
        "Simulator wall time is not hardware timing.",
    ]


def _mapped_lines() -> list[str]:
    rows = read_csv(REPO_ROOT / "results/processed/replay_consumer_mapped.csv")
    row = rows[0] if rows else {}
    overhead_rows = _preferred_csv("mapped_scaling_overhead_v2_measured.csv", "mapped_scaling_overhead_v2.csv")
    core_lut = next((item.get("percent_overhead", "NA") for item in overhead_rows if item.get("recorder_config") == "core" and item.get("metric") == "lut"), "NA")
    return ["Mapped overhead v2", f"Replay consumer ECP5-85k status: {row.get('status', 'NA')}", f"Standalone LUT={row.get('lut', 'NA')} FF={row.get('ff', 'NA')}", f"Full-core v2 core LUT overhead: {core_lut}%"]


def _recorder_config_lines() -> list[str]:
    rows = _preferred_csv("workload_scaling_v2_measured_summary.csv", "workload_scaling_v2_summary.csv")
    configs = sorted({row.get("recorder_config", "NA") for row in rows if row.get("architecture") == "v2"})
    pass_rates = [
        f"{config}: {next((row.get('replay_success_rate_pct', 'NA') for row in rows if row.get('recorder_config') == config and row.get('workload_scale') == 'stress'), 'NA')}%"
        for config in configs
    ]
    return ["Recorder config tradeoff v2", *pass_rates[:3], "All claims remain scoped to host-driven replay."]


def _consumer_lines() -> list[str]:
    tests = read_csv(REPO_ROOT / "results/processed/replay_consumer_tests.csv")
    passed = sum(1 for row in tests if row.get("passed") == "true")
    return ["Replay-consume controller", f"RTL tests passed: {passed}/{len(tests)}", "Scope: synthesizable prototype, not full-core autonomous replay."]


def _preferred_csv(preferred: str, fallback: str) -> list[dict[str, str]]:
    preferred_path = REPO_ROOT / "results/processed" / preferred
    rows = read_csv(preferred_path)
    if rows:
        return rows
    return read_csv(REPO_ROOT / "results/processed" / fallback)


def _median_field(rows: list[dict[str, str]], field: str) -> str:
    values = []
    for row in rows:
        try:
            values.append(float(row.get(field, "NA")))
        except ValueError:
            continue
    return f"{median(values):.2f}" if values else "NA"


def _int(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _write_tex(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_pdf(path: Path, lines: list[str]) -> None:
    content = ["BT", "/F1 16 Tf", "72 740 Td"]
    first = True
    for line in lines:
        if not first:
            content.append("0 -24 Td")
        content.append(f"({_pdf_esc(line)}) Tj")
        first = False
    content.append("ET")
    stream = "\n".join(content).encode("ascii", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{i} 0 obj\n".encode("ascii"))
        data.extend(obj)
        data.extend(b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    path.write_bytes(data)


def _esc(value: object) -> str:
    return str(value).replace("_", r"\_").replace("%", r"\%")


def _pdf_esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


if __name__ == "__main__":
    raise SystemExit(main())
