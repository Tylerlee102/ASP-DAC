#!/usr/bin/env python3
"""Run available ReplayCapsule-RV checks without fabricating unavailable results."""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_RTL = [
    "rtl/event_pkg.sv",
    "rtl/event_defs.svh",
    "rtl/replay_capsule_top.sv",
    "rtl/event_tap.sv",
    "rtl/event_classifier.sv",
    "rtl/capsule_buffer.sv",
    "rtl/property_checker.sv",
    "rtl/interrupt_logger.sv",
    "rtl/mmio_logger.sv",
    "rtl/event_slicer.sv",
    "rtl/replay_control.sv",
    "rtl/registers.sv",
    "rtl/hash_signature.sv",
    "rtl/rv32i_integration/replaycapsule_soc.sv",
    "rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
    "third_party/picorv32/picorv32.v",
    "third_party/picorv32/COPYING",
]

REQUIRED_EVENT_TYPES = [
    "EV_COMMIT",
    "EV_BRANCH",
    "EV_JUMP",
    "EV_STORE",
    "EV_LOAD",
    "EV_MMIO_READ",
    "EV_MMIO_WRITE",
    "EV_INTERRUPT_ENTER",
    "EV_INTERRUPT_EXIT",
    "EV_EXTERNAL_INPUT",
    "EV_PROPERTY_FAIL",
    "EV_CHECKPOINT_HASH",
]

BUG_BENCHMARKS = [
    "bug_sensor_threshold",
    "bug_interrupt_race",
    "bug_mmio_ordering",
    "bug_stack_corruption",
    "bug_uart_command",
    "bug_watchdog_timeout",
]

BENCHMARK_IDS = [
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
]

REQUIRED_TB = [
    "tb/system/tb_property_checker.sv",
    "tb/system/tb_capsule_buffer.sv",
    "tb/system/tb_replay_control.sv",
    "tb/system/tb_event_classifier_slicer.sv",
    "tb/system/tb_hash_signature.sv",
    "tb/system/tb_event_tap.sv",
    "tb/system/tb_mmio_interrupt_loggers.sv",
    "tb/system/tb_registers.sv",
    "tb/system/tb_replaycapsule_soc.sv",
    "tb/system/tb_picorv32_wrapper_smoke.sv",
]

PYTHON_FILES = [
    "scripts/build_firmware_images.py",
    "scripts/check_rtl_firmware_alignment.py",
    "scripts/export_rtl_capsules.py",
    "scripts/run_formal_checks.py",
    "scripts/run_hdl_checks.py",
    "scripts/run_randomized_interrupt_campaign.py",
    "scripts/run_replay_negative_tests.py",
    "scripts/run_rtl_smoke_ablations.py",
    "scripts/make_figures.py",
    "scripts/render_paper_tables.py",
    "scripts/summarize_evaluation_metrics.py",
    "scripts/summarize_proof_obligations.py",
    "scripts/summarize_rtl_capsule_classes.py",
    "scripts/summarize_formal_coverage.py",
    "scripts/summarize_synthesis_overhead.py",
    "scripts/replaycapsule_model.py",
    "scripts/rv32i_firmware_sim.py",
    "scripts/static_rtl_checks.py",
    "tb/replay_testbench/capsule_parser.py",
    "tb/replay_testbench/replay_compare.py",
    "tb/replay_testbench/replay_driver.py",
]


