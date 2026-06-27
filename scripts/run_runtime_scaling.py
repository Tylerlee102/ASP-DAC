#!/usr/bin/env python3
"""Measure runtime overhead across deterministic workload scales."""

from __future__ import annotations

import argparse
import re
import subprocess
import time
from statistics import mean, median

import generate_scaled_workloads
import run_runtime_overhead
from topconf_eval_common import REPO_ROOT, safe_float, write_csv


OUT_CSV = REPO_ROOT / "results/processed/runtime_scaling.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/runtime_scaling_summary.csv"

CONFIGS = ("baseline_no_recorder", "recorder_present_disabled", "recorder_enabled")

FIELDS = [
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

SUMMARY_FIELDS = [
    "workload_scale",
    "config",
    "median_cycle_overhead_pct",
    "mean_cycle_overhead_pct",
    "median_commit_overhead_pct",
    "mean_commit_overhead_pct",
    "median_sim_wall_time_overhead_pct",
    "mean_sim_wall_time_overhead_pct",
    "median_events",
    "median_capsule_bytes",
    "iqr_sim_wall_time_overhead_pct",
    "n",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    parser.add_argument("--timeout-sec", type=int, default=45)
    args = parser.parse_args()

    firmware_rows = generate_scaled_workloads._build_rows(args.mode)
    runtime_blocker = run_runtime_overhead._ensure_runtime_sims()
    rows = []
    for firmware_row in firmware_rows:
        for seed in _seeds(args.mode):
            case_rows = {config: _measure(firmware_row, seed, config, runtime_blocker, args.timeout_sec) for config in CONFIGS}
            _fill_overheads(case_rows)
            rows.extend(case_rows[config] for config in CONFIGS)
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(SUMMARY_CSV, SUMMARY_FIELDS, _summary(rows))
    print("WROTE results/processed/runtime_scaling.csv")
    print("WROTE results/processed/runtime_scaling_summary.csv")
    return 0


def _seeds(mode: str) -> tuple[int, ...]:
    return (1,) if mode == "quick" else (1, 2, 3, 4, 5)


def _measure(firmware_row: dict[str, str], seed: int, config: str, blocker: str | None, timeout_sec: int) -> dict[str, object]:
    base = {
        "benchmark": firmware_row["benchmark"],
        "variant": firmware_row["variant"],
        "seed": seed,
        "workload_scale": firmware_row["workload_scale"],
        "config": config,
        "firmware_source": firmware_row.get("firmware_source", "NA"),
        "compiler_backed": "true" if firmware_row.get("build_status") == "PASS" else "false",
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
        "notes": blocker or firmware_row.get("notes", "blocked"),
    }
    if firmware_row.get("build_status") != "PASS":
        return base
    if blocker:
        return base
    sim = run_runtime_overhead._sim_path(run_runtime_overhead.BASELINE_SIM if config == "baseline_no_recorder" else run_runtime_overhead.RECORDER_SIM)
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
        str(seed),
        "--max-cycles",
        firmware_row["max_cycles"],
    ]
    start = time.perf_counter()
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, env=run_runtime_overhead._tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout_sec)
        elapsed = time.perf_counter() - start
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {**base, "status": "TIMEOUT", "notes": f"runtime scaling timeout after {timeout_sec} seconds; {output.strip()[-120:]}"}
    parsed = _parse(completed.stdout)
    status = "MEASURED" if completed.returncode == 0 else "FAIL"
    return {
        **base,
        "cycles": parsed.get("cycles", "NA"),
        "commits": parsed.get("commits", "NA"),
        "events": parsed.get("events", "NA"),
        "capsule_bytes": parsed.get("capsule_bytes", "NA"),
        "sim_wall_time_sec": f"{elapsed:.6f}",
        "status": status,
        "notes": "measured same scaled firmware/stimulus" if status == "MEASURED" else _last_line(completed.stdout),
    }


def _fill_overheads(case_rows: dict[str, dict[str, object]]) -> None:
    baseline = case_rows["baseline_no_recorder"]
    for config in ("recorder_present_disabled", "recorder_enabled"):
        row = case_rows[config]
        if baseline["status"] != "MEASURED" or row["status"] != "MEASURED":
            continue
        row["cycle_overhead_pct"] = _pct(baseline["cycles"], row["cycles"])
        row["commit_overhead_pct"] = _pct(baseline["commits"], row["commits"])
        row["sim_wall_time_overhead_pct"] = _pct(baseline["sim_wall_time_sec"], row["sim_wall_time_sec"])


def _summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    keys = sorted({(str(row["workload_scale"]), str(row["config"])) for row in rows})
    for scale, config in keys:
        subset = [row for row in rows if row["workload_scale"] == scale and row["config"] == config and row["status"] == "MEASURED"]
        cycle = _values(subset, "cycle_overhead_pct")
        commit = _values(subset, "commit_overhead_pct")
        wall = _values(subset, "sim_wall_time_overhead_pct")
        events = _values(subset, "events")
        bytes_values = _values(subset, "capsule_bytes")
        out.append(
            {
                "workload_scale": scale,
                "config": config,
                "median_cycle_overhead_pct": _median(cycle),
                "mean_cycle_overhead_pct": _mean(cycle),
                "median_commit_overhead_pct": _median(commit),
                "mean_commit_overhead_pct": _mean(commit),
                "median_sim_wall_time_overhead_pct": _median(wall),
                "mean_sim_wall_time_overhead_pct": _mean(wall),
                "median_events": _median(events),
                "median_capsule_bytes": _median(bytes_values),
                "iqr_sim_wall_time_overhead_pct": _iqr(wall),
                "n": len(subset),
                "notes": "simulator wall time is not hardware runtime; cycle/commit overhead is architectural harness observation",
            }
        )
    return out


def _parse(text: str) -> dict[str, str]:
    out = {}
    line = _last_line(text)
    for key in ("events", "capsule_bytes", "cycles", "commits"):
        match = re.search(rf"\b{key}=([0-9]+)", line)
        if match:
            out[key] = match.group(1)
    return out


def _pct(baseline: object, value: object) -> str:
    b = safe_float(baseline)
    v = safe_float(value)
    if b is None or v is None or b == 0:
        return "NA"
    return f"{((v - b) / b * 100.0):.2f}"


def _values(rows: list[dict[str, object]], field: str) -> list[float]:
    return [value for value in (safe_float(row.get(field)) for row in rows) if value is not None]


def _median(values: list[float]) -> str:
    return f"{median(values):.6f}" if values else "NA"


def _mean(values: list[float]) -> str:
    return f"{mean(values):.6f}" if values else "NA"


def _iqr(values: list[float]) -> str:
    if not values:
        return "NA"
    ordered = sorted(values)
    return f"{(ordered[(len(ordered) * 3) // 4] - ordered[len(ordered) // 4]):.6f}"


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "no runtime output"


if __name__ == "__main__":
    raise SystemExit(main())
