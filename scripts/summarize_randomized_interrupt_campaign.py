#!/usr/bin/env python3
"""Summarize seeded RTL-smoke interrupt campaign evidence."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_CSV = REPO_ROOT / "results/processed/randomized_interrupt_campaign.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/randomized_interrupt_summary.csv"
COVERAGE_CSV = REPO_ROOT / "results/processed/randomized_interrupt_coverage.csv"

SUMMARY_FIELDS = [
    "scope",
    "family",
    "total_cases",
    "pass_cases",
    "fail_cases",
    "todo_cases",
    "seed_count",
    "unique_digests",
    "min_capsule_packets",
    "max_capsule_packets",
    "min_irq_pulse_cycles",
    "max_irq_pulse_cycles",
    "min_irq_start_cycle",
    "max_irq_end_cycle",
    "digest_matches",
    "property_matches",
    "count_matches",
    "status",
    "evidence_level",
    "notes",
]

COVERAGE_FIELDS = ["coverage_item", "status", "evidence_level", "covered_cases", "source", "notes"]


def main() -> int:
    rows = _read_rows(CAMPAIGN_CSV)
    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(SUMMARY_CSV, SUMMARY_FIELDS, _summary_rows(rows))
    _write_rows(COVERAGE_CSV, COVERAGE_FIELDS, _coverage_rows(rows))
    print(f"WROTE {SUMMARY_CSV} and {COVERAGE_CSV}")
    return 1 if any(row.get("status") == "FAIL" for row in rows) else 0


def _summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return [
            _summary_row(
                "overall",
                "all",
                [],
                "TODO",
                "No campaign rows found; run scripts/run_randomized_interrupt_campaign.py first.",
            )
        ]

    families = sorted({row.get("family", "unknown") or "unknown" for row in rows})
    summary = [
        _summary_row(
            "overall",
            "all",
            rows,
            _status_for(rows),
            "All seeded RTL-smoke interrupt cases from the current campaign.",
        )
    ]
    for family in families:
        family_rows = [row for row in rows if row.get("family") == family]
        summary.append(
            _summary_row(
                "family",
                family,
                family_rows,
                _status_for(family_rows),
                _family_notes(family),
            )
        )
    return summary


def _summary_row(
    scope: str,
    family: str,
    rows: list[dict[str, str]],
    status: str,
    notes: str,
) -> dict[str, str]:
    passing = [row for row in rows if row.get("status") == "PASS"]
    return {
        "scope": scope,
        "family": family,
        "total_cases": str(len(rows)),
        "pass_cases": str(sum(1 for row in rows if row.get("status") == "PASS")),
        "fail_cases": str(sum(1 for row in rows if row.get("status") == "FAIL")),
        "todo_cases": str(sum(1 for row in rows if row.get("status") == "TODO")),
        "seed_count": str(len({row.get("seed", "") for row in rows if row.get("seed")})),
        "unique_digests": str(len({row.get("digest_run1", "") for row in passing if _known(row.get("digest_run1"))})),
        "min_capsule_packets": _range_value(passing, "capsule_count_run1", min),
        "max_capsule_packets": _range_value(passing, "capsule_count_run1", max),
        "min_irq_pulse_cycles": _range_value(rows, "irq_pulse_cycles", min),
        "max_irq_pulse_cycles": _range_value(rows, "irq_pulse_cycles", max),
        "min_irq_start_cycle": _range_value(rows, "irq_start_cycle", min),
        "max_irq_end_cycle": _range_value(rows, "irq_end_cycle", max),
        "digest_matches": _match_count(rows, "digest_run1", "digest_run2"),
        "property_matches": _expected_property_count(rows),
        "count_matches": _match_count(rows, "capsule_count_run1", "capsule_count_run2"),
        "status": status,
        "evidence_level": "rtl-smoke",
        "notes": notes,
    }


def _coverage_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    passing = [row for row in rows if row.get("status") == "PASS"]
    after_command = [row for row in passing if row.get("family") == "irq_after_command"]
    fixed_window = [row for row in passing if row.get("family") == "fixed_irq_window"]
    all_pass = bool(rows) and len(passing) == len(rows)

    return [
        _coverage_row(
            "seeded_fresh_process_rerun",
            "PASS" if all_pass else _derived_status(rows),
            len(passing),
            "Each case runs twice through fresh vvp invocations and must reproduce property ID, count, signature, and digest.",
        ),
        _coverage_row(
            "digest_reproducibility",
            "PASS" if rows and _all_match(rows, "digest_run1", "digest_run2") else _derived_status(rows),
            _matching_rows(rows, "digest_run1", "digest_run2"),
            "Capsule-packet SHA-256 digests match across both simulator invocations.",
        ),
        _coverage_row(
            "property_id_reproducibility",
            "PASS" if rows and _expected_property_rows(rows) == len(rows) else _derived_status(rows),
            _expected_property_rows(rows),
            "Both runs report the expected interrupt-race property ID.",
        ),
        _coverage_row(
            "frozen_capsule_count_reproducibility",
            "PASS" if rows and _all_match(rows, "capsule_count_run1", "capsule_count_run2") else _derived_status(rows),
            _matching_rows(rows, "capsule_count_run1", "capsule_count_run2"),
            "Frozen packet counts match across both simulator invocations.",
        ),
        _coverage_row(
            "irq_after_command_pulse_width_jitter",
            "PASS" if after_command and len(_int_values(after_command, "irq_pulse_cycles")) > 1 else _derived_status(rows),
            len(after_command),
            "Seeded after-command cases vary interrupt pulse width after the command MMIO write.",
        ),
        _coverage_row(
            "fixed_irq_window_sweep",
            "PASS" if fixed_window and len(_int_values(fixed_window, "irq_start_cycle")) > 1 else _derived_status(rows),
            len(fixed_window),
            "Fixed-window cases sweep explicit interrupt assertion/deassertion windows.",
        ),
        _coverage_row(
            "capsule_size_variation_observed",
            "PASS" if len(_int_values(passing, "capsule_count_run1")) > 1 else _derived_status(rows),
            len(_int_values(passing, "capsule_count_run1")),
            "Passing cases produce more than one frozen capsule packet count, exercising different interrupt-visible prefixes.",
        ),
        _coverage_row(
            "record_then_replay_with_live_noise",
            "TODO",
            0,
            "Requires the full randomized record/replay RTL harness with changed live interrupts and MMIO values.",
        ),
        _coverage_row(
            "mmio_latency_randomization",
            "TODO",
            0,
            "Requires an RTL harness that varies MMIO response latency independently from interrupt timing.",
        ),
        _coverage_row(
            "buffer_pressure_overflow_randomization",
            "TODO",
            0,
            "Requires randomized buffer-capacity and overflow runs beyond the current fixed-depth smoke campaign.",
        ),
        _coverage_row(
            "interrupt_before_during_after_mmio_wait",
            "TODO",
            0,
            "Requires a checker that classifies interrupt timing relative to an exposed MMIO wait-state window.",
        ),
        _coverage_row(
            "corrupted_seed_replay_rejection",
            "TODO",
            0,
            "Randomized seed-specific corruption checks remain pending; directed RTL-smoke corruption checks are tracked separately.",
        ),
    ]


def _coverage_row(item: str, status: str, covered_cases: int, notes: str) -> dict[str, str]:
    return {
        "coverage_item": item,
        "status": status,
        "evidence_level": "rtl-smoke",
        "covered_cases": str(covered_cases),
        "source": "results/processed/randomized_interrupt_campaign.csv",
        "notes": notes,
    }


def _status_for(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "TODO"
    if any(row.get("status") == "FAIL" for row in rows):
        return "FAIL"
    if any(row.get("status") == "TODO" for row in rows):
        return "TODO"
    return "PASS"


def _derived_status(rows: list[dict[str, str]]) -> str:
    return "TODO" if not rows or any(row.get("status") == "TODO" for row in rows) else "FAIL"


def _family_notes(family: str) -> str:
    if family == "irq_after_command":
        return "Seeded pulse-width jitter after the command MMIO write."
    if family == "fixed_irq_window":
        return "Explicit interrupt assertion-window sweep over the failing interrupt-race workload."
    return "Seeded interrupt campaign family."


def _match_count(rows: list[dict[str, str]], left: str, right: str) -> str:
    return f"{_matching_rows(rows, left, right)}/{len(rows)}"


def _matching_rows(rows: list[dict[str, str]], left: str, right: str) -> int:
    return sum(1 for row in rows if _known(row.get(left)) and row.get(left) == row.get(right))


def _all_match(rows: list[dict[str, str]], left: str, right: str) -> bool:
    return bool(rows) and _matching_rows(rows, left, right) == len(rows)


def _expected_property_count(rows: list[dict[str, str]]) -> str:
    return f"{_expected_property_rows(rows)}/{len(rows)}"


def _expected_property_rows(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if _known(row.get("expected_property"))
        and row.get("property_run1") == row.get("expected_property")
        and row.get("property_run2") == row.get("expected_property")
    )


def _range_value(rows: list[dict[str, str]], field: str, selector) -> str:
    values = sorted(_int_values(rows, field))
    return str(selector(values)) if values else "NA"


def _int_values(rows: list[dict[str, str]], field: str) -> set[int]:
    values: set[int] = set()
    for row in rows:
        value = row.get(field, "")
        if value.isdigit():
            values.add(int(value))
    return values


def _known(value: str | None) -> bool:
    return value not in {None, "", "NA", "TODO"}


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
