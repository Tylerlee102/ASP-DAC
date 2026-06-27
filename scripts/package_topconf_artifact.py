#!/usr/bin/env python3
"""Package the expanded top-conference evaluation artifact."""

from __future__ import annotations

import csv
import hashlib
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"
ZIP_PATH = DIST_DIR / "replaycapsule-rv-topconf-artifact.zip"
MANIFEST_CSV = DIST_DIR / "topconf_artifact_package_manifest.csv"

INCLUDE_ROOTS = (
    "README.md",
    "artifact_evaluation.md",
    "Makefile",
    "Dockerfile",
    "requirements.txt",
    ".github",
    ".devcontainer",
    "constraints",
    "docs",
    "formal",
    "firmware",
    "rtl",
    "tb",
    "third_party",
    "scripts",
    "paper",
    "results/processed",
    "results/figures",
    "results/raw/verilator",
    "results/raw/runtime_overhead",
    "results/raw/mapped_synthesis",
    "results/raw/mapped_scaling",
    "results/raw/workload_scaling",
    "results/raw/recorder_config",
    "results/raw/event_ablation_scaling",
    "results/debug/topconf_before",
)

EXCLUDE_PARTS = {".git", ".tools", "dist", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDE_SUFFIXES = (".pyc", ".vvp", ".vcd")


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(_iter_files())
    rows = []
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            rel = path.relative_to(REPO_ROOT).as_posix()
            data = path.read_bytes()
            archive.writestr(rel, data)
            rows.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE dist/replaycapsule-rv-topconf-artifact.zip")
    print(f"WROTE dist/topconf_artifact_package_manifest.csv")
    print(f"PACKAGED {len(files)} files")
    return 0


def _iter_files():
    seen: set[Path] = set()
    for root in INCLUDE_ROOTS:
        path = REPO_ROOT / root
        if not path.exists():
            continue
        candidates = path.rglob("*") if path.is_dir() else (path,)
        for candidate in candidates:
            if candidate.is_dir() or _skip(candidate) or candidate in seen:
                continue
            seen.add(candidate)
            yield candidate


def _skip(path: Path) -> bool:
    rel_parts = set(path.relative_to(REPO_ROOT).parts)
    if rel_parts & EXCLUDE_PARTS:
        return True
    return path.suffix.lower() in EXCLUDE_SUFFIXES


if __name__ == "__main__":
    raise SystemExit(main())
