#!/usr/bin/env python3
"""Generate top-conference summary CSV and LaTeX tables from evidence CSVs."""

from __future__ import annotations

from pathlib import Path
from statistics import mean, median

from topconf_eval_common import REPO_ROOT, read_csv, safe_float, write_csv


TABLE_DIR = REPO_ROOT / "paper/tables"
SUMMARY_CSV = REPO_ROOT / "results/processed/topconf_summary.csv"

SUMMARY_FIELDS = ["group", "metric", "value", "n", "evidence", "notes"]


def main() -> int:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    summary = []
    summary.extend(_replay_summary())
    summary.extend(_negative_summary())
    summary.extend(_runtime_summary())
    summary.extend(_capsule_summary())
    summary.extend(_buffer_summary())
    summary.extend(_mapped_summary())
    summary.extend(_event_ablation_summary())
    summary.extend(_recorder_config_summary())
    write_csv(SUMMARY_CSV, SUMMARY_FIELDS, summary)
    _write_tables()
    print("WROTE results/processed/topconf_summary.csv")
    print("WROTE paper/tables/table_*.tex")
    return 0


def _replay_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    out = []
    for key_name in ("benchmark", "workload_scale"):
        for key in sorted({row.get(key_name, "NA") for row in rows}):
            subset = [row for row in rows if row.get(key_name) == key]
            passed = [row for row in subset if row.get("replay_status") == "PASS"]
            out.append(_summary("replay_correctness", f"pass_rate_by_{key_name}:{key}", _pct_count(passed, subset), len(subset), "results/processed/workload_scaling.csv", "PASS means record/replay/final signature/event match"))
    return out


def _negative_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/full_rtl_replay_negative.csv")
    rejected = [row for row in rows if row.get("actual_result") == "REJECT"]
    unexpected = [row for row in rows if row.get("actual_result") == "ACCEPT"]
    na = [row for row in rows if row.get("actual_result") == "NA"]
    return [
        _summary("negative_replay", "rejected", len(rejected), len(rows), "results/processed/full_rtl_replay_negative.csv", "corrupted capsule rejection count"),
        _summary("negative_replay", "unexpected_accepted", len(unexpected), len(rows), "results/processed/full_rtl_replay_negative.csv", "unexpected accepts remain visible"),
        _summary("negative_replay", "na", len(na), len(rows), "results/processed/full_rtl_replay_negative.csv", "not-applicable negative rows"),
    ]


def _runtime_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/runtime_scaling_summary.csv")
    out = []
    for row in rows:
        if row.get("config") != "recorder_enabled":
            continue
        scale = row.get("workload_scale", "NA")
        for metric in ("median_cycle_overhead_pct", "median_commit_overhead_pct", "median_sim_wall_time_overhead_pct"):
            out.append(_summary("runtime_scaling", f"{metric}:{scale}", row.get(metric, "NA"), row.get("n", "0"), "results/processed/runtime_scaling_summary.csv", row.get("notes", "")))
    return out


def _capsule_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/capsule_baseline_summary.csv")
    out = []
    for row in rows:
        if row.get("baseline") == "replaycapsule_core":
            out.append(_summary("capsule_scaling", f"median_bytes:{row.get('workload_scale')}", row.get("median_bytes", "NA"), row.get("n", "0"), "results/processed/capsule_baseline_summary.csv", "measured capsule bytes"))
        if row.get("baseline") == "replaycapsule_core":
            out.append(_summary("capsule_scaling", f"median_reduction_vs_full_instruction:{row.get('workload_scale')}", row.get("median_reduction_vs_full_instruction_pct", "NA"), row.get("n", "0"), "results/processed/capsule_baseline_summary.csv", "full instruction trace is formula-estimated"))
    return out


def _buffer_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/buffer_sensitivity_summary.csv")
    return [
        _summary("buffer_sensitivity", f"depth_{row.get('buffer_depth')}_{row.get('workload_scale')}_overflow_pct", row.get("overflow_rate_pct", "NA"), row.get("n", "0"), "results/processed/buffer_sensitivity_summary.csv", row.get("notes", ""))
        for row in rows
    ]


def _mapped_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/mapped_scaling_overhead.csv")
    out = []
    for row in rows:
        if row.get("claim_allowed") == "yes":
            metric = f"{row.get('metric')}:mem{row.get('memory_words')}:buf{row.get('buffer_depth')}:{row.get('recorder_config')}"
            out.append(_summary("mapped_scaling", metric, row.get("percent_overhead", "NA"), "1", "results/processed/mapped_scaling_overhead.csv", "same-target P&R overhead"))
    return out


