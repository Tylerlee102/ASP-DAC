#!/usr/bin/env python3
"""Compare ReplayCapsule sizes against labeled trace/snapshot baselines."""

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean, median

from topconf_eval_common import REPO_ROOT, read_csv, read_json, reduction_pct, safe_float, safe_int, write_csv


OUT_CSV = REPO_ROOT / "results/processed/capsule_baseline_comparison.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/capsule_baseline_summary.csv"
WORKLOAD_CSV = REPO_ROOT / "results/processed/workload_scaling.csv"
CAPSULE_DIR = REPO_ROOT / "results/raw/workload_scaling/capsules"

BASELINES = (
    "full_instruction_trace",
    "full_commit_trace",
    "pc_only_trace",
    "branch_trace",
    "riscv_etrace_branch_trace_estimate",
    "load_store_trace",
    "mmio_only_trace",
    "interrupt_only_trace",
    "interrupt_plus_mmio_trace",
    "snapshot_at_failure",
    "replaycapsule_core",
    "replaycapsule_with_diagnostics",
    "replaycapsule_with_payload_hashes",
)

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "buffer_depth",
    "baseline",
    "bytes",
    "events",
    "replay_success",
    "property_match",
    "final_signature_match",
    "event_match",
    "reduction_vs_full_instruction_pct",
    "reduction_vs_full_commit_pct",
    "reduction_vs_snapshot_pct",
    "diagnostic_context_available",
    "notes",
]

SUMMARY_FIELDS = [
    "baseline",
    "workload_scale",
    "median_buffer_depth",
    "median_bytes",
    "mean_bytes",
    "min_bytes",
    "max_bytes",
    "median_reduction_vs_full_instruction_pct",
    "median_reduction_vs_full_commit_pct",
    "n",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(WORKLOAD_CSV))
    parser.add_argument("--output", default=str(OUT_CSV))
    parser.add_argument("--summary-output", default=str(SUMMARY_CSV))
    args = parser.parse_args()

    workload_rows = read_csv(_repo_path(args.input))
    rows = []
    for row in workload_rows:
        rows.extend(_baseline_rows(row))
    out_csv = _repo_path(args.output)
    summary_csv = _repo_path(args.summary_output)
    write_csv(out_csv, FIELDS, rows)
    write_csv(summary_csv, SUMMARY_FIELDS, _summary_rows(rows))
    print(f"WROTE {_rel(out_csv)}")
    print(f"WROTE {_rel(summary_csv)}")
    return 0


def _baseline_rows(row: dict[str, str]) -> list[dict[str, object]]:
    values = _baseline_values(row)
    full_instruction = values["full_instruction_trace"]["bytes"]
    full_commit = values["full_commit_trace"]["bytes"]
    snapshot = values["snapshot_at_failure"]["bytes"]
    out = []
    for baseline in BASELINES:
        value = values[baseline]
        strict_valid = row.get("strict_replay_valid", "").lower() == "true" or (
            row.get("strict_replay_valid", "") == "" and row.get("replay_status") == "PASS" and row.get("overflow", "false").lower() != "true"
        )
        replay_success = strict_valid and baseline.startswith("replaycapsule")
        out.append(
            {
                "benchmark": row.get("benchmark", "NA"),
                "variant": row.get("variant", "NA"),
                "seed": row.get("seed", "NA"),
                "workload_scale": row.get("workload_scale", "NA"),
                "buffer_depth": row.get("buffer_depth", "NA"),
                "baseline": baseline,
                "bytes": value["bytes"],
                "events": value["events"],
                "replay_success": replay_success,
                "property_match": row.get("final_signature_match", "NA") if baseline.startswith("replaycapsule") else "NA",
                "final_signature_match": row.get("final_signature_match", "NA") if baseline.startswith("replaycapsule") else "NA",
                "event_match": row.get("event_match", "NA") if baseline.startswith("replaycapsule") else "NA",
                "reduction_vs_full_instruction_pct": reduction_pct(full_instruction, value["bytes"]),
                "reduction_vs_full_commit_pct": reduction_pct(full_commit, value["bytes"]),
                "reduction_vs_snapshot_pct": reduction_pct(snapshot, value["bytes"]),
                "diagnostic_context_available": value["diagnostic"],
                "notes": value["notes"],
            }
        )
    return out


