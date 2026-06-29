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

WORKLOAD_BUFFER_DEPTHS = {
    "smoke": 256,
    "short": 256,
    "medium": 1024,
    "long": 4096,
    "stress": 16384,
}

COMPRESSED_WORKLOAD_BUFFER_DEPTHS = {
    "smoke": 256,
    "short": 256,
    "medium": 256,
    "long": 256,
    "stress": 256,
}

FIELDS = [
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "buffer_depth",
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
    "strict_replay_valid",
    "capsule_path",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    parser.add_argument("--timeout-sec", type=int, default=45)
    parser.add_argument("--arch", choices=("v1", "v2"), default="v1")
    parser.add_argument("--recorder-config", choices=("core", "hashed", "full"), default="core")
    parser.add_argument("--output", default=str(OUT_CSV), help="processed CSV to write")
    parser.add_argument("--raw-dir", default=str(RAW_DIR), help="raw output directory")
    parser.add_argument("--allow-overflow-pass", action="store_true", help="allow replay PASS even if the capsule overflow flag asserted")
    parser.add_argument(
        "--buffer-depth",
        type=int,
        default=None,
        help="use one fixed capsule buffer depth for every workload; default is workload-aware",
    )
    args = parser.parse_args()

    out_csv = _repo_path(args.output)
    raw_dir = _repo_path(args.raw_dir)
    capsule_dir = raw_dir / "capsules"
    signature_dir = raw_dir / "signatures"
    log_dir = raw_dir / "logs"

    for path in (capsule_dir, signature_dir, log_dir):
        path.mkdir(parents=True, exist_ok=True)
    firmware_rows = generate_scaled_workloads._build_rows(args.mode)
    write_csv(generate_scaled_workloads.OUT_CSV, generate_scaled_workloads.FIELDS, firmware_rows)

    rows: list[dict[str, object]] = []
    grouped: dict[int, list[dict[str, str]]] = {}
    for firmware_row in firmware_rows:
        depth = args.buffer_depth if args.buffer_depth is not None else _depth_for_scale(firmware_row["workload_scale"], args.arch)
        grouped.setdefault(depth, []).append(firmware_row)
    for depth, depth_rows in sorted(grouped.items()):
        with _capsule_depth(depth):
            simulator_blocker = run_full_rtl_replay._ensure_simulator()
            for firmware_row in depth_rows:
                for seed in _seeds(args.mode):
                    rows.append(
                        _run_case(
                            firmware_row,
                            seed,
                            args.timeout_sec,
                            simulator_blocker,
                            depth,
                            args.arch,
                            args.recorder_config,
                            capsule_dir,
                            signature_dir,
                            log_dir,
                            strict_overflow=not args.allow_overflow_pass,
                        )
                    )
    write_csv(out_csv, FIELDS, rows)
    strict_passes = sum(1 for row in rows if row["strict_replay_valid"] == "true")
    print(f"WROTE {rel(out_csv)}")
    print(f"WORKLOAD_SCALING rows={len(rows)} strict_pass={strict_passes}")
    return 0


def _seeds(mode: str) -> tuple[int, ...]:
    return (1,) if mode == "quick" else (1, 2, 3, 4, 5)


def _depth_for_scale(scale: str, arch: str) -> int:
    if arch == "v2":
        return COMPRESSED_WORKLOAD_BUFFER_DEPTHS.get(scale, 256)
    return WORKLOAD_BUFFER_DEPTHS.get(scale, 256)


class _capsule_depth:
    def __init__(self, depth: int):
        self.depth = str(depth)
        self.previous: str | None = None

    def __enter__(self) -> None:
        import os

        self.previous = os.environ.get("REPLAYCAPSULE_CAPSULE_DEPTH")
        os.environ["REPLAYCAPSULE_CAPSULE_DEPTH"] = self.depth

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        import os

        if self.previous is None:
            os.environ.pop("REPLAYCAPSULE_CAPSULE_DEPTH", None)
        else:
            os.environ["REPLAYCAPSULE_CAPSULE_DEPTH"] = self.previous


def _run_case(
    firmware_row: dict[str, str],
    seed: int,
    timeout_sec: int,
    simulator_blocker: str | None,
    buffer_depth: int,
    arch: str,
    recorder_config: str,
    capsule_dir: Path,
    signature_dir: Path,
    log_dir: Path,
    strict_overflow: bool,
) -> dict[str, object]:
    benchmark = firmware_row["benchmark"]
    variant = firmware_row["variant"]
    scale = firmware_row["workload_scale"]
    if firmware_row["build_status"] != "PASS":
        return _blocked_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, firmware_row["notes"])
    if simulator_blocker:
        return _blocked_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, simulator_blocker)

    prefix = "" if arch == "v1" else f"{arch}_{recorder_config}_"
    base = f"{prefix}{benchmark}_{variant}_seed{seed}_{scale}"
    capsule = capsule_dir / f"{base}.json"
    record_sig = signature_dir / f"{base}_record.json"
    replay_sig = signature_dir / f"{base}_replay.json"
    firmware = REPO_ROOT / firmware_row["hex_path"]
    max_cycles = firmware_row["max_cycles"]

    record = _run_sim("record", benchmark, variant, firmware, capsule, record_sig, seed, max_cycles, timeout_sec, arch, recorder_config)
    (log_dir / f"{base}_record.log").write_text(_clean(record.stdout), encoding="utf-8")
    if record.returncode == 124:
        return _timeout_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, "record timed out", record_sig, capsule)
    if record.returncode != 0:
        return _failed_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, "FAIL", "NA", _last_line(record.stdout), record_sig, capsule)

    replay = _run_sim("replay", benchmark, variant, firmware, capsule, replay_sig, seed, max_cycles, timeout_sec, arch, recorder_config)
    (log_dir / f"{base}_replay.log").write_text(_clean(replay.stdout), encoding="utf-8")
    if replay.returncode == 124:
        return _timeout_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, "replay timed out", record_sig, capsule)

    record_payload = read_json(record_sig)
    replay_payload = read_json(replay_sig)
    final_match = _match(record_payload.get("property_id"), replay_payload.get("property_id")) and _match(record_payload.get("property_signature"), replay_payload.get("property_signature"))
    event_match = replay.returncode == 0 and _match(record_payload.get("event_count"), replay_payload.get("event_count"))
    overflow = str(record_payload.get("overflow", "NA")).lower() == "true"
    strict_valid = replay.returncode == 0 and final_match and event_match and (not overflow or not strict_overflow)
    replay_status = "PASS" if strict_valid else "OVERFLOW" if overflow and strict_overflow else "FAIL"
    notes = _last_line(replay.stdout) if replay_status != "PASS" else "record/replay complete"
    if replay_status == "OVERFLOW":
        notes = "capsule overflow invalidates strict replay availability"
    return _measured_row(
        benchmark,
        variant,
        seed,
        scale,
        buffer_depth,
        arch,
        recorder_config,
        replay_status,
        "PASS" if final_match else "FAIL",
        "PASS" if event_match else "FAIL",
        notes,
        record_payload,
        capsule,
        strict_valid,
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
    arch: str,
    recorder_config: str,
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
        "--arch",
        arch,
        "--recorder-config",
        recorder_config,
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
    buffer_depth: int,
    arch: str,
    recorder_config: str,
    replay_status: str,
    final_match: str,
    event_match: str,
    notes: str,
    payload: dict[str, object],
    capsule: Path | None,
    strict_valid: bool,
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
        "architecture": arch,
        "recorder_config": recorder_config,
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
        "buffer_depth": buffer_depth,
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
        "strict_replay_valid": str(strict_valid).lower(),
        "capsule_path": rel(capsule) if capsule else "NA",
        "notes": notes,
    }


