#!/usr/bin/env python3
"""Analyze buffer-depth overflow/replay availability from measured event counts."""

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import median

from topconf_eval_common import REPO_ROOT, read_csv, safe_float, safe_int, write_csv


OUT_CSV = REPO_ROOT / "results/processed/buffer_sensitivity.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/buffer_sensitivity_summary.csv"
DEPTHS = (4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384)

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "buffer_depth",
    "measured_buffer_depth",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/processed/workload_scaling.csv")
    parser.add_argument("--output", default=str(OUT_CSV))
    parser.add_argument("--summary-output", default=str(SUMMARY_CSV))
    args = parser.parse_args()

    workload_rows = read_csv(_repo_path(args.input))
    rows = []
    for row in workload_rows:
        for depth in DEPTHS:
            rows.append(_row(row, depth))
    out_csv = _repo_path(args.output)
    summary_csv = _repo_path(args.summary_output)
    write_csv(out_csv, FIELDS, rows)
    write_csv(summary_csv, SUMMARY_FIELDS, _summary(rows))
    print(f"WROTE {_rel(out_csv)}")
    print(f"WROTE {_rel(summary_csv)}")
    return 0


def _row(row: dict[str, str], depth: int) -> dict[str, object]:
    events = safe_int(row.get("events"))
    measured_depth = safe_int(row.get("buffer_depth")) or 256
    source_overflow = row.get("overflow", "NA").lower() == "true"
    measured_pass = row.get("strict_replay_valid", "").lower() == "true" or (
        row.get("strict_replay_valid", "") == "" and row.get("replay_status") == "PASS" and not source_overflow
    )
    if events is None:
        overflow: object = "NA"
    elif source_overflow:
        overflow = True if depth <= measured_depth else "UNKNOWN"
    elif depth == measured_depth:
        overflow = False
    else:
        overflow = events > depth
    replay_available = measured_pass and overflow is False
    capsule_bytes = _bytes_at_depth(row, depth, events)
    return {
        "benchmark": row.get("benchmark", "NA"),
        "variant": row.get("variant", "NA"),
        "seed": row.get("seed", "NA"),
        "workload_scale": row.get("workload_scale", "NA"),
        "buffer_depth": depth,
        "measured_buffer_depth": measured_depth,
        "events": row.get("events", "NA"),
        "capsule_bytes": capsule_bytes,
        "overflow": overflow,
        "replay_available": replay_available,
        "replay_status": "PASS" if replay_available else "OVERFLOW" if overflow is True else "UNKNOWN" if overflow == "UNKNOWN" else row.get("replay_status", "NA"),
        "cycles_to_failure": row.get("cycles_to_failure", "NA"),
        "commits_to_failure": row.get("commits_to_failure", "NA"),
        "notes": "ANALYTIC from measured event_count only when source row did not overflow; source-overflow rows are conservative UNKNOWN above measured depth",
    }


def _bytes_at_depth(row: dict[str, str], depth: int, events: int | None) -> object:
    capsule_bytes = safe_float(row.get("capsule_bytes"))
    if events is None or capsule_bytes is None:
        return row.get("capsule_bytes", "NA")
    if events <= 0:
        return 0
    bytes_per_event = capsule_bytes / events
    return f"{(min(events, depth) * bytes_per_event):.6f}"


def _summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    keys = sorted({(int(row["buffer_depth"]), str(row["workload_scale"])) for row in rows})
    for depth, scale in keys:
        subset = [row for row in rows if int(row["buffer_depth"]) == depth and row["workload_scale"] == scale]
        overflows = [row for row in subset if row["overflow"] is True or row["overflow"] == "true"]
        known_overflow = [row for row in subset if row["overflow"] is True or row["overflow"] is False or row["overflow"] in {"true", "false"}]
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
                "overflow_rate_pct": f"{(len(overflows) / len(known_overflow) * 100.0):.6f}" if known_overflow and rates_available else "NA",
                "replay_success_rate_pct": f"{(len(available) / n * 100.0):.6f}" if n and rates_available else "NA",
                "median_capsule_bytes": f"{median(clean_bytes):.6f}" if clean_bytes else "NA",
                "median_events": f"{median(clean_events):.6f}" if clean_events else "NA",
                "n": n,
                "notes": "summary of analytic overflow/replay availability against measured event counts",
            }
        )
    return out


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
