#!/usr/bin/env python3
"""Package the ReplayCapsule-RV artifact without local caches or fake reports."""

from __future__ import annotations

import csv
import hashlib
import zipfile
from pathlib import Path

try:
    import zlib as _zlib  # noqa: F401
except Exception:
    ZIP_COMPRESSION = zipfile.ZIP_STORED
else:
    ZIP_COMPRESSION = zipfile.ZIP_DEFLATED


REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"
ZIP_PATH = DIST_DIR / "replaycapsule-rv-artifact.zip"
MANIFEST_CSV = DIST_DIR / "artifact_package_manifest.csv"

INCLUDE_ROOTS = (
    "README.md",
    "artifact_evaluation.md",
    "Makefile",
    "Dockerfile",
    ".dockerignore",
    ".github",
    ".devcontainer",
    "requirements.txt",
    "scripts",
    "constraints",
    "docs",
    "formal",
    "firmware",
    "rtl",
    "tb",
    "third_party",
    "paper",
    "results/processed",
    "results/figures",
    "results/raw/model_suite_traces.json",
    "results/raw/firmware_sim_traces.json",
    "results/raw/phase12_sensor_threshold_trace.json",
    "results/raw/rtl_capsules",
    "results/raw/runtime_overhead",
    "results/raw/workload_scaling",
    "results/raw/event_ablation_scaling",
    "results/raw/mapped_scaling",
    "results/raw/topconf_ci",
    "results/debug/pass4",
    "results/debug/pass5_before",
    "results/debug/pass6_before",
    "results/debug/pass7_before",
    "results/debug/final_submission_lock",
)

INCLUDE_GLOBS = (
    "results/raw/verilator/build.log",
    "results/raw/mapped_synthesis/*.txt",
    "results/raw/mapped_synthesis/*.json",
    "results/raw/mapped_synthesis/*.config",
    "results/raw/mapped_synthesis/*.asc",
)

EXCLUDE_PARTS = {
    ".git",
    ".tools",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

EXCLUDE_SUFFIXES = (
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".map",
    ".out",
    ".pyc",
    ".run.xml",
    ".synctex.gz",
    ".vcd",
    ".vvp",
)

TEXT_ARCHIVE_SUFFIXES = {
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
    ".yaml",
}

PRIVATE_REPLACEMENTS = (
    ("C:" + "\\Users\\" + "ty" + "boy", "."),
    ("C:" + "/Users/" + "ty" + "boy", "."),
    ("\\Users\\" + "ty" + "boy", "\\Users\\USER"),
    ("/Users/" + "ty" + "boy", "/Users/USER"),
    ("One" + "Drive\\Documents\\" + "New project", "WORKSPACE"),
    ("One" + "Drive/Documents/" + "New project", "WORKSPACE"),
    ("One" + "Drive", "WORKSPACE"),
    ("Tyler" + "lee102", "anonymous"),
    ("github.com/" + "Tyler" + "lee102", "github.com/anonymous"),
    ("ty" + "boy", "user"),
)


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(_iter_files())
    manifest_rows = []
    with zipfile.ZipFile(ZIP_PATH, "w", compression=ZIP_COMPRESSION) as archive:
        for path in files:
            rel = path.relative_to(REPO_ROOT).as_posix()
            data = _archive_data(path)
            archive.writestr(rel, data)
            manifest_rows.append(
                {
                    "path": rel,
                    "bytes": str(len(data)),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )

    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"WROTE {_rel(ZIP_PATH)}")
    print(f"WROTE {_rel(MANIFEST_CSV)}")
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
            if candidate.is_dir():
                continue
            if _skip(candidate):
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            yield candidate
    for pattern in INCLUDE_GLOBS:
        for candidate in sorted(REPO_ROOT.glob(pattern)):
            if candidate.is_dir() or _skip(candidate) or candidate in seen:
                continue
            seen.add(candidate)
            yield candidate


def _skip(path: Path) -> bool:
    if path.relative_to(REPO_ROOT).as_posix() == "results/processed/private_marker_scan.csv":
        return True
    if path.relative_to(REPO_ROOT).as_posix() == "results/raw/verilator/build.log":
        return False
    rel_parts = set(path.relative_to(REPO_ROOT).parts)
    if rel_parts & EXCLUDE_PARTS:
        return True
    return path.suffix.lower() in EXCLUDE_SUFFIXES


def _archive_data(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() not in TEXT_ARCHIVE_SUFFIXES:
        return data
    text = data.decode("utf-8", errors="replace")
    for needle, replacement in PRIVATE_REPLACEMENTS:
        text = text.replace(needle, replacement)
    return text.encode("utf-8")


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
