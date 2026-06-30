#!/usr/bin/env python3
"""Exercise the v2 streamed capsule path with intermittent sink stalls."""

from __future__ import annotations

import os
from pathlib import Path

import run_full_rtl_replay
from topconf_eval_common import REPO_ROOT, rel, write_csv


OUT_CSV = REPO_ROOT / "results/processed/streaming_capture_tests.csv"
RAW_DIR = REPO_ROOT / "results/raw/streaming_capture_tests"
CAPSULE_DIR = RAW_DIR / "capsules"
SIGNATURE_DIR = RAW_DIR / "signatures"
CONFIGS = ("core", "hashed")

FIELDS = [
    "test_name",
    "architecture",
    "recorder_config",
    "fifo_depth",
    "benchmark",
    "variant",
    "seed",
    "expected_result",
    "actual_result",
    "passed",
    "stream_event_count",
    "stream_event_sent_count",
    "replay_critical_event_count",
    "stream_stall_count",
    "dropped_diagnostic_count",
    "replay_critical_overflow_count",
    "notes",
]


def main() -> int:
    for path in (CAPSULE_DIR, SIGNATURE_DIR):
        path.mkdir(parents=True, exist_ok=True)
    previous_depth = os.environ.get("REPLAYCAPSULE_CAPSULE_DEPTH")
    os.environ["REPLAYCAPSULE_CAPSULE_DEPTH"] = "8"
    try:
        blocker = run_full_rtl_replay._ensure_simulator()
        rows = [_run_config(config, blocker) for config in CONFIGS]
    finally:
        if previous_depth is None:
            os.environ.pop("REPLAYCAPSULE_CAPSULE_DEPTH", None)
        else:
            os.environ["REPLAYCAPSULE_CAPSULE_DEPTH"] = previous_depth

    write_csv(OUT_CSV, FIELDS, rows)
    passed = sum(1 for row in rows if row["passed"] == "true")
    print(f"WROTE {rel(OUT_CSV)}")
    print(f"STREAMING_CAPTURE_TESTS passed={passed} total={len(rows)}")
    return 0 if passed == len(rows) else 1


def _run_config(config: str, blocker: str | None) -> dict[str, object]:
    if blocker:
        return _row(config, "BLOCKED", False, notes=blocker)
    row = run_full_rtl_replay._run_case(
        "sensor_threshold_bug",
        "failing",
        1,
        100000,
        False,
        "v2",
        config,
        CAPSULE_DIR,
        SIGNATURE_DIR,
        stream_stall_test=True,
    )
    passed = (
        row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
        and row.get("replay_consumer_status") == "PASS"
        and _int(row.get("stream_stall_count")) > 0
        and _int(row.get("replay_critical_overflow_count")) == 0
        and _int(row.get("stream_event_count")) == _int(row.get("stream_event_sent_count"))
    )
    return _row(
        config,
        "PASS" if passed else row.get("replay_status", "FAIL"),
        passed,
        stream_event_count=row.get("stream_event_count", "NA"),
        stream_event_sent_count=row.get("stream_event_sent_count", "NA"),
        replay_critical_event_count=row.get("replay_critical_event_count", "NA"),
        stream_stall_count=row.get("stream_stall_count", "NA"),
        dropped_diagnostic_count=row.get("dropped_diagnostic_count", "NA"),
        replay_critical_overflow_count=row.get("replay_critical_overflow_count", "NA"),
        notes=row.get("notes", "NA"),
    )


def _row(
    config: str,
    actual: str,
    passed: bool,
    stream_event_count: object = "NA",
    stream_event_sent_count: object = "NA",
    replay_critical_event_count: object = "NA",
    stream_stall_count: object = "NA",
    dropped_diagnostic_count: object = "NA",
    replay_critical_overflow_count: object = "NA",
    notes: str = "NA",
) -> dict[str, object]:
    return {
        "test_name": f"streamed_capture_stall_depth8_{config}",
        "architecture": "v2",
        "recorder_config": config,
        "fifo_depth": 8,
        "benchmark": "sensor_threshold_bug",
        "variant": "failing",
        "seed": 1,
        "expected_result": "PASS",
        "actual_result": actual,
        "passed": "true" if passed else "false",
        "stream_event_count": stream_event_count,
        "stream_event_sent_count": stream_event_sent_count,
        "replay_critical_event_count": replay_critical_event_count,
        "stream_stall_count": stream_stall_count,
        "dropped_diagnostic_count": dropped_diagnostic_count,
        "replay_critical_overflow_count": replay_critical_overflow_count,
        "notes": notes,
    }


def _int(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return -1


if __name__ == "__main__":
    raise SystemExit(main())
