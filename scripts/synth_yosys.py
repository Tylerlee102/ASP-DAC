#!/usr/bin/env python3
"""Run Yosys synthesis when available; otherwise emit honest TODO reports."""

from __future__ import annotations

import argparse
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
    yosys = shutil.which("yosys")
    if not yosys:
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
        completed = subprocess.run([yosys, "-p", script], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        report_path(top).write_text(completed.stdout, encoding="utf-8")
        failed = failed or completed.returncode != 0
        print(f"WROTE {report_path(top)}")
    return 1 if failed else 0


def report_path(top: str) -> Path:
    return RAW_DIR / f"yosys_{top}.txt"


if __name__ == "__main__":
    raise SystemExit(main())

