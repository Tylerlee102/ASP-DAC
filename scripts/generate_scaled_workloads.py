#!/usr/bin/env python3
"""Build compiler-backed firmware images with deterministic workload delays."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import build_firmware
from topconf_eval_common import (
    REPO_ROOT,
    WORKLOAD_SCALES,
    scales_for_mode,
    variants_for_mode,
    write_csv,
)


OUT_CSV = REPO_ROOT / "results/processed/scaled_firmware_build.csv"
BUILD_ROOT = REPO_ROOT / "firmware/build_scaled"

FIELDS = [
    "benchmark",
    "variant",
    "workload_scale",
    "delay_iters",
    "max_cycles",
    "hex_path",
    "elf_path",
    "build_status",
    "firmware_source",
    "compiler",
    "sha256_hex",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    args = parser.parse_args()

    rows = _build_rows(args.mode)
    write_csv(OUT_CSV, FIELDS, rows)
    blocked = [row for row in rows if row["build_status"] != "PASS"]
    print(f"WROTE {_rel(OUT_CSV)}")
    if blocked:
        print(f"SCALED_FIRMWARE_BLOCKED rows={len(blocked)}")
    return 0


def _build_rows(mode: str) -> list[dict[str, str]]:
    tools = build_firmware._find_toolchain()
    variants = variants_for_mode(mode)
    rows: list[dict[str, str]] = []
    for benchmark, names in variants.items():
        for variant in names:
            for scale in scales_for_mode(mode):
                rows.append(_build_one(benchmark, variant, scale, tools))
    return rows


def _build_one(benchmark: str, variant: str, scale: str, tools: dict[str, str | None]) -> dict[str, str]:
    config = WORKLOAD_SCALES[scale]
    delay_iters = str(config["delay_iters"])
    max_cycles = str(config["max_cycles"])
    compiler = tools.get("compiler")
    objcopy = tools.get("objcopy")
    if not compiler or not objcopy:
        return _blocked_row(benchmark, variant, scale, delay_iters, max_cycles, "missing RISC-V compiler or objcopy")

    source_variant = "failing" if variant == "no_failure_edge" else variant
    source = REPO_ROOT / "firmware" / build_firmware.BENCHMARK_DIRS[benchmark] / f"{source_variant}.c"
    out_dir = BUILD_ROOT / scale / benchmark
    out_dir.mkdir(parents=True, exist_ok=True)
    elf = out_dir / f"{variant}.elf"
    raw_hex = out_dir / f"{variant}.objcopy.hex"
    hex_path = out_dir / f"{variant}.hex"
    map_path = out_dir / f"{variant}.map"

    command = [
        compiler,
        "-march=rv32i",
        "-mabi=ilp32",
        "-O2",
        "-ffreestanding",
        "-fno-builtin",
        "-nostdlib",
        "-nostartfiles",
        "-Wall",
        "-Wextra",
        f"-DRC_WORKLOAD_DELAY_ITERS={delay_iters}",
        f"-I{REPO_ROOT / 'firmware/common'}",
        str(build_firmware.STARTUP),
        str(source),
        "-T",
        str(build_firmware.LINKER),
        f"-Wl,-Map,{map_path}",
        "-o",
        str(elf),
    ]
    completed = _run(command)
    if completed.returncode != 0:
        return _blocked_row(benchmark, variant, scale, delay_iters, max_cycles, _last_line(completed.stdout))
    objcopy_result = _run([objcopy, "-O", "verilog", str(elf), str(raw_hex)])
    if objcopy_result.returncode != 0:
        return _blocked_row(benchmark, variant, scale, delay_iters, max_cycles, _last_line(objcopy_result.stdout))
    build_firmware._normalize_objcopy_hex(raw_hex, hex_path)
    return {
        "benchmark": benchmark,
        "variant": variant,
        "workload_scale": scale,
        "delay_iters": delay_iters,
        "max_cycles": max_cycles,
        "hex_path": _rel(hex_path),
        "elf_path": _rel(elf),
        "build_status": "PASS",
        "firmware_source": "compiler_c_scaled",
        "compiler": Path(compiler).name,
        "sha256_hex": hashlib.sha256(hex_path.read_bytes()).hexdigest(),
        "notes": f"compiler-backed scaled firmware; {WORKLOAD_SCALES[scale]['notes']}",
    }


def _blocked_row(benchmark: str, variant: str, scale: str, delay_iters: str, max_cycles: str, notes: str) -> dict[str, str]:
    return {
        "benchmark": benchmark,
        "variant": variant,
        "workload_scale": scale,
        "delay_iters": delay_iters,
        "max_cycles": max_cycles,
        "hex_path": "NA",
        "elf_path": "NA",
        "build_status": "BLOCKED",
        "firmware_source": "compiler_required",
        "compiler": "NA",
        "sha256_hex": "NA",
        "notes": notes,
    }


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "command failed"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