def _event_ablation_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/event_ablation_scaling.csv")
    out = []
    for event_class in sorted({row.get("removed_or_corrupted_event_class", "NA") for row in rows}):
        subset = [row for row in rows if row.get("removed_or_corrupted_event_class") == event_class]
        rejected = [row for row in subset if row.get("rejected") in {"true", "True", "1"}]
        diagnostic = [row for row in subset if row.get("diagnostic_only") in {"true", "True", "1"}]
        out.append(_summary("event_ablation", f"{event_class}_reject_rate", _pct_count(rejected, subset), len(subset), "results/processed/event_ablation_scaling.csv", "event-sufficiency ablation rows; diagnostic-only rows are labeled separately"))
        out.append(_summary("event_ablation", f"{event_class}_diagnostic_only_rows", len(diagnostic), len(subset), "results/processed/event_ablation_scaling.csv", "diagnostic-only corruption may accept if final replay properties still match"))
    return out


def _recorder_config_summary() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/recorder_config_replay.csv")
    out = []
    for config in sorted({row.get("recorder_config", "NA") for row in rows}):
        subset = [row for row in rows if row.get("recorder_config") == config]
        passed = [row for row in subset if row.get("replay_status") == "PASS"]
        neg_reject = [row for row in subset if row.get("negative_replay_status") == "REJECT"]
        bytes_values = [value for value in (safe_float(row.get("capsule_bytes")) for row in subset) if value is not None]
        out.append(_summary("recorder_config", f"{config}_replay_pass_rate", _pct_count(passed, subset), len(subset), "results/processed/recorder_config_replay.csv", "capture-mode replay rows"))
        out.append(_summary("recorder_config", f"{config}_payload_corruption_reject_rate", _pct_count(neg_reject, subset), len(subset), "results/processed/recorder_config_replay.csv", "payload-hash corruption check"))
        out.append(_summary("recorder_config", f"{config}_median_capsule_bytes", f"{median(bytes_values):.6f}" if bytes_values else "NA", len(bytes_values), "results/processed/recorder_config_replay.csv", "measured per capture mode"))
    return out


def _write_tables() -> None:
    _write_table("table_replay_success.tex", ["benchmark", "workload_scale", "pass", "total"], _replay_table_rows())
    _write_table("table_negative_replay.tex", ["result", "count"], _count_rows(read_csv(REPO_ROOT / "results/processed/full_rtl_replay_negative.csv"), "actual_result"))
    runtime_rows = _runtime_table_rows()
    _write_table("table_runtime_overhead.tex", ["workload_scale", "config", "median_cycle", "median_commit", "median_wall", "n"], runtime_rows)
    _write_table("table_runtime_scaling.tex", ["workload_scale", "config", "median_cycle", "median_commit", "median_wall", "n"], runtime_rows)
    _write_table("table_capsule_baselines.tex", ["baseline", "workload_scale", "median_bytes", "median_reduction_vs_full_instruction_pct", "n"], _select_fields(read_csv(REPO_ROOT / "results/processed/capsule_baseline_summary.csv"), ["baseline", "workload_scale", "median_bytes", "median_reduction_vs_full_instruction_pct", "n"]))
    _write_table("table_buffer_sensitivity.tex", ["buffer_depth", "workload_scale", "overflow_rate_pct", "replay_success_rate_pct", "n"], _select_fields(read_csv(REPO_ROOT / "results/processed/buffer_sensitivity_summary.csv"), ["buffer_depth", "workload_scale", "overflow_rate_pct", "replay_success_rate_pct", "n"]))
    _write_table("table_mapped_scaling.tex", ["memory_words", "buffer_depth", "recorder_config", "metric", "percent_overhead", "claim_allowed"], _select_fields(read_csv(REPO_ROOT / "results/processed/mapped_scaling_overhead.csv"), ["memory_words", "buffer_depth", "recorder_config", "metric", "percent_overhead", "claim_allowed"]))
    _write_table("table_event_ablation.tex", ["event_class", "rejected", "diagnostic_only", "blocked", "total"], _event_ablation_table_rows())
    _write_table("table_recorder_config_tradeoff.tex", ["recorder_config", "replay_pass_rate_pct", "median_capsule_bytes"], _recorder_table_rows())
    _write_table("table_limitations.tex", ["limitation", "paper_wording"], _limitations())


def _replay_table_rows() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    out = []
    for benchmark in sorted({row.get("benchmark", "NA") for row in rows}):
        for scale in sorted({row.get("workload_scale", "NA") for row in rows}):
            subset = [row for row in rows if row.get("benchmark") == benchmark and row.get("workload_scale") == scale]
            if subset:
                out.append({"benchmark": benchmark, "workload_scale": scale, "pass": sum(1 for row in subset if row.get("replay_status") == "PASS"), "total": len(subset)})
    return out


