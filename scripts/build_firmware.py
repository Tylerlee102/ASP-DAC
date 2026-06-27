#!/usr/bin/env python3
"""Build or verify firmware artifacts for full RTL replay."""

from __future__ import annotations

import csv
import hashlib
import os
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/firmware_build.csv"
BUILD_ROOT = REPO_ROOT / "firmware/build"
LINKER = REPO_ROOT / "firmware/linker.ld"
STARTUP = REPO_ROOT / "firmware/startup.S"

BENCHMARK_DIRS = {
    "sensor_threshold_bug": "bug_sensor_threshold",
    "interrupt_race_bug": "bug_interrupt_race",
    "mmio_ordering_bug": "bug_mmio_ordering",
    "stack_corruption_bug": "bug_stack_corruption",
    "uart_command_bug": "bug_uart_command",
    "watchdog_timeout_bug": "bug_watchdog_timeout",
}

VARIANTS = {
    "sensor_threshold_bug": ("failing", "fixed", "no_failure_edge"),
    "interrupt_race_bug": ("failing", "fixed"),
    "mmio_ordering_bug": ("failing", "fixed"),
    "stack_corruption_bug": ("failing", "fixed"),
    "uart_command_bug": ("failing", "fixed", "no_failure_edge"),
    "watchdog_timeout_bug": ("failing", "fixed", "no_failure_edge"),
}

FIELDNAMES = [
    "benchmark",
    "variant",
    "elf_path",
    "hex_path",
    "map_path",
    "build_status",
    "firmware_source",
    "compiler",
    "compiler_version",
    "size_text",
    "size_data",
    "size_bss",
    "entry_point",
    "sha256_hex",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-compiler",
        action="store_true",
        help="fail the gate unless every firmware row is compiler-generated",
    )
    args = parser.parse_args()
    require_compiler = args.require_compiler or _truthy_env("REPLAYCAPSULE_REQUIRE_COMPILER") or _truthy_env("REQUIRE_COMPILER")

    rows: list[dict[str, str]] = []
    tools = _find_toolchain()

    # Keep generated fallback HEX files on disk for local/debug use, but never
    # label them as compiler-backed rows.
    _run_python([sys.executable, "scripts/build_firmware_images.py"])

    if tools["compiler"] and tools["objcopy"] and tools["size"]:
        for benchmark in BENCHMARK_DIRS:
            for variant in VARIANTS[benchmark]:
                rows.append(_build_with_gcc(benchmark, variant, tools))
    else:
        for benchmark in BENCHMARK_DIRS:
            for variant in VARIANTS[benchmark]:
                rows.append(_fallback_row(benchmark, variant, tools))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    if require_compiler:
        non_compiler = [row for row in rows if row["build_status"] != "PASS" or row["firmware_source"] != "compiler_c"]
        if non_compiler:
            print(f"FAIL: compiler-backed firmware required but {len(non_compiler)}/{len(rows)} rows are not compiler PASS")
            return 1
    return 1 if any(row["build_status"] == "FAIL" for row in rows) else 0


def _build_with_gcc(
    benchmark: str,
    variant: str,
    tools: dict[str, str | None],
) -> dict[str, str]:
    source_variant = "failing" if variant == "no_failure_edge" else variant
    source = REPO_ROOT / "firmware" / BENCHMARK_DIRS[benchmark] / f"{source_variant}.c"
    out_dir = BUILD_ROOT / benchmark
    out_dir.mkdir(parents=True, exist_ok=True)
    elf = out_dir / f"{variant}.elf"
    hex_path = out_dir / f"{variant}.hex"
    map_path = out_dir / f"{variant}.map"
    verilog_hex = out_dir / f"{variant}.objcopy.hex"

    compiler = tools["compiler"]
    objcopy = tools["objcopy"]
    assert compiler is not None
    assert objcopy is not None
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
        f"-I{REPO_ROOT / 'firmware/common'}",
        str(STARTUP),
        str(source),
        "-T",
        str(LINKER),
        f"-Wl,-Map,{map_path}",
        "-o",
        str(elf),
    ]
    completed = _run(command)
    if completed.returncode != 0:
        return _fail_row(benchmark, variant, elf, hex_path, map_path, completed.stdout)

    objcopy_result = _run([objcopy, "-O", "verilog", str(elf), str(verilog_hex)])
    if objcopy_result.returncode != 0:
        return _fail_row(benchmark, variant, elf, hex_path, map_path, objcopy_result.stdout)
    _normalize_objcopy_hex(verilog_hex, hex_path)

    text, data, bss = _sizes(tools["size"], elf)
    entry = _entry_point(tools["readelf"], elf)
    digest = _sha256(hex_path)
    return {
        "benchmark": benchmark,
        "variant": variant,
        "elf_path": _rel(elf),
        "hex_path": _rel(hex_path),
        "map_path": _rel(map_path),
        "build_status": "PASS",
        "firmware_source": "compiler_c",
        "compiler": Path(compiler).name,
        "compiler_version": _tool_version(compiler),
        "size_text": text,
        "size_data": data,
        "size_bss": bss,
        "entry_point": entry,
        "sha256_hex": digest,
        "notes": f"built with {Path(compiler).name}",
    }


