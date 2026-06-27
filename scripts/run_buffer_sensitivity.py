#!/usr/bin/env python3
"""Analyze buffer-depth overflow/replay availability from measured event counts."""

from __future__ import annotations

from statistics import median

from topconf_eval_common import REPO_ROOT, read_csv, safe_float, safe_int, write_csv


OUT_CSV = REPO_ROOT / "results/processed/buffer_sensitivity.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/buffer_sensitivity_summary.csv"
DEPTHS = (4, 8, 16, 32, 64, 128, 256)

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "buffer_depth",
    "events",
    "capsule_bytes",
    "overflow",
    "replay_available",
    "replay_status",
    "cycles_to_failure",
    "commits_to_failure",
    "notes",
]

SUMMARY_FIELDS = [
    "buffer_depth",
    "workload_scale",
    "overflow_rate_pct",
    "replay_success_rate_pct",
    "median_capsule_bytes",
    "median_events",
    "n",
    "notes",
]


def main() -> int:
    workload_rows = read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    rows = []
    for row in workload_rows:
        for depth in DEPTHS:
            rows.append(_row(row, depth))
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(SUMMARY_CSV, SUMMARY_FIELDS, _summary(rows))
    print("WROTE results/processed/buffer_sensitivity.csv")
    print("WROTE results/processed/buffer_sensitivity_summary.csv")
    return 0


def _row(row: dict[str, str], depth: int) -> dict[str, object]:
    events = safe_int(row.get("events"))
    measured_pass = row.get("replay_status") == "PASS"
    overflow = "NA" if events is None else events > depth
    replay_available = measured_pass and overflow is False
    return {
        "benchmark": row.get("benchmark", "NA"),
        "variant": row.get("variant", "NA"),
        "seed": row.get("seed", "NA"),
        "workload_scale": row.get("workload_scale", "NA"),
        "buffer_depth": depth,
        "events": row.get("events", "NA"),
        "capsule_bytes": row.get("capsule_bytes", "NA"),
        "overflow": overflow,
        "replay_available": replay_available,
        "replay_status": "PASS" if replay_available else "OVERFLOW" if overflow is True else row.get("replay_status", "NA"),
        "cycles_to_failure": row.get("cycles_to_failure", "NA"),
        "commits_to_failure": row.get("commits_to_failure", "NA"),
        "notes": "ANALYTIC from measured event_count and proposed capsule buffer depth; no rerun performed per depth",
    }


def _summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    keys = sorted({(int(row["buffer_depth"]), str(row["workload_scale"])) for row in rows})
    for depth, scale in keys:
        subset = [row for row in rows if int(row["buffer_depth"]) == depth and row["workload_scale"] == scale]
        overflows = [row for row in subset if row["overflow"] is True or row["overflow"] == "true"]
        available = [row for row in subset if row["replay_available"] is True or row["replay_available"] == "true"]
        bytes_values = [safe_float(row["capsule_bytes"]) for row in subset]
        event_values = [safe_float(row["events"]) for row in subset]
        clean_bytes = [value for value in bytes_values if value is not None]
        clean_events = [value for value in event_values if value is not None]
        n = len(subset)
        rates_available = bool(clean_events)
        out.append(
            {
                "buffer_depth": depth,
                "workload_scale": scale,
                "overflow_rate_pct": f"{(len(overflows) / n * 100.0):.6f}" if n and rates_available else "NA",
                "replay_success_rate_pct": f"{(len(available) / n * 100.0):.6f}" if n and rates_available else "NA",
                "median_capsule_bytes": f"{median(clean_bytes):.6f}" if clean_bytes else "NA",
                "median_events": f"{median(clean_events):.6f}" if clean_events else "NA",
                "n": n,
                "notes": "summary of analytic overflow/replay availability against measured event counts",
            }
        )
    return out


if __name__ == "__main__":
    raise SystemExit(main())
