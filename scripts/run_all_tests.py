#!/usr/bin/env python3
"""Run available ReplayCapsule-RV checks without fabricating unavailable results."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN_CSV = REPO_ROOT / "results/processed/toolchain_status.csv"
LOCAL_WINLIBS_BIN = REPO_ROOT / ".tools" / "winlibs" / "mingw64" / "bin"

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
    "scripts/audit_claims.py",
    "scripts/audit_paper_numbers.py",
    "scripts/audit_todos.py",
    "scripts/build_firmware.py",
    "scripts/build_paper.py",
    "scripts/build_firmware_images.py",
    "scripts/collect_trace_sizes.py",
    "scripts/check_rtl_firmware_alignment.py",
    "scripts/check_toolchain.py",
    "scripts/export_rtl_capsules.py",
    "scripts/generate_conference_evidence_tables.py",
    "scripts/generate_submission_docs.py",
    "scripts/package_artifact.py",
    "scripts/parse_synthesis_reports.py",
    "scripts/run_ablations.py",
    "scripts/run_full_rtl_replay.py",
    "scripts/run_full_rtl_negative.py",
    "scripts/run_runtime_overhead.py",
    "scripts/run_formal_checks.py",
    "scripts/run_hdl_checks.py",
    "scripts/run_mapped_synthesis.py",
    "scripts/summarize_picorv32_smokes.py",
    "scripts/run_randomized_interrupt_campaign.py",
    "scripts/summarize_randomized_interrupt_campaign.py",
    "scripts/run_replay_negative_tests.py",
    "scripts/run_replay_experiments.py",
    "scripts/run_rtl_smoke_ablations.py",
    "scripts/synth_yosys.py",
    "scripts/make_figures.py",
    "scripts/render_paper_tables.py",
    "scripts/summarize_evaluation_metrics.py",
    "scripts/summarize_artifact_manifest.py",
    "scripts/summarize_benchmark_coverage.py",
    "scripts/summarize_proof_obligations.py",
    "scripts/summarize_overflow_contracts.py",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--final-package",
        action="store_true",
        help="verify final generated evidence/package outputs without rerunning the full toolchain",
    )
    args = parser.parse_args()
    if args.final_package:
        return _run_final_package_checks()

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
    _run_subprocess(
        rows,
        failures,
        "firmware_build",
        [sys.executable, "scripts/build_firmware.py"],
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
        "picorv32_smoke_summary",
        [sys.executable, "scripts/summarize_picorv32_smokes.py"],
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
        "randomized_interrupt_summary",
        [sys.executable, "scripts/summarize_randomized_interrupt_campaign.py"],
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
        "overflow_contracts",
        [sys.executable, "scripts/summarize_overflow_contracts.py"],
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
        "full_rtl_replay_status",
        [sys.executable, "scripts/run_full_rtl_replay.py", "--allow-fallback"],
    )
    _run_subprocess(
        rows,
        failures,
        "full_rtl_negative_status",
        [sys.executable, "scripts/run_full_rtl_negative.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "runtime_overhead_status",
        [sys.executable, "scripts/run_runtime_overhead.py"],
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
        "conference_evidence_tables",
        [sys.executable, "scripts/generate_conference_evidence_tables.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "mapped_synthesis",
        [sys.executable, "scripts/run_mapped_synthesis.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "benchmark_coverage",
        [sys.executable, "scripts/summarize_benchmark_coverage.py"],
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
        "paper_build_status",
        [sys.executable, "scripts/build_paper.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "figure_generation",
        [sys.executable, "scripts/make_figures.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "submission_doc_generation",
        [sys.executable, "scripts/generate_submission_docs.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "claim_audit",
        [sys.executable, "scripts/audit_claims.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "paper_number_audit",
        [sys.executable, "scripts/audit_paper_numbers.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "todo_audit",
        [sys.executable, "scripts/audit_todos.py"],
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
    _write_toolchain_status(rows)
    rows.append(_row("toolchain_status", "PASS", f"WROTE {_rel(TOOLCHAIN_CSV)}"))
    _run_subprocess_status_only(
        rows,
        "toolchain_check_full_rtl",
        [sys.executable, "scripts/check_toolchain.py", "--gate", "full-rtl-replay"],
    )
    _run_subprocess(
        rows,
        failures,
        "artifact_manifest",
        [sys.executable, "scripts/summarize_artifact_manifest.py"],
    )
    _run_subprocess(
        rows,
        failures,
        "artifact_package",
        [sys.executable, "scripts/package_artifact.py"],
    )
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


def _run_final_package_checks() -> int:
    rows: list[dict[str, str]] = []
    failures: list[str] = []

    firmware = _read_csv("results/processed/firmware_build.csv", rows, failures)
    compiler_pass = [
        row
        for row in firmware
        if row.get("build_status") == "PASS" and row.get("firmware_source") == "compiler_c"
    ]
    _expect(rows, failures, "final:compiler_firmware", len(compiler_pass) == 15, f"{len(compiler_pass)}/15 compiler-backed rows PASS")

    replay = _read_csv("results/processed/full_rtl_replay.csv", rows, failures)
    replay_pass = [
        row
        for row in replay
        if row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
        and row.get("compiler_backed") == "true"
        and row.get("firmware_source") == "compiler_c"
    ]
    _expect(rows, failures, "final:full_rtl_replay", len(replay_pass) == 45, f"{len(replay_pass)}/45 compiler-backed replay rows PASS")

    negative = _read_csv("results/processed/full_rtl_replay_negative.csv", rows, failures)
    unexpected = [row for row in negative if row.get("actual_result") in {"ACCEPT", "FAIL"}]
    rejected = [row for row in negative if row.get("actual_result") == "REJECT"]
    not_applicable = [row for row in negative if row.get("actual_result") == "NA"]
    _expect(
        rows,
        failures,
        "final:negative_replay",
        not unexpected and len(rejected) == 10 and len(not_applicable) == 2,
        f"rejected={len(rejected)} unexpected={len(unexpected)} na={len(not_applicable)}",
    )

    runtime = _read_csv("results/processed/runtime_overhead_summary.csv", rows, failures)
    measured_runtime = [row for row in runtime if row.get("status") == "MEASURED"]
    _expect(rows, failures, "final:runtime_overhead", len(measured_runtime) >= 9, f"{len(measured_runtime)} measured summary rows")

    mapped_summary = _read_csv("results/processed/full_core_mapped_summary.csv", rows, failures)
    mapped_pass = any(
        row.get("status") == "PASS"
        and row.get("target") == "ecp5-85k"
        and row.get("overhead_claim_allowed") == "yes"
        and row.get("baseline_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("recorder_presence_status") == "PASS"
        for row in mapped_summary
    )
    v2_mapped_pass, v2_mapped_detail = _v2_measured_mapped_status(rows, failures)
    _expect(
        rows,
        failures,
        "final:mapped_same_target",
        mapped_pass or v2_mapped_pass,
        "legacy ECP5-85K same-target mapped overhead row or " + v2_mapped_detail,
    )

    mapped_synth = _read_csv("results/processed/mapped_synthesis.csv", rows, failures)
    mapped_designs = {row.get("design"): row for row in mapped_synth if row.get("status") == "PASS" and row.get("target") == "ecp5-85k"}
    v2_designs = _v2_measured_designs()
    _expect(
        rows,
        failures,
        "final:mapped_design_rows",
        {"full_core_baseline_board", "full_core_replaycapsule_board"}.issubset(mapped_designs)
        or {"full_core_baseline_board", "full_core_v2_core_board", "full_core_v2_hashed_board", "full_core_v2_full_board"}.issubset(v2_designs),
        ", ".join(sorted(mapped_designs)) or ", ".join(sorted(v2_designs)) or "no PASS rows",
    )

    presence = _read_csv("results/processed/mapped_recorder_presence.csv", rows, failures)
    v2_presence = _v2_measured_presence_configs()
    _expect(
        rows,
        failures,
        "final:recorder_presence",
        any(row.get("status") == "PASS" for row in presence) or {"core", "hashed", "full"} <= v2_presence,
        "legacy recorder presence PASS or v2 presence configs=" + ",".join(sorted(v2_presence)),
    )

    paper_status = _read_csv("results/processed/paper_build_status.csv", rows, failures)
    paper_pass = any(row.get("target") == "paper/main.pdf" and row.get("status") == "PASS" for row in paper_status)
    _expect(rows, failures, "final:paper_pdf", paper_pass and (REPO_ROOT / "paper/main.pdf").exists(), "paper/main.pdf PASS and present")

    claim_audit = _read_csv("results/processed/claim_audit.csv", rows, failures)
    claim_reviews = [row for row in claim_audit if row.get("status") == "REVIEW"]
    _expect(rows, failures, "final:claim_audit", not claim_reviews, f"REVIEW rows={len(claim_reviews)}")

    number_audit = _read_csv("results/processed/paper_number_audit.csv", rows, failures)
    number_failures = [row for row in number_audit if row.get("status") == "FAIL"]
    _expect(rows, failures, "final:number_audit", not number_failures, f"FAIL rows={len(number_failures)}")

    todo_audit = _read_csv("results/processed/todo_audit.csv", rows, failures)
    todo_failures = [row for row in todo_audit if row.get("status") == "FAIL"]
    _expect(rows, failures, "final:todo_audit", not todo_failures, f"FAIL rows={len(todo_failures)}")

    manifest = _read_csv("results/processed/artifact_manifest.csv", rows, failures)
    missing_manifest = [
        row
        for row in manifest
        if row.get("required_for_local_gate") == "yes" and row.get("status") == "MISSING"
    ]
    _expect(rows, failures, "final:artifact_manifest", not missing_manifest, f"missing required rows={len(missing_manifest)}")

    artifact_zip = REPO_ROOT / "dist/replaycapsule-rv-artifact.zip"
    _expect(rows, failures, "final:artifact_zip", artifact_zip.exists(), _rel(artifact_zip) if artifact_zip.exists() else "missing")

    final_lock = REPO_ROOT / "results/debug/final_submission_lock"
    _expect(rows, failures, "final:evidence_lock", final_lock.exists(), _rel(final_lock) if final_lock.exists() else "missing")

    _write_summary(rows)
    for row in rows:
        detail = f" - {row['detail']}" if row["detail"] else ""
        print(f"{row['status']}: {row['name']}{detail}")
    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    return 0


def _v2_measured_mapped_status(rows: list[dict[str, str]], failures: list[str]) -> tuple[bool, str]:
    scaling = _read_csv("results/processed/mapped_scaling_v2_measured.csv", rows, failures)
    presence = _read_csv("results/processed/mapped_recorder_presence_v2_measured.csv", rows, failures)
    overhead = _read_csv("results/processed/mapped_scaling_overhead_v2_measured.csv", rows, failures)
    claim_configs = {"core", "hashed"}
    baseline_pass = any(
        row.get("architecture") == "baseline"
        and row.get("target") == "ecp5-85k"
        and row.get("status") == "PASS"
        for row in scaling
    )
    mapped_configs = {
        row.get("recorder_config")
        for row in scaling
        if row.get("architecture") == "v2" and row.get("target") == "ecp5-85k" and row.get("status") == "PASS"
    }
    presence_configs = {
        row.get("recorder_config")
        for row in presence
        if row.get("target") == "ecp5-85k"
        and row.get("status") == "PASS"
        and row.get("recorder_present") == "true"
    }
    overhead_configs = {
        row.get("recorder_config")
        for row in overhead
        if row.get("target") == "ecp5-85k" and row.get("claim_allowed") == "yes"
    }
    passed = baseline_pass and claim_configs <= mapped_configs and claim_configs <= presence_configs and claim_configs <= overhead_configs
    detail = (
        f"v2 measured mapped baseline={baseline_pass} mapped={len(mapped_configs & claim_configs)}/2 "
        f"presence={len(presence_configs & claim_configs)}/2 overhead={len(overhead_configs & claim_configs)}/2"
    )
    return passed, detail


def _v2_measured_designs() -> set[str]:
    path = REPO_ROOT / "results/processed/mapped_scaling_v2_measured.csv"
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row.get("design", "") for row in csv.DictReader(handle) if row.get("target") == "ecp5-85k" and row.get("status") == "PASS"}


def _v2_measured_presence_configs() -> set[str]:
    path = REPO_ROOT / "results/processed/mapped_recorder_presence_v2_measured.csv"
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row.get("recorder_config", "")
            for row in csv.DictReader(handle)
            if row.get("target") == "ecp5-85k"
            and row.get("status") == "PASS"
            and row.get("recorder_present") == "true"
        }


def _read_csv(rel: str, rows: list[dict[str, str]], failures: list[str]) -> list[dict[str, str]]:
    path = REPO_ROOT / rel
    if not path.exists():
        rows.append(_row(f"input:{rel}", "FAIL", "missing"))
        failures.append(f"missing {rel}")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        data = list(csv.DictReader(handle))
    rows.append(_row(f"input:{rel}", "PASS", f"{len(data)} rows"))
    return data


def _expect(
    rows: list[dict[str, str]],
    failures: list[str],
    name: str,
    condition: bool,
    detail: str,
) -> None:
    rows.append(_row(name, "PASS" if condition else "FAIL", detail))
    if not condition:
        failures.append(f"{name}: {detail}")


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


def _run_subprocess_status_only(
    rows: list[dict[str, str]],
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
    rows.append(_row(name, "PASS" if completed.returncode == 0 else "BLOCKED", _last_line(completed.stdout)))


def _record_tool_availability(rows: list[dict[str, str]], tool: str) -> None:
    found = shutil.which(tool)
    if found:
        rows.append(_row(f"tool:{tool}", "PASS", found))
    elif tool == "make" and (local_tool := _local_winlibs_tool(["make.exe", "mingw32-make.exe"])):
        rows.append(_row("tool:make", "PASS", f"workspace-local winlibs {local_tool.name}"))
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
    if name == "cxx" and (local_tool := _local_winlibs_tool(["g++.exe", "c++.exe", "clang++.exe"])):
        rows.append(_row("tool:cxx", "PASS", f"workspace-local winlibs {local_tool.name}"))
        return
    rows.append(_row(f"tool:{name}", "TODO", f"none found from: {', '.join(candidates)}"))


def _local_oss_cad_tool(tool: str) -> Path | None:
    suite = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite"
    local_name = "verilator_bin.exe" if tool == "verilator" else f"{tool}.exe"
    local_tool = suite / "bin" / local_name
    return local_tool if local_tool.exists() else None


def _local_winlibs_tool(names: list[str]) -> Path | None:
    for name in names:
        candidate = LOCAL_WINLIBS_BIN / name
        if candidate.exists():
            return candidate
    return None


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


def _write_toolchain_status(rows: list[dict[str, str]]) -> None:
    tool_rows = [row for row in rows if row["name"].startswith("tool:")]
    TOOLCHAIN_CSV.parent.mkdir(parents=True, exist_ok=True)
    with TOOLCHAIN_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tool", "status", "detail", "needed_for"])
        writer.writeheader()
        for row in tool_rows:
            tool = row["name"].removeprefix("tool:")
            writer.writerow(
                {
                    "tool": tool,
                    "status": row["status"],
                    "detail": row["detail"],
                    "needed_for": _tool_needed_for(tool),
                }
            )


def _tool_needed_for(tool: str) -> str:
    return {
        "verilator": "Verilator lint and future C++ simulation builds",
        "iverilog": "directed Icarus SystemVerilog simulations",
        "vvp": "directed Icarus simulation execution",
        "yosys": "generic synthesis and formal frontend",
        "sby": "bounded formal orchestration",
        "yosys-smtbmc": "bounded formal SMTBMC checks",
        "make": "full Verilator/C++ flow orchestration",
        "cxx": "full Verilator C++ simulation builds",
        "riscv64-unknown-elf-gcc": "external RISC-V bare-metal firmware compilation",
    }.get(tool, "local reproducibility")


def _row(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": _repo_relative_text(detail)}


def _last_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return _repo_relative_text(lines[-1]) if lines else ""


def _repo_relative_text(text: str) -> str:
    return text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
