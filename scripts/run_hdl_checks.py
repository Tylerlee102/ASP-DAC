#!/usr/bin/env python3
"""Run available HDL frontend checks without requiring system-wide installs."""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "results/raw"
OUT_CSV = REPO_ROOT / "results/processed/hdl_checks.csv"
BUILD_DIR = REPO_ROOT / ".tools/hdl_checks"
OSS_CAD_SUITE = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"


@dataclass(frozen=True)
class Tool:
    command: str
    label: str
    env: dict[str, str]


@dataclass(frozen=True)
class IverilogTest:
    name: str
    workdir: Path
    sources: tuple[str, ...]
    include_dirs: tuple[str, ...]
    run_args: tuple[str, ...] = field(default_factory=tuple)
    defines: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class VerilatorLintTarget:
    name: str
    top: str
    sources: tuple[str, ...]
    include_dirs: tuple[str, ...]


IVERILOG_TESTS = (
    IverilogTest(
        name="tb_property_checker",
        workdir=Path("tb/system"),
        sources=("tb_property_checker.sv", "../../rtl/property_checker.sv"),
        include_dirs=("../../rtl",),
    ),
    IverilogTest(
        name="tb_capsule_buffer",
        workdir=Path("tb/system"),
        sources=("tb_capsule_buffer.sv", "../../rtl/capsule_buffer.sv"),
        include_dirs=("../../rtl",),
    ),
    IverilogTest(
        name="tb_picorv32_sensor_threshold_smoke",
        workdir=Path("tb/system"),
        sources=(
            "tb_picorv32_wrapper_smoke.sv",
            "../../third_party/picorv32/picorv32.v",
            "../../rtl/event_tap.sv",
            "../../rtl/event_classifier.sv",
            "../../rtl/capsule_buffer.sv",
            "../../rtl/property_checker.sv",
            "../../rtl/event_slicer.sv",
            "../../rtl/hash_signature.sv",
            "../../rtl/replay_capsule_top.sv",
            "../../rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
        ),
        include_dirs=("../../rtl", "../../rtl/rv32i_integration", "../../third_party/picorv32"),
        run_args=(
            "+MEMFILE=firmware/build/sensor_threshold_bug/failing.mem",
            "+EXPECTED_PROPERTY=3",
            "+SENSOR_VALUE=850",
            "+COMMAND_VALUE=0",
        ),
    ),
    IverilogTest(
        name="tb_picorv32_mmio_ordering_smoke",
        workdir=Path("tb/system"),
        sources=(
            "tb_picorv32_wrapper_smoke.sv",
            "../../third_party/picorv32/picorv32.v",
            "../../rtl/event_tap.sv",
            "../../rtl/event_classifier.sv",
            "../../rtl/capsule_buffer.sv",
            "../../rtl/property_checker.sv",
            "../../rtl/event_slicer.sv",
            "../../rtl/hash_signature.sv",
            "../../rtl/replay_capsule_top.sv",
            "../../rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
        ),
        include_dirs=("../../rtl", "../../rtl/rv32i_integration", "../../third_party/picorv32"),
        run_args=(
            "+MEMFILE=firmware/build/mmio_ordering_bug/failing.mem",
            "+EXPECTED_PROPERTY=5",
            "+SENSOR_VALUE=850",
            "+COMMAND_VALUE=0",
        ),
    ),
    IverilogTest(
        name="tb_picorv32_stack_corruption_smoke",
        workdir=Path("tb/system"),
        sources=(
            "tb_picorv32_wrapper_smoke.sv",
            "../../third_party/picorv32/picorv32.v",
            "../../rtl/event_tap.sv",
            "../../rtl/event_classifier.sv",
            "../../rtl/capsule_buffer.sv",
            "../../rtl/property_checker.sv",
            "../../rtl/event_slicer.sv",
            "../../rtl/hash_signature.sv",
            "../../rtl/replay_capsule_top.sv",
            "../../rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
        ),
        include_dirs=("../../rtl", "../../rtl/rv32i_integration", "../../third_party/picorv32"),
        run_args=(
            "+MEMFILE=firmware/build/stack_corruption_bug/failing.mem",
            "+EXPECTED_PROPERTY=4",
            "+SENSOR_VALUE=850",
            "+COMMAND_VALUE=0",
        ),
    ),
    IverilogTest(
        name="tb_picorv32_uart_command_smoke",
        workdir=Path("tb/system"),
        sources=(
            "tb_picorv32_wrapper_smoke.sv",
            "../../third_party/picorv32/picorv32.v",
            "../../rtl/event_tap.sv",
            "../../rtl/event_classifier.sv",
            "../../rtl/capsule_buffer.sv",
            "../../rtl/property_checker.sv",
            "../../rtl/event_slicer.sv",
            "../../rtl/hash_signature.sv",
            "../../rtl/replay_capsule_top.sv",
            "../../rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
        ),
        include_dirs=("../../rtl", "../../rtl/rv32i_integration", "../../third_party/picorv32"),
        run_args=(
            "+MEMFILE=firmware/build/uart_command_bug/failing.mem",
            "+EXPECTED_PROPERTY=1",
            "+SENSOR_VALUE=850",
            "+COMMAND_VALUE=85",
        ),
    ),
    IverilogTest(
        name="tb_picorv32_watchdog_timeout_smoke",
        workdir=Path("tb/system"),
        sources=(
            "tb_picorv32_wrapper_smoke.sv",
            "../../third_party/picorv32/picorv32.v",
            "../../rtl/event_tap.sv",
            "../../rtl/event_classifier.sv",
            "../../rtl/capsule_buffer.sv",
            "../../rtl/property_checker.sv",
            "../../rtl/event_slicer.sv",
            "../../rtl/hash_signature.sv",
            "../../rtl/replay_capsule_top.sv",
            "../../rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
        ),
        include_dirs=("../../rtl", "../../rtl/rv32i_integration", "../../third_party/picorv32"),
        run_args=(
            "+MEMFILE=firmware/build/watchdog_timeout_bug/failing.mem",
            "+EXPECTED_PROPERTY=6",
            "+SENSOR_VALUE=850",
            "+COMMAND_VALUE=0",
            "+MAX_CYCLES=900",
        ),
        defines=("RC_ENABLE_WATCHDOG",),
    ),
)


