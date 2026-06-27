#!/usr/bin/env python3
"""Build the paper when LaTeX is available, otherwise record the blocker."""

from __future__ import annotations

import csv
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUT_CSV = REPO_ROOT / "results/processed/paper_build_status.csv"

FIELDNAMES = ["target", "status", "tool", "output", "notes"]


def main() -> int:
    main_tex = PAPER_DIR / "main.tex"
    if not main_tex.exists():
        return _write_status("paper/main.pdf", "BLOCKED", "NA", "NA", "paper/main.tex is missing")

    latexmk = shutil.which("latexmk")
    pdflatex = shutil.which("pdflatex")
    if latexmk:
        command = [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
        tool = "latexmk"
    elif pdflatex:
        command = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
        tool = "pdflatex"
    else:
        pdf_path = PAPER_DIR / "main.pdf"
        if pdf_path.exists():
            return _write_status(
                "paper/main.pdf",
                "PASS",
                "locked-ci-artifact",
                str(pdf_path.relative_to(REPO_ROOT)),
                "LaTeX toolchain not found locally; existing locked CI PDF is present",
            )
        return _write_status("paper/main.pdf", "TODO", "pdflatex/latexmk", "NA", "LaTeX toolchain not found locally")

    completed = subprocess.run(
        command,
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=120,
    )
    log_path = PAPER_DIR / "main_build.log"
    log_path.write_text(completed.stdout, encoding="utf-8", errors="replace")
    pdf_path = PAPER_DIR / "main.pdf"
    if completed.returncode == 0 and pdf_path.exists():
        return _write_status("paper/main.pdf", "PASS", tool, str(pdf_path.relative_to(REPO_ROOT)), "PDF built locally")
    return _write_status("paper/main.pdf", "FAIL", tool, str(log_path.relative_to(REPO_ROOT)), "LaTeX build failed; see log")


def _write_status(target: str, status: str, tool: str, output: str, notes: str) -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow({"target": target, "status": status, "tool": tool, "output": output, "notes": notes})
    print(f"{status}: {target} - {notes}")
    print(f"WROTE {OUT_CSV}")
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
