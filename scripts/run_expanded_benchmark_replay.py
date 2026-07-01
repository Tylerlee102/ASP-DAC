#!/usr/bin/env python3
"""Run compiler-backed v2 replay for opt-in expanded benchmark families."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/expanded_benchmark_replay_measured.csv"
FIRMWARE_CSV = REPO_ROOT / "results/processed/expanded_firmware_build.csv"
BUILD_ROOT = REPO_ROOT / "firmware/build_expanded"
RAW_DIR = REPO_ROOT / "results/raw/expanded_benchmark_replay"
DEBUG_DIR = REPO_ROOT / "results/debug/expanded_benchmark_v2"

BENCHMARKS = (
    "commanded_actuator_limit_bug",
    "late_config_sequence_bug",
    "sensor_debounce_bug",
    "status_clear_on_read_bug",
    "platform2_status_window_bug",
    "platform2_config_order_bug",
    "environmental_controller_bug",
    "power_rail_sequencer_bug",
)
VARIANTS = ("failing", "fixed")
CONFIGS = ("core", "hashed", "full")
SEEDS = (1, 2, 3)


def main() -> int:
    env = dict(os.environ)
    env["REPLAYCAPSULE_ENABLE_EXPANDED_BENCHMARKS"] = "1"
    env["REPLAYCAPSULE_FIRMWARE_BUILD_CSV"] = str(FIRMWARE_CSV)
    env["REPLAYCAPSULE_FIRMWARE_BUILD_ROOT"] = str(BUILD_ROOT)
    env["REPLAYCAPSULE_FULL_RTL_REPLAY_CSV_V2"] = str(OUT_CSV)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_CSV.exists():
        OUT_CSV.unlink()

    build = _run([sys.executable, "scripts/build_firmware.py", "--require-compiler"], env, RAW_DIR / "build_firmware.log")
    if build.returncode != 0:
        print("FAIL: expanded benchmark firmware build did not pass compiler gate")
        return 1

    failures = 0
    for config in CONFIGS:
        for benchmark in BENCHMARKS:
            for variant in VARIANTS:
                for seed in SEEDS:
                    log = RAW_DIR / f"{config}_{benchmark}_{variant}_seed{seed}.log"
                    result = _run(
                        [
                            sys.executable,
                            "scripts/run_full_rtl_replay.py",
                            "--arch",
                            "v2",
                            "--recorder-config",
                            config,
                            "--benchmark",
                            benchmark,
                            "--variant",
                            variant,
                            "--seed",
                            str(seed),
                            "--max-cycles",
                            "100000",
                            "--debug-dir",
                            str(DEBUG_DIR / config),
                        ],
                        env,
                        log,
                    )
                    if result.returncode != 0:
                        failures += 1

    rows = _read_rows(OUT_CSV)
    bad_rows = [
        row
        for row in rows
        if row.get("replay_status") != "PASS"
        or row.get("compiler_backed") != "true"
        or row.get("rtl_record_status") != "PASS"
        or row.get("capsule_export_status") != "PASS"
        or row.get("replay_consumer_status") != "PASS"
    ]
    expected_rows = len(BENCHMARKS) * len(VARIANTS) * len(CONFIGS) * len(SEEDS)
    pass_benchmarks = {row.get("benchmark") for row in rows if row.get("replay_status") == "PASS"}
    pass_seeds = {row.get("seed") for row in rows if row.get("replay_status") == "PASS"}
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"EXPANDED_BENCHMARK_ROWS total={len(rows)} bad={len(bad_rows)} command_failures={failures}")
    return 1 if failures or bad_rows or len(rows) < expected_rows or len(pass_benchmarks) < len(BENCHMARKS) or len(pass_seeds) < len(SEEDS) else 0


def _run(command: list[str], env: dict[str, str], log_path: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(_clean(completed.stdout), encoding="utf-8")
    return completed


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _clean(text: str) -> str:
    cleaned = text
    for value in {str(REPO_ROOT), str(REPO_ROOT).replace("\\", "/"), str(Path.home()), str(Path.home()).replace("\\", "/")}:
        cleaned = cleaned.replace(value, "<REDACTED_PATH>")
    return cleaned


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
