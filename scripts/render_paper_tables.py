#!/usr/bin/env python3
"""Render paper table sources from generated result CSVs."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS_CSV = REPO_ROOT / "results/processed/synthesis.csv"
SYNTHESIS_OVERHEAD_CSV = REPO_ROOT / "results/processed/synthesis_overhead.csv"
MAPPED_SYNTHESIS_CSV = REPO_ROOT / "results/processed/mapped_synthesis.csv"
REPLAY_CSV = REPO_ROOT / "results/processed/replay_experiments.csv"
TRACE_SIZES_CSV = REPO_ROOT / "results/processed/trace_sizes.csv"
EVENT_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/event_sufficiency.csv"
ABLATIONS_CSV = REPO_ROOT / "results/processed/ablations.csv"
RTL_SMOKE_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/rtl_smoke_event_sufficiency.csv"
RTL_ALIGNMENT_CSV = REPO_ROOT / "results/processed/rtl_firmware_alignment.csv"
RTL_CLASSES_CSV = REPO_ROOT / "results/processed/rtl_capsule_event_classes.csv"
FORMAL_COVERAGE_CSV = REPO_ROOT / "results/processed/formal_coverage.csv"
PROOF_OBLIGATIONS_CSV = REPO_ROOT / "results/processed/proof_obligations.csv"
EVALUATION_METRICS_CSV = REPO_ROOT / "results/processed/evaluation_metrics.csv"
FIRMWARE_BUILD_CSV = REPO_ROOT / "results/processed/firmware_build.csv"
FULL_RTL_REPLAY_CSV = REPO_ROOT / "results/processed/full_rtl_replay.csv"
FULL_RTL_NEGATIVE_CSV = REPO_ROOT / "results/processed/full_rtl_replay_negative.csv"
RUNTIME_OVERHEAD_SUMMARY_CSV = REPO_ROOT / "results/processed/runtime_overhead_summary.csv"
MAPPED_OVERHEAD_CSV = REPO_ROOT / "results/processed/mapped_overhead.csv"
MAPPED_RECORDER_PRESENCE_CSV = REPO_ROOT / "results/processed/mapped_recorder_presence.csv"
FULL_CORE_MAPPED_SUMMARY_CSV = REPO_ROOT / "results/processed/full_core_mapped_summary.csv"
PAPER_FIGURES = REPO_ROOT / "paper/figures"
PAPER_SECTIONS = REPO_ROOT / "paper/sections"

SYNTHESIS_ORDER = [
    "picorv32",
    "replay_capsule_top",
    "picorv32_replaycapsule_wrapper",
]

DESIGN_DISPLAY_NAMES = {
    "picorv32": "Baseline PicoRV32",
    "replay_capsule_top": "ReplayCapsule record-side top",
    "picorv32_replaycapsule_wrapper": "PicoRV32 + ReplayCapsule wrapper",
}

BENCHMARK_ORDER = [
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
]

BENCHMARK_DISPLAY_NAMES = {
    "sensor_threshold_bug": "Sensor threshold",
    "interrupt_race_bug": "Interrupt race",
    "mmio_ordering_bug": "MMIO ordering",
    "stack_corruption_bug": "Stack corruption",
    "uart_command_bug": "UART command",
    "watchdog_timeout_bug": "Watchdog timeout",
}


def main() -> int:
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    PAPER_SECTIONS.mkdir(parents=True, exist_ok=True)
    outputs = {
        "table01_synthesis_resources.md": _render_synthesis_table(
            _ordered_synthesis_rows(_read_rows(SYNTHESIS_CSV)),
            _read_rows(SYNTHESIS_OVERHEAD_CSV),
            _read_rows(MAPPED_SYNTHESIS_CSV),
        ),
        "table02_replay_evidence.md": _render_replay_table(
            _read_rows(REPLAY_CSV),
            _read_rows(RTL_ALIGNMENT_CSV),
            _read_rows(FULL_RTL_REPLAY_CSV),
        ),
        "table03_trace_baselines.md": _render_trace_baseline_table(
            _read_rows(TRACE_SIZES_CSV),
            _read_rows(RTL_CLASSES_CSV),
        ),
        "table04_event_sufficiency.md": _render_event_sufficiency_table(
            _read_rows(EVENT_SUFFICIENCY_CSV),
            _read_rows(ABLATIONS_CSV),
            _read_rows(RTL_SMOKE_SUFFICIENCY_CSV),
        ),
        "table05_formal_coverage.md": _render_formal_coverage_table(_read_rows(FORMAL_COVERAGE_CSV)),
        "table06_proof_obligations.md": _render_proof_obligation_table(_read_rows(PROOF_OBLIGATIONS_CSV)),
        "table07_evaluation_metrics.md": _render_evaluation_metrics_table(_read_rows(EVALUATION_METRICS_CSV)),
    }
    for name, content in outputs.items():
        (PAPER_FIGURES / name).write_text(content, encoding="utf-8")
    (PAPER_SECTIONS / "generated_numbers.tex").write_text(_render_generated_numbers(), encoding="utf-8")
    (PAPER_SECTIONS / "generated_tables.tex").write_text(_render_generated_tables(), encoding="utf-8")
    print(f"WROTE {len(outputs)} paper table(s) under {PAPER_FIGURES}")
    print(f"WROTE {PAPER_SECTIONS / 'generated_numbers.tex'}")
    print(f"WROTE {PAPER_SECTIONS / 'generated_tables.tex'}")
    return 0


def _render_synthesis_table(
    synthesis_rows: list[dict[str, str]],
    overhead_rows: list[dict[str, str]],
    mapped_rows: list[dict[str, str]],
) -> str:
    lines = [
        "# Table 1. Synthesis Resource Status",
        "",
        "Generated from `../../results/processed/synthesis.csv`, "
        "`../../results/processed/synthesis_overhead.csv`, and "
        "`../../results/processed/mapped_synthesis.csv`.",
        "",
        "Generic Yosys cell counts are measured from real local reports. "
        "Mapped rows are shown only where a real place-and-route flow produced them.",
        "",
        "| Design | Tool | Status | Generic cells | LUTs | FFs | BRAMs | Fmax MHz | Notes |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    if synthesis_rows:
        for row in synthesis_rows:
            lines.append(
                "| {design} | {tool} | {status} | {cells} | {luts} | {ffs} | {brams} | {fmax} | {notes} |".format(
                    design=_escape_cell(DESIGN_DISPLAY_NAMES.get(row.get("top", ""), row.get("top", "unknown"))),
                    tool=_escape_cell(row.get("tool", "NA")),
                    status=_escape_cell(row.get("status", "NA")),
                    cells=_escape_cell(row.get("cells", "NA")),
                    luts=_escape_cell(row.get("luts", "NA")),
                    ffs=_escape_cell(row.get("ffs", "NA")),
                    brams=_escape_cell(row.get("brams", "NA")),
                    fmax=_escape_cell(row.get("fmax_mhz", "NA")),
                    notes=_escape_cell(row.get("notes", "")),
                )
            )
    else:
        lines.append("| No synthesis rows | NA | TODO | NA | NA | NA | NA | NA | Missing synthesis CSV |")

    lines.extend(
        [
            "",
            "## Generic Cell-Overhead Context",
            "",
            "| Baseline | Instrumented build | Status | Baseline cells | Instrumented cells | Delta cells | Overhead vs baseline | Record-side cells | Notes |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    if overhead_rows:
        for row in overhead_rows:
            lines.append(
                "| {baseline} | {instrumented} | {status} | {baseline_cells} | {instrumented_cells} | {delta} | {percent} | {record_cells} | {notes} |".format(
                    baseline=_escape_cell(DESIGN_DISPLAY_NAMES.get(row.get("baseline_top", ""), row.get("baseline_top", "unknown"))),
                    instrumented=_escape_cell(
                        DESIGN_DISPLAY_NAMES.get(row.get("instrumented_top", ""), row.get("instrumented_top", "unknown"))
                    ),
                    status=_escape_cell(row.get("status", "NA")),
                    baseline_cells=_escape_cell(row.get("baseline_cells", "NA")),
                    instrumented_cells=_escape_cell(row.get("instrumented_cells", "NA")),
                    delta=_escape_cell(row.get("generic_cell_delta", "NA")),
                    percent=_percent_cell(row.get("generic_cell_overhead_percent", "NA")),
                    record_cells=_escape_cell(row.get("record_side_cells", "NA")),
                    notes=_escape_cell(row.get("notes", "")),
                )
            )
    else:
        lines.append("| No overhead row | NA | TODO | NA | NA | NA | NA | NA | Missing overhead CSV |")
    lines.extend(
        [
            "",
            "## Scoped Mapped FPGA Rows",
            "",
            "| Target | Flow | Design | Status | LUTs | FFs | BRAMs | Fmax MHz | Notes |",
            "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    if mapped_rows:
        for row in mapped_rows:
            lines.append(
                "| {target} | {flow} | {design} | {status} | {lut} | {ff} | {bram} | {fmax} | {notes} |".format(
                    target=_escape_cell(row.get("target", "NA")),
                    flow=_escape_cell(row.get("flow", "NA")),
                    design=_escape_cell(row.get("design", "NA")),
                    status=_escape_cell(row.get("status", "NA")),
                    lut=_escape_cell(row.get("lut", "NA")),
                    ff=_escape_cell(row.get("ff", "NA")),
                    bram=_escape_cell(row.get("bram", "NA")),
                    fmax=_escape_cell(row.get("fmax_mhz", "NA")),
                    notes=_escape_cell(row.get("notes", "")),
                )
            )
    else:
        lines.append("| NA | NA | No mapped rows | TODO | NA | NA | NA | NA | Missing mapped synthesis CSV |")
    return "\n".join(lines) + "\n"


def _render_replay_table(
    replay_rows: list[dict[str, str]],
    alignment_rows: list[dict[str, str]],
    full_rtl_rows: list[dict[str, str]],
) -> str:
    lines = [
        "# Table 2. Replay Evidence Status",
        "",
        "Generated from `../../results/processed/replay_experiments.csv` and "
        "`../../results/processed/rtl_firmware_alignment.csv`.",
        "",
        "Model and firmware-sim rows are commit-index replay checks. RTL-smoke rows are "
        "property/key-event alignment checks; the final row reports host-driven full RTL replay.",
        "",
        "| Benchmark | Model replay | Firmware-sim replay | RTL-smoke property alignment | RTL-smoke key-event alignment | Property ID |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for benchmark in BENCHMARK_ORDER:
        model = _find_row(replay_rows, experiment=benchmark, evidence_level="model")
        firmware = _find_row(replay_rows, experiment=f"{benchmark}_firmware_sim", evidence_level="firmware-sim")
        alignment = _find_row(alignment_rows, benchmark=benchmark, variant="failing")
        property_id = model.get("property_id") or firmware.get("property_id") or alignment.get("rtl_property_id", "NA")
        lines.append(
            "| {benchmark} | {model} | {firmware} | {property_align} | {event_align} | {property_id} |".format(
                benchmark=_escape_cell(_benchmark_name(benchmark)),
                model=_status_cell(model.get("status", "TODO"), model.get("evidence_level", "model")),
                firmware=_status_cell(firmware.get("status", "TODO"), firmware.get("evidence_level", "firmware-sim")),
                property_align=_status_cell(alignment.get("property_alignment", "TODO"), "rtl-smoke"),
                event_align=_status_cell(alignment.get("key_event_alignment", "TODO"), "rtl-smoke"),
                property_id=_escape_cell(property_id),
            )
        )
    rtl_pass = [
        row for row in full_rtl_rows
        if row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
        and row.get("firmware_source") == "compiler_c"
        and row.get("compiler_backed") == "true"
    ]
    if full_rtl_rows:
        rtl_status = "PASS" if len(rtl_pass) == len(full_rtl_rows) else "FAIL"
        rtl_notes = f"{len(rtl_pass)}/{len(full_rtl_rows)} compiler-backed host-driven Verilator rows"
    else:
        rtl_status = "TODO"
        rtl_notes = "missing full_rtl_replay.csv"
    lines.append(
        "| Full firmware-running RTL suite | {status} | {status} | NA | NA | {notes} |".format(
            status=_status_cell(rtl_status, "rtl"),
            notes=_escape_cell(rtl_notes),
        )
    )
    return "\n".join(lines) + "\n"


def _render_trace_baseline_table(trace_rows: list[dict[str, str]], rtl_class_rows: list[dict[str, str]]) -> str:
    lines = [
        "# Table 3. Trace-Size Baselines",
        "",
        "Generated from `../../results/processed/trace_sizes.csv` and "
        "`../../results/processed/rtl_capsule_event_classes.csv`.",
        "",
        "Firmware-sim rows compare baselines for the same local interpreter workload. "
        "RTL-smoke bytes are exported packet sizes only, not full benchmark-wide replay metrics.",
        "",
        "| Benchmark | Full instruction bytes | Snapshot bytes | ReplayCapsule bytes | Capsule / full-instruction | ReplayCapsule replay | RTL-smoke capsule bytes |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for benchmark in BENCHMARK_ORDER:
        full_instruction = _trace_row(trace_rows, benchmark, "full_instruction_trace", "firmware-sim")
        snapshot = _trace_row(trace_rows, benchmark, "snapshot_on_failure", "firmware-sim")
        capsule = _trace_row(trace_rows, benchmark, "property_aware_replaycapsule_rv", "firmware-sim")
        rtl_smoke = _find_row(rtl_class_rows, benchmark=benchmark, variant="failing")
        lines.append(
            "| {benchmark} | {full_bytes} | {snapshot_bytes} | {capsule_bytes} | {ratio} | {replay} | {rtl_bytes} |".format(
                benchmark=_escape_cell(_benchmark_name(benchmark)),
                full_bytes=_escape_cell(full_instruction.get("bytes", "NA")),
                snapshot_bytes=_escape_cell(snapshot.get("bytes", "NA")),
                capsule_bytes=_escape_cell(capsule.get("bytes", "NA")),
                ratio=_ratio_cell(capsule.get("bytes"), full_instruction.get("bytes")),
                replay=_status_cell(capsule.get("replay_success", "TODO"), "firmware-sim"),
                rtl_bytes=_escape_cell(rtl_smoke.get("packet_bytes", "NA")),
            )
        )
    return "\n".join(lines) + "\n"


def _render_event_sufficiency_table(
    sufficiency_rows: list[dict[str, str]],
    ablation_rows: list[dict[str, str]],
    rtl_sufficiency_rows: list[dict[str, str]],
) -> str:
    lines = [
        "# Table 4. Event-Sufficiency Ablation Summary",
        "",
        "Generated from `../../results/processed/event_sufficiency.csv`, "
        "`../../results/processed/ablations.csv`, and "
        "`../../results/processed/rtl_smoke_event_sufficiency.csv`.",
        "",
        "Model rows are commit-index replay ablations. RTL-smoke rows remove event",
        "classes from exported capsules and rerun the replay comparator; they are not",
        "full benchmark-wide RTL replay.",
        "",
        "| Benchmark | Model required classes | RTL-smoke required classes | Model event-removal ablations that break replay |",
        "| --- | --- | --- | --- |",
    ]
    for benchmark in BENCHMARK_ORDER:
        sufficiency = _find_row(sufficiency_rows, benchmark=benchmark)
        rtl_sufficiency = _find_row(rtl_sufficiency_rows, benchmark=benchmark, variant="failing")
        breaking = [
            _short_ablation(row.get("ablation", ""))
            for row in ablation_rows
            if row.get("benchmark") == benchmark
            and row.get("status") == "MEASURED"
            and row.get("replay_success") == "False"
            and row.get("ablation", "").startswith("remove_")
        ]
        lines.append(
            "| {benchmark} | {model_classes} | {rtl_classes} | {breaking} |".format(
                benchmark=_escape_cell(_benchmark_name(benchmark)),
                model_classes=_escape_cell(_format_semicolon_list(sufficiency.get("required_event_classes", "TODO"))),
                rtl_classes=_escape_cell(_format_semicolon_list(rtl_sufficiency.get("required_event_classes", "TODO"))),
                breaking=_escape_cell("; ".join(breaking) if breaking else "none observed in event-removal rows"),
            )
        )
    return "\n".join(lines) + "\n"


def _render_formal_coverage_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Table 5. Bounded Formal Coverage",
        "",
        "Generated from `../../results/processed/formal_coverage.csv`.",
        "",
        "Each row is a bounded local RTL contract check, not an end-to-end processor/replay proof.",
        "",
        "| RTL contract family | Depth | Status | Checked obligations | Explicit limit |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {family} | {depth} | {status} | {obligations} | {limit} |".format(
                family=_escape_cell(row.get("module_family", "unknown")),
                depth=_escape_cell(row.get("depth", "NA")),
                status=_status_cell(row.get("status", "TODO"), "formal-bmc"),
                obligations=_escape_cell(row.get("obligations", "NA")),
                limit=_escape_cell(row.get("explicit_limit", "NA")),
            )
        )
    if not rows:
        lines.append("| No formal coverage rows | NA | TODO | Missing formal coverage CSV | NA |")
    return "\n".join(lines) + "\n"


def _render_proof_obligation_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Table 6. Replay-Sufficiency Proof Obligations",
        "",
        "Generated from `../../results/processed/proof_obligations.csv`.",
        "",
        "This table links theorem assumptions to current evidence. It is not a",
        "mechanized end-to-end replay proof.",
        "",
        "| Obligation | Assumption | Status | Evidence level | Current limit |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {obligation} | {assumption} | {status} | {level} | {limit} |".format(
                obligation=_escape_cell(row.get("obligation_id", "unknown")),
                assumption=_escape_cell(row.get("theorem_assumption", "NA")),
                status=_escape_cell(row.get("evidence_status", "TODO")),
                level=_escape_cell(row.get("evidence_level", "NA")),
                limit=_escape_cell(row.get("current_limit", "NA")),
            )
        )
    if not rows:
        lines.append("| No proof-obligation rows | NA | TODO | NA | Missing proof-obligations CSV |")
    return "\n".join(lines) + "\n"


def _render_evaluation_metrics_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Table 7. Evaluation Metric Rollup",
        "",
        "Generated from `../../results/processed/evaluation_metrics.csv`.",
        "",
        "Metrics marked `TODO` or `BLOCKED` are unsupported rows that remain unclaimed;",
        "full RTL replay, runtime summaries, and same-target ECP5 mapped overhead are measured separately in this table.",
        "",
        "| Metric | Status | Value | Unit | Evidence level | Notes |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {metric} | {status} | {value} | {unit} | {level} | {notes} |".format(
                metric=_escape_cell(row.get("metric", "unknown")),
                status=_status_cell(row.get("status", "TODO"), row.get("evidence_level", "NA")),
                value=_escape_cell(row.get("value", "NA")),
                unit=_escape_cell(row.get("unit", "NA")),
                level=_escape_cell(row.get("evidence_level", "NA")),
                notes=_escape_cell(row.get("notes", "NA")),
            )
        )
    if not rows:
        lines.append("| No evaluation metrics | TODO | TODO | NA | NA | Missing evaluation metrics CSV |")
    return "\n".join(lines) + "\n"


def _render_generated_numbers() -> str:
    firmware_rows = _read_rows(FIRMWARE_BUILD_CSV)
    replay_rows = _read_rows(FULL_RTL_REPLAY_CSV)
    negative_rows = _read_rows(FULL_RTL_NEGATIVE_CSV)
    runtime_rows = _read_rows(RUNTIME_OVERHEAD_SUMMARY_CSV)
    mapped_rows = _read_rows(MAPPED_SYNTHESIS_CSV)
    mapped_overhead = _read_rows(MAPPED_OVERHEAD_CSV)
    mapped_summary = _read_rows(FULL_CORE_MAPPED_SUMMARY_CSV)

    replay_pass = [
        row for row in replay_rows
        if row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
    ]
    compiler_firmware = [
        row for row in firmware_rows
        if row.get("build_status") == "PASS"
        and row.get("firmware_source") == "compiler_c"
    ]
    rejected = [row for row in negative_rows if row.get("actual_result") == "REJECT"]
    unexpected_accepts = [row for row in negative_rows if row.get("actual_result") == "ACCEPT"]
    na_rows = [row for row in negative_rows if row.get("actual_result") == "NA"]
    baseline = _find_design(mapped_rows, "full_core_baseline_board")
    replay = _find_design(mapped_rows, "full_core_replaycapsule_board")

    commands = {
        "rcBenchmarks": str(len({row.get("benchmark", "") for row in firmware_rows if row.get("benchmark")})),
        "rcFirmwareImages": str(len(compiler_firmware)),
        "rcFullReplayPass": str(len(replay_pass)),
        "rcFullReplayTotal": str(len(replay_rows)),
        "rcNegativeReject": str(len(rejected)),
        "rcNegativeTotal": str(len(negative_rows)),
        "rcNegativeUnexpectedAccept": str(len(unexpected_accepts)),
        "rcNegativeNA": str(len(na_rows)),
        "rcRuntimeCycleMedian": _runtime_value(runtime_rows, "cycle_overhead_pct", "recorder_enabled_vs_baseline_no_recorder", "median"),
        "rcRuntimeCommitMedian": _runtime_value(runtime_rows, "commit_overhead_pct", "recorder_enabled_vs_baseline_no_recorder", "median"),
        "rcRuntimeWallMedian": _runtime_value(runtime_rows, "sim_wall_time_overhead_pct", "recorder_enabled_vs_baseline_no_recorder", "median"),
        "rcMappedTarget": (mapped_summary[0].get("target") if mapped_summary else "NA"),
        "rcMappedFlow": (mapped_summary[0].get("flow") if mapped_summary else "NA"),
        "rcBaselineLUT": baseline.get("lut", "NA"),
        "rcBaselineFF": baseline.get("ff", "NA"),
        "rcBaselineBRAM": baseline.get("bram", "NA"),
        "rcBaselineFmax": baseline.get("fmax_mhz", "NA"),
        "rcReplayLUT": replay.get("lut", "NA"),
        "rcReplayFF": replay.get("ff", "NA"),
        "rcReplayBRAM": replay.get("bram", "NA"),
        "rcReplayFmax": replay.get("fmax_mhz", "NA"),
        "rcMappedLUTOverhead": _overhead_value(mapped_overhead, "full_core_baseline_board_to_full_core_replaycapsule_board_lut", "percent_overhead"),
        "rcMappedFFOverhead": _overhead_value(mapped_overhead, "full_core_baseline_board_to_full_core_replaycapsule_board_ff", "percent_overhead"),
        "rcMappedBRAMOverhead": _overhead_value(mapped_overhead, "full_core_baseline_board_to_full_core_replaycapsule_board_bram", "percent_overhead"),
        "rcMappedFmaxDelta": _overhead_value(mapped_overhead, "full_core_baseline_board_to_full_core_replaycapsule_board_fmax_mhz", "percent_overhead"),
    }
    lines = [
        "% Auto-generated by scripts/render_paper_tables.py from results/processed/*.csv.",
        "% Do not edit numeric values here by hand.",
    ]
    for key, value in commands.items():
        lines.append(f"\\newcommand{{\\{key}}}{{{_latex_escape_value(value)}}}")
    return "\n".join(lines) + "\n"


def _render_generated_tables() -> str:
    return "\n\n".join(
        [
            "% Auto-generated by scripts/render_paper_tables.py from results/processed/*.csv.",
            _latex_benchmark_table(_read_rows(FIRMWARE_BUILD_CSV)),
            _latex_replay_success_table(_read_rows(FULL_RTL_REPLAY_CSV)),
            _latex_negative_table(_read_rows(FULL_RTL_NEGATIVE_CSV)),
            _latex_runtime_table(_read_rows(RUNTIME_OVERHEAD_SUMMARY_CSV)),
            _latex_mapped_table(_read_rows(MAPPED_SYNTHESIS_CSV), _read_rows(MAPPED_OVERHEAD_CSV)),
            _latex_limitations_table(),
        ]
    ) + "\n"


def _latex_benchmark_table(rows: list[dict[str, str]]) -> str:
    by_benchmark: dict[str, set[str]] = {}
    for row in rows:
        if row.get("build_status") != "PASS":
            continue
        by_benchmark.setdefault(row.get("benchmark", "unknown"), set()).add(row.get("variant", "unknown"))
    lines = [
        "\\begin{table}[t]",
        "\\caption{Compiler-backed firmware benchmark suite. Source: \\texttt{results/processed/firmware\\_build.csv}.}",
        "\\label{tab:benchmarks}",
        "\\centering",
        "\\begin{tabular}{lll}",
        "\\toprule",
        "Family & Variants & Failure mechanism \\\\",
        "\\midrule",
    ]
    mechanisms = {
        "sensor_threshold_bug": "MMIO sensor threshold and deadline check",
        "interrupt_race_bug": "interrupt delivery inside a critical window",
        "mmio_ordering_bug": "unsafe command/output MMIO ordering",
        "stack_corruption_bug": "protected-store observation reaches checker",
        "uart_command_bug": "unsafe UART command drives actuator write",
        "watchdog_timeout_bug": "missed heartbeat under long-running path",
    }
    for benchmark in BENCHMARK_ORDER:
        variants = ", ".join(sorted(by_benchmark.get(benchmark, set()))) or "NA"
        lines.append(f"{_latex_escape(_benchmark_name(benchmark))} & {_latex_escape(variants)} & {_latex_escape(mechanisms[benchmark])} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines)


def _latex_replay_success_table(rows: list[dict[str, str]]) -> str:
    pass_rows = [
        row for row in rows
        if row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
    ]
    compiler_rows = [row for row in rows if row.get("firmware_source") == "compiler_c" and row.get("compiler_backed") == "true"]
    lines = [
        "\\begin{table}[t]",
        "\\caption{Host-driven full RTL replay success. Source: \\texttt{results/processed/full\\_rtl\\_replay.csv}.}",
        "\\label{tab:replay-success}",
        "\\centering",
        "\\begin{tabular}{lrrl}",
        "\\toprule",
        "Evidence & Pass & Total & Firmware source \\\\",
        "\\midrule",
        f"Record/replay/signature match & {len(pass_rows)} & {len(rows)} & compiler C \\\\",
        f"Compiler-backed rows & {len(compiler_rows)} & {len(rows)} & compiler C \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def _latex_negative_table(rows: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.get("actual_result", "NA")] = counts.get(row.get("actual_result", "NA"), 0) + 1
    lines = [
        "\\begin{table}[t]",
        "\\caption{Full RTL corrupted-capsule behavior. Source: \\texttt{results/processed/full\\_rtl\\_replay\\_negative.csv}.}",
        "\\label{tab:negative}",
        "\\centering",
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Result & Rows \\\\",
        "\\midrule",
    ]
    for result in ("REJECT", "ACCEPT", "NA"):
        lines.append(f"{result} & {counts.get(result, 0)} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines)


def _latex_runtime_table(rows: list[dict[str, str]]) -> str:
    wanted = [
        ("baseline_no_recorder", "sim_wall_time_sec"),
        ("recorder_present_disabled", "sim_wall_time_sec"),
        ("recorder_enabled", "sim_wall_time_sec"),
        ("recorder_present_disabled_vs_baseline_no_recorder", "cycle_overhead_pct"),
        ("recorder_enabled_vs_baseline_no_recorder", "cycle_overhead_pct"),
        ("recorder_enabled_vs_baseline_no_recorder", "sim_wall_time_overhead_pct"),
    ]
    lines = [
        "\\begin{table}[t]",
        "\\caption{Runtime and simulator-overhead summary. Source: \\texttt{results/processed/runtime\\_overhead\\_summary.csv}. Simulator wall time is not a hardware timing claim.}",
        "\\label{tab:runtime}",
        "\\centering",
        "\\begin{tabular}{llrr}",
        "\\toprule",
        "Config & Metric & Median & N \\\\",
        "\\midrule",
    ]
    for config, metric in wanted:
        row = _find_row(rows, config=config, metric=metric)
        lines.append(
            f"{_latex_escape(config.replace('_', ' '))} & {_latex_escape(metric.replace('_', ' '))} & {row.get('median', 'NA')} & {row.get('n', 'NA')} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines)


def _latex_mapped_table(mapped_rows: list[dict[str, str]], overhead_rows: list[dict[str, str]]) -> str:
    baseline = _find_design(mapped_rows, "full_core_baseline_board")
    replay = _find_design(mapped_rows, "full_core_replaycapsule_board")
    lines = [
        "\\begin{table}[t]",
        "\\caption{Full-core mapped ECP5 overhead. Sources: \\texttt{results/processed/mapped\\_synthesis.csv} and \\texttt{results/processed/mapped\\_overhead.csv}.}",
        "\\label{tab:mapped-overhead}",
        "\\centering",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Design/metric & LUT & FF & BRAM & Fmax MHz \\\\",
        "\\midrule",
        f"Baseline board & {baseline.get('lut', 'NA')} & {baseline.get('ff', 'NA')} & {baseline.get('bram', 'NA')} & {baseline.get('fmax_mhz', 'NA')} \\\\",
        f"ReplayCapsule board & {replay.get('lut', 'NA')} & {replay.get('ff', 'NA')} & {replay.get('bram', 'NA')} & {replay.get('fmax_mhz', 'NA')} \\\\",
        (
            "Overhead "
            f"& {_overhead_value(overhead_rows, 'full_core_baseline_board_to_full_core_replaycapsule_board_lut', 'percent_overhead')}\\% "
            f"& {_overhead_value(overhead_rows, 'full_core_baseline_board_to_full_core_replaycapsule_board_ff', 'percent_overhead')}\\% "
            f"& {_overhead_value(overhead_rows, 'full_core_baseline_board_to_full_core_replaycapsule_board_bram', 'percent_overhead')}\\% "
            f"& {_overhead_value(overhead_rows, 'full_core_baseline_board_to_full_core_replaycapsule_board_fmax_mhz', 'percent_overhead')}\\% \\\\"
        ),
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def _latex_limitations_table() -> str:
    lines = [
        "\\begin{table}[t]",
        "\\caption{Scope and limitations.}",
        "\\label{tab:limitations}",
        "\\centering",
        "\\begin{tabular}{ll}",
        "\\toprule",
        "Topic & Current scope \\\\",
        "\\midrule",
        "Processor & single-hart RV32I/PicoRV32 \\\\",
        "Nondeterminism & commit-indexed interrupt/MMIO boundary events \\\\",
        "Replay engine & host-driven Verilator harness \\\\",
        "Replay hardware & record-side recorder only; no replay-consume datapath \\\\",
        "Memory system & no multicore, DMA, cache-coherence, or analog-device model \\\\",
        "Optimization & fidelity and auditability prioritized over area minimization \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def _ordered_synthesis_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_top = {row.get("top", ""): row for row in rows}
    ordered = [by_top[top] for top in SYNTHESIS_ORDER if top in by_top]
    ordered.extend(row for row in rows if row.get("top", "") not in set(SYNTHESIS_ORDER))
    return ordered


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _percent_cell(value: str) -> str:
    escaped = _escape_cell(value)
    return escaped if escaped in {"", "NA", "TODO"} else f"{escaped}%"


def _find_row(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    return next((row for row in rows if all(row.get(key) == value for key, value in criteria.items())), {})


def _find_design(rows: list[dict[str, str]], design: str) -> dict[str, str]:
    return next((row for row in rows if row.get("design") == design and row.get("status") == "PASS"), {})


def _runtime_value(rows: list[dict[str, str]], metric: str, config: str, field: str) -> str:
    return _find_row(rows, metric=metric, config=config).get(field, "NA")


def _overhead_value(rows: list[dict[str, str]], metric: str, field: str) -> str:
    return next((row.get(field, "NA") for row in rows if row.get("metric") == metric), "NA")


def _latex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
    )


def _latex_escape_value(value: str) -> str:
    if value == "NA":
        return value
    return _latex_escape(value)


def _trace_row(rows: list[dict[str, str]], benchmark: str, baseline: str, evidence_level: str) -> dict[str, str]:
    return _find_row(rows, benchmark=benchmark, variant="failing", baseline=baseline, evidence_level=evidence_level)


def _status_cell(status: str, evidence_level: str) -> str:
    status = _escape_cell(status)
    evidence_level = _escape_cell(evidence_level)
    return f"{status} ({evidence_level})" if evidence_level else status


def _benchmark_name(benchmark: str) -> str:
    return BENCHMARK_DISPLAY_NAMES.get(benchmark, benchmark)


def _ratio_cell(numerator: str | None, denominator: str | None) -> str:
    try:
        numerator_int = int(numerator or "")
        denominator_int = int(denominator or "")
    except ValueError:
        return "NA"
    if denominator_int <= 0:
        return "NA"
    return f"{(numerator_int / denominator_int):.2f}x"


def _format_semicolon_list(value: str) -> str:
    if not value:
        return "NA"
    return "; ".join(item.strip().replace("_", " ") for item in value.split(";") if item.strip())


def _short_ablation(value: str) -> str:
    return value.removeprefix("remove_").replace("_values", "").replace("_events", "").replace("_", " ")


if __name__ == "__main__":
    raise SystemExit(main())
