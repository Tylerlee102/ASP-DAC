#!/usr/bin/env python3
"""Summarize local overflow contract evidence without inventing runtime rates."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HDL_CSV = REPO_ROOT / "results/processed/hdl_checks.csv"
FORMAL_CSV = REPO_ROOT / "results/processed/formal_coverage.csv"
SMOKE_CSV = REPO_ROOT / "results/processed/picorv32_smoke_summary.csv"
OUT_CSV = REPO_ROOT / "results/processed/overflow_contracts.csv"

FIELDNAMES = ["contract", "status", "evidence_level", "covered_cases", "source", "notes"]


def main() -> int:
    hdl_rows = _read_rows(HDL_CSV)
    formal_rows = _read_rows(FORMAL_CSV)
    smoke_rows = _read_rows(SMOKE_CSV)
    rows = [
        _directed_buffer_overflow_row(hdl_rows),
        _formal_capsule_buffer_row(formal_rows),
        _formal_recorder_overflow_row(formal_rows),
        _picorv32_no_overflow_row(smoke_rows),
        _runtime_overflow_todo_row(),
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if any(row["status"] == "FAIL" for row in rows) else 0


def _directed_buffer_overflow_row(rows: list[dict[str, str]]) -> dict[str, str]:
    row = _find(rows, check="tb_capsule_buffer")
    raw_log = row.get("raw_log", "results/raw/tb_capsule_buffer_vvp_run.txt")
    log_path = REPO_ROOT / Path(raw_log.replace("\\", "/"))
    marker_present = log_path.exists() and "RC_BUFFER_OVERFLOW_CHECK" in log_path.read_text(encoding="utf-8")
    status = "PASS" if row.get("status") == "PASS" and marker_present else "FAIL"
    return _row(
        "directed_capsule_buffer_first_overflow",
        status,
        "rtl-smoke",
        1 if status == "PASS" else 0,
        "results/processed/hdl_checks.csv; results/raw/tb_capsule_buffer_vvp_run.txt",
        "Depth-4 directed buffer simulation fills to capacity, checks first overflow, preserves count, and observes sticky overflow after freeze.",
    )


def _formal_capsule_buffer_row(rows: list[dict[str, str]]) -> dict[str, str]:
    row = _find(rows, module_family="capsule_buffer")
    obligations = row.get("obligations", "")
    status = "PASS" if row.get("status") == "PASS" and "sticky overflow" in obligations and "first-overflow behavior" in obligations else "FAIL"
    return _row(
        "formal_capsule_buffer_overflow_invariants",
        status,
        "formal-bmc",
        1 if status == "PASS" else 0,
        "results/processed/formal_coverage.csv",
        "Bounded capsule-buffer checks include count bounds, sticky overflow, and first-overflow behavior.",
    )


def _formal_recorder_overflow_row(rows: list[dict[str, str]]) -> dict[str, str]:
    row = _find(rows, module_family="replay_capsule_top")
    obligations = row.get("obligations", "")
    status = "PASS" if row.get("status") == "PASS" and "overflow reachability" in obligations else "FAIL"
    return _row(
        "formal_recorder_overflow_reachability",
        status,
        "formal-bmc",
        1 if status == "PASS" else 0,
        "results/processed/formal_coverage.csv",
        "Bounded top-level recorder cover checks include overflow reachability.",
    )


def _picorv32_no_overflow_row(rows: list[dict[str, str]]) -> dict[str, str]:
    checked = [
        row
        for row in rows
        if row.get("status") == "PASS" and row.get("capsule_overflow") in {"0", "1"}
    ]
    pass_count = sum(1 for row in checked if row.get("capsule_overflow") == "0")
    status = "PASS" if checked and pass_count == len(checked) else "FAIL"
    return _row(
        "picorv32_wrapper_smoke_no_overflow_sanity",
        status,
        "rtl-smoke",
        pass_count,
        "results/processed/picorv32_smoke_summary.csv",
        "Current PicoRV32 wrapper smoke capsules report no overflow; this is a smoke sanity check, not a benchmark-wide overflow-rate measurement.",
    )


def _runtime_overflow_todo_row() -> dict[str, str]:
    return _row(
        "benchmark_runtime_overflow_rate",
        "TODO",
        "rtl",
        0,
        "results/processed/overflow_contracts.csv",
        "Requires benchmark-wide firmware-running RTL counters or traces under realistic buffer configurations.",
    )


def _row(
    contract: str,
    status: str,
    evidence_level: str,
    covered_cases: int,
    source: str,
    notes: str,
) -> dict[str, str]:
    return {
        "contract": contract,
        "status": status,
        "evidence_level": evidence_level,
        "covered_cases": str(covered_cases),
        "source": source,
        "notes": notes,
    }


def _find(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in criteria.items()):
            return row
    return {}


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    raise SystemExit(main())
