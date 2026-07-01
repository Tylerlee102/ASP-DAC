#!/usr/bin/env python3
"""Check numeric paper claims against generated CSV/config artifacts."""

from __future__ import annotations

import csv
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUT_CSV = REPO_ROOT / "results/processed/paper_number_audit.csv"

FIELDNAMES = ["status", "file", "line", "number", "context", "notes"]

TOKEN_RE = re.compile(r"(?<![A-Za-z\\])(?<![A-Za-z]-)(\d+(?:\.\d+)?%?x?)(?![A-Za-z])")


def main() -> int:
    allowed = _allowed_numbers()
    rows: list[dict[str, str]] = []
    for path in _tex_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if _skip_line(line):
                continue
            for match in TOKEN_RE.finditer(line):
                token = match.group(1)
                normalized = token.rstrip("%x")
                if normalized not in allowed:
                    rows.append(
                        {
                            "status": "FAIL",
                            "file": rel,
                            "line": str(lineno),
                            "number": token,
                            "context": line.strip(),
                            "notes": "number not found in generated CSV, generated table, or explicit config",
                        }
                    )

    if not rows:
        rows.append(
            {
                "status": "PASS",
                "file": "paper",
                "line": "NA",
                "number": "NA",
                "context": "No uncited numeric claims found.",
                "notes": "numeric audit passed",
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    failures = [row for row in rows if row["status"] == "FAIL"]
    print(f"WROTE {OUT_CSV}; FAIL rows={len(failures)}")
    return 1 if failures else 0


def _allowed_numbers() -> set[str]:
    values: set[str] = set()
    for path in sorted((REPO_ROOT / "results/processed").glob("*.csv")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in TOKEN_RE.finditer(text):
            values.add(match.group(1).rstrip("%x"))
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                row_count = sum(1 for _ in csv.DictReader(handle))
            values.add(str(row_count))
        except (OSError, csv.Error):
            pass
    for path in sorted((REPO_ROOT / "paper/figures").glob("table*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in TOKEN_RE.finditer(text):
            values.add(match.group(1).rstrip("%x"))
    for path in (REPO_ROOT / "Makefile", REPO_ROOT / "requirements.txt"):
        if not path.exists():
            continue
        for match in TOKEN_RE.finditer(path.read_text(encoding="utf-8", errors="replace")):
            values.add(match.group(1).rstrip("%x"))
    return values


def _tex_files() -> list[Path]:
    paths = [PAPER_DIR / "main.tex"]
    sections = PAPER_DIR / "sections"
    if sections.exists():
        paths.extend(sorted(sections.glob("*.tex")))
    return [path for path in paths if path.exists()]


def _skip_line(line: str) -> bool:
    stripped = line.strip()
    return (
        stripped.startswith("%")
        or stripped.startswith("\\label")
        or stripped.startswith("\\ref")
        or "\\cite" in stripped
        or "\\texttt" in stripped
        or "\\IfFileExists" in stripped
        or "\\parbox" in stripped
        or "\\bibliographystyle" in stripped
        or "\\documentclass" in stripped
        or "\\includegraphics" in stripped
        or "\\input" in stripped
    )


if __name__ == "__main__":
    raise SystemExit(main())
