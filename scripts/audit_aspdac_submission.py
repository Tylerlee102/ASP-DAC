#!/usr/bin/env python3
"""Audit ASP-DAC 2027 review-submission formatting constraints."""

from __future__ import annotations

import csv
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUT_CSV = REPO_ROOT / "results/processed/aspdac_submission_audit.csv"

FIELDNAMES = ["check", "status", "file", "detail", "source"]

ASPDAC_PAPER_GUIDE = "https://www.aspdac.com/aspdac2027/author/technical_paper/"
ASPDAC_CFP = "https://www.aspdac.com/aspdac2027/cfp/"


def main() -> int:
    rows: list[dict[str, str]] = []
    main_tex = PAPER_DIR / "main.tex"
    text = main_tex.read_text(encoding="utf-8") if main_tex.exists() else ""

    rows.append(_source_check(
        "acm_primary_template",
        "\\documentclass" in text and "acmart" in _documentclass_line(text) and "sigconf" in _documentclass_line(text),
        "paper/main.tex",
        "initial manuscript must use the ACM Primary Article Template, sample-sigconf/acmart format",
        ASPDAC_PAPER_GUIDE,
    ))
    rows.append(_source_check(
        "not_ieee_format",
        "IEEEtran" not in text and "IEEEauthorblock" not in text,
        "paper/main.tex",
        "ASP-DAC 2027 requires ACM format, not IEEEtran",
        ASPDAC_PAPER_GUIDE,
    ))
    rows.append(_source_check(
        "anonymous_review_mode",
        "anonymous" in _documentclass_line(text),
        "paper/main.tex",
        "initial manuscripts must be double-blind and omit author-identifying information",
        ASPDAC_PAPER_GUIDE,
    ))
    rows.append(_source_check(
        "abstract_before_maketitle",
        _index(text, "\\input{sections/abstract}") < _index(text, "\\maketitle"),
        "paper/main.tex",
        "acmart expects the abstract before maketitle",
        "ACM Primary Article Template",
    ))
    rows.append(_source_check(
        "acm_bibliography_style",
        "\\bibliographystyle{ACM-Reference-Format}" in text,
        "paper/main.tex",
        "bibliography should use ACM reference formatting for ACM proceedings",
        "ACM Primary Article Template",
    ))
    rows.append(_source_check(
        "references_flushed_after_content",
        "\\clearpage" in text and "\\label{aspdac:references-start}" in text,
        "paper/main.tex",
        "all figures and tables must count in the six-page body before references",
        ASPDAC_CFP,
    ))
    rows.extend(_private_marker_rows())
    rows.extend(_build_artifact_rows(text))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    failures = [row for row in rows if row["status"] == "FAIL"]
    print(f"WROTE {OUT_CSV}; FAIL rows={len(failures)}")
    return 1 if failures else 0


def _build_artifact_rows(main_tex: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pdf = PAPER_DIR / "main.pdf"
    log = PAPER_DIR / "main.log"
    aux = PAPER_DIR / "main.aux"

    newest_source = _newest_source_mtime()
    pdf_fresh = pdf.exists() and pdf.stat().st_mtime >= newest_source
    rows.append(_row(
        "fresh_pdf",
        "PASS" if pdf_fresh else "FAIL",
        "paper/main.pdf",
        "PDF must be rebuilt after the latest LaTeX source/table/reference change",
        ASPDAC_PAPER_GUIDE,
    ))
    if not pdf_fresh:
        return rows

    total_pages = _pages_from_log(log)
    if total_pages is None:
        total_pages = _pages_from_pdf_bytes(pdf)
    rows.append(_row(
        "pdf_total_pages",
        "PASS" if total_pages is not None and total_pages <= 7 else "FAIL",
        "paper/main.pdf",
        f"total_pages={total_pages}; ASP-DAC permits six body pages plus one reference page",
        ASPDAC_CFP,
    ))

    reference_page = _reference_start_page(aux)
    rows.append(_row(
        "reference_start_page",
        "PASS" if reference_page is not None else "FAIL",
        "paper/main.aux",
        f"reference_start_page={reference_page}; expected label aspdac:references-start",
        ASPDAC_CFP,
    ))
    if reference_page is not None:
        content_pages = reference_page - 1
        rows.append(_row(
            "body_page_limit",
            "PASS" if content_pages <= 6 else "FAIL",
            "paper/main.pdf",
            f"body_pages_before_references={content_pages}; limit is 6 including figures and tables",
            ASPDAC_CFP,
        ))

    return rows


def _private_marker_rows() -> list[dict[str, str]]:
    forbidden = (
        "C:" + "\\Users\\",
        "One" + "Drive",
        "ty" + "boy",
        "github.com/" + "ty" + "boy",
    )
    rows: list[dict[str, str]] = []
    for path in [PAPER_DIR / "main.tex", *sorted((PAPER_DIR / "sections").glob("*.tex")), PAPER_DIR / "references.bib"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = [marker for marker in forbidden if marker.lower() in text.lower()]
        rows.append(_row(
            "private_marker_scan",
            "FAIL" if matches else "PASS",
            path.relative_to(REPO_ROOT).as_posix(),
            "private/local identity marker(s): " + ", ".join(matches) if matches else "no private/local identity markers",
            ASPDAC_PAPER_GUIDE,
        ))
    return rows


def _documentclass_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("\\documentclass"):
            return line
    return ""


def _index(text: str, needle: str) -> int:
    found = text.find(needle)
    return found if found >= 0 else 10**9


def _newest_source_mtime() -> float:
    patterns = [
        "main.tex",
        "sections/*.tex",
        "tables/*.tex",
        "references.bib",
    ]
    mtimes: list[float] = []
    for pattern in patterns:
        mtimes.extend(path.stat().st_mtime for path in PAPER_DIR.glob(pattern) if path.exists())
    return max(mtimes) if mtimes else 0.0


def _pages_from_log(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Output written on .+? \((\d+) pages?", text)
    return int(match.group(1)) if match else None


def _pages_from_pdf_bytes(path: Path) -> int | None:
    if not path.exists():
        return None
    data = path.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page\b", data))
    return pages or None


def _reference_start_page(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\newlabel\{aspdac:references-start\}\{\{.*?\}\{(\d+)\}", text)
    return int(match.group(1)) if match else None


def _source_check(check: str, passed: bool, file: str, detail: str, source: str) -> dict[str, str]:
    return _row(check, "PASS" if passed else "FAIL", file, detail, source)


def _row(check: str, status: str, file: str, detail: str, source: str) -> dict[str, str]:
    return {"check": check, "status": status, "file": file, "detail": detail, "source": source}


if __name__ == "__main__":
    raise SystemExit(main())
