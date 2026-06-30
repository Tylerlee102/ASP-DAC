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
    "complementary",
    "do not",
    "does not",
    "disallowed",
    "excluded",
    "excludes",
    "current weakness",
    "fix plan",
    "forbidden",
    "future",
    "generated partial",
    "highest-risk",
    "instead",
    "limit",
    "limitation",
    "limitations",
    "metric",
    "missing",
    "missing gate",
    "must not",
    "no ",
    "no evidence",
    "not a",
    "not claim",
    "not generated",
    "not implemented",
    "not ",
    "not supported",
    "out of scope",
    "outside the scope",
    "partial",
    "pending",
    "preserved",
    "rather than",
    "reported as",
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
    "would require",
)


@dataclass(frozen=True)
class ClaimPattern:
    claim_type: str
    regex: re.Pattern[str]
    guidance: str


PATTERNS = (
    ClaimPattern(
        "first_claim",
        re.compile(r"\b(first ever|first deterministic|first hardware|first fpga|first embedded|first risc-v|first trace)\b", re.IGNORECASE),
        "Avoid first-ever claims unless a systematic survey supports them.",
    ),
    ClaimPattern(
        "guarantee_claim",
        re.compile(r"\b(guarantee(?:s|d)?|complete determinism)\b", re.IGNORECASE),
        "Guarantees must be scoped to stated assumptions and generated evidence.",
    ),
    ClaimPattern(
        "minimality_claim",
        re.compile(r"\bminimal(?:ity)?\b", re.IGNORECASE),
        "Minimality wording is only allowed in explicit limitation or do-not-claim contexts.",
    ),
    ClaimPattern(
        "overhead_hype",
        re.compile(r"\b(negligible|low overhead)\b", re.IGNORECASE),
        "Do not call measured overhead low or negligible.",
    ),
    ClaimPattern(
        "unsupported_scope",
        re.compile(r"\b(full-system|multicore|DMA|cache-coherent|universal)\b", re.IGNORECASE),
        "Scope expansion terms are only allowed in explicit limitation or do-not-claim contexts.",
    ),
    ClaimPattern(
        "asic_power_claim",
        re.compile(r"\b(ASIC|power)\b", re.IGNORECASE),
        "ASIC and power wording is only allowed when stating that no ASIC/power claim is made.",
    ),
    ClaimPattern(
        "production_claim",
        re.compile(r"\bproduction-ready\b", re.IGNORECASE),
        "Do not call the prototype production-ready.",
    ),
    ClaimPattern(
        "trace_replacement_claim",
        re.compile(r"\b(replacement for trace|replacement for risc-v trace|replaces e-trace|replaces n-trace|replaces trace)\b", re.IGNORECASE),
        "Do not claim replacement for trace/debug standards.",
    ),
    ClaimPattern(
        "synthesizable_replay_consume_claim",
        re.compile(r"\bsynthesizable replay-consume\b", re.IGNORECASE),
        "Synthesizable replay-consume wording is only allowed in limitation contexts.",
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
                    status = "CAVEATED" if _is_caveated(context) or _is_config_name_use(pattern.claim_type, match.group(0), context) else "REVIEW"
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
            paths.extend(path for path in root.rglob("*.tex") if not _skip(path))
    return sorted(set(paths))


def _skip(path: Path) -> bool:
    return bool(set(path.relative_to(REPO_ROOT).parts) & SKIP_PARTS)


def _is_caveated(line: str) -> bool:
    text = line.lower()
    return any(marker in text for marker in SAFE_CONTEXT)


def _is_config_name_use(claim_type: str, matched_text: str, context: str) -> bool:
    if claim_type != "minimality_claim" or matched_text.lower() != "minimal":
        return False
    text = context.lower()
    config_markers = (
        "`minimal`",
        "_minimal_",
        "recorder config",
        "minimal/core/hashed",
        "minimal, core, and hashed",
        "minimal recorder profile",
        "v2 minimal ecp5",
        "v2 minimal full-core",
    )
    return any(marker in text for marker in config_markers)


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
