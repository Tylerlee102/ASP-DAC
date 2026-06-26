#!/usr/bin/env python3
"""Audit final paper sources for unresolved draft markers and missing assets."""

from __future__ import annotations

import csv
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUT_CSV = REPO_ROOT / "results/processed/todo_audit.csv"

FORBIDDEN = (
    ("todo_marker", re.compile(r"\bTODO\b", re.IGNORECASE), "remove TODO markers from final paper body"),
    ("draft_currently", re.compile(r"draft currently", re.IGNORECASE), "avoid project-status wording"),
    ("pending_claim", re.compile(r"\bpending\b", re.IGNORECASE), "use precise limitations instead of pending claims"),
)

EXPECTED_ASSETS = (
    "paper/figures/architecture_overview.svg",
    "paper/figures/replay_flow.svg",
    "paper/figures/baseline_trace_sizes.svg",
    "paper/figures/ablation_heatmap.svg",
    "paper/figures/synthesis_status.svg",
    "paper/figures/table_event_sufficiency.md",
)

FIELDNAMES = ["check", "status", "file", "line", "detail"]


def main() -> int:
    rows: list[dict[str, str]] = []
    tex_files = _tex_files()
    for path in tex_files:
        rel = _rel(path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for name, regex, detail in FORBIDDEN:
                if regex.search(line):
                    rows.append(_row(name, "FAIL", rel, lineno, detail))

    rows.extend(_asset_rows())
    rows.extend(_citation_rows(tex_files))
    if not rows:
        rows.append(_row("paper_todo_audit", "PASS", "paper", "NA", "no unresolved TODO/draft markers, expected assets present, citations defined"))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    failures = [row for row in rows if row["status"] == "FAIL"]
    print(f"WROTE {OUT_CSV}; FAIL rows={len(failures)}")
    return 1 if failures else 0


def _asset_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for asset in EXPECTED_ASSETS:
        if not (REPO_ROOT / asset).exists():
            rows.append(_row("missing_asset", "FAIL", asset, "NA", "expected paper figure/table asset is missing"))
    return rows


def _citation_rows(tex_files: list[Path]) -> list[dict[str, str]]:
    cited: set[str] = set()
    for path in tex_files:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\\cite[tp]?\{([^}]+)\}", text):
            cited.update(key.strip() for key in match.group(1).split(",") if key.strip())

    bib_path = PAPER_DIR / "references.bib"
    if not cited:
        return [_row("citation_presence", "FAIL", "paper", "NA", "paper should cite related work")]
    if not bib_path.exists():
        return [_row("bibliography", "FAIL", "paper/references.bib", "NA", "bibliography file is missing")]

    bib_text = bib_path.read_text(encoding="utf-8")
    defined = set(re.findall(r"@\w+\{([^,\s]+)", bib_text))
    rows: list[dict[str, str]] = []
    for key in sorted(cited - defined):
        rows.append(_row("undefined_citation", "FAIL", "paper/references.bib", "NA", f"citation key {key} is not defined"))
    return rows


def _tex_files() -> list[Path]:
    paths = [PAPER_DIR / "main.tex"]
    sections = PAPER_DIR / "sections"
    if sections.exists():
        paths.extend(sorted(sections.glob("*.tex")))
    return [path for path in paths if path.exists()]


def _row(check: str, status: str, file: str, line: int | str, detail: str) -> dict[str, str]:
    return {"check": check, "status": status, "file": file, "line": str(line), "detail": detail}


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
