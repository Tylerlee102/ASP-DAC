#!/usr/bin/env python3
"""Run bounded formal checks when local SymbiYosys tooling is available."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "results/raw"
OUT_CSV = REPO_ROOT / "results/processed/formal_checks.csv"
BUILD_DIR = REPO_ROOT / ".tools/formal_checks"
LOCAL_PYTHON_PKG = REPO_ROOT / ".tools/python"
LOCAL_PYTHON_BIN = LOCAL_PYTHON_PKG / "bin"
OSS_CAD_SUITE = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"


@dataclass(frozen=True)
class FormalTarget:
    name: str
    sby_file: Path
    depth: int
    notes: str


FORMAL_TARGETS = (
    FormalTarget(
        name="replay_capsule_top_bmc",
        sby_file=Path("formal/yosys_smtbmc_scripts/replay_capsule_top_bmc.sby"),
        depth=16,
        notes="bounded recorder invariants over depth 16",
    ),
)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    failures: list[str] = []
    tool = _find_sby_tool()
    if not tool:
        for target in FORMAL_TARGETS:
            rows.append(_row(target.name, "TODO", "sby/smtbmc", "", "formal tooling not available"))
        _write_rows(rows)
        print(f"WROTE {OUT_CSV}")
        return 0

    for target in FORMAL_TARGETS:
        log_path = RAW_DIR / f"formal_{target.name}.txt"
        run_dir = BUILD_DIR / target.name
        cmd = [tool.command, "-f", "-d", str(run_dir.relative_to(REPO_ROOT)), str(target.sby_file)]
        completed = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            env=tool.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_path.write_text(_clean_log(completed.stdout), encoding="utf-8")
        raw_log = str(log_path.relative_to(REPO_ROOT))
        if completed.returncode == 0 and "DONE (PASS" in completed.stdout:
            rows.append(_row(target.name, "PASS", tool.label, raw_log, target.notes))
        else:
            failures.append(f"{target.name} formal check failed")
            rows.append(_row(target.name, "FAIL", tool.label, raw_log, "bounded formal check failed"))

    _write_rows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if failures else 0


@dataclass(frozen=True)
class FormalTool:
    command: str
    label: str
    env: dict[str, str]


def _find_sby_tool() -> FormalTool | None:
    env = dict(os.environ)
    path_entries: list[str] = []
    labels: list[str] = []

    shim_dir = BUILD_DIR / "bin"
    shim_dir.mkdir(parents=True, exist_ok=True)

    yowasp_yosys = LOCAL_PYTHON_BIN / "yowasp-yosys.exe"
    oss_yosys = OSS_CAD_SUITE / "bin" / "yosys.exe"
    if oss_yosys.exists():
        path_entries.extend([str(OSS_CAD_SUITE / "bin"), str(OSS_CAD_SUITE / "lib")])
        labels.append("oss-cad-suite:yosys")
    elif LOCAL_PYTHON_PKG.exists() and yowasp_yosys.exists():
        _write_cmd_shim(shim_dir / "yosys.cmd", yowasp_yosys)
        path_entries.append(str(shim_dir))
        labels.append("yowasp-yosys")
    elif shutil.which("yosys"):
        labels.append("yosys")
    else:
        return None

    yowasp_smtbmc = LOCAL_PYTHON_BIN / "yowasp-yosys-smtbmc.exe"
    yowasp_sby = LOCAL_PYTHON_BIN / "yowasp-sby.exe"
    if LOCAL_PYTHON_PKG.exists() and yowasp_smtbmc.exists():
        _write_cmd_shim(shim_dir / "yosys-smtbmc.cmd", yowasp_smtbmc)
        if str(shim_dir) not in path_entries:
            path_entries.append(str(shim_dir))
        existing_pythonpath = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(LOCAL_PYTHON_PKG) if not existing_pythonpath else str(LOCAL_PYTHON_PKG) + os.pathsep + existing_pythonpath
        labels.append("yowasp-yosys-smtbmc")
    elif shutil.which("yosys-smtbmc"):
        labels.append("yosys-smtbmc")
    else:
        return None

    if LOCAL_PYTHON_PKG.exists() and yowasp_sby.exists():
        command = str(yowasp_sby)
        labels.insert(0, "yowasp-sby")
    elif system_sby := shutil.which("sby"):
        command = system_sby
        labels.insert(0, "sby")
    else:
        return None

    env["PATH"] = os.pathsep.join([*path_entries, env.get("PATH", "")])
    return FormalTool(command=command, label="+".join(labels), env=env)


def _write_cmd_shim(path: Path, target: Path) -> None:
    path.write_text(f"@echo off\r\n\"{target}\" %*\r\n", encoding="ascii")


def _clean_log(text: str) -> str:
    cleaned = text.replace(str(REPO_ROOT), "<repo>")
    cleaned = re.sub(r"SBY \d{2}:\d{2}:\d{2} ", "SBY ", cleaned)
    cleaned = re.sub(r"##\s+0:00:\d{2}\s+", "## <time> ", cleaned)
    cleaned = re.sub(
        r"summary: Elapsed clock time \[H:MM:SS \(secs\)\]: .+",
        "summary: Elapsed clock time <time>",
        cleaned,
    )
    lines = [line.rstrip() for line in cleaned.splitlines()]
    return "\n".join(lines) + "\n" if lines else ""


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "status", "tool", "raw_log", "notes"])
        writer.writeheader()
        writer.writerows(rows)


def _row(check: str, status: str, tool: str, raw_log: str, notes: str) -> dict[str, str]:
    return {"check": check, "status": status, "tool": tool, "raw_log": raw_log, "notes": notes}


if __name__ == "__main__":
    raise SystemExit(main())
