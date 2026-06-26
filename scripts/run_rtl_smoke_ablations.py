#!/usr/bin/env python3
"""Run event-class ablations over exported RTL-smoke capsules."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tb" / "replay_testbench"))
from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


EXPORT_CSV = REPO_ROOT / "results/processed/rtl_capsule_exports.csv"
OUT_CSV = REPO_ROOT / "results/processed/rtl_smoke_ablations.csv"
OUT_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/rtl_smoke_event_sufficiency.csv"

ABLATIONS = {
    "remove_pc_context": lambda event: event.get("kind") == "pc",
    "remove_branch_events": lambda event: event.get("kind") == "branch",
    "remove_store_events": lambda event: event.get("kind") == "store",
    "remove_mmio_read_values": lambda event: event.get("kind") == "mmio" and event.get("direction") == "read",
    "remove_mmio_write_observations": lambda event: event.get("kind") == "mmio" and event.get("direction") == "write",
    "remove_interrupt_timing": lambda event: event.get("kind") == "interrupt",
    "remove_external_input_values": lambda event: event.get("kind") == "input",
    "remove_checkpoint_hashes": lambda event: event.get("kind") == "checkpoint",
}


def main() -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not EXPORT_CSV.exists():
        _write_rows([_todo_row("suite", "NA", "missing rtl capsule export CSV")], [])
        _print_written()
        return 0

    rows: list[dict[str, str]] = []
    sufficiency_rows: list[dict[str, str]] = []
    failed = False
    with EXPORT_CSV.open(newline="", encoding="utf-8") as handle:
        for export in csv.DictReader(handle):
            if export.get("status") != "PASS":
                rows.append(_todo_row(export.get("benchmark", "unknown"), export.get("variant", "unknown"), "source export row is not PASS"))
                continue
            try:
                capsule_path = REPO_ROOT / export["capsule_json"]
                payload = json.loads(capsule_path.read_text(encoding="utf-8"))
                parsed = parse_capsule(json.dumps(payload), source=f"{export['benchmark']}:{export['variant']}:rtl")
                required_classes: list[str] = []
                for ablation, should_remove in ABLATIONS.items():
                    ablated_payload, removed_count = _remove_events(payload, should_remove)
                    observed = parse_capsule(
                        json.dumps(ablated_payload),
                        source=f"{export['benchmark']}:{export['variant']}:{ablation}",
                    )
                    comparison = compare_capsules(parsed, observed, mode="commit-index")
                    if removed_count and not comparison.success and export.get("variant") == "failing":
                        required_classes.append(ablation.replace("remove_", ""))
                    rows.append(
                        {
                            "ablation": ablation,
                            "benchmark": export["benchmark"],
                            "variant": export["variant"],
                            "status": "MEASURED",
                            "replay_success": str(comparison.success),
                            "evidence_level": "rtl-smoke",
                            "removed_event_count": str(removed_count),
                            "capsule_json": export["capsule_json"],
                            "reason": _reason(comparison.success, removed_count, comparison.errors),
                        }
                    )
                if export.get("variant") == "failing":
                    sufficiency_rows.append(
                        {
                            "benchmark": export["benchmark"],
                            "variant": export["variant"],
                            "evidence_level": "rtl-smoke",
                            "required_event_classes": ";".join(required_classes) if required_classes else "none_observed",
                            "notes": "derived from exported RTL-smoke capsules by removing event classes and rerunning the replay comparator; not benchmark-wide RTL replay",
                        }
                    )
            except Exception as exc:  # noqa: BLE001 - preserve per-capsule failures
                failed = True
                rows.append(_failure_row(export, str(exc)))

    _write_rows(rows, sufficiency_rows)
    _print_written()
    return 1 if failed else 0


def _print_written() -> None:
    print(f"WROTE {OUT_CSV} and {OUT_SUFFICIENCY_CSV}")


def _remove_events(payload: dict[str, object], should_remove) -> tuple[dict[str, object], int]:
    events = payload.get("events", [])
    if not isinstance(events, list):
        raise ValueError("capsule payload has no events list")
    kept_events = []
    removed_count = 0
    for event in events:
        if isinstance(event, dict) and should_remove(event):
            removed_count += 1
        else:
            kept_events.append(event)
    ablated = dict(payload)
    ablated["events"] = kept_events
    return ablated, removed_count


def _reason(success: bool, removed_count: int, errors: tuple[str, ...]) -> str:
    if removed_count == 0:
        return "event class absent from this RTL-smoke capsule"
    if success:
        return "removed event class did not affect comparator match for this RTL-smoke capsule"
    return "; ".join(errors)


def _write_rows(rows: list[dict[str, str]], sufficiency_rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "ablation",
                "benchmark",
                "variant",
                "status",
                "replay_success",
                "evidence_level",
                "removed_event_count",
                "capsule_json",
                "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    with OUT_SUFFICIENCY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["benchmark", "variant", "evidence_level", "required_event_classes", "notes"],
        )
        writer.writeheader()
        writer.writerows(sufficiency_rows)


def _todo_row(benchmark: str, variant: str, reason: str) -> dict[str, str]:
    return {
        "ablation": "rtl_smoke_ablations",
        "benchmark": benchmark,
        "variant": variant,
        "status": "TODO",
        "replay_success": "TODO",
        "evidence_level": "rtl-smoke",
        "removed_event_count": "NA",
        "capsule_json": "NA",
        "reason": reason,
    }


def _failure_row(export: dict[str, str], reason: str) -> dict[str, str]:
    row = _todo_row(export.get("benchmark", "unknown"), export.get("variant", "unknown"), reason)
    row["status"] = "FAIL"
    row["replay_success"] = "False"
    row["capsule_json"] = export.get("capsule_json", "NA")
    return row


if __name__ == "__main__":
    raise SystemExit(main())
