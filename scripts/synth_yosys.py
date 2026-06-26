#!/usr/bin/env python3
"""Run Yosys synthesis when available; otherwise emit honest TODO reports."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "results/raw"

SYNTH_TARGETS = {
    "replay_capsule_top": [
        "rtl/event_pkg.sv",
        "rtl/event_tap.sv",
        "rtl/event_classifier.sv",
        "rtl/capsule_buffer.sv",
        "rtl/property_checker.sv",
        "rtl/event_slicer.sv",
        "rtl/hash_signature.sv",
        "rtl/replay_capsule_top.sv",
    ],
    "picorv32_replaycapsule_wrapper": [
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
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", choices=sorted(SYNTH_TARGETS), help="single top to synthesize")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    targets = [args.top] if args.top else list(SYNTH_TARGETS)
    yosys_cmd, yosys_env, yosys_label = _find_yosys()
    if not yosys_cmd:
        for top in targets:
            report_path(top).write_text(f"STATUS: TODO\nTOP: {top}\nREASON: yosys not found on PATH\n", encoding="utf-8")
        print(f"TODO yosys not found; wrote {len(targets)} report(s) under {RAW_DIR}")
        return 0

    failed = False
    for top in targets:
        script = "; ".join(
            [
                "read_verilog -sv " + " ".join(SYNTH_TARGETS[top]),
                f"hierarchy -check -top {top}",
                "proc",
                "opt",
                "stat",
            ]
        )
        completed = subprocess.run(
            [*yosys_cmd, "-p", script],
            cwd=REPO_ROOT,
            env=yosys_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        completed_stdout = _clean_report(f"TOOL: {yosys_label}\nTOP: {top}\n" + completed.stdout)
        report_path(top).write_text(completed_stdout, encoding="utf-8")
        failed = failed or completed.returncode != 0
        print(f"WROTE {report_path(top)}")
    return 1 if failed else 0


def report_path(top: str) -> Path:
    return RAW_DIR / f"yosys_{top}.txt"


def _clean_report(text: str) -> str:
    text = re.sub(
        r"End of script\. Logfile hash: ([0-9a-f]+), time: [^,]+, user: [^,]+, system: [^\n]+",
        r"End of script. Logfile hash: \1, time: <time>, user: <time>, system: <time>",
        text,
    )
    text = re.sub(r"Time spent: .+", "Time spent: <normalized>", text)
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def _find_yosys() -> tuple[list[str] | None, dict[str, str] | None, str]:
    system_yosys = shutil.which("yosys")
    if system_yosys:
        return [system_yosys], None, "yosys"

    local_bin = REPO_ROOT / ".tools" / "python" / "bin" / "yowasp-yosys.exe"
    local_pkg = REPO_ROOT / ".tools" / "python"
    if local_bin.exists() and local_pkg.exists():
        env = dict(os.environ)
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(local_pkg) if not existing else str(local_pkg) + os.pathsep + existing
        return [str(local_bin)], env, "yowasp-yosys"

    return None, None, "missing"


if __name__ == "__main__":
    raise SystemExit(main())
