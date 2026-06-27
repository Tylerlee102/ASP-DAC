#!/usr/bin/env python3
"""Write a repo-relative toolchain status CSV for selected gates."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/toolchain_status.csv"
OSS_CAD_SUITE = Path(os.environ.get("REPLAYCAPSULE_OSS_CAD_SUITE", REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"))
LOCAL_PYTHON = REPO_ROOT / ".tools/python"
LOCAL_PYTHON_BIN = LOCAL_PYTHON / "bin"
LOCAL_WINLIBS_BIN = REPO_ROOT / ".tools/winlibs/mingw64/bin"

FIELDNAMES = ["tool", "required_for", "available", "version", "required", "source", "notes"]


@dataclass(frozen=True)
class ToolSpec:
    tool: str
    candidates: tuple[str, ...]
    version_args: tuple[str, ...]
    required_for: tuple[str, ...]
    notes: str


TOOLS = (
    ToolSpec("python", (sys.executable,), ("--version",), ("reproduce", "full-rtl-replay", "paper"), "Python driver scripts"),
    ToolSpec("make", ("make", "gmake", "mingw32-make"), ("--version",), ("full-rtl-replay",), "top-level orchestration and Verilator build"),
    ToolSpec("g++", ("g++", "c++", "clang++"), ("--version",), ("full-rtl-replay",), "C++ compiler for Verilator harness"),
    ToolSpec("verilator", ("verilator",), ("--version",), ("full-rtl-replay",), "RTL harness build"),
    ToolSpec(
        "riscv64-unknown-elf-gcc",
        ("riscv64-unknown-elf-gcc", "riscv-none-elf-gcc", "riscv64-elf-gcc", "riscv32-unknown-elf-gcc"),
        ("--version",),
        ("firmware", "full-rtl-replay"),
        "preferred embedded RISC-V compiler; accepted aliases are bare-metal RV32-capable toolchains",
    ),
    ToolSpec(
        "riscv64-unknown-elf-objcopy",
        ("riscv64-unknown-elf-objcopy", "riscv-none-elf-objcopy", "riscv64-elf-objcopy", "riscv32-unknown-elf-objcopy"),
        ("--version",),
        ("firmware",),
        "ELF to HEX conversion",
    ),
    ToolSpec(
        "riscv64-unknown-elf-size",
        ("riscv64-unknown-elf-size", "riscv-none-elf-size", "riscv64-elf-size", "riscv32-unknown-elf-size"),
        ("--version",),
        ("firmware",),
        "compiler-backed firmware size accounting",
    ),
    ToolSpec("iverilog", ("iverilog",), ("-V",), ("rtl-smoke",), "directed Icarus simulations"),
    ToolSpec("vvp", ("vvp",), ("-V",), ("rtl-smoke",), "Icarus simulation runtime"),
    ToolSpec("yosys", ("yosys",), ("-V",), ("mapped-synthesis", "formal"), "synthesis/formal frontend"),
    ToolSpec("nextpnr-ice40", ("nextpnr-ice40",), ("--version",), ("mapped-synthesis",), "optional iCE40 mapped FPGA flow"),
    ToolSpec("nextpnr-ecp5", ("nextpnr-ecp5",), ("--version",), ("mapped-synthesis",), "optional ECP5 mapped FPGA flow"),
    ToolSpec("openroad", ("openroad",), ("-version",), ("mapped-synthesis",), "optional ASIC flow"),
    ToolSpec("latexmk", ("latexmk",), ("--version",), ("paper",), "LaTeX build wrapper"),
    ToolSpec("pdflatex", ("pdflatex",), ("--version",), ("paper",), "PDF LaTeX engine"),
    ToolSpec("lualatex", ("lualatex",), ("--version",), ("paper",), "fallback PDF LaTeX engine"),
    ToolSpec("firmware-hex-fallback", tuple(), tuple(), ("full-rtl-replay",), "existing generated HEX/MEM images can feed RTL when compiler is unavailable; fallback is not a compiler pass"),
)

GATE_ALIASES = {
    "local": ("reproduce", "rtl-smoke", "formal"),
    "test": ("reproduce", "rtl-smoke", "formal"),
    "reproduce": ("reproduce", "rtl-smoke", "formal", "firmware"),
    "firmware": ("firmware",),
    "rtl-smoke": ("rtl-smoke",),
    "full-rtl-replay": ("full-rtl-replay", "firmware"),
    "mapped-synthesis": ("mapped-synthesis",),
    "mapped": ("mapped-synthesis",),
    "paper": ("paper",),
    "all": ("reproduce", "rtl-smoke", "formal", "firmware", "full-rtl-replay", "mapped-synthesis", "paper"),
}


@dataclass(frozen=True)
class LocatedTool:
    command: str
    label: str
    env: dict[str, str] | None = None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", default="local", choices=sorted(GATE_ALIASES))
    parser.add_argument("--out", type=Path, default=OUT_CSV)
    args = parser.parse_args()

    selected = set(GATE_ALIASES[args.gate])
    rows = [_row_for_tool(tool, selected) for tool in TOOLS]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(
            "{state}: {tool} ({required_for}) - {notes}".format(
                state="PASS" if row["available"] == "yes" else "BLOCKED" if row["required"] == "yes" else "TODO",
                tool=row["tool"],
                required_for=row["required_for"],
                notes=row["notes"],
            )
        )
    print(f"WROTE {_rel(args.out)}")
    return 1 if any(row["required"] == "yes" and row["available"] == "no" for row in rows) else 0


def _row_for_tool(tool: ToolSpec, selected: set[str]) -> dict[str, str]:
    required = _is_required(tool, selected)
    if tool.tool == "firmware-hex-fallback":
        available = _firmware_fallback_available()
        fallback_required = _firmware_fallback_required(selected)
        return {
            "tool": tool.tool,
            "required_for": ",".join(tool.required_for),
            "available": "yes" if available else "no",
            "version": "generated-hex" if available else "NA",
            "required": "yes" if fallback_required else "no",
            "source": "generated-fallback" if available else "missing",
            "notes": tool.notes if available else "missing fallback HEX/MEM images; run scripts/build_firmware_images.py",
        }

    located = _find_tool(tool)
    if located is None:
        fallback_ok = tool.tool in {
            "riscv64-unknown-elf-gcc",
            "riscv64-unknown-elf-objcopy",
            "riscv64-unknown-elf-size",
        } and _firmware_fallback_required(selected)
        fallback_notes = "; firmware-hex-fallback is available for selected gate" if fallback_ok else ""
        return {
            "tool": tool.tool,
            "required_for": ",".join(tool.required_for),
            "available": "no",
            "version": "NA",
            "required": "no" if fallback_ok else "yes" if required else "no",
            "source": "missing",
            "notes": tool.notes + "; tool not found" + fallback_notes,
        }

    return {
        "tool": tool.tool,
        "required_for": ",".join(tool.required_for),
        "available": "yes",
        "version": _version(located, tool.version_args),
        "required": "yes" if required else "no",
        "source": _source_label(located.label),
        "notes": f"{tool.notes}; {located.label}",
    }


def _find_tool(tool: ToolSpec) -> LocatedTool | None:
    if tool.tool == "python":
        return LocatedTool(sys.executable, "current interpreter")
    local = _find_local_tool(tool.tool)
    if local is not None:
        return local
    for candidate in tool.candidates:
        found = shutil.which(candidate)
        if found:
            return LocatedTool(found, candidate)
    return None


def _find_local_tool(name: str) -> LocatedTool | None:
    if name == "make":
        for local_name in ("make.exe", "mingw32-make.exe"):
            path = LOCAL_WINLIBS_BIN / local_name
            if path.exists():
                return LocatedTool(str(path), f"workspace-local {_rel(path)}", _winlibs_env())
    if name == "g++":
        for local_name in ("g++.exe", "c++.exe", "clang++.exe"):
            path = LOCAL_WINLIBS_BIN / local_name
            if path.exists():
                return LocatedTool(str(path), f"workspace-local {_rel(path)}", _winlibs_env())
    if name in {"iverilog", "vvp", "nextpnr-ice40", "nextpnr-ecp5", "yosys"}:
        path = OSS_CAD_SUITE / "bin" / f"{name}.exe"
        if path.exists():
            return LocatedTool(str(path), f"workspace-local {_rel(path)}", _oss_env())
    if name == "verilator":
        for local_name in ("verilator_bin.exe", "verilator.exe", "verilator"):
            path = OSS_CAD_SUITE / "bin" / local_name
            if path.exists():
                return LocatedTool(str(path), f"workspace-local {_rel(path)}", _oss_env(verilator=True))
    if name == "yosys":
        path = LOCAL_PYTHON_BIN / "yowasp-yosys.exe"
        if path.exists():
            return LocatedTool(str(path), f"workspace-local {_rel(path)}", _yowasp_env())
    return None


def _version(tool: LocatedTool, args: tuple[str, ...]) -> str:
    if not args:
        return "NA"
    try:
        completed = subprocess.run(
            [tool.command, *args],
            cwd=REPO_ROOT,
            env=tool.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=15,
        )
    except Exception as exc:  # noqa: BLE001
        return f"version probe failed: {exc}"
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return lines[0] if lines else "version probe produced no output"


def _firmware_fallback_available() -> bool:
    build = REPO_ROOT / "firmware/build"
    required = (
        "sensor_threshold_bug",
        "interrupt_race_bug",
        "mmio_ordering_bug",
        "stack_corruption_bug",
        "uart_command_bug",
        "watchdog_timeout_bug",
    )
    return all((build / benchmark / "failing.hex").exists() and (build / benchmark / "fixed.hex").exists() for benchmark in required)


def _is_required(tool: ToolSpec, selected: set[str]) -> bool:
    if tool.tool in {"nextpnr-ice40", "nextpnr-ecp5", "openroad"} and "mapped-synthesis" in selected:
        preferred = _preferred_mapped_backend()
        return tool.tool == preferred or preferred is None
    if tool.tool in {
        "riscv64-unknown-elf-gcc",
        "riscv64-unknown-elf-objcopy",
        "riscv64-unknown-elf-size",
    } and _firmware_fallback_required(selected):
        return False
    return bool(set(tool.required_for) & selected)


def _firmware_fallback_required(selected: set[str]) -> bool:
    return bool({"firmware", "full-rtl-replay"} & selected) and not _require_compiler() and not _preferred_firmware_toolchain_available()


def _preferred_firmware_toolchain_available() -> bool:
    return _any_available(
        ("riscv64-unknown-elf-gcc", "riscv-none-elf-gcc", "riscv64-elf-gcc", "riscv32-unknown-elf-gcc")
    ) and _any_available(
        ("riscv64-unknown-elf-objcopy", "riscv-none-elf-objcopy", "riscv64-elf-objcopy", "riscv32-unknown-elf-objcopy")
    ) and _any_available(
        ("riscv64-unknown-elf-size", "riscv-none-elf-size", "riscv64-elf-size", "riscv32-unknown-elf-size")
    )


def _any_available(names: tuple[str, ...]) -> bool:
    return any(shutil.which(name) is not None for name in names)


def _require_compiler() -> bool:
    return os.environ.get("REPLAYCAPSULE_REQUIRE_COMPILER", "").strip().lower() in {"1", "true", "yes", "on"} or os.environ.get(
        "REQUIRE_COMPILER", ""
    ).strip().lower() in {"1", "true", "yes", "on"}


def _preferred_mapped_backend() -> str | None:
    for name in ("nextpnr-ice40", "nextpnr-ecp5", "openroad"):
        spec = next(tool for tool in TOOLS if tool.tool == name)
        if _find_tool(spec) is not None:
            return name
    return None


def _source_label(label: str) -> str:
    if label == "current interpreter":
        return "current-python"
    if label.startswith("workspace-local"):
        return "workspace-local"
    return "path"


def _oss_env(verilator: bool = False) -> dict[str, str]:
    env = dict(os.environ)
    parts = []
    for path in (LOCAL_WINLIBS_BIN, OSS_CAD_SUITE / "bin", OSS_CAD_SUITE / "lib"):
        if path.exists():
            parts.append(str(path))
    parts.append(env.get("PATH", ""))
    env["PATH"] = os.pathsep.join(parts)
    if verilator:
        verilator_root = OSS_CAD_SUITE / "share" / "verilator"
        if verilator_root.exists():
            env["VERILATOR_ROOT"] = str(verilator_root)
        else:
            env.pop("VERILATOR_ROOT", None)
    return env


def _winlibs_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(LOCAL_WINLIBS_BIN), env.get("PATH", "")])
    return env


def _yowasp_env() -> dict[str, str]:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(LOCAL_PYTHON) if not existing else str(LOCAL_PYTHON) + os.pathsep + existing
    return env


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return Path(path).name


if __name__ == "__main__":
    raise SystemExit(main())
