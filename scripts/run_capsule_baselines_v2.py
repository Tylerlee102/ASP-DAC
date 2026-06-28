#!/usr/bin/env python3
"""Compare v1 measured capsules and v2 estimated capsule formats against trace baselines."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean, median

from run_buffer_sensitivity_v2 import _estimated_v2_bytes, _estimated_v2_events
from topconf_eval_common import REPO_ROOT, read_csv, reduction_pct, safe_float, safe_int, write_csv


OUT_CSV = REPO_ROOT / "results/processed/capsule_baseline_comparison_v2.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/capsule_baseline_summary_v2.csv"
BASELINES = (
    "full_instruction_trace",
    "full_commit_trace",
    "pc_only_trace",
    "branch_trace",
    "load_store_trace",
    "mmio_only_trace",
    "interrupt_only_trace",
    "interrupt_plus_mmio_trace",
    "snapshot_at_failure",
    "v1_replaycapsule_full",
    "v2_minimal",
    "v2_core",
    "v2_hashed",
    "v2_diagnostic",
    "v2_full",
)

FIELDS = [
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "baseline",
    "bytes",
    "events",
    "measured_or_estimated",
    "replay_success",
    "property_match",
    "final_signature_match",
    "event_match",
    "reduction_vs_full_instruction_pct",
    "reduction_vs_full_commit_pct",
    "reduction_vs_snapshot_pct",
    "diagnostic_context_available",
    "notes",
]

SUMMARY_FIELDS = [
    "architecture",
    "recorder_config",
    "baseline",
    "workload_scale",
    "median_bytes",
    "mean_bytes",
    "min_bytes",
    "max_bytes",
    "median_reduction_vs_full_instruction_pct",
    "median_reduction_vs_full_commit_pct",
    "n",
    "notes",
]


def main() -> int:
    workload_rows = read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    rows = []
    for row in workload_rows:
        rows.extend(_rows_for_case(row))
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(SUMMARY_CSV, SUMMARY_FIELDS, _summary(rows))
    print("WROTE results/processed/capsule_baseline_comparison_v2.csv")
    print("WROTE results/processed/capsule_baseline_summary_v2.csv")
    return 0


def _rows_for_case(row: dict[str, str]) -> list[dict[str, object]]:
    values = _values(row)
    full_instruction = values["full_instruction_trace"]["bytes"]
    full_commit = values["full_commit_trace"]["bytes"]
    snapshot = values["snapshot_at_failure"]["bytes"]
    out = []
    for baseline in BASELINES:
        value = values[baseline]
        architecture, config = _arch_config(baseline)
        out.append(
            {
                "architecture": architecture,
                "recorder_config": config,
                "benchmark": row.get("benchmark", "NA"),
                "variant": row.get("variant", "NA"),
                "seed": row.get("seed", "NA"),
                "workload_scale": row.get("workload_scale", "NA"),
                "baseline": baseline,
                "bytes": value["bytes"],
                "events": value["events"],
                "measured_or_estimated": value["kind"],
                "replay_success": row.get("replay_status") == "PASS" if baseline == "v1_replaycapsule_full" else "NA",
                "property_match": row.get("final_signature_match", "NA") if baseline == "v1_replaycapsule_full" else "NA",
                "final_signature_match": row.get("final_signature_match", "NA") if baseline == "v1_replaycapsule_full" else "NA",
                "event_match": row.get("event_match", "NA") if baseline == "v1_replaycapsule_full" else "NA",
                "reduction_vs_full_instruction_pct": reduction_pct(full_instruction, value["bytes"]),
                "reduction_vs_full_commit_pct": reduction_pct(full_commit, value["bytes"]),
                "reduction_vs_snapshot_pct": reduction_pct(snapshot, value["bytes"]),
                "diagnostic_context_available": value["diagnostic"],
                "notes": value["notes"],
            }
        )
    return out


def _values(row: dict[str, str]) -> dict[str, dict[str, object]]:
    commits = safe_int(row.get("commits"))
    events = safe_int(row.get("events"))
    capsule_bytes = safe_int(row.get("capsule_bytes"))
    if commits is None or events is None or capsule_bytes is None:
        return {baseline: _value("NA", "NA", "unavailable", "NA", "upstream row has no measured size") for baseline in BASELINES}
    common = {
        "full_instruction_trace": _value(commits * 8, commits, "estimated", "false", "ESTIMATED formula=commits*(pc+instruction=8B)"),
        "full_commit_trace": _value(commits * 16, commits, "estimated", "false", "ESTIMATED formula=commits*(pc+instruction+digest=16B)"),
        "pc_only_trace": _value(commits * 4, commits, "estimated", "false", "ESTIMATED formula=commits*pc32"),
        "branch_trace": _value(max(1, commits // 8) * 12, max(1, commits // 8), "estimated", "false", "ESTIMATED branch trace proxy"),
        "load_store_trace": _value(max(1, events // 2) * 12, max(1, events // 2), "estimated", "false", "ESTIMATED load/store trace proxy"),
        "mmio_only_trace": _value(max(1, events // 4) * 12, max(1, events // 4), "estimated", "false", "ESTIMATED MMIO-only trace proxy"),
        "interrupt_only_trace": _value(max(1, events // 16) * 12, max(1, events // 16), "estimated", "false", "ESTIMATED interrupt-only trace proxy"),
        "interrupt_plus_mmio_trace": _value(max(1, events // 3) * 12, max(1, events // 3), "estimated", "false", "ESTIMATED interrupt+MMIO trace proxy"),
        "snapshot_at_failure": _value(4096, 1, "estimated", "true", "ESTIMATED fixed 4KiB state snapshot"),
        "v1_replaycapsule_full": _value(capsule_bytes, events, "measured", "true", "MEASURED from workload_scaling capsule_bytes"),
    }
    for config in ("minimal", "core", "hashed", "diagnostic", "full"):
        est_events = _estimated_v2_events(events, config)
        est_bytes = _estimated_v2_bytes(est_events, config)
        common[f"v2_{config}"] = _value(
            est_bytes,
            est_events,
            "estimated",
            "true" if config in {"diagnostic", "full"} else "false",
            "ESTIMATED v2 compressed capsule size; no v2 replay PASS claimed",
        )
    return common


def _value(bytes_value: object, events: object, kind: str, diagnostic: object, notes: str) -> dict[str, object]:
    return {"bytes": bytes_value, "events": events, "kind": kind, "diagnostic": diagnostic, "notes": notes}


def _arch_config(baseline: str) -> tuple[str, str]:
    if baseline.startswith("v1_"):
        return "v1", "full"
    if baseline.startswith("v2_"):
        return "v2", baseline.removeprefix("v2_")
    return "baseline", "trace_or_snapshot"


def _summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["architecture"]), str(row["recorder_config"]), str(row["baseline"]), str(row["workload_scale"]))].append(row)
    out = []
    for (arch, config, baseline, scale), subset in sorted(grouped.items()):
        bytes_values = [safe_float(row["bytes"]) for row in subset]
        red_i = [safe_float(row["reduction_vs_full_instruction_pct"]) for row in subset]
        red_c = [safe_float(row["reduction_vs_full_commit_pct"]) for row in subset]
        clean_bytes = [value for value in bytes_values if value is not None]
        clean_i = [value for value in red_i if value is not None]
        clean_c = [value for value in red_c if value is not None]
        out.append(
            {
                "architecture": arch,
                "recorder_config": config,
                "baseline": baseline,
                "workload_scale": scale,
                "median_bytes": f"{median(clean_bytes):.6f}" if clean_bytes else "NA",
                "mean_bytes": f"{mean(clean_bytes):.6f}" if clean_bytes else "NA",
                "min_bytes": f"{min(clean_bytes):.6f}" if clean_bytes else "NA",
                "max_bytes": f"{max(clean_bytes):.6f}" if clean_bytes else "NA",
                "median_reduction_vs_full_instruction_pct": f"{median(clean_i):.6f}" if clean_i else "NA",
                "median_reduction_vs_full_commit_pct": f"{median(clean_c):.6f}" if clean_c else "NA",
                "n": len(subset),
                "notes": "detailed CSV marks each row measured_or_estimated",
            }
        )
    return out


if __name__ == "__main__":
    raise SystemExit(main())
