#!/usr/bin/env python3
"""Build v1/v2 buffer-depth sensitivity tables with measured and analytic labels."""

from __future__ import annotations

import math
from statistics import median

from topconf_eval_common import REPO_ROOT, read_csv, safe_float, safe_int, write_csv


OUT_CSV = REPO_ROOT / "results/processed/buffer_sensitivity_v2.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/buffer_sensitivity_v2_summary.csv"
DEPTHS = (4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048)
CONFIGS = ("v1_full", "v2_minimal", "v2_core", "v2_hashed", "v2_diagnostic", "v2_full")

FIELDS = [
    "architecture",
    "recorder_config",
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
    "architecture",
    "recorder_config",
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
    for source in workload_rows:
        for config in CONFIGS:
            for depth in DEPTHS:
                rows.append(_row(source, config, depth))
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(SUMMARY_CSV, SUMMARY_FIELDS, _summary(rows))
    print("WROTE results/processed/buffer_sensitivity_v2.csv")
    print("WROTE results/processed/buffer_sensitivity_v2_summary.csv")
    return 0


def _row(source: dict[str, str], config: str, depth: int) -> dict[str, object]:
    architecture = "v1" if config == "v1_full" else "v2"
    recorder_config = "full" if config == "v1_full" else config.removeprefix("v2_")
    source_events = safe_int(source.get("events"))
    events = source_events if config == "v1_full" else _estimated_v2_events(source_events, recorder_config)
    bytes_value = safe_int(source.get("capsule_bytes")) if config == "v1_full" else _estimated_v2_bytes(events, recorder_config)
    overflow = "NA" if events is None else events > depth
    if config == "v1_full":
        replay_available = source.get("replay_status") == "PASS" and overflow is False
        replay_status = "PASS" if replay_available else "OVERFLOW" if overflow is True else source.get("replay_status", "NA")
        notes = "v1 analytic depth sweep from measured workload_scaling row"
    else:
        replay_available = overflow is False
        replay_status = "BLOCKED_CAPACITY_FIT" if replay_available else "ANALYTIC_OVERFLOW"
        notes = (
            "ANALYTIC v2 storage estimate only; no full-core v2 replay PASS is claimed. "
            "Replay consumer RTL is tested separately."
        )
        if source.get("overflow") == "true":
            notes += " Source v1 event count is a lower bound because the 256-entry v1 buffer overflowed."
    return {
        "architecture": architecture,
        "recorder_config": recorder_config,
        "benchmark": source.get("benchmark", "NA"),
        "variant": source.get("variant", "NA"),
        "seed": source.get("seed", "NA"),
        "workload_scale": source.get("workload_scale", "NA"),
        "buffer_depth": depth,
        "events": events if events is not None else "NA",
        "capsule_bytes": bytes_value if bytes_value is not None else "NA",
        "overflow": overflow,
        "replay_available": replay_available,
        "replay_status": replay_status,
        "cycles_to_failure": source.get("cycles_to_failure", "NA"),
        "commits_to_failure": source.get("commits_to_failure", "NA"),
        "notes": notes,
    }


def _estimated_v2_events(events: int | None, config: str) -> int | None:
    if events is None:
        return None
    factors = {
        "minimal": 0.12,
        "core": 0.35,
        "hashed": 0.35,
        "diagnostic": 0.65,
        "full": 1.00,
    }
    return max(1, math.ceil(events * factors.get(config, 1.0)))


def _estimated_v2_bytes(events: int | None, config: str) -> int | None:
    if events is None:
        return None
    per_event = {
        "minimal": 8,
        "core": 8,
        "hashed": 8,
        "diagnostic": 12,
        "full": 16,
    }.get(config, 8)
    return 16 + events * per_event


def _summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    keys = sorted({(str(row["architecture"]), str(row["recorder_config"]), int(row["buffer_depth"]), str(row["workload_scale"])) for row in rows})
    for arch, config, depth, scale in keys:
        subset = [row for row in rows if row["architecture"] == arch and row["recorder_config"] == config and int(row["buffer_depth"]) == depth and row["workload_scale"] == scale]
        n = len(subset)
        overflows = [row for row in subset if row["overflow"] is True or row["overflow"] == "true"]
        passes = [row for row in subset if row["replay_status"] == "PASS"]
        byte_values = [safe_float(row["capsule_bytes"]) for row in subset]
        event_values = [safe_float(row["events"]) for row in subset]
        clean_bytes = [value for value in byte_values if value is not None]
        clean_events = [value for value in event_values if value is not None]
        out.append(
            {
                "architecture": arch,
                "recorder_config": config,
                "buffer_depth": depth,
                "workload_scale": scale,
                "overflow_rate_pct": f"{(len(overflows) / n * 100.0):.6f}" if n and clean_events else "NA",
                "replay_success_rate_pct": f"{(len(passes) / n * 100.0):.6f}" if arch == "v1" and n and clean_events else "NA",
                "median_capsule_bytes": f"{median(clean_bytes):.6f}" if clean_bytes else "NA",
                "median_events": f"{median(clean_events):.6f}" if clean_events else "NA",
                "n": n,
                "notes": "v2 replay_success_rate_pct is NA because v2 full-core replay is not integrated/measured",
            }
        )
    return out


if __name__ == "__main__":
    raise SystemExit(main())
