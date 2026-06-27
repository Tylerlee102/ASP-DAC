#!/usr/bin/env python3
"""Fail if public text or packaged artifacts contain local path markers."""

from __future__ import annotations

import argparse
import csv
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/private_marker_scan.csv"

NEEDLES = (
    "C:" + "\\Users\\",
    "C:" + "/Users/",
    "OneDrive\\Documents\\" + "New project",
    "OneDrive/Documents/" + "New project",
    "::git-" + "stage",
    "::git-" + "commit",
    "::git-" + "push",
)

SKIP_DIRS = {
    ".git",
    ".tools",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "firmware/build",
    "firmware/build_scaled",
}

TEXT_SUFFIXES = {
    "",
    ".c",
    ".cpp",
    ".csv",
    ".h",
    ".json",
    ".ld",
    ".lpf",
    ".md",
    ".py",
    ".sh",
    ".sv",
    ".svh",
    ".tex",
    ".txt",
    ".v",
    ".yml",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-zips", action="store_true", help="scan repository text only")
    args = parser.parse_args()

    rows = []
    rows.extend(_scan_files())
    if not args.skip_zips:
        rows.extend(_scan_zips())
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["location", "marker", "status", "notes"])
        writer.writeheader()
        if rows:
            writer.writerows(rows)
        else:
            writer.writerow({"location": "repo", "marker": "none", "status": "PASS", "notes": "no private markers found"})
    if rows:
        for row in rows:
            print(f"PRIVATE_MARKER {row['location']} {row['marker']}")
        return 1
    print("PRIVATE_MARKER_SCAN PASS")
    return 0


def _scan_files() -> list[dict[str, str]]:
    rows = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if path.is_dir() or _skip(path):
            continue
        rows.extend(_scan_bytes(_rel(path), path.read_bytes()))
    return rows


def _scan_zips() -> list[dict[str, str]]:
    rows = []
    for archive_path in sorted((REPO_ROOT / "dist").glob("*.zip")) if (REPO_ROOT / "dist").exists() else []:
        with zipfile.ZipFile(archive_path) as archive:
            for name in archive.namelist():
                if name.endswith("/"):
                    continue
                rows.extend(_scan_bytes(f"{_rel(archive_path)}!{name}", archive.read(name)))
    return rows


def _scan_bytes(location: str, data: bytes) -> list[dict[str, str]]:
    rows = []
    for needle in NEEDLES:
        if needle.encode("utf-8") in data:
            rows.append({"location": location, "marker": needle, "status": "FAIL", "notes": "remove or rewrite with repo-relative path"})
    return rows


def _skip(path: Path) -> bool:
    if path == OUT_CSV:
        return True
    rel = path.relative_to(REPO_ROOT).as_posix()
    if any(rel == skip or rel.startswith(skip + "/") for skip in SKIP_DIRS):
        return True
    if path.suffix.lower() == ".zip":
        return True
    return path.suffix.lower() not in TEXT_SUFFIXES


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
