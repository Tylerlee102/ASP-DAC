#!/usr/bin/env python3
"""Run replay/runtime summaries across recorder capture configurations."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import generate_scaled_workloads
import run_full_rtl_replay
import run_runtime_overhead
from topconf_eval_common import RECORDER_CONFIGS, REPO_ROOT, read_csv, read_json, rel, safe_float, write_csv


REPLAY_CSV = REPO_ROOT / "results/processed/recorder_config_replay.csv"
RUNTIME_CSV = REPO_ROOT / "results/processed/recorder_config_runtime.csv"
MAPPED_CSV = REPO_ROOT / "results/processed/recorder_config_mapped.csv"
RAW_DIR = REPO_ROOT / "results/raw/recorder_config"

REPLAY_FIELDS = [
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "replay_status",
    "negative_replay_status",
    "event_match",
    "final_signature_match",
    "capsule_bytes",
    "events",
    "notes",
]

RUNTIME_FIELDS = [
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "cycles",
    "commits",
    "sim_wall_time_sec",
    "cycle_overhead_pct",
    "commit_overhead_pct",
    "sim_wall_time_overhead_pct",
    "notes",
]

MAPPED_FIELDS = [
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
    "fmax_mhz",
    "status",
    "report_path",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    parser.add_argument("--timeout-sec", type=int, default=35)
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    firmware_rows = [row for row in generate_scaled_workloads._build_rows(args.mode) if row.get("build_status") == "PASS"]
    replay_blocker = run_full_rtl_replay._ensure_simulator()
    runtime_blocker = run_runtime_overhead._ensure_runtime_sims()

    replay_rows = []
    runtime_rows = []
    for firmware_row in firmware_rows:
        for seed in _seeds(args.mode):
            baseline = _runtime_baseline(firmware_row, seed, runtime_blocker, args.timeout_sec)
            for config in RECORDER_CONFIGS:
                replay_rows.append(_replay_config(firmware_row, seed, config, replay_blocker, args.timeout_sec))
                runtime_rows.append(_runtime_config(firmware_row, seed, config, baseline, runtime_blocker, args.timeout_sec))
    write_csv(REPLAY_CSV, REPLAY_FIELDS, replay_rows)
    write_csv(RUNTIME_CSV, RUNTIME_FIELDS, runtime_rows)
    write_csv(MAPPED_CSV, MAPPED_FIELDS, _mapped_rows())
    print("WROTE results/processed/recorder_config_replay.csv")
    print("WROTE results/processed/recorder_config_runtime.csv")
    print("WROTE results/processed/recorder_config_mapped.csv")
    return 0


def _seeds(mode: str) -> tuple[int, ...]:
    return (1,) if mode == "quick" else (1, 2, 3, 4, 5)


def _replay_config(firmware_row: dict[str, str], seed: int, config: str, blocker: str | None, timeout_sec: int) -> dict[str, object]:
    base = f"{firmware_row['benchmark']}_{firmware_row['variant']}_seed{seed}_{firmware_row['workload_scale']}_{config}"
    capsule = RAW_DIR / f"{base}.json"
    record_sig = RAW_DIR / f"{base}_record_signature.json"
    replay_sig = RAW_DIR / f"{base}_replay_signature.json"
    if blocker:
        return _replay_row(config, firmware_row, seed, "BLOCKED", "NA", "NA", "NA", "NA", "NA", blocker)
    record = _rtl_run("record", firmware_row, seed, config, capsule, record_sig, timeout_sec)
    if record.returncode != 0:
        return _replay_row(config, firmware_row, seed, "TIMEOUT" if record.returncode == 124 else "FAIL", "NA", "NA", "NA", "NA", "NA", _last_line(record.stdout))
    replay = _rtl_run("replay", firmware_row, seed, config, capsule, replay_sig, timeout_sec)
    record_payload = read_json(record_sig)
    replay_payload = read_json(replay_sig)
    final_match = str(record_payload.get("property_signature")) == str(replay_payload.get("property_signature")) and str(record_payload.get("property_id")) == str(replay_payload.get("property_id"))
    event_match = replay.returncode == 0 and str(record_payload.get("event_count")) == str(replay_payload.get("event_count"))
    status = "PASS" if replay.returncode == 0 and final_match and event_match else "FAIL"
    negative = _negative_payload_check(firmware_row, seed, config, capsule, timeout_sec)
    return _replay_row(
        config,
        firmware_row,
        seed,
        status,
        negative,
        "PASS" if event_match else "FAIL",
        "PASS" if final_match else "FAIL",
        record_payload.get("capsule_bytes", "NA"),
        record_payload.get("event_count", "NA"),
        RECORDER_CONFIGS[config]["notes"],
    )


def _rtl_run(mode: str, firmware_row: dict[str, str], seed: int, config: str, capsule: Path, signature: Path, timeout_sec: int) -> subprocess.CompletedProcess[str]:
    command = [
        str(run_full_rtl_replay._sim_path()),
        "--mode",
        mode,
        "--benchmark",
        firmware_row["benchmark"],
        "--variant",
        firmware_row["variant"],
        "--firmware",
        firmware_row["hex_path"],
        "--capsule",
        rel(capsule),
        "--signature",
        rel(signature),
        "--seed",
        str(seed),
        "--max-cycles",
        firmware_row["max_cycles"],
        "--capture-mode",
        str(RECORDER_CONFIGS[config]["capture_mode"]),
    ]
    try:
        return subprocess.run(command, cwd=REPO_ROOT, env=run_full_rtl_replay._tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(command, 124, output + f"\nTIMEOUT after {timeout_sec} seconds\n")


def _negative_payload_check(firmware_row: dict[str, str], seed: int, config: str, capsule: Path, timeout_sec: int) -> str:
    payload = read_json(capsule)
    events = payload.get("events", [])
    if not isinstance(events, list) or not events:
        return "NA"
    events[0]["payload_hash"] = "0x00000000" if events[0].get("payload_hash") != "0x00000000" else "0x00000001"
    corrupt = capsule.with_name(capsule.stem + "_payload_corrupt.json")
    signature = capsule.with_name(capsule.stem + "_payload_corrupt_signature.json")
    corrupt.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    replay = _rtl_run("replay", firmware_row, seed, config, corrupt, signature, timeout_sec)
    return "REJECT" if replay.returncode != 0 else "UNEXPECTED_ACCEPT"


def _runtime_baseline(firmware_row: dict[str, str], seed: int, blocker: str | None, timeout_sec: int) -> dict[str, object]:
    if blocker:
        return {"status": "BLOCKED", "notes": blocker}
    return _runtime_run(firmware_row, seed, "baseline_no_recorder", None, timeout_sec)


def _runtime_config(
    firmware_row: dict[str, str],
    seed: int,
    config: str,
    baseline: dict[str, object],
    blocker: str | None,
    timeout_sec: int,
) -> dict[str, object]:
    if blocker:
        return _runtime_row(config, firmware_row, seed, "NA", "NA", "NA", "NA", "NA", "NA", blocker)
    measured = _runtime_run(firmware_row, seed, "recorder_enabled", config, timeout_sec)
    return _runtime_row(
        config,
        firmware_row,
        seed,
        measured.get("cycles", "NA"),
        measured.get("commits", "NA"),
        measured.get("sim_wall_time_sec", "NA"),
        _pct(baseline.get("cycles"), measured.get("cycles")),
        _pct(baseline.get("commits"), measured.get("commits")),
        _pct(baseline.get("sim_wall_time_sec"), measured.get("sim_wall_time_sec")),
        measured.get("notes", "measured"),
    )


def _runtime_run(firmware_row: dict[str, str], seed: int, harness_config: str, recorder_config: str | None, timeout_sec: int) -> dict[str, object]:
    sim = run_runtime_overhead._sim_path(run_runtime_overhead.BASELINE_SIM if harness_config == "baseline_no_recorder" else run_runtime_overhead.RECORDER_SIM)
    command = [
        str(sim),
        "--config",
        harness_config,
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
    if recorder_config is not None:
        command.extend(["--capture-mode", str(RECORDER_CONFIGS[recorder_config]["capture_mode"])])
    start = time.perf_counter()
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, env=run_runtime_overhead._tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout_sec)
        elapsed = time.perf_counter() - start
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "notes": f"runtime timeout after {timeout_sec} seconds"}
    parsed = _parse_runtime(completed.stdout)
    return {**parsed, "sim_wall_time_sec": f"{elapsed:.6f}", "status": "MEASURED" if completed.returncode == 0 else "FAIL", "notes": _last_line(completed.stdout)}


def _mapped_rows() -> list[dict[str, object]]:
    mapped = read_csv(REPO_ROOT / "results/processed/mapped_scaling.csv")
    if not mapped:
        return [
            {
                "recorder_config": config,
                "target": "NA",
                "flow": "NA",
                "design": "full_core_replaycapsule_board",
                "memory_words": "NA",
                "buffer_depth": "NA",
                "lut": "NA",
                "ff": "NA",
                "bram": "NA",
                "dsp": "NA",
                "fmax_mhz": "NA",
                "status": "BLOCKED",
                "report_path": "NA",
                "notes": "mapped_scaling.csv not generated",
            }
            for config in RECORDER_CONFIGS
        ]
    return [
        {
            "recorder_config": row.get("recorder_config", "NA"),
            "target": row.get("target", "NA"),
            "flow": row.get("flow", "NA"),
            "design": row.get("design", "NA"),
            "memory_words": row.get("memory_words", "NA"),
            "buffer_depth": row.get("buffer_depth", "NA"),
            "lut": row.get("lut", "NA"),
            "ff": row.get("ff", "NA"),
            "bram": row.get("bram", "NA"),
            "dsp": row.get("dsp", "NA"),
            "fmax_mhz": row.get("fmax_mhz", "NA"),
            "status": row.get("status", "NA"),
            "report_path": row.get("report_path", "NA"),
            "notes": row.get("notes", "NA"),
        }
        for row in mapped
    ]


def _replay_row(config: str, firmware_row: dict[str, str], seed: int, status: object, negative: object, event_match: object, final_match: object, bytes_value: object, events: object, notes: str) -> dict[str, object]:
    return {
        "recorder_config": config,
        "benchmark": firmware_row["benchmark"],
        "variant": firmware_row["variant"],
        "seed": seed,
        "workload_scale": firmware_row["workload_scale"],
        "replay_status": status,
        "negative_replay_status": negative,
        "event_match": event_match,
        "final_signature_match": final_match,
        "capsule_bytes": bytes_value,
        "events": events,
        "notes": notes,
    }


def _runtime_row(config: str, firmware_row: dict[str, str], seed: int, cycles: object, commits: object, wall: object, cycle_overhead: object, commit_overhead: object, wall_overhead: object, notes: str) -> dict[str, object]:
    return {
        "recorder_config": config,
        "benchmark": firmware_row["benchmark"],
        "variant": firmware_row["variant"],
        "seed": seed,
        "workload_scale": firmware_row["workload_scale"],
        "cycles": cycles,
        "commits": commits,
        "sim_wall_time_sec": wall,
        "cycle_overhead_pct": cycle_overhead,
        "commit_overhead_pct": commit_overhead,
        "sim_wall_time_overhead_pct": wall_overhead,
        "notes": notes,
    }


def _parse_runtime(text: str) -> dict[str, str]:
    out = {}
    line = _last_line(text)
    for token in line.split():
        if "=" in token:
            key, value = token.split("=", 1)
            if key in {"cycles", "commits", "events", "capsule_bytes"}:
                out[key] = value.strip('"')
    return out


def _pct(baseline: object, value: object) -> str:
    b = safe_float(baseline)
    v = safe_float(value)
    if b is None or v is None or b == 0:
        return "NA"
    return f"{((v - b) / b * 100.0):.2f}"


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "no output"


if __name__ == "__main__":
    raise SystemExit(main())
