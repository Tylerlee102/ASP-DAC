#!/usr/bin/env python3
"""Measure fair runtime perturbation rows against a no-recorder PicoRV32 baseline."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean, median


REPO_ROOT = Path(__file__).resolve().parents[1]
FULL_RTL_CSV = REPO_ROOT / "results/processed/full_rtl_replay.csv"
OUT_CSV = REPO_ROOT / "results/processed/runtime_overhead.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/runtime_overhead_summary.csv"
RAW_DIR = REPO_ROOT / "results/raw/runtime_overhead"
BASELINE_SIM = REPO_ROOT / "build/verilator/runtime_baseline_sim"
RECORDER_SIM = REPO_ROOT / "build/verilator/runtime_recorder_sim"
LOCAL_WINLIBS_BIN = REPO_ROOT / ".tools/winlibs/mingw64/bin"
OSS_CAD_SUITE = Path(os.environ.get("REPLAYCAPSULE_OSS_CAD_SUITE", REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"))

RUNTIME_DEPENDENCY_PATHS = (
    "tb/verilator/replaycapsule_verilator_top.sv",
    "tb/verilator/picorv32_baseline_top.sv",
    "third_party/picorv32/picorv32.v",
    "rtl/event_pkg.sv",
    "rtl/event_tap.sv",
    "rtl/event_classifier.sv",
    "rtl/capsule_buffer.sv",
    "rtl/property_checker.sv",
    "rtl/event_slicer.sv",
    "rtl/hash_signature.sv",
    "rtl/replay_capsule_top.sv",
    "rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
    "tb/verilator/runtime_main.cpp",
    "Makefile",
)

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
    rows = [row for row in _full_rtl_rows() if row.get("compiler_backed") == "true" and row.get("firmware_source") == "compiler_c"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    blocker = _ensure_runtime_sims()
    if not rows:
        measured: list[dict[str, str]] = []
        summary = [_blocked_summary("cycle_overhead_pct", "recorder_enabled_vs_baseline", "no compiler-backed full RTL replay rows available")]
    elif blocker:
        measured = []
        for row in rows:
            measured.extend(
                [
                    _blocked_row(row, "baseline_no_recorder", blocker),
                    _blocked_row(row, "recorder_present_disabled", blocker),
                    _blocked_row(row, "recorder_enabled", blocker),
                ]
            )
        summary = [
            _blocked_summary("cycle_overhead_pct", "recorder_enabled_vs_baseline", blocker),
            _blocked_summary("commit_overhead_pct", "recorder_enabled_vs_baseline", blocker),
            _blocked_summary("sim_wall_time_overhead_pct", "recorder_enabled_vs_baseline", blocker),
        ]
    else:
        measured = []
        by_case: dict[tuple[str, str, str], dict[str, dict[str, str]]] = {}
        for row in rows:
            case_key = (row["benchmark"], row["variant"], row["seed"])
            case_rows = {
                "baseline_no_recorder": _measure_config(row, "baseline_no_recorder", _sim_path(BASELINE_SIM)),
                "recorder_present_disabled": _measure_config(row, "recorder_present_disabled", _sim_path(RECORDER_SIM)),
                "recorder_enabled": _measure_config(row, "recorder_enabled", _sim_path(RECORDER_SIM)),
            }
            _fill_overheads(case_rows)
            by_case[case_key] = case_rows
            measured.extend(case_rows[config] for config in ("baseline_no_recorder", "recorder_present_disabled", "recorder_enabled"))
        summary = _summaries(measured)

    _write_csv(OUT_CSV, FIELDNAMES, measured)
    _write_csv(SUMMARY_CSV, SUMMARY_FIELDS, summary)
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(SUMMARY_CSV)}")
    return 0


def _ensure_runtime_sims() -> str | None:
    baseline = _sim_path(BASELINE_SIM)
    recorder = _sim_path(RECORDER_SIM)
    if baseline.exists() and recorder.exists() and not _runtime_sim_needs_rebuild(baseline, recorder):
        return None
    make = _find_make()
    verilator = _find_verilator()
    cxx = _find_cxx()
    missing = []
    if not make:
        missing.append("make/gmake")
    if not verilator:
        missing.append("verilator")
    if not cxx:
        missing.append("g++/c++/clang++")
    if missing:
        return "missing " + ", ".join(missing) + "; runtime baseline/recorder simulators not available"

    completed = subprocess.run(
        [make, "runtime-harnesses", f"PYTHON={Path(sys.executable).as_posix()}", f"VERILATOR={Path(verilator).name}"],
        cwd=REPO_ROOT,
        env=_tool_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (RAW_DIR / "runtime_harnesses_make.log").write_text(_clean(completed.stdout), encoding="utf-8")
    if completed.returncode != 0:
        return "runtime harness build failed; see results/raw/runtime_overhead/runtime_harnesses_make.log"
    if not _sim_path(BASELINE_SIM).exists():
        return "runtime baseline simulator missing after build"
    if not _sim_path(RECORDER_SIM).exists():
        return "runtime recorder simulator missing after build"
    return None


def _runtime_sim_needs_rebuild(baseline: Path, recorder: Path) -> bool:
    sim_mtime = min(baseline.stat().st_mtime, recorder.stat().st_mtime)
    for rel_path in RUNTIME_DEPENDENCY_PATHS:
        path = REPO_ROOT / rel_path
        if path.exists() and path.stat().st_mtime > sim_mtime:
            return True
    return False


def _measure_config(row: dict[str, str], config: str, sim: Path) -> dict[str, str]:
    benchmark = row["benchmark"]
    variant = row["variant"]
    seed = row["seed"]
    firmware = REPO_ROOT / "firmware/build" / benchmark / f"{variant}.hex"
    if not firmware.exists() and variant == "no_failure_edge":
        firmware = REPO_ROOT / "firmware/build" / benchmark / "failing.hex"
    if not firmware.exists():
        return _blocked_row(row, config, f"compiler-backed firmware HEX missing: {_rel(firmware)}")

    command = [
        str(sim),
        "--config",
        config,
        "--benchmark",
        benchmark,
        "--variant",
        variant,
        "--firmware",
        _rel(firmware),
        "--seed",
        seed,
        "--max-cycles",
        "100000",
    ]
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=REPO_ROOT, env=_tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    elapsed = time.perf_counter() - start
    parsed = _parse_runtime_line(completed.stdout)
    failure_expected = row.get("property_id_record") not in {"0", "NA", ""}
    cycles = parsed.get("cycles", "NA")
    commits = parsed.get("commits", "NA")
    status = "MEASURED" if completed.returncode == 0 else "FAIL"
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "config": config,
        "firmware_source": row.get("firmware_source", "NA"),
        "compiler_backed": row.get("compiler_backed", "false"),
        "cycles_to_completion": "NA" if failure_expected else cycles,
        "cycles_to_failure": cycles if failure_expected else "NA",
        "commits_to_completion": "NA" if failure_expected else commits,
        "commits_to_failure": commits if failure_expected else "NA",
        "event_count": parsed.get("events", "NA"),
        "capsule_bytes": parsed.get("capsule_bytes", "NA"),
        "sim_wall_time_sec": f"{elapsed:.6f}",
        "cycle_overhead_pct": "NA",
        "commit_overhead_pct": "NA",
        "sim_wall_time_overhead_pct": "NA",
        "baseline_config": "NA" if config == "baseline_no_recorder" else "baseline_no_recorder",
        "status": status,
        "notes": _clean(_last_line(completed.stdout)) if status == "FAIL" else "measured same firmware/stimulus on runtime harness",
    }


def _fill_overheads(case_rows: dict[str, dict[str, str]]) -> None:
    baseline = case_rows["baseline_no_recorder"]
    for config in ("recorder_present_disabled", "recorder_enabled"):
        row = case_rows[config]
        if baseline["status"] != "MEASURED" or row["status"] != "MEASURED":
            continue
        row["cycle_overhead_pct"] = _pct_delta(_cycle_value(baseline), _cycle_value(row))
        row["commit_overhead_pct"] = _pct_delta(_commit_value(baseline), _commit_value(row))
        row["sim_wall_time_overhead_pct"] = _pct_delta(_float_or_none(baseline["sim_wall_time_sec"]), _float_or_none(row["sim_wall_time_sec"]))


def _cycle_value(row: dict[str, str]) -> float | None:
    return _float_or_none(row["cycles_to_failure"] if row["cycles_to_failure"] != "NA" else row["cycles_to_completion"])


def _commit_value(row: dict[str, str]) -> float | None:
    return _float_or_none(row["commits_to_failure"] if row["commits_to_failure"] != "NA" else row["commits_to_completion"])


def _pct_delta(baseline: float | None, value: float | None) -> str:
    if baseline is None or value is None or baseline == 0:
        return "NA"
    return f"{((value - baseline) / baseline * 100.0):.2f}"


def _summaries(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for config in ("baseline_no_recorder", "recorder_present_disabled", "recorder_enabled"):
        wall_values = [_float_or_none(row["sim_wall_time_sec"]) for row in rows if row["config"] == config and row["status"] == "MEASURED"]
        out.append(_summary("sim_wall_time_sec", config, [value for value in wall_values if value is not None], "MEASURED", "simulator wall-clock time; not hardware runtime"))
    for config in ("recorder_present_disabled", "recorder_enabled"):
        for metric in ("cycle_overhead_pct", "commit_overhead_pct", "sim_wall_time_overhead_pct"):
            values = [_float_or_none(row[metric]) for row in rows if row["config"] == config and row["status"] == "MEASURED"]
            clean = [value for value in values if value is not None]
            status = "MEASURED" if clean else "BLOCKED"
            notes = "relative to baseline_no_recorder with same firmware/stimulus" if clean else "no comparable measured baseline/config pairs"
            out.append(_summary(metric, f"{config}_vs_baseline_no_recorder", clean, status, notes))
    return out


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


def _parse_runtime_line(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    line = _last_line(text)
    for key in ("events", "capsule_bytes", "cycles", "commits", "property"):
        match = re.search(rf"\b{key}=([0-9]+)", line)
        if match:
            out[key] = match.group(1)
    return out


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _summary(metric: str, config: str, values: list[float], status: str, notes: str) -> dict[str, str]:
    if values:
        return {
            "metric": metric,
            "config": config,
            "median": f"{median(values):.6f}",
            "mean": f"{mean(values):.6f}",
            "min": f"{min(values):.6f}",
            "max": f"{max(values):.6f}",
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


def _float_or_none(value: str) -> float | None:
    try:
        if value == "NA":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def _find_make() -> str | None:
    for path in (LOCAL_WINLIBS_BIN / "make.exe", LOCAL_WINLIBS_BIN / "mingw32-make.exe"):
        if path.exists():
            return str(path)
    return shutil.which("make") or shutil.which("gmake") or shutil.which("mingw32-make")


def _find_verilator() -> str | None:
    if OSS_CAD_SUITE.exists():
        for path in (OSS_CAD_SUITE / "bin/verilator_bin.exe", OSS_CAD_SUITE / "bin/verilator.exe", OSS_CAD_SUITE / "bin/verilator"):
            if path.exists():
                return str(path)
    return shutil.which("verilator")


def _find_cxx() -> str | None:
    for path in (LOCAL_WINLIBS_BIN / "g++.exe", LOCAL_WINLIBS_BIN / "c++.exe", LOCAL_WINLIBS_BIN / "clang++.exe"):
        if path.exists():
            return str(path)
    return shutil.which("g++") or shutil.which("c++") or shutil.which("clang++")


def _sim_path(base: Path) -> Path:
    if base.exists():
        return base
    exe = base.with_suffix(".exe")
    if exe.exists():
        return exe
    return base


def _tool_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in ("VERILATOR_ROOT", "VERILATOR_BIN", "OSS_CAD_SUITE"):
        env.pop(key, None)
    parts = []
    if LOCAL_WINLIBS_BIN.exists():
        parts.append(str(LOCAL_WINLIBS_BIN))
    if OSS_CAD_SUITE.exists():
        for path in (OSS_CAD_SUITE / "bin", OSS_CAD_SUITE / "lib"):
            if path.exists():
                parts.append(str(path))
    git_usr_bin = _git_usr_bin()
    if git_usr_bin is not None:
        parts.append(str(git_usr_bin))
    parts.append(env.get("PATH", ""))
    env["PATH"] = os.pathsep.join(parts)
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


def _clean(text: str) -> str:
    cleaned = text
    replacements = [str(REPO_ROOT), str(REPO_ROOT).replace("\\", "/"), str(Path.home()), str(Path.home()).replace("\\", "/")]
    for value in replacements:
        cleaned = cleaned.replace(value, ".")
    cleaned = re.sub(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+", ".", cleaned)
    return cleaned


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