def _blocked_row(benchmark: str, variant: str, seed: int, scale: str, buffer_depth: int, arch: str, recorder_config: str, notes: str) -> dict[str, object]:
    return _empty_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, "BLOCKED", notes)


def _timeout_row(benchmark: str, variant: str, seed: int, scale: str, buffer_depth: int, arch: str, recorder_config: str, notes: str, signature: Path, capsule: Path) -> dict[str, object]:
    payload = read_json(signature)
    if payload:
        return _measured_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, "TIMEOUT", "NA", "NA", notes, payload, capsule, False)
    return _empty_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, "TIMEOUT", notes)


def _failed_row(benchmark: str, variant: str, seed: int, scale: str, buffer_depth: int, arch: str, recorder_config: str, replay_status: str, final_match: str, notes: str, signature: Path, capsule: Path) -> dict[str, object]:
    payload = read_json(signature)
    if payload:
        return _measured_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, replay_status, final_match, "FAIL", notes, payload, capsule, False)
    return _empty_row(benchmark, variant, seed, scale, buffer_depth, arch, recorder_config, replay_status, notes)


def _empty_row(benchmark: str, variant: str, seed: int, scale: str, buffer_depth: int, arch: str, recorder_config: str, status: str, notes: str) -> dict[str, object]:
    return {
        "architecture": arch,
        "recorder_config": recorder_config,
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
        "buffer_depth": buffer_depth,
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
        "strict_replay_valid": "false",
        "capsule_path": "NA",
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


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


if __name__ == "__main__":
    raise SystemExit(main())