def main() -> int:
    rows: list[dict[str, str]] = []
    failures: list[str] = []

    _check_required_files(rows, failures)
    _check_event_pkg(rows, failures)
    _check_firmware_benchmarks(rows, failures)
    _check_required_testbenches(rows, failures)
    _compile_python(rows, failures)
    _run_subprocess(
        rows,
        failures,
        "firmware_image_build",
        [sys.executable, "scripts/build_firmware_images.py"],
    )
    _check_firmware_images(rows, failures)
    _run_subprocess(
        rows,
        failures,
        "static_rtl_contract_checks",
        [sys.executable, "scripts/static_rtl_checks.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "hdl_frontend_checks",
        [sys.executable, "scripts/run_hdl_checks.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "rtl_capsule_export_compare",
        [sys.executable, "scripts/export_rtl_capsules.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "rtl_capsule_event_classes",
        [sys.executable, "scripts/summarize_rtl_capsule_classes.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "rtl_smoke_ablations",
        [sys.executable, "scripts/run_rtl_smoke_ablations.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "rtl_firmware_alignment",
        [sys.executable, "scripts/check_rtl_firmware_alignment.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "randomized_interrupt_campaign",
        [sys.executable, "scripts/run_randomized_interrupt_campaign.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "bounded_formal_checks",
        [sys.executable, "scripts/run_formal_checks.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "formal_coverage_matrix",
        [sys.executable, "scripts/summarize_formal_coverage.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "replay_driver_demo_cycle",
        [sys.executable, "tb/replay_testbench/replay_driver.py", "--demo", "--mode", "cycle-index"],
    )
    _run_subprocess(
        rows,
        failures,
        "replay_driver_demo_commit",
        [sys.executable, "tb/replay_testbench/replay_driver.py", "--demo", "--mode", "commit-index"],
    )
    _run_subprocess(
        rows,
        failures,
        "model_suite",
        [
            sys.executable,
            "scripts/replaycapsule_model.py",
            "--self-test",
            "--dump-json",
            "results/raw/phase12_sensor_threshold_trace.json",
            "--dump-suite-json",
            "results/raw/model_suite_traces.json",
        ],
    )
    _run_subprocess(
        rows,
        failures,
        "rv32i_firmware_sim",
        [
            sys.executable,
            "scripts/rv32i_firmware_sim.py",
            "--self-test",
            "--out-csv",
            "results/processed/firmware_sim_replay.csv",
            "--out-json",
            "results/raw/firmware_sim_traces.json",
        ],
    )
    _run_subprocess(
        rows,
        failures,
        "replay_experiments",
        [sys.executable, "scripts/run_replay_experiments.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "replay_negative_tests",
        [sys.executable, "scripts/run_replay_negative_tests.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "trace_size_collection",
        [sys.executable, "scripts/collect_trace_sizes.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "ablation_suite",
        [sys.executable, "scripts/run_ablations.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "proof_obligation_matrix",
        [sys.executable, "scripts/summarize_proof_obligations.py"],
    )
    _run_subprocess(rows, failures, "yosys_synthesis_probe", [sys.executable, "scripts/synth_yosys.py"])
    _run_subprocess(
        rows,
        failures,
        "synthesis_report_parse",
        [sys.executable, "scripts/parse_synthesis_reports.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "synthesis_overhead_summary",
        [sys.executable, "scripts/summarize_synthesis_overhead.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "evaluation_metrics_summary",
        [sys.executable, "scripts/summarize_evaluation_metrics.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "paper_table_generation",
        [sys.executable, "scripts/render_paper_tables.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "figure_generation",
        [sys.executable, "scripts/make_figures.py"],
    )
    _record_tool_availability(rows, "verilator")
    _record_tool_availability(rows, "iverilog")
    _record_tool_availability(rows, "vvp")
    _record_tool_availability(rows, "yosys")
    _record_tool_availability(rows, "sby")
    _record_tool_availability(rows, "yosys-smtbmc")
    _record_tool_availability(rows, "make")
    _record_any_tool_availability(rows, "cxx", ["c++", "g++", "clang++", "cl"])
    _record_tool_availability(rows, "riscv64-unknown-elf-gcc")
    _write_summary(rows)

    for row in rows:
        status = row["status"]
        detail = f" - {row['detail']}" if row["detail"] else ""
        print(f"{status}: {row['name']}{detail}")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    return 0


def _check_required_files(rows: list[dict[str, str]], failures: list[str]) -> None:
    missing = [path for path in REQUIRED_RTL if not (REPO_ROOT / path).exists()]
    if missing:
        failures.extend(f"missing required RTL file {path}" for path in missing)
        rows.append(_row("rtl_required_files", "FAIL", ", ".join(missing)))
    else:
        rows.append(_row("rtl_required_files", "PASS", f"{len(REQUIRED_RTL)} files present"))


def _check_event_pkg(rows: list[dict[str, str]], failures: list[str]) -> None:
    event_pkg = (REPO_ROOT / "rtl/event_pkg.sv").read_text(encoding="utf-8")
    missing = [name for name in REQUIRED_EVENT_TYPES if name not in event_pkg]
    if missing:
        failures.extend(f"missing event type {name}" for name in missing)
        rows.append(_row("event_type_definitions", "FAIL", ", ".join(missing)))
    else:
        rows.append(_row("event_type_definitions", "PASS", f"{len(REQUIRED_EVENT_TYPES)} event names present"))


def _check_firmware_benchmarks(rows: list[dict[str, str]], failures: list[str]) -> None:
    missing: list[str] = []
    for benchmark in BUG_BENCHMARKS:
        for filename in ["README.md", "failing.c", "fixed.c"]:
            path = REPO_ROOT / "firmware" / benchmark / filename
            if not path.exists():
                missing.append(str(path.relative_to(REPO_ROOT)))
    if missing:
        failures.extend(f"missing firmware benchmark artifact {path}" for path in missing)
        rows.append(_row("firmware_benchmark_pairs", "FAIL", ", ".join(missing)))
    else:
        rows.append(_row("firmware_benchmark_pairs", "PASS", f"{len(BUG_BENCHMARKS)} failing/fixed pairs present"))


def _check_required_testbenches(rows: list[dict[str, str]], failures: list[str]) -> None:
    missing = [path for path in REQUIRED_TB if not (REPO_ROOT / path).exists()]
    if missing:
        failures.extend(f"missing directed SystemVerilog testbench {path}" for path in missing)
        rows.append(_row("directed_sv_testbenches", "FAIL", ", ".join(missing)))
    else:
        rows.append(_row("directed_sv_testbenches", "PASS", f"{len(REQUIRED_TB)} source-present testbenches"))


def _check_firmware_images(rows: list[dict[str, str]], failures: list[str]) -> None:
    missing: list[str] = []
    for benchmark in BENCHMARK_IDS:
        for variant in ["failing", "fixed"]:
            for suffix in [".hex", ".mem", ".json"]:
                path = REPO_ROOT / "firmware" / "build" / benchmark / f"{variant}{suffix}"
                if not path.exists():
                    missing.append(str(path.relative_to(REPO_ROOT)))
    if missing:
        failures.extend(f"missing firmware image artifact {path}" for path in missing)
        rows.append(_row("firmware_image_artifacts", "FAIL", ", ".join(missing)))
    else:
        rows.append(_row("firmware_image_artifacts", "PASS", f"{len(BENCHMARK_IDS) * 2} image sets present"))


def _compile_python(rows: list[dict[str, str]], failures: list[str]) -> None:
    for path in PYTHON_FILES:
        try:
            source = (REPO_ROOT / path).read_text(encoding="utf-8")
            compile(source, path, "exec")
        except SyntaxError as exc:
            detail = f"{exc.msg} at line {exc.lineno}"
            failures.append(f"{path} does not compile: {detail}")
            rows.append(_row(f"syntax:{path}", "FAIL", detail))
        else:
            rows.append(_row(f"syntax:{path}", "PASS", ""))


def _run_subprocess(
    rows: list[dict[str, str]],
    failures: list[str],
    name: str,
    command: list[str],
) -> None:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode == 0:
        rows.append(_row(name, "PASS", _last_line(completed.stdout)))
    else:
        failures.append(f"{name} failed with exit code {completed.returncode}: {completed.stdout}")
        rows.append(_row(name, "FAIL", _last_line(completed.stdout)))


def _record_tool_availability(rows: list[dict[str, str]], tool: str) -> None:
    found = shutil.which(tool)
    if found:
        rows.append(_row(f"tool:{tool}", "PASS", found))
    elif tool == "sby" and _local_yowasp_tool("yowasp-sby.exe"):
        rows.append(_row("tool:sby", "PASS", "workspace-local yowasp-sby"))
    elif tool == "yosys-smtbmc" and _local_yowasp_tool("yowasp-yosys-smtbmc.exe"):
        rows.append(_row("tool:yosys-smtbmc", "PASS", "workspace-local yowasp-yosys-smtbmc"))
    elif tool == "yosys" and _local_yowasp_yosys():
        rows.append(_row("tool:yosys", "PASS", "workspace-local yowasp-yosys"))
    elif local_tool := _local_oss_cad_tool(tool):
        rows.append(_row(f"tool:{tool}", "PASS", f"workspace-local oss-cad-suite {local_tool.name}"))
    else:
        rows.append(_row(f"tool:{tool}", "TODO", "external tool not found locally"))


def _record_any_tool_availability(rows: list[dict[str, str]], name: str, candidates: list[str]) -> None:
    for tool in candidates:
        found = shutil.which(tool)
        if found:
            rows.append(_row(f"tool:{name}", "PASS", f"{tool}: {found}"))
            return
    rows.append(_row(f"tool:{name}", "TODO", f"none found from: {', '.join(candidates)}"))


def _local_oss_cad_tool(tool: str) -> Path | None:
    suite = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite"
    local_name = "verilator_bin.exe" if tool == "verilator" else f"{tool}.exe"
    local_tool = suite / "bin" / local_name
    return local_tool if local_tool.exists() else None


def _local_yowasp_yosys() -> bool:
    return (
        (REPO_ROOT / ".tools" / "python" / "bin" / "yowasp-yosys.exe").exists()
        and (REPO_ROOT / ".tools" / "python").exists()
    )


def _local_yowasp_tool(filename: str) -> bool:
    return (
        (REPO_ROOT / ".tools" / "python" / "bin" / filename).exists()
        and (REPO_ROOT / ".tools" / "python").exists()
    )


def _write_summary(rows: list[dict[str, str]]) -> None:
    out = REPO_ROOT / "results/processed/summary.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "status", "detail"])
        writer.writeheader()
        writer.writerows(rows)


def _row(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def _last_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


if __name__ == "__main__":
    raise SystemExit(main())
