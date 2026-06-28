#!/usr/bin/env python3
"""Fail if any full RTL replay PASS is backed by fallback firmware."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPLAY = (
    REPO_ROOT / "results/processed/full_rtl_replay.csv",
    REPO_ROOT / "results/processed/full_rtl_replay_v2.csv",
)
DEFAULT_FIRMWARE = REPO_ROOT / "results/processed/firmware_build.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firmware", type=Path, default=DEFAULT_FIRMWARE)
    parser.add_argument("--replay", type=Path, nargs="*", default=list(DEFAULT_REPLAY))
    args = parser.parse_args()

    firmware_rows = _rows(args.firmware)
    firmware_by_case = {(row.get("benchmark", ""), row.get("variant", "")): row for row in firmware_rows}
    failures: list[str] = []

    for replay_csv in args.replay:
        if not replay_csv.exists():
            continue
        for row in _rows(replay_csv):
            if not _is_replay_pass(row):
                continue
            key = (row.get("benchmark", ""), row.get("variant", ""))
            firmware = firmware_by_case.get(key)
            if firmware is None:
                failures.append(f"{_rel(replay_csv)} {key[0]}/{key[1]} PASS has no firmware_build.csv row")
                continue
            if row.get("compiler_backed") != "true" or row.get("firmware_source") != "compiler_c":
                failures.append(
                    f"{_rel(replay_csv)} {key[0]}/{key[1]} PASS row is not marked compiler-backed "
                    f"(compiler_backed={row.get('compiler_backed')}, firmware_source={row.get('firmware_source')})"
                )
            blocker = _firmware_blocker(firmware)
            if blocker:
                failures.append(f"{_rel(replay_csv)} {key[0]}/{key[1]} PASS uses invalid firmware evidence: {blocker}")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print("PASS: no full RTL replay PASS row is backed by fallback firmware")
    return 0


def _rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _is_replay_pass(row: dict[str, str]) -> bool:
    return (
        row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
    )


def _firmware_blocker(row: dict[str, str]) -> str:
    required = {
        "build_status": "PASS",
        "firmware_source": "compiler_c",
        "status": "PASS",
        "build_source": "compiler_c",
        "compiler_available": "true",
        "fallback_used": "false",
        "artifact_sanity": "PASS",
    }
    mismatches = [f"{field}={row.get(field, 'MISSING')}" for field, expected in required.items() if row.get(field) != expected]
    return "; ".join(mismatches)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
