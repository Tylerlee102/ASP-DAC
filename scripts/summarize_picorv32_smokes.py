#!/usr/bin/env python3
"""Summarize and sanity-check PicoRV32 wrapper smoke run logs."""

from __future__ import annotations

import csv
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HDL_CSV = REPO_ROOT / "results/processed/hdl_checks.csv"
OUT_CSV = REPO_ROOT / "results/processed/picorv32_smoke_summary.csv"
COVERAGE_CSV = REPO_ROOT / "results/processed/picorv32_smoke_coverage.csv"

BEGIN_RE = re.compile(
    r"RC_CAPSULE_BEGIN\s+count=(?P<count>\d+)\s+property=(?P<property>\d+)\s+"
    r"signature=(?P<signature>[0-9a-fA-F]+)\s+frozen=(?P<frozen>[01])\s+overflow=(?P<overflow>[01])"
)
EVENT_RE = re.compile(r"RC_CAPSULE_EVENT\s+index=(?P<index>\d+)\s+packet=(?P<packet>[0-9a-fA-F]+)")

SUMMARY_FIELDS = [
    "check",
    "benchmark",
    "variant",
    "expectation",
    "status",
    "evidence_level",
    "property_observed",
    "capsule_event_count",
    "capsule_frozen",
    "capsule_overflow",
    "signature",
    "packet_lines",
    "raw_log",
    "notes",
]

COVERAGE_FIELDS = ["coverage_item", "status", "evidence_level", "covered_cases", "source", "notes"]


EDGE_CASES = {
    "sensor_threshold_below_threshold": ("sensor_threshold_bug", "no_failure_edge", "no_property_failure"),
    "uart_command_no_command": ("uart_command_bug", "no_failure_edge", "no_property_failure"),
    "watchdog_timeout_below_threshold": ("watchdog_timeout_bug", "no_failure_edge", "no_property_failure"),
}