def _runtime_table_rows() -> list[dict[str, object]]:
    return [
        {
            "workload_scale": row.get("workload_scale", "NA"),
            "config": row.get("config", "NA"),
            "median_cycle": row.get("median_cycle_overhead_pct", "NA"),
            "median_commit": row.get("median_commit_overhead_pct", "NA"),
            "median_wall": row.get("median_sim_wall_time_overhead_pct", "NA"),
            "n": row.get("n", "0"),
        }
        for row in read_csv(REPO_ROOT / "results/processed/runtime_scaling_summary.csv")
    ]


def _recorder_table_rows() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/recorder_config_replay.csv")
    out = []
    for config in sorted({row.get("recorder_config", "NA") for row in rows}):
        subset = [row for row in rows if row.get("recorder_config") == config]
        bytes_values = [value for value in (safe_float(row.get("capsule_bytes")) for row in subset) if value is not None]
        out.append(
            {
                "recorder_config": config,
                "replay_pass_rate_pct": _pct_count([row for row in subset if row.get("replay_status") == "PASS"], subset),
                "median_capsule_bytes": f"{median(bytes_values):.6f}" if bytes_values else "NA",
            }
        )
    return out


def _event_ablation_table_rows() -> list[dict[str, object]]:
    rows = read_csv(REPO_ROOT / "results/processed/event_ablation_scaling.csv")
    out = []
    for event_class in sorted({row.get("removed_or_corrupted_event_class", "NA") for row in rows}):
        subset = [row for row in rows if row.get("removed_or_corrupted_event_class") == event_class]
        out.append(
            {
                "event_class": event_class,
                "rejected": sum(1 for row in subset if row.get("rejected") in {"true", "True", "1"}),
                "diagnostic_only": sum(1 for row in subset if row.get("diagnostic_only") in {"true", "True", "1"}),
                "blocked": sum(1 for row in subset if row.get("replay_status") == "BLOCKED"),
                "total": len(subset),
            }
        )
    return out


def _limitations() -> list[dict[str, object]]:
    return [
        {"limitation": "host_driven_replay", "paper_wording": "Full-core replay consume remains host-driven in the Verilator harness."},
        {"limitation": "v2_consumer_scope", "paper_wording": "The v2 replay-consume controller is tested and host-streamed in full-core replay, but autonomous capsule storage and MMIO/IRQ replay muxing are not integrated."},
        {"limitation": "buffer_depth_tradeoff", "paper_wording": "Replay-critical workload scaling uses workload-aware capsule depth; stress rows require the deepest generated setting."},
        {"limitation": "mapped_scope", "paper_wording": "Mapped data measures bring-up/debug instrumentation, not an area-optimized autonomous replay-consume engine."},
        {"limitation": "high_area_overhead", "paper_wording": "FF/LUT overhead remains high even after disabling unselected recorder logic."},
        {"limitation": "no_asic_power", "paper_wording": "ASIC area, timing, and power are not evaluated."},
        {"limitation": "single_hart_scope", "paper_wording": "Evaluation is single-hart RV32I and excludes multicore, DMA, caches/coherence, and arbitrary peripherals."},
    ]


def _write_table(name: str, columns: list[str], rows: list[dict[str, object]]) -> None:
    lines = ["\\begin{tabular}{" + "l" * len(columns) + "}", " \\hline", " & ".join(_esc(column) for column in columns) + " \\\\", " \\hline"]
    for row in rows:
        lines.append(" & ".join(_esc(row.get(column, "NA")) for column in columns) + " \\\\")
    lines.extend([" \\hline", "\\end{tabular}", ""])
    (TABLE_DIR / name).write_text("\n".join(lines), encoding="utf-8")


def _count_rows(rows: list[dict[str, str]], field: str) -> list[dict[str, object]]:
    return [{"result": key, "count": sum(1 for row in rows if row.get(field) == key)} for key in sorted({row.get(field, "NA") for row in rows})]


def _select_fields(rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, object]]:
    return [{field: row.get(field, "NA") for field in fields} for row in rows]


def _summary(group: str, metric: str, value: object, n: object, evidence: str, notes: str) -> dict[str, object]:
    return {"group": group, "metric": metric, "value": value, "n": n, "evidence": evidence, "notes": notes}


def _pct_count(numerator: list[object], denominator: list[object]) -> str:
    return f"{(len(numerator) / len(denominator) * 100.0):.6f}" if denominator else "NA"


def _esc(value: object) -> str:
    text = str(value)
    return text.replace("\\", "\\textbackslash{}").replace("_", "\\_").replace("%", "\\%").replace("&", "\\&")


if __name__ == "__main__":
    raise SystemExit(main())
