#!/usr/bin/env python3
"""Inventory every current v2 failure/blocker required for zero-fail closure."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/v2_zero_fail_bug_inventory.csv"

FIELDS = [
    "bug_id",
    "area",
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "memory_words",
    "buffer_depth",
    "target",
    "flow",
    "current_status",
    "error_code",
    "first_failure_stage",
    "root_cause",
    "evidence_file",
    "required_for_zero_fail",
    "fix_status",
    "notes",
]


def main() -> int:
    rows: list[dict[str, str]] = []
    rows.extend(_full_rtl_rows())
    rows.extend(_workload_rows())
    rows.extend(_buffer_rows())
    rows.extend(_capsule_rows())
    rows.extend(_runtime_rows())
    rows.extend(_mapped_rows())
    rows.extend(_replay_consumer_rows())
    rows.extend(_expanded_benchmark_rows())
    for index, row in enumerate(rows, start=1):
        row["bug_id"] = f"V2ZF-{index:05d}"
    _write_csv(OUT_CSV, rows)
    summary = Counter(row["area"] for row in rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    print("BUG_INVENTORY " + " ".join(f"{area}={count}" for area, count in sorted(summary.items())))
    return 0


def _full_rtl_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/full_rtl_replay_v2.csv"
    out = []
    for row in _read_csv(path):
        statuses = {
            "rtl_record_status": row.get("rtl_record_status", "NA"),
            "capsule_export_status": row.get("capsule_export_status", "NA"),
            "replay_status": row.get("replay_status", "NA"),
            "replay_consumer_checked": row.get("replay_consumer_checked", "NA"),
            "replay_consumer_status": row.get("replay_consumer_status", "NA"),
            "commit_match": row.get("commit_match", "NA"),
            "event_match": row.get("event_match", "NA"),
            "final_signature_match": row.get("final_signature_match", "NA"),
        }
        if _is_clean_replay_row(statuses):
            continue
        out.append(
            _bug(
                area=_area_for_replay(row),
                row=row,
                current_status=_current_status(statuses),
                error_code=_error_code(row.get("notes", "")),
                first_failure_stage=_first_bad_stage(statuses),
                root_cause=_root_cause_for(row),
                evidence_file=_rel(path),
                notes=row.get("notes", ""),
            )
        )
    return out


def _workload_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/workload_scaling_v2_measured.csv"
    out = []
    for row in _read_csv(path):
        statuses = {
            "replay_status": row.get("replay_status", "NA"),
            "final_signature_match": row.get("final_signature_match", "NA"),
            "event_match": row.get("event_match", "NA"),
            "overflow": row.get("overflow", "NA"),
        }
        if (
            row.get("measured_or_estimated") == "MEASURED"
            and row.get("replay_status") == "PASS"
            and row.get("final_signature_match") == "PASS"
            and row.get("event_match") == "PASS"
            and row.get("overflow") != "true"
        ):
            continue
        out.append(
            _bug(
                area=_area_for_workload(row),
                row=row,
                current_status=_current_status(statuses),
                error_code=_error_code(row.get("notes", "")),
                first_failure_stage=_first_bad_stage(statuses),
                root_cause=_root_cause_for(row),
                evidence_file=_rel(path),
                notes=row.get("notes", ""),
            )
        )
    return out


def _buffer_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/buffer_sensitivity_v2_measured.csv"
    out = []
    for row in _read_csv(path):
        if row.get("architecture") != "v2":
            continue
        status = row.get("replay_status", "NA")
        measured = row.get("measured_or_estimated", "NA")
        overflow = row.get("overflow", "NA")
        if measured == "BLOCKED" and "not measured at this buffer depth" in row.get("notes", ""):
            continue
        if measured == "MEASURED" and status == "PASS" and overflow != "true":
            continue
        out.append(
            _bug(
                area="BUFFER_OVERFLOW" if overflow == "true" else "BUFFER_OVERFLOW",
                row=row,
                current_status="BLOCKED" if measured == "BLOCKED" else status,
                error_code="NA",
                first_failure_stage="buffer_depth_measurement" if measured == "BLOCKED" else "replay_status",
                root_cause="depth not measured" if measured == "BLOCKED" else _root_cause_for(row),
                evidence_file=_rel(path),
                notes=row.get("notes", ""),
            )
        )
    return out


def _capsule_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/capsule_baseline_comparison_v2_measured.csv"
    out = []
    for row in _read_csv(path):
        if row.get("architecture") != "v2":
            continue
        if row.get("measured_or_estimated") != "MEASURED":
            out.append(
                _bug(
                    area="CAPSULE_EXPORT",
                    row=row,
                    current_status="BLOCKED",
                    error_code="NA",
                    first_failure_stage="capsule_measurement",
                    root_cause="v2 capsule row is not measured",
                    evidence_file=_rel(path),
                    notes=row.get("notes", ""),
                )
            )
            continue
        if row.get("bytes") in {"", "NA"} or row.get("events") in {"", "NA"}:
            out.append(
                _bug(
                    area="CAPSULE_EXPORT",
                    row=row,
                    current_status="BLOCKED",
                    error_code="NA",
                    first_failure_stage="capsule_measurement",
                    root_cause="missing measured capsule bytes/events",
                    evidence_file=_rel(path),
                    notes=row.get("notes", ""),
                )
            )
    return out


def _runtime_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/runtime_scaling_v2_measured.csv"
    out = []
    for row in _read_csv(path):
        if row.get("config") == "baseline_no_recorder":
            continue
        if row.get("status") == "MEASURED":
            continue
        out.append(
            _bug(
                area="RUNTIME_HARNESS",
                row=row,
                current_status=row.get("status", "NA"),
                error_code="NA",
                first_failure_stage="runtime_harness",
                root_cause="missing v2 runtime harness mode",
                evidence_file=_rel(path),
                notes=row.get("notes", ""),
            )
        )
    return out


def _mapped_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/mapped_scaling_v2_measured.csv"
    out = []
    required_configs = _claimable_mapped_configs()
    for row in _read_csv(path):
        if row.get("architecture") != "v2":
            continue
        if row.get("recorder_config") not in required_configs:
            continue
        if row.get("status") == "PASS":
            continue
        out.append(
            _bug(
                area="MAPPED_SYNTHESIS",
                row=row,
                current_status=row.get("status", "NA"),
                error_code="NA",
                first_failure_stage="place_and_route",
                root_cause="full-core v2 board mapping flow blocked",
                evidence_file=_rel(path),
                notes=row.get("notes", ""),
            )
        )
    presence_path = REPO_ROOT / "results/processed/mapped_recorder_presence_v2_measured.csv"
    for row in _read_csv(presence_path):
        if row.get("architecture") != "v2":
            continue
        if row.get("recorder_config") not in required_configs:
            continue
        if row.get("status") == "PASS" and row.get("recorder_present") == "true":
            continue
        out.append(
            _bug(
                area="RECORDER_PRESENCE",
                row=row,
                current_status=row.get("status", "NA"),
                error_code="NA",
                first_failure_stage="recorder_presence",
                root_cause="recorder presence not proven in mapped v2 design",
                evidence_file=_rel(presence_path),
                notes=row.get("notes", ""),
            )
        )
    return out


def _replay_consumer_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/replay_consumer_system_tests.csv"
    out = []
    for row in _read_csv(path):
        if row.get("passed") == "true":
            continue
        out.append(
            _bug(
                area="REPLAY_CONSUME_SYSTEM",
                row=row,
                current_status=row.get("actual_result", "FAIL"),
                error_code=row.get("error_code", "NA"),
                first_failure_stage=row.get("test_name", "system_test"),
                root_cause="unexpected replay-consume system test result",
                evidence_file=_rel(path),
                notes=row.get("notes", ""),
            )
        )
    return out


def _expanded_benchmark_rows() -> list[dict[str, str]]:
    path = REPO_ROOT / "results/processed/expanded_benchmark_replay_measured.csv"
    if not path.exists():
        return [
            _bug(
                area="BENCHMARK_EXPANSION",
                row={},
                current_status="BLOCKED",
                error_code="NA",
                first_failure_stage="expanded_benchmark_measurement",
                root_cause="missing expanded_benchmark_replay_measured.csv",
                evidence_file=_rel(path),
                notes="at least two new benchmark families are required",
            )
        ]
    out = []
    rows = _read_csv(path)
    passed_rows = [
        row for row in rows
        if row.get("replay_status") == "PASS"
        and row.get("compiler_backed") == "true"
        and row.get("rtl_record_status") == "PASS"
        and row.get("capsule_export_status") == "PASS"
        and row.get("replay_consumer_status") == "PASS"
    ]
    passed_families = {row.get("benchmark", "") for row in passed_rows}
    passed_configs = {row.get("recorder_config", "") for row in passed_rows}
    passed_seeds = {row.get("seed", "") for row in passed_rows}
    for row in rows:
        if row in passed_rows:
            continue
        out.append(
            _bug(
                area="BENCHMARK_EXPANSION",
                row=row,
                current_status=row.get("replay_status", "BLOCKED"),
                error_code=_error_code(row.get("notes", "")),
                first_failure_stage="expanded_benchmark_replay",
                root_cause="expanded benchmark row not passing compiler-backed replay",
                evidence_file=_rel(path),
                notes=row.get("notes", ""),
            )
        )
    if len(passed_families) < 2:
        out.append(
            _bug(
                area="BENCHMARK_EXPANSION",
                row={},
                current_status="BLOCKED",
                error_code="NA",
                first_failure_stage="expanded_benchmark_coverage",
                root_cause="fewer than two benchmark families have measured PASS rows",
                evidence_file=_rel(path),
                notes=f"passing_families={len(passed_families)}",
            )
        )
    if not {"core", "hashed", "full"} <= passed_configs or len(passed_seeds) < 3:
        out.append(
            _bug(
                area="BENCHMARK_EXPANSION",
                row={},
                current_status="BLOCKED",
                error_code="NA",
                first_failure_stage="expanded_benchmark_coverage",
                root_cause="expanded benchmark coverage does not span all required configs and seeds",
                evidence_file=_rel(path),
                notes=f"passing_configs={','.join(sorted(passed_configs))}; passing_seeds={','.join(sorted(passed_seeds))}",
            )
        )
    return out


def _bug(
    *,
    area: str,
    row: dict[str, str],
    current_status: str,
    error_code: str,
    first_failure_stage: str,
    root_cause: str,
    evidence_file: str,
    notes: str,
) -> dict[str, str]:
    return {
        "bug_id": "",
        "area": area,
        "architecture": row.get("architecture", "v2"),
        "recorder_config": row.get("recorder_config", row.get("config", "NA")),
        "benchmark": row.get("benchmark", "NA"),
        "variant": row.get("variant", "NA"),
        "seed": row.get("seed", "NA"),
        "workload_scale": row.get("workload_scale", "NA"),
        "memory_words": row.get("memory_words", "NA"),
        "buffer_depth": row.get("buffer_depth", "NA"),
        "target": row.get("target", "NA"),
        "flow": row.get("flow", "NA"),
        "current_status": current_status,
        "error_code": error_code,
        "first_failure_stage": first_failure_stage,
        "root_cause": root_cause,
        "evidence_file": evidence_file,
        "required_for_zero_fail": "true",
        "fix_status": "OPEN",
        "notes": notes,
    }


def _is_clean_replay_row(statuses: dict[str, str]) -> bool:
    return (
        statuses.get("rtl_record_status") == "PASS"
        and statuses.get("capsule_export_status") == "PASS"
        and statuses.get("replay_status") == "PASS"
        and statuses.get("replay_consumer_checked") == "true"
        and statuses.get("replay_consumer_status") == "PASS"
        and statuses.get("commit_match") in {"PASS", "NA"}
        and statuses.get("event_match") == "PASS"
        and statuses.get("final_signature_match") == "PASS"
    )


def _claimable_mapped_configs() -> set[str]:
    overhead_path = REPO_ROOT / "results/processed/mapped_scaling_overhead_v2_measured.csv"
    configs = {
        row.get("recorder_config", "")
        for row in _read_csv(overhead_path)
        if row.get("claim_allowed") == "yes"
    }
    return configs or {"minimal"}


def _current_status(statuses: dict[str, str]) -> str:
    for value in statuses.values():
        if value in {"TIMEOUT", "BLOCKED"}:
            return value
    for value in statuses.values():
        if value in {"FAIL", "MISMATCH"}:
            return value
    if statuses.get("overflow") == "true":
        return "FAIL"
    return "FAIL"


def _first_bad_stage(statuses: dict[str, str]) -> str:
    for key, value in statuses.items():
        if value not in {"PASS", "true", "True", "false", "False", "NA", ""}:
            return key
    return "unknown"


def _area_for_replay(row: dict[str, str]) -> str:
    if row.get("recorder_config") in {"hashed", "full"} and _error_code(row.get("notes", "")) == "EVENT_MISMATCH":
        return "PAYLOAD_HASH"
    return "ORIGINAL_REPLAY"


def _area_for_workload(row: dict[str, str]) -> str:
    if row.get("recorder_config") in {"hashed", "full"} and _error_code(row.get("notes", "")) == "EVENT_MISMATCH":
        return "PAYLOAD_HASH"
    if row.get("benchmark") == "interrupt_race_bug" and row.get("variant") == "failing":
        return "INTERRUPT_TIMING"
    if row.get("overflow") == "true":
        return "BUFFER_OVERFLOW"
    return "WORKLOAD_SCALING"


def _root_cause_for(row: dict[str, str]) -> str:
    notes = row.get("notes", "")
    code = _error_code(notes)
    if row.get("recorder_config") in {"hashed", "full"} and code == "EVENT_MISMATCH":
        return "hashed payload replaces raw replay payload"
    if row.get("benchmark") == "interrupt_race_bug" and row.get("variant") == "failing":
        return "interrupt timing/commit mismatch under scaled delay"
    if row.get("overflow") == "true":
        return "capsule buffer overflow"
    if code != "NA":
        return code
    return notes or "unknown"


def _error_code(notes: str) -> str:
    match = re.search(r"error_code=([A-Z0-9_]+)", notes or "")
    return match.group(1) if match else "NA"


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