def main() -> int:
    hdl_rows = _read_rows(HDL_CSV)
    smoke_rows = [_summary_row(row) for row in hdl_rows if row.get("check", "").startswith("tb_picorv32")]
    coverage_rows = _coverage_rows(smoke_rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(OUT_CSV, SUMMARY_FIELDS, smoke_rows)
    _write_rows(COVERAGE_CSV, COVERAGE_FIELDS, coverage_rows)
    print(f"WROTE {OUT_CSV} and {COVERAGE_CSV}")
    return 1 if any(row.get("status") == "FAIL" for row in smoke_rows + coverage_rows) else 0


def _summary_row(row: dict[str, str]) -> dict[str, str]:
    check = row.get("check", "")
    benchmark, variant, expectation = _classify_check(check)
    raw_log = row.get("raw_log", "")
    parsed = _parse_log(raw_log)
    status, notes = _validate(row, parsed, expectation)
    return {
        "check": check,
        "benchmark": benchmark,
        "variant": variant,
        "expectation": expectation,
        "status": status,
        "evidence_level": "rtl-smoke",
        "property_observed": parsed.get("property", "NA"),
        "capsule_event_count": parsed.get("count", "NA"),
        "capsule_frozen": parsed.get("frozen", "NA"),
        "capsule_overflow": parsed.get("overflow", "NA"),
        "signature": parsed.get("signature", "NA"),
        "packet_lines": parsed.get("packet_lines", "NA"),
        "raw_log": raw_log,
        "notes": notes,
    }


def _coverage_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    pass_rows = [row for row in rows if row.get("status") == "PASS"]
    failing = [row for row in pass_rows if row.get("expectation") == "property_failure"]
    fixed = [row for row in pass_rows if row.get("variant") == "fixed"]
    edge = [row for row in pass_rows if row.get("variant") == "no_failure_edge"]
    no_failure = [row for row in pass_rows if row.get("expectation") == "no_property_failure"]
    benchmarks = {row.get("benchmark") for row in pass_rows if row.get("benchmark") not in {"", "unknown"}}
    return [
        _coverage_row(
            "picorv32_wrapper_smokes_total",
            "PASS" if len(pass_rows) == len(rows) and len(rows) >= 15 else "FAIL",
            len(pass_rows),
            "All PicoRV32 wrapper smoke rows passed log-level capsule sanity checks.",
        ),
        _coverage_row(
            "failing_image_property_capsules",
            "PASS" if len(failing) >= 6 else "FAIL",
            len(failing),
            "Failing firmware images produced nonzero property IDs, frozen capsules, and no overflow.",
        ),
        _coverage_row(
            "fixed_image_no_failure_capsules",
            "PASS" if len(fixed) >= 6 else "FAIL",
            len(fixed),
            "Fixed firmware images completed without property failures while still recording capsule events.",
        ),
        _coverage_row(
            "no_failure_edge_capsules",
            "PASS" if len(edge) >= 3 else "FAIL",
            len(edge),
            "Selected no-failure edge cases completed with property ID zero and no overflow.",
        ),
        _coverage_row(
            "six_benchmark_wrapper_coverage",
            "PASS" if len(benchmarks) >= 6 else "FAIL",
            len(benchmarks),
            "Wrapper smokes cover all six local benchmark families.",
        ),
        _coverage_row(
            "no_failure_property_absence",
            "PASS" if no_failure and all(row.get("property_observed") == "0" for row in no_failure) else "FAIL",
            len(no_failure),
            "All fixed and edge no-failure smokes report property ID zero.",
        ),
    ]


def _coverage_row(item: str, status: str, covered_cases: int, notes: str) -> dict[str, str]:
    return {
        "coverage_item": item,
        "status": status,
        "evidence_level": "rtl-smoke",
        "covered_cases": str(covered_cases),
        "source": "results/processed/picorv32_smoke_summary.csv",
        "notes": notes,
    }


def _classify_check(check: str) -> tuple[str, str, str]:
    stem = check.removeprefix("tb_picorv32_").removesuffix("_smoke")
    if stem in EDGE_CASES:
        return EDGE_CASES[stem]
    if stem.endswith("_fixed"):
        benchmark = stem.removesuffix("_fixed") + "_bug"
        return benchmark, "fixed", "no_property_failure"
    return stem + "_bug", "failing", "property_failure"


def _parse_log(raw_log: str) -> dict[str, str]:
    if not raw_log:
        return {}
    path = REPO_ROOT / raw_log
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    begin = BEGIN_RE.search(text)
    packets = [match.group("packet").lower() for match in EVENT_RE.finditer(text)]
    property_packet = _property_packet(packets)
    property_event_id = str((property_packet >> 32) & 0xFF) if property_packet is not None else "0"
    property_signature = f"{property_packet & 0xFFFF_FFFF:08x}" if property_packet is not None else "NA"
    if begin is None:
        return {"packet_lines": str(len(packets))}
    return {
        "count": begin.group("count"),
        "property": property_event_id if property_packet is not None else begin.group("property"),
        "signature": property_signature if property_packet is not None else begin.group("signature").lower(),
        "frozen": begin.group("frozen"),
        "overflow": begin.group("overflow"),
        "packet_lines": str(len(packets)),
    }


def _property_packet(packets: list[str]) -> int | None:
    for packet_hex in packets:
        packet = int(packet_hex, 16)
        if ((packet >> 164) & 0xF) == 0xA:
            return packet
    return None


def _validate(row: dict[str, str], parsed: dict[str, str], expectation: str) -> tuple[str, str]:
    if row.get("status") != "PASS":
        return "TODO" if row.get("status") == "TODO" else "FAIL", "underlying HDL check did not pass"
    if not parsed.get("count"):
        return "FAIL", "raw log did not contain RC_CAPSULE_BEGIN"
    count = int(parsed.get("count", "0"))
    packet_lines = int(parsed.get("packet_lines", "0"))
    if parsed.get("frozen") == "1" and count != packet_lines:
        return "FAIL", "frozen capsule count does not match emitted packet lines"
    if parsed.get("frozen") == "0" and packet_lines < count:
        return "FAIL", "live capsule dump emitted fewer packet lines than begin count"
    if parsed.get("overflow") != "0":
        return "FAIL", "wrapper smoke reported capsule overflow"
    if count <= 0:
        return "FAIL", "wrapper smoke did not record capsule events"
    if expectation == "property_failure":
        if parsed.get("property") == "0":
            return "FAIL", "expected property failure but raw log reported property ID zero"
        if parsed.get("frozen") != "1":
            return "FAIL", "expected failing image to freeze the capsule"
        return "PASS", "failing image produced frozen nonzero-property capsule"
    if parsed.get("property") != "0":
        return "FAIL", "expected no property failure but raw log reported nonzero property ID"
    if parsed.get("frozen") != "0":
        return "FAIL", "expected no-failure smoke to leave capsule unfrozen"
    return "PASS", "no-failure image completed with property ID zero and recorded capsule events"


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
