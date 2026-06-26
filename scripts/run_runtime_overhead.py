#!/usr/bin/env python3
"""Measure current harness runtime rows and report overhead blockers honestly."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_BASE = REPO_ROOT / "build/verilator/replaycapsule_sim"
FULL_RTL_CSV = REPO_ROOT / "results/processed/full_rtl_replay.csv"
OUT_CSV = REPO_ROOT / "results/processed/runtime_overhead.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/runtime_overhead_summary.csv"
RAW_DIR = REPO_ROOT / "results/raw/runtime_overhead"
LOCAL_WINLIBS_BIN = REPO_ROOT / ".tools/winlibs/mingw64/bin"
OSS_CAD_SUITE = Path(os.environ.get("REPLAYCAPSULE_OSS_CAD_SUITE", REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"))

FIELDNAMES = [
    "benchmark",
    "variant",
    "seed",
    "config",
    "firmware_source",
    "compiler_backed",
    "cycles_to_completion",
    "cycles_to_failure",
    "commits_to_completion",
    "commits_to_failure",
    "event_count",
    "capsule_bytes",
    "sim_wall_time_sec",
    "cycle_overhead_pct",
    "commit_overhead_pct",
    "sim_wall_time_overhead_pct",
    "baseline_config",
    "status",
    "notes",
]

SUMMARY_FIELDS = ["metric", "config", "median", "mean", "min", "max", "n", "status", "notes"]


def main() -> int:
    rows = _full_rtl_rows()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sim = _sim_path()

    if not rows:
        measured: list[dict[str, str]] = []
        summary = [
            _summary("sim_wall_time_sec", "recorder_enabled", [], "BLOCKED", "results/processed/full_rtl_replay.csv is missing or empty"),
            _blocked_summary("cycle_overhead_pct", "recorder_enabled_vs_baseline", "no full RTL rows available"),
            _blocked_summary("sim_wall_time_overhead_pct", "recorder_enabled_vs_baseline", "no full RTL rows available"),
        ]
    elif sim is None:
        measured = [_blocked_row(row, "recorder_enabled", "Verilator simulator is unavailable") for row in rows]
        summary = [
            _summary("sim_wall_time_sec", "recorder_enabled", [], "BLOCKED", "Verilator simulator is unavailable"),
            _blocked_summary("cycle_overhead_pct", "recorder_enabled_vs_baseline", "baseline and current-harness measurements unavailable"),
            _blocked_summary("sim_wall_time_overhead_pct", "recorder_enabled_vs_baseline", "baseline and current-harness measurements unavailable"),
        ]
    else:
        measured = []
        for row in rows:
            measured.append(_measure_current_harness(sim, row))
            measured.append(_blocked_row(row, "baseline_no_recorder", "no baseline core wrapper without ReplayCapsule instrumentation exists"))
            measured.append(_blocked_row(row, "recorder_present_disabled", "current Verilator top has no runtime recorder-disable control"))
        current = [row for row in measured if row["config"] == "recorder_enabled" and row["status"] == "MEASURED"]
        wall_times = [float(row["sim_wall_time_sec"]) for row in current if row["sim_wall_time_sec"] != "NA"]
        summary = [
            _summary("sim_wall_time_sec", "recorder_enabled", wall_times, "MEASURED", "current host-driven Verilator recorder-enabled wall-clock rows; not overhead"),
            _blocked_summary("cycle_overhead_pct", "recorder_enabled_vs_baseline", "no comparable baseline core wrapper without ReplayCapsule instrumentation exists"),
            _blocked_summary("commit_overhead_pct", "recorder_enabled_vs_baseline", "no comparable baseline core wrapper without ReplayCapsule instrumentation exists"),
            _blocked_summary("sim_wall_time_overhead_pct", "recorder_enabled_vs_baseline", "no comparable baseline core wrapper without ReplayCapsule instrumentation exists"),
        ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(measured)
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary)
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(SUMMARY_CSV)}")
    return 0


def _measure_current_harness(sim: Path, row: dict[str, str]) -> dict[str, str]:
    benchmark = row["benchmark"]
    variant = row["variant"]
    seed = row["seed"]
    firmware = REPO_ROOT / "firmware/build" / benchmark / f"{variant}.hex"
    if not firmware.exists() and variant == "no_failure_edge":
        firmware = REPO_ROOT / "firmware/build" / benchmark / "failing.hex"
    capsule = RAW_DIR / f"{benchmark}_{variant}_seed{seed}_record.json"
    signature = RAW_DIR / f"{benchmark}_{variant}_seed{seed}_signature.json"
    command = [
        str(sim),
        "--mode",
        "record",
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
        seed,
        "--max-cycles",
        "100000",
    ]
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=REPO_ROOT, env=_tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    elapsed = time.perf_counter() - start
    parsed = _parse_harness_line(completed.stdout)
    status = "MEASURED" if completed.returncode == 0 else "FAIL"
    cycles = parsed.get("cycles", row.get("cycles_to_failure", "NA"))
    commits = parsed.get("commits", row.get("commits_to_failure", "NA"))
    failure_expected = row.get("property_id_record") not in {"0", "NA", ""}
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "config": "recorder_enabled",
        "firmware_source": row.get("firmware_source", "NA"),
        "compiler_backed": row.get("compiler_backed", "false"),
        "cycles_to_completion": "NA" if failure_expected else cycles,
        "cycles_to_failure": cycles if failure_expected else "NA",
        "commits_to_completion": "NA" if failure_expected else commits,
        "commits_to_failure": commits if failure_expected else "NA",
        "event_count": parsed.get("events", "NA"),
        "capsule_bytes": row.get("capsule_bytes", "NA"),
        "sim_wall_time_sec": f"{elapsed:.6f}",
        "cycle_overhead_pct": "NA",
        "commit_overhead_pct": "NA",
        "sim_wall_time_overhead_pct": "NA",
        "baseline_config": "baseline_no_recorder",
        "status": status,
        "notes": _clean(_last_line(completed.stdout)) if status == "FAIL" else "measured current recorder-enabled host-driven Verilator run; no baseline overhead computed",
    }


def _blocked_row(row: dict[str, str], config: str, notes: str) -> dict[str, str]:
    return {
        "benchmark": row["benchmark"],
        "variant": row["variant"],
        "seed": row["seed"],
        "config": config,
        "firmware_source": row.get("firmware_source", "NA"),
        "compiler_backed": row.get("compiler_backed", "false"),
        "cycles_to_completion": "NA",
        "cycles_to_failure": "NA",
        "commits_to_completion": "NA",
        "commits_to_failure": "NA",
        "event_count": "NA",
        "capsule_bytes": "NA",
        "sim_wall_time_sec": "NA",
        "cycle_overhead_pct": "NA",
        "commit_overhead_pct": "NA",
        "sim_wall_time_overhead_pct": "NA",
        "baseline_config": "NA" if config == "baseline_no_recorder" else "baseline_no_recorder",
        "status": "BLOCKED",
        "notes": notes,
    }


def _full_rtl_rows() -> list[dict[str, str]]:
    if not FULL_RTL_CSV.exists():
        return []
    with FULL_RTL_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _sim_path() -> Path | None:
    for candidate in (SIM_BASE, SIM_BASE.with_suffix(".exe")):
        if candidate.exists():
            return candidate
    return None


def _parse_harness_line(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    line = _last_line(text)
    for key in ("events", "cycles", "commits"):
        match = re.search(rf"\b{key}=([0-9]+)", line)
        if match:
            out[key] = match.group(1)
    return out


def _summary(metric: str, config: str, values: list[float], status: str, notes: str) -> dict[str, str]:
    if values:
        values = sorted(values)
        total = sum(values)
        return {
            "metric": metric,
            "config": config,
            "median": _median(values),
            "mean": f"{total / len(values):.6f}",
            "min": f"{values[0]:.6f}",
            "max": f"{values[-1]:.6f}",
            "n": str(len(values)),
            "status": status,
            "notes": notes,
        }
    return {
        "metric": metric,
        "config": config,
        "median": "NA",
        "mean": "NA",
        "min": "NA",
        "max": "NA",
        "n": "0",
        "status": status,
        "notes": notes,
    }


def _blocked_summary(metric: str, config: str, notes: str) -> dict[str, str]:
    return _summary(metric, config, [], "BLOCKED", notes)


def _median(values: list[float]) -> str:
    if not values:
        return "NA"
    values = sorted(values)
    middle = len(values) // 2
    if len(values) % 2:
        median = values[middle]
    else:
        median = (values[middle - 1] + values[middle]) / 2
    return f"{median:.6f}"


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def _clean(text: str) -> str:
    return text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")


def _tool_env() -> dict[str, str]:
    env = dict(os.environ)
    parts = [str(LOCAL_WINLIBS_BIN), str(OSS_CAD_SUITE / "bin"), str(OSS_CAD_SUITE / "lib")]
    git_usr_bin = _git_usr_bin()
    if git_usr_bin is not None:
        parts.append(str(git_usr_bin))
    parts.append(env.get("PATH", ""))
    env["PATH"] = os.pathsep.join(parts)
    env["VERILATOR_ROOT"] = (OSS_CAD_SUITE / "share" / "verilator").as_posix()
    return env


def _git_usr_bin() -> Path | None:
    git = shutil.which("git")
    if not git:
        return None
    path = Path(git)
    for parent in path.parents:
        candidate = parent / "usr/bin"
        if (candidate / "uname.exe").exists():
            return candidate
    return None


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
