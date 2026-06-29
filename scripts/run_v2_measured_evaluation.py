#!/usr/bin/env python3
"""Generate measured v2 evaluation evidence without upgrading estimates to PASS."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from statistics import median

import generate_scaled_workloads
import run_full_rtl_replay
import run_mapped_synthesis
import run_runtime_overhead
from topconf_eval_common import REPO_ROOT, read_csv, read_json, reduction_pct, safe_float, safe_int, write_csv


WORKLOAD_OUT = REPO_ROOT / "results/processed/workload_scaling_v2_measured.csv"
WORKLOAD_SUMMARY = REPO_ROOT / "results/processed/workload_scaling_v2_measured_summary.csv"
BUFFER_OUT = REPO_ROOT / "results/processed/buffer_sensitivity_v2_measured.csv"
BUFFER_SUMMARY = REPO_ROOT / "results/processed/buffer_sensitivity_v2_measured_summary.csv"
CAPSULE_OUT = REPO_ROOT / "results/processed/capsule_baseline_comparison_v2_measured.csv"
CAPSULE_SUMMARY = REPO_ROOT / "results/processed/capsule_baseline_summary_v2_measured.csv"
RUNTIME_OUT = REPO_ROOT / "results/processed/runtime_scaling_v2_measured.csv"
RUNTIME_SUMMARY = REPO_ROOT / "results/processed/runtime_scaling_v2_measured_summary.csv"
MAPPED_OUT = REPO_ROOT / "results/processed/mapped_scaling_v2_measured.csv"
MAPPED_OVERHEAD = REPO_ROOT / "results/processed/mapped_scaling_overhead_v2_measured.csv"
MAPPED_PRESENCE = REPO_ROOT / "results/processed/mapped_recorder_presence_v2_measured.csv"

RAW_DIR = REPO_ROOT / "results/raw/workload_scaling_v2_measured"
CAPSULE_DIR = RAW_DIR / "capsules"
SIGNATURE_DIR = RAW_DIR / "signatures"
LOG_DIR = RAW_DIR / "logs"
MAPPED_RAW_DIR = REPO_ROOT / "results/raw/mapped_scaling_v2_measured"

CONFIGS = ("core", "hashed", "full")
DEPTHS = (64, 128, 256, 512, 1024, 2048)
WORKLOADS = ("smoke", "short", "medium", "long", "stress")
CURRENT_MEASURED_DEPTH = 256

WORKLOAD_FIELDS = [
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "measured_or_estimated",
    "firmware_source",
    "compiler_backed",
    "cycles",
    "commits",
    "events",
    "capsule_bytes",
    "event_rate_per_kinst",
    "cycles_to_failure",
    "commits_to_failure",
    "property_id",
    "replay_status",
    "final_signature_match",
    "event_match",
    "overflow",
    "notes",
]

WORKLOAD_SUMMARY_FIELDS = [
    "architecture",
    "recorder_config",
    "workload_scale",
    "pass_count",
    "fail_count",
    "timeout_count",
    "blocked_count",
    "replay_success_rate_pct",
    "overflow_rate_pct",
    "median_events",
    "median_capsule_bytes",
    "n",
    "notes",
]

BUFFER_FIELDS = [
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "buffer_depth",
    "measured_or_estimated",
    "events",
    "capsule_bytes",
    "overflow",
    "replay_status",
    "notes",
]

BUFFER_SUMMARY_FIELDS = [
    "architecture",
    "recorder_config",
    "buffer_depth",
    "workload_scale",
    "pass_count",
    "fail_count",
    "timeout_count",
    "blocked_count",
    "replay_success_rate_pct",
    "overflow_rate_pct",
    "median_events",
    "median_capsule_bytes",
    "n",
    "notes",
]

CAPSULE_FIELDS = [
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "baseline",
    "measured_or_estimated",
    "bytes",
    "events",
    "replay_success",
    "final_signature_match",
    "event_match",
    "reduction_vs_full_instruction_pct",
    "reduction_vs_full_commit_pct",
    "reduction_vs_snapshot_pct",
    "notes",
]

RUNTIME_FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "config",
    "firmware_source",
    "compiler_backed",
    "cycles",
    "commits",
    "events",
    "capsule_bytes",
    "sim_wall_time_sec",
    "cycle_overhead_pct",
    "commit_overhead_pct",
    "sim_wall_time_overhead_pct",
    "baseline_config",
    "status",
    "notes",
]

MAPPED_FIELDS = [
    "architecture",
    "recorder_config",
    "target",
    "flow",
    "design",
    "memory_words",
    "buffer_depth",
    "lut",
    "ff",
    "bram",
    "dsp",
    "cells",
    "area_um2",
    "fmax_mhz",
    "wns",
    "tns",
    "power_mw",
    "status",
    "report_path",
    "notes",
]

MAPPED_OVERHEAD_FIELDS = [
    "architecture",
    "recorder_config",
    "target",
    "flow",
    "memory_words",
    "buffer_depth",
    "metric",
    "baseline",
    "with_replaycapsule",
    "delta",
    "percent_overhead",
    "claim_allowed",
    "notes",
]

MAPPED_PRESENCE_FIELDS = [
    "architecture",
    "recorder_config",
    "design",
    "target",
    "flow",
    "memory_words",
    "buffer_depth",
    "recorder_present",
    "evidence",
    "status",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-sec", type=int, default=45)
    parser.add_argument("--skip-workload", action="store_true")
    parser.add_argument("--measure-all-buffer-depths", action="store_true")
    args = parser.parse_args()

    for path in (CAPSULE_DIR, SIGNATURE_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)

    if args.skip_workload and WORKLOAD_OUT.exists():
        workload_rows = read_csv(WORKLOAD_OUT)
    else:
        workload_rows = _measure_workloads(args.timeout_sec)
        write_csv(WORKLOAD_OUT, WORKLOAD_FIELDS, workload_rows)
        write_csv(WORKLOAD_SUMMARY, WORKLOAD_SUMMARY_FIELDS, _workload_summary(workload_rows))
        print(f"WROTE {_rel(WORKLOAD_OUT)}")
        print(f"WROTE {_rel(WORKLOAD_SUMMARY)}")

    buffer_depth_rows = {CURRENT_MEASURED_DEPTH: workload_rows}
    if args.measure_all_buffer_depths:
        for depth in DEPTHS:
            if depth == CURRENT_MEASURED_DEPTH:
                continue
            print(f"V2_BUFFER_DEPTH_START depth={depth}", flush=True)
            buffer_depth_rows[depth] = _measure_workloads_at_depth(args.timeout_sec, depth)

    _write_buffer_tables(workload_rows, buffer_depth_rows if args.measure_all_buffer_depths else None)
    _write_capsule_tables(workload_rows)
    _write_runtime_tables()
    _write_mapped_tables()
    return 0


def _measure_workloads(timeout_sec: int) -> list[dict[str, object]]:
    firmware_rows = generate_scaled_workloads._build_rows("full")
    write_csv(generate_scaled_workloads.OUT_CSV, generate_scaled_workloads.FIELDS, firmware_rows)
    blocker = run_full_rtl_replay._ensure_simulator()
    rows: list[dict[str, object]] = []
    total = len(firmware_rows) * 5 * len(CONFIGS)
    count = 0
    for config in CONFIGS:
        for firmware_row in firmware_rows:
            for seed in (1, 2, 3, 4, 5):
                count += 1
                if count == 1 or count % 50 == 0:
                    print(f"V2_WORKLOAD_PROGRESS {count}/{total} config={config}", flush=True)
                rows.append(_run_workload_case(firmware_row, seed, config, blocker, timeout_sec))
    return rows


def _measure_workloads_at_depth(timeout_sec: int, depth: int) -> list[dict[str, object]]:
    previous = os.environ.get("REPLAYCAPSULE_CAPSULE_DEPTH")
    os.environ["REPLAYCAPSULE_CAPSULE_DEPTH"] = str(depth)
    try:
        return _measure_workloads(timeout_sec)
    finally:
        if previous is None:
            os.environ.pop("REPLAYCAPSULE_CAPSULE_DEPTH", None)
        else:
            os.environ["REPLAYCAPSULE_CAPSULE_DEPTH"] = previous


def _run_workload_case(
    firmware_row: dict[str, str],
    seed: int,
    config: str,
    blocker: str | None,
    timeout_sec: int,
) -> dict[str, object]:
    benchmark = firmware_row["benchmark"]
    variant = firmware_row["variant"]
    scale = firmware_row["workload_scale"]
    if firmware_row.get("build_status") != "PASS":
        return _empty_workload_row(benchmark, variant, seed, scale, config, "BLOCKED", firmware_row.get("notes", "firmware build blocked"))
    if blocker:
        return _empty_workload_row(benchmark, variant, seed, scale, config, "BLOCKED", blocker)

    depth = _active_capsule_depth()
    depth_suffix = "" if depth == CURRENT_MEASURED_DEPTH else f"_depth{depth}"
    base = f"v2_{config}_{benchmark}_{variant}_seed{seed}_{scale}{depth_suffix}"
    capsule = CAPSULE_DIR / f"{base}.json"
    record_sig = SIGNATURE_DIR / f"{base}_record.json"
    replay_sig = SIGNATURE_DIR / f"{base}_replay.json"
    firmware = REPO_ROOT / firmware_row["hex_path"]

    record = _run_sim("record", benchmark, variant, firmware, capsule, record_sig, seed, firmware_row["max_cycles"], config, timeout_sec)
    (LOG_DIR / f"{base}_record.log").write_text(_clean(record.stdout), encoding="utf-8")
    if record.returncode == 124:
        return _workload_from_payload(benchmark, variant, seed, scale, config, "TIMEOUT", "NA", "NA", "record timed out", read_json(record_sig))
    if record.returncode != 0:
        return _workload_from_payload(benchmark, variant, seed, scale, config, "FAIL", "NA", "FAIL", _last_line(record.stdout), read_json(record_sig))

    replay = _run_sim("replay", benchmark, variant, firmware, capsule, replay_sig, seed, firmware_row["max_cycles"], config, timeout_sec)
    (LOG_DIR / f"{base}_replay.log").write_text(_clean(replay.stdout), encoding="utf-8")
    if replay.returncode == 124:
        return _workload_from_payload(benchmark, variant, seed, scale, config, "TIMEOUT", "NA", "NA", "replay timed out", read_json(record_sig))

    record_payload = read_json(record_sig)
    replay_payload = read_json(replay_sig)
    final_match = _same(record_payload.get("property_id"), replay_payload.get("property_id")) and _same(
        record_payload.get("property_signature"), replay_payload.get("property_signature")
    )
    event_match = replay.returncode == 0
    status = "PASS" if final_match and event_match else "FAIL"
    return _workload_from_payload(
        benchmark,
        variant,
        seed,
        scale,
        config,
        status,
        "PASS" if final_match else "FAIL",
        "PASS" if event_match else "FAIL",
        "record/replay complete" if status == "PASS" else _last_line(replay.stdout),
        record_payload,
    )


def _run_sim(
    mode: str,
    benchmark: str,
    variant: str,
    firmware: Path,
    capsule: Path,
    signature: Path,
    seed: int,
    max_cycles: str,
    config: str,
    timeout_sec: int,
) -> subprocess.CompletedProcess[str]:
    command = [
        str(run_full_rtl_replay._sim_path()),
        "--mode",
        mode,
        "--benchmark",
        benchmark,
        "--variant",
        variant,
        "--firmware",
        _rel(firmware),
        "--capsule",
        _rel(capsule),
        "--signature",
        _rel(signature),
        "--seed",
        str(seed),
        "--max-cycles",
        str(max_cycles),
        "--arch",
        "v2",
        "--recorder-config",
        config,
    ]
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=run_full_rtl_replay._tool_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout_sec,
        )
        completed.elapsed_sec = time.perf_counter() - start  # type: ignore[attr-defined]
        return completed
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(command, 124, output + f"\nTIMEOUT after {timeout_sec} seconds\n")


def _workload_from_payload(
    benchmark: str,
    variant: str,
    seed: int,
    scale: str,
    config: str,
    status: str,
    final_match: str,
    event_match: str,
    notes: str,
    payload: dict[str, object],
) -> dict[str, object]:
    cycles = payload.get("cycles_to_failure", "NA")
    commits = payload.get("commits_to_failure", "NA")
    events = payload.get("event_count", "NA")
    event_rate = "NA"
    commit_value = safe_float(commits)
    event_value = safe_float(events)
    if commit_value and event_value is not None:
        event_rate = f"{(event_value / commit_value * 1000.0):.6f}"
    property_id = str(payload.get("property_id", "NA"))
    failure_seen = property_id not in {"0", "NA", ""}
    return {
        "architecture": "v2",
        "recorder_config": config,
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
        "measured_or_estimated": "MEASURED",
        "firmware_source": "compiler_c_scaled",
        "compiler_backed": "true",
        "cycles": cycles,
        "commits": commits,
        "events": events,
        "capsule_bytes": payload.get("capsule_bytes", "NA"),
        "event_rate_per_kinst": event_rate,
        "cycles_to_failure": cycles if failure_seen else "NA",
        "commits_to_failure": commits if failure_seen else "NA",
        "property_id": property_id,
        "replay_status": status,
        "final_signature_match": final_match,
        "event_match": event_match,
        "overflow": str(payload.get("overflow", "NA")).lower(),
        "notes": _clean(notes),
    }


def _empty_workload_row(benchmark: str, variant: str, seed: int, scale: str, config: str, status: str, notes: str) -> dict[str, object]:
    return {
        "architecture": "v2",
        "recorder_config": config,
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
        "measured_or_estimated": "BLOCKED",
        "firmware_source": "compiler_c_scaled",
        "compiler_backed": "false",
        "cycles": "NA",
        "commits": "NA",
        "events": "NA",
        "capsule_bytes": "NA",
        "event_rate_per_kinst": "NA",
        "cycles_to_failure": "NA",
        "commits_to_failure": "NA",
        "property_id": "NA",
        "replay_status": status,
        "final_signature_match": "NA",
        "event_match": "NA",
        "overflow": "NA",
        "notes": _clean(notes),
    }


def _workload_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["architecture"]), str(row["recorder_config"]), str(row["workload_scale"]))].append(row)
    out = []
    for (arch, config, scale), subset in sorted(grouped.items()):
        n = len(subset)
        passes = sum(1 for row in subset if row["replay_status"] == "PASS")
        fails = sum(1 for row in subset if row["replay_status"] == "FAIL")
        timeouts = sum(1 for row in subset if row["replay_status"] == "TIMEOUT")
        blocked = sum(1 for row in subset if row["replay_status"] == "BLOCKED")
        overflows = sum(1 for row in subset if row["overflow"] == "true")
        events = _values(subset, "events")
        bytes_values = _values(subset, "capsule_bytes")
        out.append(
            {
                "architecture": arch,
                "recorder_config": config,
                "workload_scale": scale,
                "pass_count": passes,
                "fail_count": fails,
                "timeout_count": timeouts,
                "blocked_count": blocked,
                "replay_success_rate_pct": _pct_count(passes, n),
                "overflow_rate_pct": _pct_count(overflows, n) if events else "NA",
                "median_events": _median(events),
                "median_capsule_bytes": _median(bytes_values),
                "n": n,
                "notes": "all v2 rows are simulator-measured; FAIL rows are retained",
            }
        )
    return out


def _active_capsule_depth() -> int:
    try:
        return int(os.environ.get("REPLAYCAPSULE_CAPSULE_DEPTH", str(CURRENT_MEASURED_DEPTH)))
    except ValueError:
        return CURRENT_MEASURED_DEPTH


def _write_buffer_tables(workload_rows: list[dict[str, object]], v2_depth_rows: dict[int, list[dict[str, object]]] | None = None) -> None:
    rows: list[dict[str, object]] = []
    if v2_depth_rows is None:
        for source in read_csv(REPO_ROOT / "results/processed/workload_scaling.csv"):
            for depth in DEPTHS:
                rows.append(_buffer_row("v1", "full", source, depth))
    if v2_depth_rows is None:
        for source in workload_rows:
            for depth in DEPTHS:
                rows.append(_buffer_row("v2", str(source["recorder_config"]), source, depth))
    else:
        for depth, sources in sorted(v2_depth_rows.items()):
            for source in sources:
                rows.append(_buffer_row("v2", str(source["recorder_config"]), source, depth, measured_depth=True))
    write_csv(BUFFER_OUT, BUFFER_FIELDS, rows)
    write_csv(BUFFER_SUMMARY, BUFFER_SUMMARY_FIELDS, _status_summary(rows, "buffer_depth"))
    print(f"WROTE {_rel(BUFFER_OUT)}")
    print(f"WROTE {_rel(BUFFER_SUMMARY)}")


def _buffer_row(arch: str, config: str, source: dict[str, object], depth: int, measured_depth: bool = False) -> dict[str, object]:
    if depth != CURRENT_MEASURED_DEPTH and not measured_depth:
        return {
            "architecture": arch,
            "recorder_config": config,
            "benchmark": source.get("benchmark", "NA"),
            "variant": source.get("variant", "NA"),
            "seed": source.get("seed", "NA"),
            "workload_scale": source.get("workload_scale", "NA"),
            "buffer_depth": depth,
            "measured_or_estimated": "BLOCKED",
            "events": "NA",
            "capsule_bytes": "NA",
            "overflow": "NA",
            "replay_status": "BLOCKED",
            "notes": "not measured at this buffer depth; current simulator evidence uses depth 256 only",
        }
    return {
        "architecture": arch,
        "recorder_config": config,
        "benchmark": source.get("benchmark", "NA"),
        "variant": source.get("variant", "NA"),
        "seed": source.get("seed", "NA"),
        "workload_scale": source.get("workload_scale", "NA"),
        "buffer_depth": depth,
        "measured_or_estimated": source.get("measured_or_estimated", "MEASURED"),
        "events": source.get("events", "NA"),
        "capsule_bytes": source.get("capsule_bytes", "NA"),
        "overflow": source.get("overflow", "NA"),
        "replay_status": source.get("replay_status", "NA"),
        "notes": f"measured with current full-core simulator buffer depth {depth}",
    }


def _write_capsule_tables(workload_rows: list[dict[str, object]]) -> None:
    rows = []
    v1_by_key = {
        (row["benchmark"], row["variant"], row["seed"], row["workload_scale"]): row
        for row in read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    }
    v2_by_key: dict[tuple[str, str, str, str], dict[str, dict[str, object]]] = defaultdict(dict)
    for row in workload_rows:
        key = (str(row["benchmark"]), str(row["variant"]), str(row["seed"]), str(row["workload_scale"]))
        v2_by_key[key][str(row["recorder_config"])] = row
    for key, configs in sorted(v2_by_key.items()):
        baseline_row = configs.get("core") or next(iter(configs.values()))
        rows.extend(_capsule_baselines_for_case(key, baseline_row, v1_by_key.get(key), configs))
    write_csv(CAPSULE_OUT, CAPSULE_FIELDS, rows)
    write_csv(CAPSULE_SUMMARY, _capsule_summary_fields(), _capsule_summary(rows))
    print(f"WROTE {_rel(CAPSULE_OUT)}")
    print(f"WROTE {_rel(CAPSULE_SUMMARY)}")


def _capsule_baselines_for_case(
    key: tuple[str, str, str, str],
    baseline_row: dict[str, object],
    v1_row: dict[str, str] | None,
    configs: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    benchmark, variant, seed, scale = key
    commits = safe_int(baseline_row.get("commits"))
    snapshot = 4096
    full_instruction = commits * 8 if commits is not None else None
    full_commit = commits * 16 if commits is not None else None
    base_values = [
        ("baseline", "full_instruction_trace", "ESTIMATED", full_instruction, commits, "ESTIMATED formula=commits*(pc+instruction=8B)"),
        ("baseline", "full_commit_trace", "ESTIMATED", full_commit, commits, "ESTIMATED formula=commits*(pc+instruction+digest=16B)"),
        ("baseline", "snapshot_at_failure", "ESTIMATED", snapshot, 1, "ESTIMATED fixed 4KiB state snapshot"),
    ]
    out = [
        _capsule_row("baseline", cfg, benchmark, variant, seed, scale, name, kind, bytes_value, events, baseline_row, notes)
        for cfg, name, kind, bytes_value, events, notes in base_values
    ]
    if v1_row:
        out.append(_capsule_row("v1", "full", benchmark, variant, seed, scale, "v1_full", "MEASURED", v1_row.get("capsule_bytes"), v1_row.get("events"), v1_row, "MEASURED v1 workload capsule"))
    for config in CONFIGS:
        row = configs.get(config)
        if row:
            out.append(_capsule_row("v2", config, benchmark, variant, seed, scale, f"v2_{config}", "MEASURED", row.get("capsule_bytes"), row.get("events"), row, "MEASURED v2 exported capsule"))
    return out


def _capsule_row(
    arch: str,
    config: str,
    benchmark: str,
    variant: str,
    seed: str,
    scale: str,
    baseline: str,
    kind: str,
    bytes_value: object,
    events: object,
    source: dict[str, object],
    notes: str,
) -> dict[str, object]:
    full_i = safe_float(source.get("commits"))
    full_instruction = full_i * 8 if full_i is not None else None
    full_commit = full_i * 16 if full_i is not None else None
    return {
        "architecture": arch,
        "recorder_config": config,
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
        "baseline": baseline,
        "measured_or_estimated": kind,
        "bytes": bytes_value if bytes_value is not None else "NA",
        "events": events if events is not None else "NA",
        "replay_success": source.get("replay_status") == "PASS" if arch in {"v1", "v2"} else "NA",
        "final_signature_match": source.get("final_signature_match", "NA") if arch in {"v1", "v2"} else "NA",
        "event_match": source.get("event_match", "NA") if arch in {"v1", "v2"} else "NA",
        "reduction_vs_full_instruction_pct": reduction_pct(full_instruction, bytes_value),
        "reduction_vs_full_commit_pct": reduction_pct(full_commit, bytes_value),
        "reduction_vs_snapshot_pct": reduction_pct(4096, bytes_value),
        "notes": notes,
    }


def _capsule_summary_fields() -> list[str]:
    return [
        "architecture",
        "recorder_config",
        "baseline",
        "workload_scale",
        "measured_rows",
        "estimated_rows",
        "pass_count",
        "fail_count",
        "median_bytes",
        "median_reduction_vs_full_instruction_pct",
        "n",
        "notes",
    ]


def _capsule_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["architecture"]), str(row["recorder_config"]), str(row["baseline"]), str(row["workload_scale"]))].append(row)
    out = []
    for (arch, config, baseline, scale), subset in sorted(grouped.items()):
        measured = sum(1 for row in subset if row["measured_or_estimated"] == "MEASURED")
        estimated = sum(1 for row in subset if str(row["measured_or_estimated"]).lower() == "estimated")
        passes = sum(1 for row in subset if row["replay_success"] is True or row["replay_success"] == "true")
        fails = sum(1 for row in subset if row["replay_success"] is False or row["replay_success"] == "false")
        out.append(
            {
                "architecture": arch,
                "recorder_config": config,
                "baseline": baseline,
                "workload_scale": scale,
                "measured_rows": measured,
                "estimated_rows": estimated,
                "pass_count": passes,
                "fail_count": fails,
                "median_bytes": _median(_values(subset, "bytes")),
                "median_reduction_vs_full_instruction_pct": _median(_values(subset, "reduction_vs_full_instruction_pct")),
                "n": len(subset),
                "notes": "v2 baseline rows are measured only when measured_or_estimated=MEASURED",
            }
        )
    return out


def _write_runtime_tables() -> None:
    rows: list[dict[str, object]] = []
    blocker = run_runtime_overhead._ensure_runtime_sims()
    firmware_by_scale = _runtime_representative_firmware()
    for scale in WORKLOADS:
        firmware_row = firmware_by_scale.get(scale)
        case_rows = {
            config: _measure_runtime_row(firmware_row, config, blocker)
            for config in (
                "baseline_no_recorder",
                "v2_recorder_present_disabled",
                "v2_recorder_enabled_core",
                "v2_recorder_enabled_hashed",
                "v2_recorder_enabled_full",
            )
        }
        _fill_runtime_overheads(case_rows)
        rows.extend(case_rows[config] for config in case_rows)
    write_csv(RUNTIME_OUT, RUNTIME_FIELDS, rows)
    write_csv(RUNTIME_SUMMARY, ["workload_scale", "config", "measured_rows", "blocked_rows", "notes"], _runtime_summary(rows))
    print(f"WROTE {_rel(RUNTIME_OUT)}")
    print(f"WROTE {_rel(RUNTIME_SUMMARY)}")


def _runtime_representative_firmware() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in generate_scaled_workloads._build_rows("full"):
        if row.get("benchmark") == "sensor_threshold_bug" and row.get("variant") == "failing" and row.get("build_status") == "PASS":
            out[row["workload_scale"]] = row
    return out


def _measure_runtime_row(firmware_row: dict[str, str] | None, config: str, blocker: str | None) -> dict[str, object]:
    if firmware_row is None:
        return _blocked_runtime_row("NA", config, "missing representative scaled firmware row")
    scale = firmware_row["workload_scale"]
    if blocker:
        return _blocked_runtime_row(scale, config, blocker)
    sim = run_runtime_overhead._sim_path(
        run_runtime_overhead.BASELINE_SIM if config == "baseline_no_recorder" else run_runtime_overhead.RECORDER_SIM
    )
    command = [
        str(sim),
        "--config",
        config,
        "--benchmark",
        firmware_row["benchmark"],
        "--variant",
        firmware_row["variant"],
        "--firmware",
        firmware_row["hex_path"],
        "--seed",
        "1",
        "--max-cycles",
        firmware_row["max_cycles"],
    ]
    start = time.perf_counter()
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, env=run_runtime_overhead._tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=45)
        elapsed = time.perf_counter() - start
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        row = _blocked_runtime_row(scale, config, f"runtime measurement timeout; {output.strip()[-120:]}")
        row["status"] = "TIMEOUT"
        return row
    parsed = _parse_runtime_stdout(completed.stdout)
    status = "MEASURED" if completed.returncode == 0 else "FAIL"
    return {
        "benchmark": firmware_row["benchmark"],
        "variant": firmware_row["variant"],
        "seed": "1",
        "workload_scale": scale,
        "config": config,
        "firmware_source": "compiler_c_scaled",
        "compiler_backed": "true",
        "cycles": parsed.get("cycles", "NA"),
        "commits": parsed.get("commits", "NA"),
        "events": parsed.get("events", "NA"),
        "capsule_bytes": parsed.get("capsule_bytes", "NA"),
        "sim_wall_time_sec": f"{elapsed:.6f}",
        "cycle_overhead_pct": "NA",
        "commit_overhead_pct": "NA",
        "sim_wall_time_overhead_pct": "NA",
        "baseline_config": "NA" if config == "baseline_no_recorder" else "baseline_no_recorder",
        "status": status,
        "notes": "measured representative compiler-backed scaled workload" if status == "MEASURED" else _last_line(completed.stdout),
    }


def _parse_runtime_stdout(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    line = _last_line(text)
    for key in ("cycles", "commits", "events", "capsule_bytes"):
        marker = f"{key}="
        for part in line.split():
            if part.startswith(marker):
                out[key] = part[len(marker):].strip('"')
    return out


def _fill_runtime_overheads(case_rows: dict[str, dict[str, object]]) -> None:
    baseline = case_rows["baseline_no_recorder"]
    for config, row in case_rows.items():
        if config == "baseline_no_recorder":
            continue
        if baseline["status"] != "MEASURED" or row["status"] != "MEASURED":
            continue
        row["cycle_overhead_pct"] = _pct_delta(baseline["cycles"], row["cycles"])
        row["commit_overhead_pct"] = _pct_delta(baseline["commits"], row["commits"])
        row["sim_wall_time_overhead_pct"] = _pct_delta(baseline["sim_wall_time_sec"], row["sim_wall_time_sec"])


def _pct_delta(baseline: object, value: object) -> str:
    b = safe_float(baseline)
    v = safe_float(value)
    if b is None or v is None or b == 0:
        return "NA"
    return f"{((v - b) / b * 100.0):.2f}"


def _blocked_runtime_row(scale: str, config: str, notes: str) -> dict[str, object]:
    return {
        "benchmark": "sensor_threshold_bug",
        "variant": "failing",
        "seed": "1",
        "workload_scale": scale,
        "config": config,
        "firmware_source": "compiler_c_scaled",
        "compiler_backed": "true",
        "cycles": "NA",
        "commits": "NA",
        "events": "NA",
        "capsule_bytes": "NA",
        "sim_wall_time_sec": "NA",
        "cycle_overhead_pct": "NA",
        "commit_overhead_pct": "NA",
        "sim_wall_time_overhead_pct": "NA",
        "baseline_config": "NA" if config == "baseline_no_recorder" else "baseline_no_recorder",
        "status": "BLOCKED",
        "notes": notes,
    }


def _runtime_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["workload_scale"]), str(row["config"]))].append(row)
    return [
        {
            "workload_scale": scale,
            "config": config,
            "measured_rows": sum(1 for row in subset if row["status"] == "MEASURED"),
            "blocked_rows": sum(1 for row in subset if row["status"] == "BLOCKED"),
            "notes": "measured v2 runtime rows use the integrated runtime harness; blocked_rows should be zero",
        }
        for (scale, config), subset in sorted(grouped.items())
    ]


def _write_mapped_tables() -> None:
    MAPPED_RAW_DIR.mkdir(parents=True, exist_ok=True)
    yosys = run_mapped_synthesis._find_tool("yosys")
    target = run_mapped_synthesis.FULL_CORE_TARGETS[0]
    nextpnr = run_mapped_synthesis._find_tool(target.nextpnr_name)
    memory = 128
    depth = 16
    baseline = _run_v2_mapped_design("baseline", "full", memory, depth, yosys, nextpnr)
    mapped_rows = [baseline]
    for config in CONFIGS:
        mapped_rows.append(_run_v2_mapped_design("v2", config, memory, depth, yosys, nextpnr))
    overhead_rows = [
        {
            "architecture": row["architecture"],
            "recorder_config": row["recorder_config"],
            "target": row["target"],
            "flow": row["flow"],
            "memory_words": row["memory_words"],
            "buffer_depth": row["buffer_depth"],
            "metric": metric,
            "baseline": "NA",
            "with_replaycapsule": "NA",
            "delta": "NA",
            "percent_overhead": "NA",
            "claim_allowed": _mapped_claim_allowed(baseline, row),
            "notes": "same-target measured full-core v2 overhead" if _mapped_claim_allowed(baseline, row) == "yes" else "requires same-target PASS baseline and v2 rows",
        }
        for row in mapped_rows
        if row["architecture"] == "v2"
        for metric in ("lut", "ff", "bram", "fmax_mhz")
    ]
    for row in overhead_rows:
        baseline_value = baseline.get(str(row["metric"]), "NA")
        matched = next(
            item for item in mapped_rows
            if item["architecture"] == "v2" and item["recorder_config"] == row["recorder_config"]
        )
        mapped_value = matched.get(str(row["metric"]), "NA")
        row["baseline"] = baseline_value
        row["with_replaycapsule"] = mapped_value
        row["delta"] = _delta_value(baseline_value, mapped_value)
        row["percent_overhead"] = _pct_delta(baseline_value, mapped_value)
    presence_rows = [
        _v2_presence_row(row)
        for row in mapped_rows
        if row["architecture"] == "v2"
    ]
    write_csv(MAPPED_OUT, MAPPED_FIELDS, mapped_rows)
    write_csv(MAPPED_OVERHEAD, MAPPED_OVERHEAD_FIELDS, overhead_rows)
    write_csv(MAPPED_PRESENCE, MAPPED_PRESENCE_FIELDS, presence_rows)
    print(f"WROTE {_rel(MAPPED_OUT)}")
    print(f"WROTE {_rel(MAPPED_OVERHEAD)}")
    print(f"WROTE {_rel(MAPPED_PRESENCE)}")


def _run_v2_mapped_design(
    architecture: str,
    config: str,
    memory_words: int,
    buffer_depth: int,
    yosys: str | None,
    nextpnr: str | None,
) -> dict[str, object]:
    target = run_mapped_synthesis.FULL_CORE_TARGETS[0]
    design = "full_core_baseline_board" if architecture == "baseline" else f"full_core_v2_{config}_board"
    if not yosys:
        return _blocked_mapped_row(architecture, config, design, memory_words, buffer_depth, "missing yosys")
    if not nextpnr:
        return _blocked_mapped_row(architecture, config, design, memory_words, buffer_depth, f"missing {target.nextpnr_name}")
    stem = f"{design}_mem{memory_words}_buf{buffer_depth}_{target.suffix}"
    json_path = MAPPED_RAW_DIR / f"{stem}.json"
    bitstream_path = MAPPED_RAW_DIR / f"{stem}.{target.output_ext}"
    yosys_log = MAPPED_RAW_DIR / f"{stem}_yosys.txt"
    nextpnr_log = MAPPED_RAW_DIR / f"{stem}_nextpnr.txt"
    for stale in (bitstream_path,):
        if stale.exists():
            stale.unlink()
    if not json_path.exists() or not yosys_log.exists():
        y = run_mapped_synthesis._run_tool([yosys, "-p", _v2_mapped_yosys_script(architecture, config, memory_words, buffer_depth, json_path)], run_mapped_synthesis.YOSYS_TIMEOUT_SECONDS)
        yosys_log.write_text(run_mapped_synthesis._clean(y.stdout), encoding="utf-8")
        if y.returncode != 0 or not json_path.exists():
            row = _blocked_mapped_row(architecture, config, design, memory_words, buffer_depth, "SYNTH_FAIL: " + run_mapped_synthesis._last_error_line(yosys_log))
            row["status"] = "FAIL"
            row["report_path"] = _rel(yosys_log)
            return row
        run_mapped_synthesis._sanitize_file(json_path)
    command = [nextpnr, *target.nextpnr_args, "--json", _rel(json_path), "--textcfg", _rel(bitstream_path)]
    if run_mapped_synthesis.ECP5_LPF.exists():
        command.extend(["--lpf", _rel(run_mapped_synthesis.ECP5_LPF)])
    n = run_mapped_synthesis._run_tool(command, 900)
    nextpnr_log.write_text(run_mapped_synthesis._clean(n.stdout), encoding="utf-8")
    if n.returncode != 0 or not bitstream_path.exists():
        row = _blocked_mapped_row(architecture, config, design, memory_words, buffer_depth, "P&R_FAIL: " + run_mapped_synthesis._last_error_line(nextpnr_log))
        row["status"] = "FAIL"
        row["report_path"] = _rel(nextpnr_log)
        return row
    metrics = run_mapped_synthesis._ecp5_metrics(yosys_log.read_text(encoding="utf-8", errors="replace") + "\n" + nextpnr_log.read_text(encoding="utf-8", errors="replace"))
    return {
        "architecture": architecture,
        "recorder_config": config,
        "target": target.name,
        "flow": target.flow,
        "design": design,
        "memory_words": memory_words,
        "buffer_depth": buffer_depth,
        "lut": metrics.get("lut", "NA"),
        "ff": metrics.get("ff", "NA"),
        "bram": metrics.get("bram", "NA"),
        "dsp": metrics.get("dsp", "NA"),
        "cells": metrics.get("cells", "NA"),
        "area_um2": "NA",
        "fmax_mhz": metrics.get("fmax_mhz", "NA"),
        "wns": "NA",
        "tns": "NA",
        "power_mw": "NA",
        "status": "PASS",
        "report_path": _rel(nextpnr_log),
        "notes": "real same-target ECP5 full-core place-and-route completed",
    }


def _v2_mapped_yosys_script(architecture: str, config: str, memory_words: int, buffer_depth: int, json_path: Path) -> str:
    if architecture == "baseline":
        sources = run_mapped_synthesis.DESIGNS["full_core_baseline_board"].sources
        top = run_mapped_synthesis.DESIGNS["full_core_baseline_board"].top
        commands = [
            "read_verilog -sv -Irtl -Irtl/mapped -Irtl/rv32i_integration -Ithird_party/picorv32 " + " ".join(sources),
            f"chparam -set MEM_WORDS {memory_words} {top}",
        ]
    else:
        sources = (
            "third_party/picorv32/picorv32.v",
            *run_mapped_synthesis.RTL_COMMON,
            "rtl/mapped/mapped_memory.sv",
            "rtl/mapped/full_core_replaycapsule_v2_board_top.sv",
        )
        top = "full_core_replaycapsule_v2_board_top"
        config_select = {"core": 1, "hashed": 2, "full": 4}[config]
        addr_w = max(1, (buffer_depth - 1).bit_length())
        commands = [
            "read_verilog -sv -Irtl -Irtl/mapped -Irtl/rv32i_integration -Ithird_party/picorv32 " + " ".join(sources),
            f"chparam -set MEM_WORDS {memory_words} {top}",
            f"chparam -set CAPSULE_DEPTH {buffer_depth} {top}",
            f"chparam -set CAPSULE_ADDR_W {addr_w} {top}",
            f"chparam -set REPLAYCAPSULE_CONFIG {config_select} {top}",
        ]
    commands.append(f"synth_ecp5 -top {top} -json {_rel(json_path)}")
    return "; ".join(commands)


def _mapped_claim_allowed(baseline: dict[str, object], row: dict[str, object]) -> str:
    return "yes" if baseline.get("status") == "PASS" and row.get("status") == "PASS" else "no"


def _v2_presence_row(row: dict[str, object]) -> dict[str, object]:
    report = REPO_ROOT / str(row.get("report_path", ""))
    json_path = Path(str(report).replace("_nextpnr.txt", ".json"))
    yosys_path = Path(str(report).replace("_nextpnr.txt", "_yosys.txt"))
    text = ""
    for path in (json_path, yosys_path, report):
        if path.exists():
            text += "\n" + path.read_text(encoding="utf-8", errors="replace")
    present = row.get("status") == "PASS" and "rcv2_recorder" in text and "u_picorv32" in text
    return {
        "architecture": row["architecture"],
        "recorder_config": row["recorder_config"],
        "design": row["design"],
        "target": row["target"],
        "flow": row["flow"],
        "memory_words": row["memory_words"],
        "buffer_depth": row["buffer_depth"],
        "recorder_present": "true" if present else "false",
        "evidence": _rel(yosys_path) if yosys_path.exists() else row.get("report_path", "NA"),
        "status": "PASS" if present else "FAIL",
        "notes": "full-core v2 recorder hierarchy found in mapped netlist/log" if present else "v2 recorder hierarchy not found",
    }


def _delta_value(left: object, right: object) -> str:
    l = safe_float(left)
    r = safe_float(right)
    if l is None or r is None:
        return "NA"
    return f"{(r - l):.2f}"


def _blocked_mapped_row(arch: str, config: str, design: str, memory: int, depth: int, notes: str) -> dict[str, object]:
    return {
        "architecture": arch,
        "recorder_config": config,
        "target": "ecp5-85k",
        "flow": "yosys+synth_ecp5+nextpnr-ecp5",
        "design": design,
        "memory_words": memory,
        "buffer_depth": depth,
        "lut": "NA",
        "ff": "NA",
        "bram": "NA",
        "dsp": "NA",
        "cells": "NA",
        "area_um2": "NA",
        "fmax_mhz": "NA",
        "wns": "NA",
        "tns": "NA",
        "power_mw": "NA",
        "status": "BLOCKED",
        "report_path": "NA",
        "notes": notes,
    }


def _status_summary(rows: list[dict[str, object]], extra: str) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["architecture"]), str(row["recorder_config"]), str(row["workload_scale"]), str(row[extra]))].append(row)
    out = []
    for (arch, config, scale, extra_value), subset in sorted(grouped.items()):
        n = len(subset)
        passes = sum(1 for row in subset if row["replay_status"] == "PASS")
        fails = sum(1 for row in subset if row["replay_status"] == "FAIL")
        timeouts = sum(1 for row in subset if row["replay_status"] == "TIMEOUT")
        blocked = sum(1 for row in subset if row["replay_status"] == "BLOCKED")
        overflows = sum(1 for row in subset if row["overflow"] == "true")
        notes = (
            "all rows in this group come from measured v2 replay runs"
            if arch == "v2" and blocked == 0
            else "legacy comparison rows are retained as blocked placeholders where this depth was not measured"
        )
        out.append(
            {
                "architecture": arch,
                "recorder_config": config,
                extra: extra_value,
                "workload_scale": scale,
                "pass_count": passes,
                "fail_count": fails,
                "timeout_count": timeouts,
                "blocked_count": blocked,
                "replay_success_rate_pct": _pct_count(passes, n),
                "overflow_rate_pct": _pct_count(overflows, n) if _values(subset, "events") else "NA",
                "median_events": _median(_values(subset, "events")),
                "median_capsule_bytes": _median(_values(subset, "capsule_bytes")),
                "n": n,
                "notes": notes,
            }
        )
    return out


def _values(rows: list[dict[str, object]], field: str) -> list[float]:
    return [value for value in (safe_float(row.get(field)) for row in rows) if value is not None]


def _median(values: list[float]) -> str:
    return f"{median(values):.6f}" if values else "NA"


def _pct_count(count: int, total: int) -> str:
    return f"{(count / total * 100.0):.6f}" if total else "NA"


def _same(left: object, right: object) -> bool:
    return str(left) == str(right)


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "no simulator output"


def _clean(text: str) -> str:
    return run_full_rtl_replay._clean(text)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
