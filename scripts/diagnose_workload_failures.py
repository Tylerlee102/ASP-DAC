#!/usr/bin/env python3
"""Classify every non-PASS workload-scaling row without changing the source result."""

from __future__ import annotations

from topconf_eval_common import REPO_ROOT, read_csv, write_csv


OUT_CSV = REPO_ROOT / "results/processed/workload_failure_diagnosis.csv"
FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "status",
    "first_failure_stage",
    "root_cause",
    "buffer_depth",
    "events",
    "capsule_bytes",
    "overflow",
    "expected_failure",
    "actual_failure",
    "first_divergence",
    "fix_needed",
    "notes",
]


def main() -> int:
    rows = [row for row in read_csv(REPO_ROOT / "results/processed/workload_scaling.csv") if row.get("replay_status") != "PASS"]
    out = [_diagnose(row) for row in rows]
    write_csv(OUT_CSV, FIELDS, out)
    print(f"WROTE results/processed/workload_failure_diagnosis.csv")
    print(f"WORKLOAD_FAILURE_DIAGNOSIS rows={len(out)}")
    return 0


def _diagnose(row: dict[str, str]) -> dict[str, object]:
    notes = row.get("notes", "")
    overflow = row.get("overflow", "NA")
    final_match = row.get("final_signature_match", "NA")
    event_match = row.get("event_match", "NA")
    root = "UNKNOWN"
    stage = "replay"
    expected = "false"
    fix = "inspect raw replay logs and event comparator"
    divergence = notes or "NA"

    if row.get("replay_status") == "TIMEOUT":
        root = "TIMEOUT_LIMIT_TOO_LOW"
        stage = "record_or_replay_timeout"
        fix = "raise timeout after checking simulator progress"
    elif overflow == "true":
        root = "BUFFER_OVERFLOW"
        stage = "record_buffer_capacity"
        expected = "true"
        fix = "increase buffer depth or use v2 adaptive compressed replay-critical capture"
        if "WRONG_PROPERTY" in notes:
            divergence = "property mismatch after overflow; overflow is the first visible capacity failure"
    elif "TRUNC" in notes.upper():
        root = "CAPSULE_TRUNCATION"
        stage = "capsule_export"
        fix = "preserve complete capsule stream"
    elif event_match == "FAIL":
        root = "EVENT_MISMATCH"
        stage = "replay_compare"
        fix = "debug first mismatching event"
    elif final_match == "FAIL" or "WRONG_PROPERTY" in notes:
        root = "PROPERTY_MISMATCH"
        stage = "property_compare"
        fix = "debug property checker inputs and replay stimulus"
    elif row.get("replay_status") == "BLOCKED":
        root = "SCRIPT_BUG" if "missing" not in notes.lower() else "EXPECTED_NO_REPLAY"
        stage = "harness_setup"
        fix = "restore missing prerequisite before rerunning"

    return {
        "benchmark": row.get("benchmark", "NA"),
        "variant": row.get("variant", "NA"),
        "seed": row.get("seed", "NA"),
        "workload_scale": row.get("workload_scale", "NA"),
        "status": row.get("replay_status", "NA"),
        "first_failure_stage": stage,
        "root_cause": root,
        "buffer_depth": "256",
        "events": row.get("events", "NA"),
        "capsule_bytes": row.get("capsule_bytes", "NA"),
        "overflow": overflow,
        "expected_failure": expected,
        "actual_failure": notes or row.get("replay_status", "NA"),
        "first_divergence": divergence,
        "fix_needed": fix,
        "notes": "diagnostic row; source workload_scaling.csv was not modified",
    }


if __name__ == "__main__":
    raise SystemExit(main())
