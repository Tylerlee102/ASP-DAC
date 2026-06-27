#!/usr/bin/env python3
"""Shared definitions for ReplayCapsule-RV top-conference evaluation scripts."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import mean, median


REPO_ROOT = Path(__file__).resolve().parents[1]

BENCHMARKS = (
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
)

VARIANTS = {
    "sensor_threshold_bug": ("failing", "fixed", "no_failure_edge"),
    "interrupt_race_bug": ("failing", "fixed"),
    "mmio_ordering_bug": ("failing", "fixed"),
    "stack_corruption_bug": ("failing", "fixed"),
    "uart_command_bug": ("failing", "fixed", "no_failure_edge"),
    "watchdog_timeout_bug": ("failing", "fixed", "no_failure_edge"),
}

SEEDS = (1, 2, 3, 4, 5)
QUICK_SEEDS = (1,)

WORKLOAD_SCALES = {
    "smoke": {"delay_iters": 0, "max_cycles": 5_000, "notes": "default firmware-length smoke stimulus"},
    "short": {"delay_iters": 64, "max_cycles": 10_000, "notes": "small deterministic pre-trigger delay"},
    "medium": {"delay_iters": 256, "max_cycles": 50_000, "notes": "medium deterministic pre-trigger delay"},
    "long": {"delay_iters": 1024, "max_cycles": 100_000, "notes": "long deterministic pre-trigger delay"},
    "stress": {"delay_iters": 4096, "max_cycles": 200_000, "notes": "stress deterministic pre-trigger delay"},
}

QUICK_SCALES = ("smoke", "medium", "stress")
FULL_SCALES = tuple(WORKLOAD_SCALES)

RECORDER_CONFIGS = {
    "minimal": {"capture_mode": 0x1, "notes": "MMIO/interrupt/property-fail capture mode"},
    "core": {"capture_mode": 0x3, "notes": "ReplayCapsule-RV property-relevant capture mode"},
    "hashed": {"capture_mode": 0x3, "notes": "core capture mode; hash evidence is carried by signatures"},
    "diagnostic": {"capture_mode": 0x0, "notes": "capture-all diagnostic mode"},
    "full": {"capture_mode": 0x0, "notes": "capture-all diagnostic mode with strongest status evidence"},
}

MAPPED_MEMORY_WORDS = (512, 1024, 2048, 4096, 8192)
MAPPED_BUFFER_DEPTHS = (8, 16, 32, 64, 128)
MAPPED_CONFIGS = ("core", "hashed", "full")


def processed_path(name: str) -> Path:
    return REPO_ROOT / "results" / "processed" / name


def raw_path(*parts: str) -> Path:
    return REPO_ROOT / "results" / "raw" / Path(*parts)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fieldnames})


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def variants_for_mode(mode: str) -> dict[str, tuple[str, ...]]:
    if mode == "quick":
        return {benchmark: ("failing",) for benchmark in BENCHMARKS}
    return VARIANTS


def seeds_for_mode(mode: str) -> tuple[int, ...]:
    return QUICK_SEEDS if mode == "quick" else SEEDS


def scales_for_mode(mode: str) -> tuple[str, ...]:
    return QUICK_SCALES if mode == "quick" else FULL_SCALES


def case_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row.get("benchmark", ""),
        row.get("variant", ""),
        row.get("seed", ""),
        row.get("workload_scale", ""),
    )


def safe_float(value: object) -> float | None:
    try:
        if value in (None, "", "NA"):
            return None
        numeric = float(str(value))
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric):
        return None
    return numeric


def safe_int(value: object) -> int | None:
    numeric = safe_float(value)
    if numeric is None:
        return None
    return int(numeric)


def pct_delta(baseline: object, value: object) -> str:
    b = safe_float(baseline)
    v = safe_float(value)
    if b is None or v is None or b == 0:
        return "NA"
    return f"{((v - b) / b * 100.0):.2f}"


def reduction_pct(baseline: object, value: object) -> str:
    b = safe_float(baseline)
    v = safe_float(value)
    if b is None or v is None or b == 0:
        return "NA"
    return f"{((b - v) / b * 100.0):.2f}"


def summarize_values(values: list[float]) -> dict[str, str]:
    if not values:
        return {
            "median": "NA",
            "mean": "NA",
            "min": "NA",
            "max": "NA",
            "iqr": "NA",
            "n": "0",
        }
    ordered = sorted(values)
    q1 = ordered[len(ordered) // 4]
    q3 = ordered[(len(ordered) * 3) // 4]
    return {
        "median": f"{median(ordered):.6f}",
        "mean": f"{mean(ordered):.6f}",
        "min": f"{min(ordered):.6f}",
        "max": f"{max(ordered):.6f}",
        "iqr": f"{(q3 - q1):.6f}",
        "n": str(len(ordered)),
    }


def compiler_backed_firmware_rows() -> list[dict[str, str]]:
    rows = read_csv(processed_path("firmware_build.csv"))
    return [
        row
        for row in rows
        if row.get("build_status") == "PASS" and row.get("firmware_source") == "compiler_c"
    ]


def status_count(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(field, "NA") or "NA"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _csv_value(value: object) -> str:
    if value is None:
        return "NA"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
