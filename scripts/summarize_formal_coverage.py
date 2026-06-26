#!/usr/bin/env python3
"""Summarize bounded formal proof coverage for reviewer-facing evidence."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORMAL_CSV = REPO_ROOT / "results/processed/formal_checks.csv"
OUT_CSV = REPO_ROOT / "results/processed/formal_coverage.csv"
OUT_MD = REPO_ROOT / "docs/formal_coverage_matrix.md"


@dataclass(frozen=True)
class CoverageRow:
    module_family: str
    rtl_sources: str
    bmc_check: str
    cover_check: str
    depth: int
    obligations: str
    explicit_limit: str


COVERAGE_ROWS = (
    CoverageRow(
        module_family="event_tap",
        rtl_sources="rtl/event_tap.sv",
        bmc_check="event_tap_bmc",
        cover_check="event_tap_cover",
        depth=2,
        obligations="priority ordering, event field routing, multievent-pending flag",
        explicit_limit="local event-source harness; not a full CPU proof",
    ),
    CoverageRow(
        module_family="event_classifier_slicer",
        rtl_sources="rtl/event_classifier.sv; rtl/event_slicer.sv",
        bmc_check="event_classifier_slicer_bmc",
        cover_check="event_classifier_slicer_cover",
        depth=8,
        obligations="capture-policy classification, required-event retention, LAST_K context-window behavior",
        explicit_limit="bounded policy proof; workload-scale event coverage comes from simulation rows",
    ),
    CoverageRow(
        module_family="property_checker",
        rtl_sources="rtl/property_checker.sv",
        bmc_check="property_checker_bmc",
        cover_check="property_checker_cover",
        depth=8,
        obligations="six failure-family IDs/signatures, reset/clear behavior, state exposure",
        explicit_limit="synthetic checker stimuli with reduced deadline constants",
    ),
    CoverageRow(
        module_family="hash_signature",
        rtl_sources="rtl/hash_signature.sv",
        bmc_check="hash_signature_bmc",
        cover_check="hash_signature_cover",
        depth=4,
        obligations="reset seed, clear seed, no-event stability, exact rotate/XOR update",
        explicit_limit="integrity accumulator behavior only; no cryptographic-strength claim",
    ),
    CoverageRow(
        module_family="mmio_interrupt_loggers",
        rtl_sources="rtl/mmio_logger.sv; rtl/interrupt_logger.sv",
        bmc_check="mmio_interrupt_loggers_bmc",
        cover_check="mmio_interrupt_loggers_cover",
        depth=6,
        obligations="MMIO read/write packet fields, interrupt enter/exit fields, depth tracking, unpaired-exit sticky flag",
        explicit_limit="local logger interfaces; not a complete bus-protocol proof",
    ),
    CoverageRow(
        module_family="registers",
        rtl_sources="rtl/registers.sv",
        bmc_check="registers_bmc",
        cover_check="registers_cover",
        depth=6,
        obligations="address decode, readback muxing, reset defaults, global clear, control writes, one-cycle clear pulse",
        explicit_limit="register-block contract only; no external bus timing proof",
    ),
    CoverageRow(
        module_family="replay_control",
        rtl_sources="rtl/replay_control.sv",
        bmc_check="replay_control_bmc",
        cover_check="replay_control_cover",
        depth=8,
        obligations="event consume/inject rules, time mismatch handling, non-injectable event handling, sticky underflow",
        explicit_limit="local event packets; no firmware-running SoC replay proof",
    ),
    CoverageRow(
        module_family="replay_mismatch_guards",
        rtl_sources="rtl/replay_control.sv",
        bmc_check="replay_mismatch_bmc",
        cover_check="replay_mismatch_cover",
        depth=14,
        obligations="wrong-cycle rejection, wrong-commit rejection, wrong-kind rejection, early-EOF underflow, clear recovery, exact payload injection",
        explicit_limit="deterministic mismatch microsequence; no full replay-stream comparator proof",
    ),
    CoverageRow(
        module_family="capsule_buffer",
        rtl_sources="rtl/capsule_buffer.sv",
        bmc_check="capsule_buffer_bmc",
        cover_check="capsule_buffer_cover",
        depth=12,
        obligations="count bounds, freeze immutability, frozen-count stability, sticky overflow, first-overflow behavior",
        explicit_limit="small four-entry proof configuration",
    ),
    CoverageRow(
        module_family="replay_capsule_top",
        rtl_sources="rtl/replay_capsule_top.sv and local submodules",
        bmc_check="replay_capsule_top_bmc",
        cover_check="replay_capsule_top_cover",
        depth=16,
        obligations="top-level recorder count bounds, failure-to-freeze behavior, frozen-count stability, overflow reachability",
        explicit_limit="bounded recorder harness; not an end-to-end processor/replay theorem",
    ),
)


def main() -> int:
    statuses = _read_formal_statuses()
    rows = [_coverage_dict(row, statuses) for row in COVERAGE_ROWS]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(rows)
    _write_markdown(rows)
    print(f"WROTE {OUT_CSV} and {OUT_MD}")
    return 0


def _read_formal_statuses() -> dict[str, dict[str, str]]:
    if not FORMAL_CSV.exists():
        return {}
    with FORMAL_CSV.open(newline="", encoding="utf-8") as handle:
        return {row["check"]: row for row in csv.DictReader(handle)}


def _coverage_dict(row: CoverageRow, statuses: dict[str, dict[str, str]]) -> dict[str, str]:
    bmc = statuses.get(row.bmc_check, {})
    cover = statuses.get(row.cover_check, {})
    bmc_status = bmc.get("status", "TODO")
    cover_status = cover.get("status", "TODO")
    if bmc_status == "PASS" and cover_status == "PASS":
        status = "PASS"
    elif bmc_status == "FAIL" or cover_status == "FAIL":
        status = "FAIL"
    else:
        status = "TODO"
    evidence = "; ".join(
        item
        for item in [
            bmc.get("raw_log", ""),
            cover.get("raw_log", ""),
        ]
        if item
    )
    return {
        "module_family": row.module_family,
        "rtl_sources": row.rtl_sources,
        "bmc_check": row.bmc_check,
        "cover_check": row.cover_check,
        "depth": str(row.depth),
        "status": status,
        "evidence": evidence,
        "obligations": row.obligations,
        "explicit_limit": row.explicit_limit,
    }


def _write_csv(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "module_family",
                "rtl_sources",
                "bmc_check",
                "cover_check",
                "depth",
                "status",
                "evidence",
                "obligations",
                "explicit_limit",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(rows: list[dict[str, str]]) -> None:
    pass_count = sum(1 for row in rows if row["status"] == "PASS")
    lines = [
        "# Formal Coverage Matrix",
        "",
        "Generated by `scripts/summarize_formal_coverage.py` from `results/processed/formal_checks.csv`.",
        "",
        f"Current status: {pass_count} of {len(rows)} module-family coverage rows PASS.",
        "",
        "| Module family | RTL sources | BMC / cover | Depth | Status | Obligations checked | Explicit limit |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {module_family} | {rtl_sources} | {bmc_check} / {cover_check} | {depth} | {status} | {obligations} | {explicit_limit} |".format(
                **{key: _escape_pipe(value) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "This table is evidence packaging, not a stronger claim than the underlying checks.",
            "The bounded proofs cover local RTL contracts and reachability cases; full firmware-running RTL replay, mapped FPGA resource/timing, and an end-to-end mechanized replay-sufficiency theorem remain outside the current local evidence.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _escape_pipe(value: str) -> str:
    return value.replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
