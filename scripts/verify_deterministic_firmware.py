#!/usr/bin/env python3
"""Build firmware twice in clean directories and compare compiler HEX hashes."""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/deterministic_firmware.csv"
BUILD_ROOT = REPO_ROOT / "build/deterministic_firmware"
SOURCE_DATE_EPOCH = "1704067200"

FIELDS = [
    "benchmark",
    "variant",
    "first_hex",
    "second_hex",
    "first_sha256",
    "second_sha256",
    "status",
    "notes",
]


def main() -> int:
    first_root = BUILD_ROOT / "first"
    second_root = BUILD_ROOT / "second"
    shutil.rmtree(first_root, ignore_errors=True)
    shutil.rmtree(second_root, ignore_errors=True)

    first_csv = first_root / "firmware_build.csv"
    second_csv = second_root / "firmware_build.csv"
    first_code = _run_build(first_root, first_csv)
    second_code = _run_build(second_root, second_csv)

    rows: list[dict[str, str]] = []
    failures: list[str] = []
    first_rows = _case_rows(first_csv)
    second_rows = _case_rows(second_csv)
    for key in sorted(set(first_rows) | set(second_rows)):
        first = first_rows.get(key)
        second = second_rows.get(key)
        if first is None or second is None:
            row = _row(key, first, second, "FAIL", "missing row in one build")
            failures.append(f"{key[0]}/{key[1]} missing row in one build")
        elif not _is_compiler_row(first) or not _is_compiler_row(second):
            row = _row(key, first, second, "FAIL", "one or both rows are not compiler-backed PASS")
            failures.append(f"{key[0]}/{key[1]} not compiler-backed in both builds")
        elif first.get("sha256_hex") != second.get("sha256_hex"):
            row = _row(key, first, second, "FAIL", "HEX hashes differ")
            failures.append(f"{key[0]}/{key[1]} hash mismatch")
        else:
            row = _row(key, first, second, "PASS", "hashes match")
        rows.append(row)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    if first_code != 0 or second_code != 0:
        failures.append(f"build return codes first={first_code} second={second_code}")
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        print(f"WROTE {_rel(OUT_CSV)}")
        return 1
    print(f"PASS: deterministic compiler firmware hashes match for {len(rows)} rows")
    print(f"WROTE {_rel(OUT_CSV)}")
    return 0


def _run_build(root: Path, out_csv: Path) -> int:
    root.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["REPLAYCAPSULE_FIRMWARE_BUILD_ROOT"] = str(root)
    env["REPLAYCAPSULE_FIRMWARE_BUILD_CSV"] = str(out_csv)
    env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    completed = subprocess.run(
        [sys.executable, "scripts/build_firmware.py", "--require-compiler"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log = root / "build.log"
    log.write_text(completed.stdout, encoding="utf-8")
    return completed.returncode


def _case_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row.get("benchmark", ""), row.get("variant", "")): row for row in csv.DictReader(handle)}


def _is_compiler_row(row: dict[str, str]) -> bool:
    return (
        row.get("build_status") == "PASS"
        and row.get("firmware_source") == "compiler_c"
        and row.get("status") == "PASS"
        and row.get("build_source") == "compiler_c"
        and row.get("compiler_available") == "true"
        and row.get("fallback_used") == "false"
        and row.get("artifact_sanity") == "PASS"
    )


def _row(
    key: tuple[str, str],
    first: dict[str, str] | None,
    second: dict[str, str] | None,
    status: str,
    notes: str,
) -> dict[str, str]:
    first = first or {}
    second = second or {}
    return {
        "benchmark": key[0],
        "variant": key[1],
        "first_hex": first.get("hex_path", "NA"),
        "second_hex": second.get("hex_path", "NA"),
        "first_sha256": first.get("sha256_hex", "NA"),
        "second_sha256": second.get("sha256_hex", "NA"),
        "status": status,
        "notes": notes,
    }


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
