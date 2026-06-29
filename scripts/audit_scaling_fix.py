#!/usr/bin/env python3
"""Audit the compressed workload-scaling fix evidence."""

from __future__ import annotations

import csv
from pathlib import Path

from topconf_eval_common import REPO_ROOT, read_csv, write_csv


OUT_CSV = REPO_ROOT / "results/processed/scaling_fix_audit.csv"
FIELDS = ["check", "status", "evidence", "detail"]
SCALES = ("smoke", "short", "medium", "long", "stress")


def main() -> int:
    rows = [
        _workload_rows_clean(),
        _workload_scale_coverage(),
        _depth_256_summary_clean(),
        _capsule_summary_present(),
    ]
    write_csv(OUT_CSV, FIELDS, rows)
    failures = [row for row in rows if row["status"] != "PASS"]
    print(f"WROTE {rel(OUT_CSV)}; FAIL rows={len(failures)}")
    return 1 if failures else 0


def _workload_rows_clean() -> dict[str, str]:
    rows = read_csv(REPO_ROOT / "results/processed/workload_scaling_fixed.csv")
    bad = [
        row
        for row in rows
        if row.get("architecture") != "v2"
        or row.get("recorder_config") != "core"
        or row.get("replay_status") != "PASS"
        or row.get("overflow") != "false"
        or row.get("strict_replay_valid") != "true"
    ]
    return _row(
        "workload_rows_clean",
        not bad and len(rows) > 0,
        "results/processed/workload_scaling_fixed.csv",
        f"rows={len(rows)} bad_rows={len(bad)}",
    )


def _workload_scale_coverage() -> dict[str, str]:
    rows = read_csv(REPO_ROOT / "results/processed/workload_scaling_fixed.csv")
    counts = {scale: 0 for scale in SCALES}
    for row in rows:
        scale = row.get("workload_scale", "")
        if scale in counts:
            counts[scale] += 1
    missing = [scale for scale, count in counts.items() if count == 0]
    balanced = len(set(counts.values())) == 1 and not missing
    return _row(
        "workload_scale_coverage",
        balanced,
        "results/processed/workload_scaling_fixed.csv",
        ";".join(f"{scale}={count}" for scale, count in counts.items()),
    )


def _depth_256_summary_clean() -> dict[str, str]:
    rows = read_csv(REPO_ROOT / "results/processed/buffer_sensitivity_fixed_summary.csv")
    depth_rows = [row for row in rows if row.get("buffer_depth") == "256"]
    by_scale = {row.get("workload_scale", ""): row for row in depth_rows}
    bad = [
        scale
        for scale in SCALES
        if by_scale.get(scale, {}).get("overflow_rate_pct") != "0.000000"
        or by_scale.get(scale, {}).get("replay_success_rate_pct") != "100.000000"
    ]
    return _row(
        "depth_256_summary_clean",
        not bad,
        "results/processed/buffer_sensitivity_fixed_summary.csv",
        f"checked_scales={len(by_scale)} bad_scales={','.join(bad) if bad else 'none'}",
    )


def _capsule_summary_present() -> dict[str, str]:
    rows = read_csv(REPO_ROOT / "results/processed/capsule_baseline_summary_fixed.csv")
    capsule = [row for row in rows if row.get("baseline") == "replaycapsule_core"]
    by_scale = {row.get("workload_scale", ""): row for row in capsule}
    bad = [
        scale
        for scale in SCALES
        if by_scale.get(scale, {}).get("median_bytes", "NA") in {"", "NA"}
        or by_scale.get(scale, {}).get("median_buffer_depth") != "256.000000"
    ]
    return _row(
        "capsule_summary_present",
        not bad,
        "results/processed/capsule_baseline_summary_fixed.csv",
        f"checked_scales={len(by_scale)} bad_scales={','.join(bad) if bad else 'none'}",
    )


def _row(check: str, passed: bool, evidence: str, detail: str) -> dict[str, str]:
    return {"check": check, "status": "PASS" if passed else "FAIL", "evidence": evidence, "detail": detail}


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