def _baseline_values(row: dict[str, str]) -> dict[str, dict[str, object]]:
    commits_value = safe_int(row.get("commits"))
    events_value = safe_int(row.get("events"))
    capsule_value = safe_int(row.get("capsule_bytes"))
    if commits_value is None or events_value is None or capsule_value is None:
        return {baseline: _unavailable("BLOCKED upstream workload row; no measured size or trace estimate") for baseline in BASELINES}
    commits = commits_value
    events = events_value
    capsule_bytes = capsule_value
    event_counts = _event_counts(row)
    branch_events = event_counts.get(1, 0) + event_counts.get(2, 0)
    etrace_sync_packets = max(1, (commits + 63) // 64)
    mem_events = sum(event_counts.get(event_type, 0) for event_type in (3, 4, 5, 6))
    mmio_events = event_counts.get(5, 0) + event_counts.get(6, 0)
    irq_events = event_counts.get(7, 0) + event_counts.get(8, 0)
    return {
        "full_instruction_trace": _estimated(commits * 8, commits, "ESTIMATED formula=commits*(pc+instruction=8B)", False),
        "full_commit_trace": _estimated(commits * 16, commits, "ESTIMATED formula=commits*(pc+instruction+register-digest=16B)", False),
        "pc_only_trace": _estimated(commits * 4, commits, "ESTIMATED formula=commits*pc32", False),
        "branch_trace": _estimated(branch_events * 12, branch_events, "ESTIMATED formula=branch/jump events*(type+pc+target=12B)", False),
        "riscv_etrace_branch_trace_estimate": _estimated(
            branch_events * 4 + etrace_sync_packets * 8,
            branch_events,
            "ESTIMATED RISC-V E-Trace/N-Trace-style branch stream; formula=branch/jump events*4B + 64-commit sync packets*8B",
            False,
        ),
        "load_store_trace": _estimated(mem_events * 12, mem_events, "ESTIMATED formula=load/store/MMIO events*(type+addr+data=12B)", False),
        "mmio_only_trace": _estimated(mmio_events * 12, mmio_events, "ESTIMATED formula=MMIO read/write events*(type+addr+data=12B)", False),
        "interrupt_only_trace": _estimated(irq_events * 12, irq_events, "ESTIMATED formula=interrupt events*(type+pc+commit=12B)", False),
        "interrupt_plus_mmio_trace": _estimated((irq_events + mmio_events) * 12, irq_events + mmio_events, "ESTIMATED formula=(interrupt+MMIO events)*12B", False),
        "snapshot_at_failure": _estimated(4096, 1, "ESTIMATED fixed 4KiB state snapshot at failure", True),
        "replaycapsule_core": _measured(capsule_bytes, events, "MEASURED from workload_scaling capsule_bytes", True),
        "replaycapsule_with_diagnostics": _estimated(capsule_bytes + events * 8, events, "ESTIMATED measured capsule plus 8B/event diagnostic context", True),
        "replaycapsule_with_payload_hashes": _estimated(capsule_bytes + events * 4, events, "ESTIMATED measured capsule plus 4B/event payload hash", True),
    }


def _event_counts(row: dict[str, str]) -> dict[int, int]:
    capsule_path = row.get("capsule_path", "")
    if capsule_path and capsule_path != "NA":
        payload = read_json(_repo_path(capsule_path))
    else:
        prefix = "" if row.get("architecture", "v1") in {"", "v1", "NA"} else f"{row.get('architecture')}_{row.get('recorder_config', 'core')}_"
        base = f"{prefix}{row.get('benchmark')}_{row.get('variant')}_seed{row.get('seed')}_{row.get('workload_scale')}.json"
        payload = read_json(CAPSULE_DIR / base)
    counts: dict[int, int] = {}
    for event in payload.get("events", []) if isinstance(payload.get("events"), list) else []:
        if not isinstance(event, dict):
            continue
        event_type = event.get("event_type")
        try:
            key = int(event_type)
        except (TypeError, ValueError):
            continue
        counts[key] = counts.get(key, 0) + 1
    return counts


def _estimated(bytes_value: int, events: int, notes: str, diagnostic: bool) -> dict[str, object]:
    return {"bytes": max(bytes_value, 0), "events": max(events, 0), "notes": notes, "diagnostic": diagnostic}


def _measured(bytes_value: int, events: int, notes: str, diagnostic: bool) -> dict[str, object]:
    return {"bytes": max(bytes_value, 0), "events": max(events, 0), "notes": notes, "diagnostic": diagnostic}


def _unavailable(notes: str) -> dict[str, object]:
    return {"bytes": "NA", "events": "NA", "notes": notes, "diagnostic": "NA"}


def _summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    keys = sorted({(str(row["baseline"]), str(row["workload_scale"])) for row in rows})
    for baseline, scale in keys:
        subset = [row for row in rows if row["baseline"] == baseline and row["workload_scale"] == scale]
        byte_values = [safe_float(row["bytes"]) for row in subset]
        buffer_depths = [safe_float(row.get("buffer_depth")) for row in subset]
        bytes_clean = [value for value in byte_values if value is not None]
        depths_clean = [value for value in buffer_depths if value is not None]
        red_i = [safe_float(row["reduction_vs_full_instruction_pct"]) for row in subset]
        red_c = [safe_float(row["reduction_vs_full_commit_pct"]) for row in subset]
        out.append(
            {
                "baseline": baseline,
                "workload_scale": scale,
                "median_buffer_depth": _fmt(median(depths_clean)) if depths_clean else "NA",
                "median_bytes": _fmt(median(bytes_clean)) if bytes_clean else "NA",
                "mean_bytes": _fmt(mean(bytes_clean)) if bytes_clean else "NA",
                "min_bytes": _fmt(min(bytes_clean)) if bytes_clean else "NA",
                "max_bytes": _fmt(max(bytes_clean)) if bytes_clean else "NA",
                "median_reduction_vs_full_instruction_pct": _fmt(median([v for v in red_i if v is not None])) if any(v is not None for v in red_i) else "NA",
                "median_reduction_vs_full_commit_pct": _fmt(median([v for v in red_c if v is not None])) if any(v is not None for v in red_c) else "NA",
                "n": len(subset),
                "notes": "summary preserves ESTIMATED labels in detailed CSV",
            }
        )
    return out


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
