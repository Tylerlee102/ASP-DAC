#!/usr/bin/env python3
"""Run v2 same-instance replay from the RTL captured capsule store."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import run_full_rtl_replay as full


REPO_ROOT = Path(os.environ.get("REPLAYCAPSULE_REPO_ROOT", Path(__file__).resolve().parents[1]))
OUT_CSV = REPO_ROOT / "results/processed/self_replay_handoff_v2.csv"
RAW_DIR = REPO_ROOT / "results/raw/self_replay_handoff"
CAPSULE_DIR = REPO_ROOT / "results/raw/self_replay_handoff/capsules"
SIGNATURE_DIR = REPO_ROOT / "results/raw/self_replay_handoff/signatures"

BASE_BENCHMARKS = (
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
)
EXPANDED_BENCHMARKS = (
    "commanded_actuator_limit_bug",
    "late_config_sequence_bug",
    "sensor_debounce_bug",
    "status_clear_on_read_bug",
    "platform2_status_window_bug",
    "platform2_config_order_bug",
    "environmental_controller_bug",
    "power_rail_sequencer_bug",
)
VARIANTS = {
    "sensor_threshold_bug": ("failing", "fixed", "no_failure_edge"),
    "interrupt_race_bug": ("failing", "fixed"),
    "mmio_ordering_bug": ("failing", "fixed"),
    "stack_corruption_bug": ("failing", "fixed"),
    "uart_command_bug": ("failing", "fixed", "no_failure_edge"),
    "watchdog_timeout_bug": ("failing", "fixed", "no_failure_edge"),
    "commanded_actuator_limit_bug": ("failing", "fixed"),
    "late_config_sequence_bug": ("failing", "fixed"),
    "sensor_debounce_bug": ("failing", "fixed"),
    "status_clear_on_read_bug": ("failing", "fixed"),
    "platform2_status_window_bug": ("failing", "fixed"),
    "platform2_config_order_bug": ("failing", "fixed"),
    "environmental_controller_bug": ("failing", "fixed"),
    "power_rail_sequencer_bug": ("failing", "fixed"),
}
CONFIGS = ("core", "hashed", "full")
FIELDS = [
    "architecture",
    "recorder_config",
    "benchmark",
    "variant",
    "seed",
    "firmware_source",
    "compiler_backed",
    "firmware_sha256",
    "self_replay_status",
    "capsule_export_status",
    "property_id",
    "event_match",
    "final_signature_match",
    "capsule_bytes",
    "cycles_to_failure",
    "commits_to_failure",
    "overflow",
    "replay_consumer_status",
    "replay_consumer_checked",
    "replay_consumer_consumed",
    "replay_consumer_expected",
    "replay_consumer_error_code",
    "replay_stimulus_source",
    "stream_event_count",
    "stream_event_sent_count",
    "replay_critical_event_count",
    "stream_stall_count",
    "dropped_diagnostic_count",
    "replay_critical_overflow_count",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-expanded", action="store_true", help="also run the expanded benchmark families")
    parser.add_argument("--quick", action="store_true", help="run only failing seed 1 rows")
    parser.add_argument("--benchmark", choices=BASE_BENCHMARKS + EXPANDED_BENCHMARKS)
    parser.add_argument("--variant")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--recorder-config", choices=CONFIGS)
    parser.add_argument("--max-cycles", type=int, default=100000)
    args = parser.parse_args()
    if args.variant and not args.benchmark:
        parser.error("--variant requires --benchmark")
    if args.benchmark and args.variant not in (None, *VARIANTS[args.benchmark]):
        parser.error(f"{args.variant} is not a known variant for {args.benchmark}")

    blocker = full._ensure_simulator()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    SIGNATURE_DIR.mkdir(parents=True, exist_ok=True)

    benchmarks = [args.benchmark] if args.benchmark else list(BASE_BENCHMARKS)
    if args.include_expanded and not args.benchmark:
        benchmarks.extend(EXPANDED_BENCHMARKS)
    configs = [args.recorder_config] if args.recorder_config else list(CONFIGS)
    seeds = [args.seed] if args.seed is not None else [1] if args.quick else [1, 2, 3]

    rows: list[dict[str, str]] = []
    if blocker:
        for config in configs:
            for benchmark in benchmarks:
                variants = [args.variant] if args.variant else ["failing"] if args.quick else list(VARIANTS[benchmark])
                for variant in variants:
                    for seed in seeds:
                        rows.append(_blocked_row(config, benchmark, variant, seed, blocker))
        _write_rows(rows)
        print(f"WROTE {full._rel(OUT_CSV)}")
        print(f"SELF_REPLAY_HANDOFF rows={len(rows)} bad={len(rows)} blocker={blocker}")
        return 1

    failures = 0
    for config in configs:
      for benchmark in benchmarks:
        variants = [args.variant] if args.variant else ["failing"] if args.quick else list(VARIANTS[benchmark])
        for variant in variants:
          for seed in seeds:
            row = _run_case(config, benchmark, variant, seed, args.max_cycles)
            if row["self_replay_status"] != "PASS":
                failures += 1
            rows.append(row)

    _write_rows(rows)
    bad = [row for row in rows if row["self_replay_status"] != "PASS" or row["replay_consumer_status"] != "PASS"]
    print(f"WROTE {full._rel(OUT_CSV)}")
    print(f"SELF_REPLAY_HANDOFF rows={len(rows)} bad={len(bad)} command_failures={failures}")
    return 1 if bad or failures else 0


def _run_case(config: str, benchmark: str, variant: str, seed: int, max_cycles: int) -> dict[str, str]:
    firmware = _firmware_path(benchmark, variant)
    base = f"self_{config}_{benchmark}_{variant}_seed{seed}"
    capsule = CAPSULE_DIR / f"{base}.json"
    signature = SIGNATURE_DIR / f"{base}.json"
    log = RAW_DIR / f"{base}.log"
    firmware_meta = _firmware_meta(firmware)
    if not firmware.exists():
        row = _blocked_row(config, benchmark, variant, seed, f"missing firmware {full._rel(firmware)}")
        row.update(firmware_meta)
        return row

    command = [
        str(full._sim_path()),
        "--mode",
        "self_replay",
        "--benchmark",
        benchmark,
        "--variant",
        variant,
        "--firmware",
        full._rel(firmware),
        "--capsule",
        full._rel(capsule),
        "--signature",
        full._rel(signature),
        "--seed",
        str(seed),
        "--max-cycles",
        str(max_cycles),
        "--arch",
        "v2",
        "--recorder-config",
        config,
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=full._tool_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text(full._clean(completed.stdout), encoding="utf-8")
    payload = _read_json(signature)
    replay_ok = payload.get("replay_ok") is True
    consumer_ok = payload.get("replay_consumer_ok") is True
    source = str(payload.get("replay_stimulus_source", "NA"))
    status = (
        "PASS"
        if completed.returncode == 0
        and replay_ok
        and consumer_ok
        and source == "rtl_replay_mode_controller_capture_store_mmio_irq"
        else "FAIL"
    )
    notes = str(payload.get("notes") or (completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else "no simulator output"))
    return {
        "architecture": "v2",
        "recorder_config": config,
        "benchmark": benchmark,
        "variant": variant,
        "seed": str(seed),
        **firmware_meta,
        "self_replay_status": status,
        "capsule_export_status": "PASS" if capsule.exists() else "FAIL",
        "property_id": str(payload.get("property_id", "NA")),
        "event_match": "PASS" if "record/replay replay-critical events match" in notes else "FAIL",
        "final_signature_match": "PASS" if replay_ok else "FAIL",
        "capsule_bytes": str(payload.get("capsule_bytes", "NA")),
        "cycles_to_failure": str(payload.get("cycles_to_failure", "NA")),
        "commits_to_failure": str(payload.get("commits_to_failure", "NA")),
        "overflow": _csv_bool(payload.get("overflow", "NA")),
        "replay_consumer_status": "PASS" if consumer_ok else "FAIL",
        "replay_consumer_checked": _csv_bool(payload.get("replay_consumer_checked", "NA")),
        "replay_consumer_consumed": str(payload.get("replay_consumer_consumed", "NA")),
        "replay_consumer_expected": str(payload.get("replay_consumer_expected", "NA")),
        "replay_consumer_error_code": str(payload.get("replay_consumer_error_code", "NA")),
        "replay_stimulus_source": source,
        "stream_event_count": str(payload.get("stream_event_count", "NA")),
        "stream_event_sent_count": str(payload.get("stream_event_sent_count", "NA")),
        "replay_critical_event_count": str(payload.get("replay_critical_event_count", "NA")),
        "stream_stall_count": str(payload.get("stream_stall_count", "NA")),
        "dropped_diagnostic_count": str(payload.get("dropped_diagnostic_count", "NA")),
        "replay_critical_overflow_count": str(payload.get("replay_critical_overflow_count", "NA")),
        "notes": full._clean(notes),
    }


def _firmware_path(benchmark: str, variant: str) -> Path:
    root = REPO_ROOT / ("firmware/build_expanded" if benchmark in EXPANDED_BENCHMARKS else "firmware/build")
    return root / benchmark / f"{variant}.hex"


def _firmware_meta(path: Path) -> dict[str, str]:
    return {
        "firmware_source": "compiler_c" if path.exists() else "missing",
        "compiler_backed": "true" if path.exists() else "false",
        "firmware_sha256": full._sha256(path) if path.exists() else "NA",
    }


def _blocked_row(config: str, benchmark: str, variant: str, seed: int, notes: str) -> dict[str, str]:
    return {
        "architecture": "v2",
        "recorder_config": config,
        "benchmark": benchmark,
        "variant": variant,
        "seed": str(seed),
        "firmware_source": "NA",
        "compiler_backed": "false",
        "firmware_sha256": "NA",
        "self_replay_status": "BLOCKED",
        "capsule_export_status": "NA",
        "property_id": "NA",
        "event_match": "NA",
        "final_signature_match": "NA",
        "capsule_bytes": "NA",
        "cycles_to_failure": "NA",
        "commits_to_failure": "NA",
        "overflow": "NA",
        "replay_consumer_status": "NA",
        "replay_consumer_checked": "false",
        "replay_consumer_consumed": "NA",
        "replay_consumer_expected": "NA",
        "replay_consumer_error_code": "NA",
        "replay_stimulus_source": "rtl_replay_mode_controller_capture_store_mmio_irq",
        "stream_event_count": "NA",
        "stream_event_sent_count": "NA",
        "replay_critical_event_count": "NA",
        "stream_stall_count": "NA",
        "dropped_diagnostic_count": "NA",
        "replay_critical_overflow_count": "NA",
        "notes": notes,
    }


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _csv_bool(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _write_rows(rows: list[dict[str, str]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