COMMON_RTL = (
    "rtl/event_pkg.sv",
    "rtl/event_tap.sv",
    "rtl/event_classifier.sv",
    "rtl/capsule_buffer.sv",
    "rtl/property_checker.sv",
    "rtl/event_slicer.sv",
    "rtl/hash_signature.sv",
    "rtl/replay_capsule_top.sv",
)


VERILATOR_TARGETS = (
    VerilatorLintTarget(
        name="verilator_lint_replay_capsule_top",
        top="replay_capsule_top",
        sources=COMMON_RTL,
        include_dirs=("rtl",),
    ),
    VerilatorLintTarget(
        name="verilator_lint_picorv32_wrapper",
        top="picorv32_replaycapsule_wrapper",
        sources=("third_party/picorv32/picorv32.v", *COMMON_RTL, "rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv"),
        include_dirs=("rtl", "rtl/rv32i_integration", "third_party/picorv32"),
    ),
)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    failures: list[str] = []
    _run_iverilog_tests(rows, failures)
    _run_verilator_lint(rows, failures)
    _write_rows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if failures else 0


def _run_iverilog_tests(rows: list[dict[str, str]], failures: list[str]) -> None:
    iverilog = _find_tool("iverilog")
    vvp = _find_tool("vvp")
    if not iverilog or not vvp:
        for test in IVERILOG_TESTS:
            rows.append(_row(test.name, "TODO", "iverilog/vvp", "", "Icarus Verilog or vvp not available"))
        return

    for test in IVERILOG_TESTS:
        cwd = REPO_ROOT / test.workdir
        output_path = BUILD_DIR / f"{test.name}.vvp"
        compile_log = RAW_DIR / f"{test.name}_iverilog_compile.txt"
        run_log = RAW_DIR / f"{test.name}_vvp_run.txt"
        compile_cmd = [iverilog.command, "-g2012"]
        for include_dir in test.include_dirs:
            compile_cmd.extend(["-I", include_dir])
        for define in test.defines:
            compile_cmd.append(f"-D{define}")
        compile_cmd.extend(["-o", os.path.relpath(output_path, cwd), *test.sources])
        compile_result = _run(compile_cmd, cwd=cwd, env=iverilog.env)
        compile_log.write_text(_clean_log(compile_result.stdout) or "compile passed without output\n", encoding="utf-8")
        if compile_result.returncode != 0:
            failures.append(f"{test.name} Icarus compile failed")
            rows.append(_row(test.name, "FAIL", iverilog.label, str(compile_log.relative_to(REPO_ROOT)), "compile failed"))
            continue

        run_cmd = [vvp.command, os.path.relpath(output_path, REPO_ROOT), *test.run_args]
        run_result = _run(run_cmd, cwd=REPO_ROOT, env=vvp.env)
        run_log.write_text(_clean_log(run_result.stdout), encoding="utf-8")
        if run_result.returncode != 0:
            failures.append(f"{test.name} vvp run failed")
            rows.append(_row(test.name, "FAIL", vvp.label, str(run_log.relative_to(REPO_ROOT)), "simulation failed"))
            continue

        rows.append(_row(test.name, "PASS", f"{iverilog.label}+{vvp.label}", str(run_log.relative_to(REPO_ROOT)), "compile and simulation passed"))


