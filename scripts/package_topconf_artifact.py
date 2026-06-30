#!/usr/bin/env python3
"""Package the expanded top-conference evaluation artifact."""

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
    "results/raw/topconf_ci",
    "results/debug/topconf_before",
)

EXCLUDE_PARTS = {".git", ".tools", "dist", "__pycache__", ".pytest_cache", ".mypy_cache"}
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
    rows = []
    zip_tmp = ZIP_PATH.with_name(ZIP_PATH.name + ".tmp")
    manifest_tmp = MANIFEST_CSV.with_name(MANIFEST_CSV.name + ".tmp")
    for tmp in (zip_tmp, manifest_tmp):
        if tmp.exists():
            tmp.unlink()
    try:
        with zipfile.ZipFile(zip_tmp, "w", compression=ZIP_COMPRESSION) as archive:
            for path in files:
                rel = path.relative_to(REPO_ROOT).as_posix()
                data = _archive_data(path)
                archive.writestr(rel, data)
                rows.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        with manifest_tmp.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["path", "bytes", "sha256"])
            writer.writeheader()
            writer.writerows(rows)
        zip_tmp.replace(ZIP_PATH)
        manifest_tmp.replace(MANIFEST_CSV)
    finally:
        for tmp in (zip_tmp, manifest_tmp):
            if tmp.exists():
                tmp.unlink()
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
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel == "results/processed/private_marker_scan.csv":
        return True
    if rel.startswith(("results/raw/mapped_synthesis/", "results/raw/mapped_scaling/")) and path.suffix.lower() in {".json", ".config", ".asc"}:
        return True
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


if __name__ == "__main__":
    raise SystemExit(main())