def _fallback_row(benchmark: str, variant: str, tools: dict[str, str | None]) -> dict[str, str]:
    source_variant = "failing" if variant == "no_failure_edge" else variant
    out_dir = BUILD_ROOT / benchmark
    source_hex = out_dir / f"{source_variant}.hex"
    hex_path = out_dir / f"{variant}.hex"
    if variant == "no_failure_edge" and source_hex.exists() and not hex_path.exists():
        hex_path.write_text(source_hex.read_text(encoding="utf-8"), encoding="utf-8")
    if hex_path.exists():
        digest = _sha256(hex_path)
        status = "FALLBACK"
        notes = (
            "RISC-V compiler unavailable; verified generated HEX fallback "
            f"sha256={digest[:16]}. This is not a compiler-backed firmware pass."
        )
    else:
        status = "BLOCKED"
        missing = []
        if not tools["compiler"]:
            missing.append("riscv64-unknown-elf-gcc")
        if not tools["objcopy"]:
            missing.append("riscv64-unknown-elf-objcopy")
        if not tools["size"]:
            missing.append("riscv64-unknown-elf-size")
        notes = "missing " + ", ".join(missing)
    return {
        "benchmark": benchmark,
        "variant": variant,
        "elf_path": "NA",
        "hex_path": _rel(hex_path) if hex_path.exists() else "NA",
        "map_path": "NA",
        "build_status": status,
        "firmware_source": "fallback_hex" if status == "FALLBACK" else "missing",
        "compiler": "NA",
        "compiler_version": "NA",
        "size_text": "NA",
        "size_data": "NA",
        "size_bss": "NA",
        "entry_point": "NA",
        "sha256_hex": digest if hex_path.exists() else "NA",
        "notes": notes,
    }


def _normalize_objcopy_hex(source: Path, dest: Path) -> None:
    memory: dict[int, int] = {}
    addr = 0
    for token in source.read_text(encoding="utf-8", errors="replace").split():
        if token.startswith("@"):
            addr = int(token[1:], 16)
            continue
        value = int(token, 16)
        if len(token) <= 2:
            memory[addr] = value & 0xFF
            addr += 1
        else:
            width = len(token) // 2
            for index in range(width):
                shift = (width - index - 1) * 8
                memory[addr] = (value >> shift) & 0xFF
                addr += 1
    lines: list[str] = []
    for word_addr in range(0, max(memory.keys(), default=-1) + 1, 4):
        word = 0
        for byte_index in range(4):
            word |= memory.get(word_addr + byte_index, 0) << (8 * byte_index)
        lines.append(f"@{word_addr:08x} {word:08x}")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sizes(size_tool: str | None, elf: Path) -> tuple[str, str, str]:
    if not size_tool:
        return "NA", "NA", "NA"
    completed = _run([size_tool, str(elf)])
    lines = [line.split() for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) >= 2 and len(lines[1]) >= 3:
        return lines[1][0], lines[1][1], lines[1][2]
    return "NA", "NA", "NA"


def _entry_point(readelf: str | None, elf: Path) -> str:
    if not readelf:
        return "NA"
    completed = _run([readelf, "-h", str(elf)])
    for line in completed.stdout.splitlines():
        if "Entry point address:" in line:
            return line.split(":", 1)[1].strip()
    return "NA"


def _fail_row(benchmark: str, variant: str, elf: Path, hex_path: Path, map_path: Path, output: str) -> dict[str, str]:
    return {
        "benchmark": benchmark,
        "variant": variant,
        "elf_path": _rel(elf),
        "hex_path": _rel(hex_path),
        "map_path": _rel(map_path),
        "build_status": "FAIL",
        "firmware_source": "compiler_failed",
        "compiler": "NA",
        "compiler_version": "NA",
        "size_text": "NA",
        "size_data": "NA",
        "size_bss": "NA",
        "entry_point": "NA",
        "sha256_hex": "NA",
        "notes": _clean(output).splitlines()[-1] if _clean(output).splitlines() else "firmware build failed",
    }


def _find_toolchain() -> dict[str, str | None]:
    prefixes = []
    env_prefix = os.environ.get("RISCV_PREFIX")
    if env_prefix:
        prefixes.append(env_prefix)
    prefixes.extend(
        [
            "riscv64-unknown-elf-",
            "riscv-none-elf-",
            "riscv64-elf-",
            "riscv32-unknown-elf-",
        ]
    )
    best: dict[str, str | None] = {
        "compiler": None,
        "objcopy": None,
        "size": None,
        "readelf": None,
    }
    for prefix in prefixes:
        compiler = shutil.which(prefix + "gcc")
        objcopy = shutil.which(prefix + "objcopy")
        size = shutil.which(prefix + "size")
        readelf = shutil.which(prefix + "readelf")
        if compiler or objcopy or size:
            best = {
                "compiler": compiler,
                "objcopy": objcopy,
                "size": size,
                "readelf": readelf,
            }
        if compiler and objcopy and size:
            return best
    return best


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _run_python(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=False)


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _clean(text: str) -> str:
    return text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tool_version(tool: str) -> str:
    completed = _run([tool, "--version"])
    for line in completed.stdout.splitlines():
        if line.strip():
            return _clean(line.strip())
    return "version probe produced no output"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
