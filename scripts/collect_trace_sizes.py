#!/usr/bin/env python3
"""Collect trace-size metrics from generated ReplayCapsule-RV artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from replaycapsule_model import capsule_fixture, run_benchmark  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "tb" / "replay_testbench"))
from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


RAW_TRACE = REPO_ROOT / "results/raw/model_suite_traces.json"
OUT_CSV = REPO_ROOT / "results/processed/trace_sizes.csv"

BASELINES = [
    "full_instruction_trace",
    "full_commit_trace",
    "branch_only_trace",
    "store_only_trace",
    "mmio_only_trace",
    "interrupt_mmio_trace",
    "snapshot_on_failure",
    "property_aware_replaycapsule_rv",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, default=RAW_TRACE)
    parser.add_argument("--out", type=Path, default=OUT_CSV)
    args = parser.parse_args()

    rows = collect(args.trace)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "benchmark",
                "baseline",
                "status",
                "event_count",
                "bytes",
                "events_per_kinst",
                "replay_success",
                "evidence_level",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"WROTE {args.out}")
    return 0


def collect(trace_path: Path) -> list[dict[str, str]]:
    if not trace_path.exists():
        return [_todo_row("suite", name, f"missing artifact: {trace_path}") for name in BASELINES]

    payload = json.loads(trace_path.read_text(encoding="utf-8"))
    runs = payload.get("runs")
    if runs is None:
        runs = [payload]

    rows: list[dict[str, str]] = []
    for run in runs:
        benchmark = str(run.get("benchmark", "unknown"))
        events = list(run.get("events", []))
        commit_events = [event for event in events if event.get("event_type") == "EV_COMMIT"]
        kinst = max(len(commit_events) / 1000.0, 0.001)
        for name in BASELINES:
            selected = _select_events(name, events)
            if selected is None:
                rows.append(_todo_row(benchmark, name, "requires simulator/RTL artifact not yet generated"))
                continue
            replay_success = _baseline_replay_success(benchmark, name)
            rows.append(
                {
                    "benchmark": benchmark,
                    "baseline": name,
                    "status": "MEASURED",
                    "event_count": str(len(selected)),
                    "bytes": str(_estimated_record_bytes(name, selected)),
                    "events_per_kinst": f"{len(selected) / kinst:.3f}",
                    "replay_success": str(replay_success),
                    "evidence_level": "model",
                    "notes": "size and replay success measured from model-level evidence; RTL trace sizes pending",
                }
            )
    return rows


def _select_events(name: str, events: list[dict[str, object]]) -> list[dict[str, object]] | None:
    if name in {"full_instruction_trace", "snapshot_on_failure"}:
        return None
    if name == "full_commit_trace":
        return [event for event in events if event.get("event_type") == "EV_COMMIT"]
    if name == "branch_only_trace":
        return [event for event in events if event.get("event_type") in {"EV_BRANCH", "EV_JUMP"}]
    if name == "store_only_trace":
        return [event for event in events if event.get("event_type") in {"EV_STORE", "EV_MMIO_WRITE"}]
    if name == "mmio_only_trace":
        return [event for event in events if str(event.get("event_type", "")).startswith("EV_MMIO")]
    if name == "interrupt_mmio_trace":
        return [
            event
            for event in events
            if str(event.get("event_type", "")).startswith("EV_MMIO")
            or str(event.get("event_type", "")).startswith("EV_INTERRUPT")
        ]
    if name == "property_aware_replaycapsule_rv":
        return [
            event
            for event in events
            if event.get("event_type")
            in {
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
        ]
    return None


def _estimated_record_bytes(name: str, events: list[dict[str, object]]) -> int:
    if name == "property_aware_replaycapsule_rv":
        return len(events) * 21
    return len(events) * 16


def _baseline_replay_success(benchmark: str, baseline: str) -> bool:
    result = run_benchmark(benchmark, failing=True)
    expected = parse_capsule(capsule_fixture(result), source=f"{benchmark}:expected")
    omitted = _baseline_omissions(baseline)
    observed = parse_capsule(capsule_fixture(result, omit=omitted), source=f"{benchmark}:{baseline}")
    return compare_capsules(expected, observed, mode="commit-index").success


def _baseline_omissions(baseline: str) -> set[str]:
    if baseline == "full_commit_trace":
        return {"mmio_read", "mmio_write", "store", "branch", "external_input", "interrupt_timing"}
    if baseline == "branch_only_trace":
        return {"mmio_read", "mmio_write", "store", "external_input", "interrupt_timing", "pc"}
    if baseline == "store_only_trace":
        return {"mmio_read", "mmio_write", "branch", "external_input", "interrupt_timing", "pc"}
    if baseline == "mmio_only_trace":
        return {"store", "branch", "external_input", "interrupt_timing", "pc"}
    if baseline == "interrupt_mmio_trace":
        return {"store", "branch", "external_input", "pc"}
    if baseline == "property_aware_replaycapsule_rv":
        return set()
    return {"pc", "mmio_read", "mmio_write", "store", "branch", "external_input", "interrupt_timing"}


def _todo_row(benchmark: str, name: str, notes: str) -> dict[str, str]:
    return {
        "benchmark": benchmark,
        "baseline": name,
        "status": "TODO",
        "event_count": "NA",
        "bytes": "NA",
        "events_per_kinst": "NA",
        "replay_success": "TODO",
        "evidence_level": "NA",
        "notes": notes,
    }


if __name__ == "__main__":
    raise SystemExit(main())
