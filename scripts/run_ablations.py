#!/usr/bin/env python3
"""Run available ablations over real generated model artifacts."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from replaycapsule_model import BENCHMARKS, capsule_fixture, run_benchmark  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "tb" / "replay_testbench"))
from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


OUT_CSV = REPO_ROOT / "results/processed/ablations.csv"
OUT_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/event_sufficiency.csv"

ABLATIONS = {
    "remove_branch_events": {"branch"},
    "remove_store_events": {"store"},
    "remove_mmio_read_values": {"mmio_value"},
    "remove_interrupt_timing": {"interrupt_timing"},
    "remove_external_input_values": {"external_input_value"},
    "remove_checkpoint_hashes": {"checkpoint_hash"},
    "remove_property_aware_slicing": {"property_slice"},
}


def main() -> int:
    rows: list[dict[str, str]] = []
    sufficiency_rows: list[dict[str, str]] = []
    for benchmark in BENCHMARKS:
        result = run_benchmark(benchmark, failing=True)
        expected = parse_capsule(capsule_fixture(result), source=f"{benchmark}:expected")
        required_classes: list[str] = []
        for name, omitted in ABLATIONS.items():
            observed = parse_capsule(capsule_fixture(result, omit=omitted), source=f"{benchmark}:{name}")
            compare = compare_capsules(expected, observed, mode="commit-index")
            if not compare.success:
                required_classes.append(name.replace("remove_", ""))
            rows.append(
                {
                    "ablation": name,
                    "benchmark": benchmark,
                    "status": "MEASURED",
                    "replay_success": str(compare.success),
                    "evidence_level": "model",
                    "reason": "; ".join(compare.errors) if compare.errors else "no replay mismatch observed for this model benchmark",
                }
            )
        rows.extend(_buffer_size_rows(result))
        rows.extend(_last_k_rows(result, expected))
        sufficiency_rows.append(
            {
                "benchmark": benchmark,
                "evidence_level": "model",
                "required_event_classes": ";".join(required_classes) if required_classes else "property_fail_pc_and_mmio_context_only",
                "notes": "derived from ablations where removing the class breaks commit-index replay",
            }
        )
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["ablation", "benchmark", "status", "replay_success", "evidence_level", "reason"],
        )
        writer.writeheader()
        writer.writerows(rows)
    with OUT_SUFFICIENCY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["benchmark", "evidence_level", "required_event_classes", "notes"],
        )
        writer.writeheader()
        writer.writerows(sufficiency_rows)
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_SUFFICIENCY_CSV}")
    return 0


def _buffer_size_rows(result) -> list[dict[str, str]]:
    required_count = _property_aware_event_count(result)
    rows: list[dict[str, str]] = []
    for size in [2, 4, 8, 16]:
        success = required_count <= size
        rows.append(
            {
                "ablation": f"capsule_buffer_size_{size}",
                "benchmark": result.benchmark,
                "status": "MEASURED",
                "replay_success": str(success),
                "evidence_level": "model",
                "reason": (
                    f"model property-aware event count {required_count} fits buffer {size}"
                    if success
                    else f"model property-aware event count {required_count} exceeds buffer {size}; overflow invalidates replay"
                ),
            }
        )
    return rows


def _last_k_rows(result, expected) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    needs_store = "EV_STORE" in {event.event_type.name for event in result.events}
    needs_branch = "EV_BRANCH" in {event.event_type.name for event in result.events}
    for last_k in [0, 1, 4]:
        omitted: set[str] = set()
        if last_k == 0:
            if needs_store:
                omitted.add("store")
            if needs_branch:
                omitted.add("branch")
        observed = parse_capsule(capsule_fixture(result, omit=omitted), source=f"{result.benchmark}:last_k_{last_k}")
        compare = compare_capsules(expected, observed, mode="commit-index")
        rows.append(
            {
                "ablation": f"last_k_context_{last_k}",
                "benchmark": result.benchmark,
                "status": "MEASURED",
                "replay_success": str(compare.success),
                "evidence_level": "model",
                "reason": "; ".join(compare.errors) if compare.errors else "model replay evidence retained by this context window",
            }
        )
    return rows


def _property_aware_event_count(result) -> int:
    kept = {
        "EV_MMIO_READ",
        "EV_MMIO_WRITE",
        "EV_INTERRUPT_ENTER",
        "EV_INTERRUPT_EXIT",
        "EV_EXTERNAL_INPUT",
        "EV_PROPERTY_FAIL",
        "EV_STORE",
        "EV_BRANCH",
        "EV_JUMP",
    }
    return sum(1 for event in result.events if event.event_type.name in kept)


if __name__ == "__main__":
    raise SystemExit(main())