def _run_verilator_lint(rows: list[dict[str, str]], failures: list[str]) -> None:
    verilator = _find_tool("verilator")
    if not verilator:
        for target in VERILATOR_TARGETS:
            rows.append(_row(target.name, "TODO", "verilator", "", "Verilator not available"))
        return

    for target in VERILATOR_TARGETS:
        log_path = RAW_DIR / f"{target.name}.txt"
        cmd = [verilator.command, "--sv", "--lint-only"]
        for include_dir in target.include_dirs:
            cmd.append(f"-I{include_dir}")
        cmd.extend(["--top-module", target.top, *target.sources])
        result = _run(cmd, cwd=REPO_ROOT, env=verilator.env)
        log_path.write_text(_clean_log(result.stdout), encoding="utf-8")
        if result.returncode != 0:
            failures.append(f"{target.name} failed")
            rows.append(_row(target.name, "FAIL", verilator.label, str(log_path.relative_to(REPO_ROOT)), "lint failed"))
        else:
            rows.append(_row(target.name, "PASS", verilator.label, str(log_path.relative_to(REPO_ROOT)), "lint-only frontend check passed"))


def _find_tool(name: str) -> Tool | None:
    system_tool = shutil.which(name)
    if system_tool:
        return Tool(system_tool, name, dict(os.environ))

    local_name = "verilator_bin.exe" if name == "verilator" else f"{name}.exe"
    local_path = OSS_CAD_SUITE / "bin" / local_name
    if local_path.exists():
        return Tool(str(_short_path(local_path)), f"oss-cad-suite:{name}", _oss_env(verilator=name == "verilator"))

    return None


def _oss_env(verilator: bool = False) -> dict[str, str]:
    env = dict(os.environ)
    suite = _short_path(OSS_CAD_SUITE)
    env["PATH"] = os.pathsep.join([str(suite / "bin"), str(suite / "lib"), env.get("PATH", "")])
    if verilator:
        env["VERILATOR_ROOT"] = str(suite / "share" / "verilator")
    return env


def _short_path(path: Path) -> Path:
    if os.name != "nt":
        return path
    try:
        import ctypes

        buffer = ctypes.create_unicode_buffer(1024)
        result = ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, len(buffer))
        if result:
            return Path(buffer.value)
    except Exception:
        pass
    return path


def _run(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _clean_log(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
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
