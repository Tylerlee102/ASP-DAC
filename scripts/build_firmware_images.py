#!/usr/bin/env python3
"""Build deterministic RV32I firmware image artifacts for benchmark programs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from replaycapsule_model import BENCHMARKS  # noqa: E402
from rv32i_firmware_sim import build_program  # noqa: E402


OUT_DIR = REPO_ROOT / "firmware" / "build"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    count = 0
    for benchmark in BENCHMARKS:
        for failing in [True, False]:
            program = build_program(benchmark, failing=failing)
            variant = "failing" if failing else "fixed"
            root = args.out_dir / benchmark
            root.mkdir(parents=True, exist_ok=True)
            hex_path = root / f"{variant}.hex"
            mem_path = root / f"{variant}.mem"
            meta_path = root / f"{variant}.json"
            hex_path.write_text("\n".join(f"{word:08x}" for word in program.words) + "\n", encoding="utf-8")
            mem_path.write_text(
                "\n".join(f"@{index:08x} {word:08x}" for index, word in enumerate(program.words)) + "\n",
                encoding="utf-8",
            )
            meta_path.write_text(
                json.dumps(
                    {
                        "benchmark": benchmark,
                        "variant": variant,
                        "reset_pc": "0x00000080",
                        "word_count": len(program.words),
                        "labels": {label: f"0x{pc:08x}" for label, pc in program.labels.items()},
                        "interrupt_commit": program.interrupt_commit,
                        "sensor_value": program.sensor_value,
                        "command_value": program.command_value,
                        "hex": str(hex_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                        "mem": str(mem_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            count += 1
    print(f"WROTE {count} firmware image sets under {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

