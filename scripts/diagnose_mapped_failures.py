#!/usr/bin/env python3
"""Classify mapped scaling failures from generated rows and logs."""

from __future__ import annotations

from pathlib import Path

from topconf_eval_common import REPO_ROOT, read_csv, rel, write_csv


OUT_CSV = REPO_ROOT / "results/processed/mapped_failure_diagnosis.csv"
MAPPED_CSV = REPO_ROOT / "results/processed/mapped_scaling.csv"

FIELDS = [
    "design",
    "target",
    "flow",
    "memory_words",
    "buffer_depth",
    "recorder_config",
    "first_failure_stage",
    "primary_root_cause",
    "resource_utilization_at_failure",
    "evidence_log",
    "fix_attempted",
    "status",
    "notes",
]


def main() -> int:
    rows = [_diagnose(row) for row in read_csv(MAPPED_CSV)]
    write_csv(OUT_CSV, FIELDS, rows)
    print("WROTE results/processed/mapped_failure_diagnosis.csv")
    return 0


def _diagnose(row: dict[str, str]) -> dict[str, object]:
    report = REPO_ROOT / row.get("report_path", "NA")
    text = report.read_text(encoding="utf-8", errors="replace") if report.exists() else row.get("notes", "")
    if row.get("status") == "PASS":
        return _base(row, "P&R_PASS", "place-and-route completed", _util(row), row.get("report_path", "NA"), "not needed", "PASS", "mapped row passed")
    stage = _stage(row, text)
    cause = _cause(text + "\n" + row.get("notes", ""))
    return _base(row, stage, cause, _util(row), row.get("report_path", "NA"), "no automatic RTL change attempted", "DIAGNOSED", row.get("notes", ""))


def _stage(row: dict[str, str], text: str) -> str:
    notes = row.get("notes", "").upper()
    upper = text.upper() + "\n" + notes
    if "TIMEOUT" in upper:
        return "UNKNOWN"
    if "SYNTH" in upper or "YOSYS" in upper:
        return "SYNTH_FAIL"
    if "PACK" in upper:
        return "PACK_FAIL"
    if "PLACE" in upper:
        return "PLACE_FAIL"
    if "ROUTE" in upper:
        return "ROUTE_FAIL"
    if "TIMING" in upper:
        return "TIMING_FAIL"
    if "CONSTRAINT" in upper or "LPF" in upper:
        return "MISSING_CONSTRAINT"
    if "UNSUPPORTED" in upper:
        return "UNSUPPORTED_CONSTRUCT"
    if "MEMORY" in upper or "RAM" in upper:
        return "MEMORY_INFERENCE_FAIL"
    if "RESOURCE" in upper or "NO BELS" in upper or "BEL" in upper:
        return "RESOURCE_EXHAUSTION"
    return "UNKNOWN"


def _cause(text: str) -> str:
    upper = text.upper()
    if "TIMEOUT" in upper:
        return "UNKNOWN: mapped tool timeout"
    if "NO BELS" in upper:
        return "RESOURCE_EXHAUSTION: placer reported no BELs remaining"
    if "TIMING" in upper:
        return "TIMING_FAIL: timing target not met"
    if "LPF" in upper or "CONSTRAINT" in upper:
        return "MISSING_CONSTRAINT: constraint issue in mapped flow"
    if "YOSYS" in upper or "SYNTH" in upper:
        return "SYNTH_FAIL: synthesis did not produce a mapped JSON"
    return "UNKNOWN: inspect evidence log"


def _util(row: dict[str, str]) -> str:
    return f"lut={row.get('lut', 'NA')} ff={row.get('ff', 'NA')} bram={row.get('bram', 'NA')} dsp={row.get('dsp', 'NA')} fmax_mhz={row.get('fmax_mhz', 'NA')}"


def _base(
    row: dict[str, str],
    stage: str,
    cause: str,
    util: str,
    evidence: str,
    fix_attempted: str,
    status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "design": row.get("design", "NA"),
        "target": row.get("target", "NA"),
        "flow": row.get("flow", "NA"),
        "memory_words": row.get("memory_words", "NA"),
        "buffer_depth": row.get("buffer_depth", "NA"),
        "recorder_config": row.get("recorder_config", "NA"),
        "first_failure_stage": stage,
        "primary_root_cause": cause,
        "resource_utilization_at_failure": util,
        "evidence_log": evidence,
        "fix_attempted": fix_attempted,
        "status": status,
        "notes": notes,
    }


if __name__ == "__main__":
    raise SystemExit(main())
