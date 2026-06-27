#!/usr/bin/env python3
"""Run compiler-backed workload scaling through the RTL record/replay harness."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import generate_scaled_workloads
import run_full_rtl_replay
from topconf_eval_common import REPO_ROOT, read_json, rel, safe_float, write_csv


OUT_CSV = REPO_ROOT / "results/processed/workload_scaling.csv"
RAW_DIR = REPO_ROOT / "results/raw/workload_scaling"
CAPSULE_DIR = RAW_DIR / "capsules"
SIGNATURE_DIR = RAW_DIR / "signatures"
LOG_DIR = RAW_DIR / "logs"

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    parser.add_argument("--timeout-sec", type=int, default=45)
    args = parser.parse_args()

    for path in (CAPSULE_DIR, SIGNATURE_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)
    firmware_rows = generate_scaled_workloads._build_rows(args.mode)
    write_csv(generate_scaled_workloads.OUT_CSV, generate_scaled_workloads.FIELDS, firmware_rows)
    simulator_blocker = run_full_rtl_replay._ensure_simulator()

    rows: list[dict[str, object]] = []
    for firmware_row in firmware_rows:
        for seed in _seeds(args.mode):
            rows.append(_run_case(firmware_row, seed, args.timeout_sec, simulator_blocker))
    write_csv(OUT_CSV, FIELDS, rows)
    print(f"WROTE {rel(OUT_CSV)}")
    print(f"WORKLOAD_SCALING rows={len(rows)} pass={sum(1 for row in rows if row['replay_status'] == 'PASS')}")
    return 0


def _seeds(mode: str) -> tuple[int, ...]:
    return (1,) if mode == "quick" else (1, 2, 3, 4, 5)


def _run_case(firmware_row: dict[str, str], seed: int, timeout_sec: int, simulator_blocker: str | None) -> dict[str, object]:
    benchmark = firmware_row["benchmark"]
    variant = firmware_row["variant"]
    scale = firmware_row["workload_scale"]
    if firmware_row["build_status"] != "PASS":
        return _blocked_row(benchmark, variant, seed, scale, firmware_row["notes"])
    if simulator_blocker:
        return _blocked_row(benchmark, variant, seed, scale, simulator_blocker)

    base = f"{benchmark}_{variant}_seed{seed}_{scale}"
    capsule = CAPSULE_DIR / f"{base}.json"
    record_sig = SIGNATURE_DIR / f"{base}_record.json"
    replay_sig = SIGNATURE_DIR / f"{base}_replay.json"
    firmware = REPO_ROOT / firmware_row["hex_path"]
    max_cycles = firmware_row["max_cycles"]

    record = _run_sim("record", benchmark, variant, firmware, capsule, record_sig, seed, max_cycles, timeout_sec)
    (LOG_DIR / f"{base}_record.log").write_text(_clean(record.stdout), encoding="utf-8")
    if record.returncode == 124:
        return _timeout_row(benchmark, variant, seed, scale, "record timed out", record_sig)
    if record.returncode != 0:
        return _failed_row(benchmark, variant, seed, scale, "FAIL", "NA", _last_line(record.stdout), record_sig)

    replay = _run_sim("replay", benchmark, variant, firmware, capsule, replay_sig, seed, max_cycles, timeout_sec)
    (LOG_DIR / f"{base}_replay.log").write_text(_clean(replay.stdout), encoding="utf-8")
    if replay.returncode == 124:
        return _timeout_row(benchmark, variant, seed, scale, "replay timed out", record_sig)

    record_payload = read_json(record_sig)
    replay_payload = read_json(replay_sig)
    final_match = _match(record_payload.get("property_id"), replay_payload.get("property_id")) and _match(record_payload.get("property_signature"), replay_payload.get("property_signature"))
    event_match = replay.returncode == 0 and _match(record_payload.get("event_count"), replay_payload.get("event_count"))
    replay_status = "PASS" if replay.returncode == 0 and final_match and event_match else "FAIL"
    return _measured_row(
        benchmark,
        variant,
        seed,
        scale,
        replay_status,
        "PASS" if final_match else "FAIL",
        "PASS" if event_match else "FAIL",
        _last_line(replay.stdout) if replay_status != "PASS" else "record/replay complete",
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
        rel(firmware),
        "--capsule",
        rel(capsule),
        "--signature",
        rel(signature),
        "--seed",
        str(seed),
        "--max-cycles",
        str(max_cycles),
    ]
    try:
        return subprocess.run(command, cwd=REPO_ROOT, env=run_full_rtl_replay._tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(command, 124, output + f"\nTIMEOUT after {timeout_sec} seconds\n")


def _measured_row(
    benchmark: str,
    variant: str,
    seed: int,
    scale: str,
    replay_status: str,
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
    failure_seen = property_id not in ("0", "NA", "")
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
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
        "replay_status": replay_status,
        "final_signature_match": final_match,
        "event_match": event_match,
        "overflow": str(payload.get("overflow", "NA")).lower(),
        "notes": notes,
    }


def _blocked_row(benchmark: str, variant: str, seed: int, scale: str, notes: str) -> dict[str, object]:
    return _empty_row(benchmark, variant, seed, scale, "BLOCKED", notes)


def _timeout_row(benchmark: str, variant: str, seed: int, scale: str, notes: str, signature: Path) -> dict[str, object]:
    payload = read_json(signature)
    if payload:
        return _measured_row(benchmark, variant, seed, scale, "TIMEOUT", "NA", "NA", notes, payload)
    return _empty_row(benchmark, variant, seed, scale, "TIMEOUT", notes)


def _failed_row(benchmark: str, variant: str, seed: int, scale: str, replay_status: str, final_match: str, notes: str, signature: Path) -> dict[str, object]:
    payload = read_json(signature)
    if payload:
        return _measured_row(benchmark, variant, seed, scale, replay_status, final_match, "FAIL", notes, payload)
    return _empty_row(benchmark, variant, seed, scale, replay_status, notes)


def _empty_row(benchmark: str, variant: str, seed: int, scale: str, status: str, notes: str) -> dict[str, object]:
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
        "firmware_source": "compiler_required",
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
        "notes": notes,
    }


def _match(left: object, right: object) -> bool:
    return str(left) == str(right)


def _last_line(text: str) -> str:
    lines = [line.strip() for line in _clean(text).splitlines() if line.strip()]
    return lines[-1] if lines else "no simulator output"


def _clean(text: str) -> str:
    cleaned = text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")
    cleaned = cleaned.replace(str(Path.home()), ".").replace(str(Path.home()).replace("\\", "/"), ".")
    return cleaned


if __name__ == "__main__":
    raise SystemExit(main())
