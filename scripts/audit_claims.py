#!/usr/bin/env python3
"""Audit paper/docs language for uncaveated high-risk claims."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/claim_audit.csv"

SCAN_ROOTS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "artifact_evaluation.md",
    REPO_ROOT / "docs",
    REPO_ROOT / "paper",
]

SKIP_PARTS = {
    ".git",
    ".tools",
    "results",
}

SAFE_CONTEXT = (
    "avoid",
    "blocked",
    "caveat",
    "do not",
    "does not",
    "current weakness",
    "fix plan",
    "future",
    "generated partial",
    "highest-risk",
    "instead",
    "limit",
    "metric",
    "missing",
    "missing gate",
    "must not",
    "no ",
    "not generated",
    "not ",
    "out of scope",
    "pending",
    "preserved",
    "rather than",
    "require",
    "requirement",
    "required",
    "remain",
    "requires",
    "should not",
    "status svg",
    "target",
    "todo",
    "undefined c behavior",
    "until",
    "will report",
    "without",
)


@dataclass(frozen=True)
class ClaimPattern:
    claim_type: str
    regex: re.Pattern[str]
    guidance: str


PATTERNS = (
    ClaimPattern(
        "first_or_replacement_claim",
        re.compile(r"\b(first ever|first deterministic replay|first hardware replay|first fpga replay|replaces e-trace|replaces n-trace|supersedes)\b", re.IGNORECASE),
        "Avoid first-ever/replacement claims unless the related-work evidence is complete.",
    ),
    ClaimPattern(
        "guarantee_claim",
        re.compile(r"\bguarantee(?:s|d)?\b", re.IGNORECASE),
        "Guarantees must be scoped to the stated assumptions and generated evidence.",
    ),
    ClaimPattern(
        "compression_or_overhead_target",
        re.compile(r"(?<![\d.])(10x|100x|<5%|0-3%)(?![\d.])", re.IGNORECASE),
        "Numerical targets must be presented as goals unless generated measurements support them.",
    ),
    ClaimPattern(
        "mapped_hardware_metric",
        re.compile(r"\b(mapped fpga|lut/ff/bram|fmax|runtime overhead|runtime slowdown)\b", re.IGNORECASE),
        "Mapped hardware and timing metrics must remain TODO/NA until backed by real tool reports.",
    ),
    ClaimPattern(
        "full_rtl_scope",
        re.compile(r"\b(full benchmark(?:-wide)?|benchmark-wide|full rtl|firmware-running rtl)\b", re.IGNORECASE),
        "Full RTL scope must be described as pending unless benchmark-wide RTL evidence exists.",
    ),
    ClaimPattern(
        "proof_strength",
        re.compile(r"\b(mechanized end-to-end|end-to-end proof|complete bus-protocol proof|proves)\b", re.IGNORECASE),
        "Proof language must distinguish bounded/local checks from a mechanized end-to-end theorem.",
    ),
)

FIELDNAMES = ["claim_type", "status", "file", "line", "matched_text", "excerpt", "guidance"]


def main() -> int:
    rows: list[dict[str, str]] = []
    for path in _markdown_files():
        rel_path = _rel(path)
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            lineno = index + 1
            context = " ".join(lines[max(0, index - 6) : min(len(lines), index + 7)])
            for pattern in PATTERNS:
                for match in pattern.regex.finditer(line):
                    status = "CAVEATED" if _is_caveated(context) else "REVIEW"
                    rows.append(
                        {
                            "claim_type": pattern.claim_type,
                            "status": status,
                            "file": rel_path,
                            "line": str(lineno),
                            "matched_text": match.group(0),
                            "excerpt": line.strip(),
                            "guidance": pattern.guidance,
                        }
                    )

    if not rows:
        rows.append(
            {
                "claim_type": "all",
                "status": "PASS",
                "file": "NA",
                "line": "NA",
                "matched_text": "NA",
                "excerpt": "No high-risk claim patterns found.",
                "guidance": "Keep generated evidence and paper claims aligned.",
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    review_count = sum(1 for row in rows if row["status"] == "REVIEW")
    print(f"WROTE {OUT_CSV}; REVIEW rows={review_count}")
    return 1 if review_count else 0


def _markdown_files() -> list[Path]:
    paths: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            paths.append(root)
        elif root.is_dir():
            paths.extend(path for path in root.rglob("*.md") if not _skip(path))
    return sorted(set(paths))


def _skip(path: Path) -> bool:
    return bool(set(path.relative_to(REPO_ROOT).parts) & SKIP_PARTS)


def _is_caveated(line: str) -> bool:
    text = line.lower()
    return any(marker in text for marker in SAFE_CONTEXT)


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
