#!/usr/bin/env python3
"""Build and run a focused true-ISR Hazard3 smoke."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import ctypes
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / "build" / "hazard3_irq_smoke"
RAW_DIR = REPO_ROOT / "results" / "raw" / "hazard3_irq_smoke"
OUT_CSV = REPO_ROOT / "results" / "processed" / "hazard3_irq_smoke.csv"
OUT_MD = REPO_ROOT / "docs" / "hazard3_irq_smoke.md"
FIRMWARE = REPO_ROOT / "firmware" / "hazard3_irq_smoke" / "hazard3_irq_smoke.S"
LINKER = REPO_ROOT / "firmware" / "hazard3_irq_smoke" / "linker.ld"
TB = REPO_ROOT / "tb" / "system" / "tb_hazard3_irq_smoke.v"
HDL = REPO_ROOT / "third_party" / "hazard3" / "hdl"
FIELDS = [
    "check",
    "status",
    "cycles",
    "request_writes",
    "isr_writes",
    "isr_value",
    "ack_writes",
    "done_value",
    "irq_final",
    "raw_log",
    "notes",
]
PASS_RE = re.compile(
    r"HAZARD3_IRQ_SMOKE_PASS cycles=(?P<cycles>\d+) "
    r"request_writes=(?P<request>\d+) isr_writes=(?P<isr>\d+) isr_value=(?P<isr_value>\d+) "
    r"ack_writes=(?P<ack>\d+) done_value=(?P<done>\d+) irq_final=(?P<irq>\d+)"
)


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    row = _blocked_row("not run")
    tools = _find_tools()
    missing = [name for name, value in tools.items() if not value]
    if missing:
        row = _blocked_row(f"missing tools: {', '.join(missing)}")
    else:
        build = _build_firmware(tools)
        if build.returncode != 0:
            row = _blocked_row(f"firmware build failed; see {_rel(RAW_DIR / 'firmware_build.txt')}")
        else:
            _convert_verilog_hex_to_mem(BUILD_DIR / "hazard3_irq_smoke.hex", BUILD_DIR / "hazard3_irq_smoke.mem")
            compile_result = _compile_sim(tools)
            if compile_result.returncode != 0:
                row = _blocked_row(f"Icarus compile failed; see {_rel(RAW_DIR / 'iverilog_compile.txt')}")
            else:
                row = _run_sim(tools)
    rows = [row]
    _write_csv(rows)
    _write_doc(rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OUT_MD)}")
    print(f"HAZARD3_IRQ_SMOKE status={row['status']}")
    return 0 if row["status"] == "PASS" else 1


def _find_tools() -> dict[str, str | None]:
    bin_dirs = [path for path in (REPO_ROOT / ".tools" / "toolchains").glob("**/bin") if path.is_dir()]
    gcc = _find_named_tool(("riscv-none-elf-gcc.exe", "riscv64-unknown-elf-gcc.exe"), bin_dirs)
    objcopy = _find_named_tool(("riscv-none-elf-objcopy.exe", "riscv64-unknown-elf-objcopy.exe"), bin_dirs)
    oss_bin = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite" / "bin"
    iverilog = _first_existing([oss_bin / "iverilog.exe"]) or shutil.which("iverilog")
    vvp = _first_existing([oss_bin / "vvp.exe"]) or shutil.which("vvp")
    return {"gcc": gcc, "objcopy": objcopy, "iverilog": iverilog, "vvp": vvp}


def _build_firmware(tools: dict[str, str | None]) -> subprocess.CompletedProcess[str]:
    elf = BUILD_DIR / "hazard3_irq_smoke.elf"
    hex_path = BUILD_DIR / "hazard3_irq_smoke.hex"
    map_path = BUILD_DIR / "hazard3_irq_smoke.map"
    cmd = [
        tools["gcc"] or "",
        "-march=rv32i_zicsr",
        "-mabi=ilp32",
        "-ffreestanding",
        "-fno-builtin",
        "-nostdlib",
        "-nostartfiles",
        "-Wall",
        "-Wextra",
        str(FIRMWARE),
        "-T",
        str(LINKER),
        f"-Wl,-Map,{map_path}",
        "-o",
        str(elf),
    ]
    completed = _run(cmd, RAW_DIR / "firmware_build.txt", env=_tool_env(tools["gcc"]))
    if completed.returncode == 0:
        objcopy_cmd = [tools["objcopy"] or "", "-O", "verilog", "--verilog-data-width=4", str(elf), str(hex_path)]
        objcopy_result = _run(objcopy_cmd, RAW_DIR / "firmware_objcopy.txt", env=_tool_env(tools["objcopy"]))
        if objcopy_result.returncode != 0:
            return objcopy_result
    return completed


def _compile_sim(tools: dict[str, str | None]) -> subprocess.CompletedProcess[str]:
    files = [str((HDL / line.split(maxsplit=1)[1]).relative_to(REPO_ROOT)) for line in _read(HDL / "hazard3.f").splitlines() if line.startswith("file ")]
    cmd = [
        tools["iverilog"] or "",
        "-g2012",
        "-I",
        "third_party/hazard3/hdl",
        "-o",
        str(BUILD_DIR / "tb_hazard3_irq_smoke.vvp"),
        str(TB.relative_to(REPO_ROOT)),
        *files,
    ]
    return _run(cmd, RAW_DIR / "iverilog_compile.txt", env=_tool_env(tools["iverilog"]))


def _run_sim(tools: dict[str, str | None]) -> dict[str, str]:
    log = RAW_DIR / "vvp_run.txt"
    cmd = [
        tools["vvp"] or "",
        str(BUILD_DIR / "tb_hazard3_irq_smoke.vvp"),
        f"+MEMFILE={_rel(BUILD_DIR / 'hazard3_irq_smoke.mem')}",
        "+MAX_CYCLES=2000",
    ]
    completed = _run(cmd, log, env=_tool_env(tools["vvp"]))
    text = _read(log)
    match = PASS_RE.search(text)
    status = (
        "PASS"
        if completed.returncode == 0
        and match
        and match.group("request") == "1"
        and match.group("isr") == "1"
        and match.group("isr_value") == "1"
        and match.group("ack") == "1"
        and match.group("done") == "1"
        and match.group("irq") == "0"
        else "FAIL"
    )
    return {
        "check": "hazard3_true_isr_smoke",
        "status": status,
        "cycles": match.group("cycles") if match else "NA",
        "request_writes": match.group("request") if match else "NA",
        "isr_writes": match.group("isr") if match else "NA",
        "isr_value": match.group("isr_value") if match else "NA",
        "ack_writes": match.group("ack") if match else "NA",
        "done_value": match.group("done") if match else "NA",
        "irq_final": match.group("irq") if match else "NA",
        "raw_log": _rel(log),
        "notes": "Hazard3 executed a standard machine external interrupt handler, acknowledged the IRQ from the handler, returned with mret, and foreground code wrote done." if status == "PASS" else _last_line(text),
    }


def _convert_verilog_hex_to_mem(source: Path, dest: Path) -> None:
    words: dict[int, int] = {}
    byte_buffer: dict[int, int] = {}
    address = 0
    for raw in source.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split()
        if not parts:
            continue
        if parts[0].startswith("@"):
            address = int(parts[0][1:], 16)
            parts = parts[1:]
        for token in parts:
            value = int(token, 16)
            if len(token) <= 2:
                byte_buffer[address] = value
                address += 1
            else:
                words[address] = value
                address += 1
    for byte_addr, value in byte_buffer.items():
        index = byte_addr // 4
        shift = (byte_addr % 4) * 8
        words[index] = (words.get(index, 0) & ~(0xFF << shift)) | (value << shift)
    lines = [f"@{index:08x} {words[index]:08x}" for index in sorted(words)]
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run(cmd: list[str], log: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text((completed.stdout or "").strip() + "\n", encoding="utf-8")
    return completed


def _tool_env(tool: str | None) -> dict[str, str]:
    env = os.environ.copy()
    if tool:
        env["PATH"] = str(Path(tool).parent) + os.pathsep + env.get("PATH", "")
    oss = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite"
    if oss.exists():
        suite = _short_path(oss)
        env["PATH"] = os.pathsep.join([str(suite / "bin"), str(suite / "lib"), env.get("PATH", "")])
    return env


def _write_csv(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_doc(rows: list[dict[str, str]]) -> None:
    row = rows[0]
    lines = [
        "# Hazard3 IRQ Smoke",
        "",
        f"Status: `{row['status']}`.",
        "",
        "This focused smoke builds a tiny RV32I+Zicsr firmware image for the vendored Hazard3 core, asserts a machine external interrupt through a simple AHB memory/MMIO shell, requires the ISR to acknowledge the interrupt, and requires foreground code to write a done marker after returning through `mret`.",
        "",
        "| Check | Status | Cycles | ISR writes | Ack writes | Done | IRQ final | Evidence |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        f"| `{row['check']}` | `{row['status']}` | {row['cycles']} | {row['isr_writes']} | {row['ack_writes']} | {row['done_value']} | {row['irq_final']} | `{row['raw_log']}` |",
        "",
        "Allowed from this evidence:",
        "",
        "- The vendored Hazard3 candidate can execute a real machine external interrupt handler in a focused Icarus testbench.",
        "- The handler uses standard CSR interrupt setup and `mret`, not PicoRV32 custom IRQ instructions.",
        "",
        "Do not claim from this evidence:",
        "",
        "- ReplayCapsule wrapping around Hazard3.",
        "- Hazard3 ReplayCapsule record/replay or v2 MMIO+IRQ replay-consumer stimulus.",
        "- Board/silicon integration.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _blocked_row(notes: str) -> dict[str, str]:
    return {
        "check": "hazard3_true_isr_smoke",
        "status": "BLOCKED",
        "cycles": "NA",
        "request_writes": "NA",
        "isr_writes": "NA",
        "isr_value": "NA",
        "ack_writes": "NA",
        "done_value": "NA",
        "irq_final": "NA",
        "raw_log": "",
        "notes": notes,
    }


def _find_named_tool(names: tuple[str, ...], bin_dirs: list[Path]) -> str | None:
    for bin_dir in bin_dirs:
        for name in names:
            candidate = bin_dir / name
            if candidate.exists():
                return str(candidate)
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def _first_existing(paths: list[Path]) -> str | None:
    for path in paths:
        if path.exists():
            return str(_short_path(path))
    return None


def _short_path(path: Path) -> Path:
    if os.name != "nt":
        return path
    try:
        buffer = ctypes.create_unicode_buffer(1024)
        result = ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, len(buffer))
        if result:
            return Path(buffer.value)
    except Exception:
        pass
    return path


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "no output"


if __name__ == "__main__":
    raise SystemExit(main())
