#!/usr/bin/env python3
"""Create v1/v2 workload-scaling comparison tables without upgrading unmeasured rows to PASS."""

from __future__ import annotations

from collections import defaultdict

from run_buffer_sensitivity_v2 import _estimated_v2_bytes, _estimated_v2_events
from topconf_eval_common import REPO_ROOT, read_csv, safe_float, safe_int, write_csv


OUT_CSV = REPO_ROOT / "results/processed/workload_scaling_v2.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/workload_scaling_v2_summary.csv"
ARCH_CONFIGS = (
    ("v1", "full"),
    ("v2", "core"),
    ("v2", "hashed"),
    ("v2", "full"),
)

FIELDS = [
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "firmware_source",
    "compiler_backed",
    "cycles",
    "commits",
    "events",
    "capsule_bytes",
    "event_rate_per_kinst",
    "cycles_to_failure",
    "commits_to_failure",
    "property_id",
    "replay_status",
    "final_signature_match",
    "event_match",
    "overflow",
    "notes",
]

SUMMARY_FIELDS = [
    "architecture",
    "recorder_config",
    "workload_scale",
    "pass_count",
    "fail_count",
    "timeout_count",
    "blocked_count",
    "replay_success_rate_pct",
    "overflow_rate_pct",
    "median_events",
    "median_capsule_bytes",
    "n",
    "notes",
]


def main() -> int:
    source_rows = read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    rows = []
    for source in source_rows:
        for architecture, config in ARCH_CONFIGS:
            rows.append(_row(source, architecture, config))
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(SUMMARY_CSV, SUMMARY_FIELDS, _summary(rows))
    print("WROTE results/processed/workload_scaling_v2.csv")
    print("WROTE results/processed/workload_scaling_v2_summary.csv")
    return 0


def _row(source: dict[str, str], architecture: str, config: str) -> dict[str, object]:
    if architecture == "v1":
        return {
            "architecture": "v1",
            "recorder_config": "full",
            "benchmark": source.get("benchmark", "NA"),
            "variant": source.get("variant", "NA"),
            "seed": source.get("seed", "NA"),
            "workload_scale": source.get("workload_scale", "NA"),
            "firmware_source": source.get("firmware_source", "NA"),
            "compiler_backed": source.get("compiler_backed", "NA"),
            "cycles": source.get("cycles", "NA"),
            "commits": source.get("commits", "NA"),
            "events": source.get("events", "NA"),
            "capsule_bytes": source.get("capsule_bytes", "NA"),
            "event_rate_per_kinst": source.get("event_rate_per_kinst", "NA"),
            "cycles_to_failure": source.get("cycles_to_failure", "NA"),
            "commits_to_failure": source.get("commits_to_failure", "NA"),
            "property_id": source.get("property_id", "NA"),
            "replay_status": source.get("replay_status", "NA"),
            "final_signature_match": source.get("final_signature_match", "NA"),
            "event_match": source.get("event_match", "NA"),
            "overflow": source.get("overflow", "NA"),
            "notes": "measured v1 workload_scaling row",
        }

    source_events = safe_int(source.get("events"))
    events = _estimated_v2_events(source_events, config)
    capsule_bytes = _estimated_v2_bytes(events, config)
    commits = safe_float(source.get("commits"))
    event_rate = "NA"
    if commits and events is not None:
        event_rate = f"{(events / commits * 1000.0):.6f}"
    overflow = "NA" if events is None else events > 1024
    notes = (
        "ANALYTIC v2 capacity/size row derived from measured v1 workload row; "
        "full-core v2 record/replay is not integrated, so replay_status is BLOCKED and no PASS is claimed."
    )
    if source.get("overflow") == "true":
        notes += " Source v1 event count is a lower bound because v1 overflowed at 256 events."
    return {
        "architecture": "v2",
        "recorder_config": config,
        "benchmark": source.get("benchmark", "NA"),
        "variant": source.get("variant", "NA"),
        "seed": source.get("seed", "NA"),
        "workload_scale": source.get("workload_scale", "NA"),
        "firmware_source": source.get("firmware_source", "NA"),
        "compiler_backed": source.get("compiler_backed", "NA"),
        "cycles": source.get("cycles", "NA"),
        "commits": source.get("commits", "NA"),
        "events": events if events is not None else "NA",
        "capsule_bytes": capsule_bytes if capsule_bytes is not None else "NA",
        "event_rate_per_kinst": event_rate,
        "cycles_to_failure": source.get("cycles_to_failure", "NA"),
        "commits_to_failure": source.get("commits_to_failure", "NA"),
        "property_id": source.get("property_id", "NA"),
        "replay_status": "BLOCKED",
        "final_signature_match": "NA",
        "event_match": "NA",
        "overflow": overflow,
        "notes": notes,
    }


def _summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["architecture"]), str(row["recorder_config"]), str(row["workload_scale"]))].append(row)
    out = []
    for (arch, config, scale), subset in sorted(grouped.items()):
        n = len(subset)
        passes = sum(1 for row in subset if row["replay_status"] == "PASS")
        fails = sum(1 for row in subset if row["replay_status"] == "FAIL")
        timeouts = sum(1 for row in subset if row["replay_status"] == "TIMEOUT")
        blocked = sum(1 for row in subset if row["replay_status"] == "BLOCKED")
        overflows = sum(1 for row in subset if row["overflow"] is True or row["overflow"] == "true")
        event_values = [safe_float(row["events"]) for row in subset]
        byte_values = [safe_float(row["capsule_bytes"]) for row in subset]
        clean_events = sorted(value for value in event_values if value is not None)
        clean_bytes = sorted(value for value in byte_values if value is not None)
        out.append(
            {
                "architecture": arch,
                "recorder_config": config,
                "workload_scale": scale,
                "pass_count": passes,
                "fail_count": fails,
                "timeout_count": timeouts,
                "blocked_count": blocked,
                "replay_success_rate_pct": f"{(passes / n * 100.0):.6f}" if n else "NA",
                "overflow_rate_pct": f"{(overflows / n * 100.0):.6f}" if n and clean_events else "NA",
                "median_events": f"{_median(clean_events):.6f}" if clean_events else "NA",
                "median_capsule_bytes": f"{_median(clean_bytes):.6f}" if clean_bytes else "NA",
                "n": n,
                "notes": "v2 rows are capacity estimates and remain BLOCKED until full-core v2 replay is integrated",
            }
        )
    return out


def _median(values: list[float]) -> float:
    mid = len(values) // 2
    if len(values) % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


if __name__ == "__main__":
    raise SystemExit(main())
