#!/usr/bin/env python3
"""Render paper table sources from generated result CSVs."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS_CSV = REPO_ROOT / "results/processed/synthesis.csv"
SYNTHESIS_OVERHEAD_CSV = REPO_ROOT / "results/processed/synthesis_overhead.csv"
REPLAY_CSV = REPO_ROOT / "results/processed/replay_experiments.csv"
TRACE_SIZES_CSV = REPO_ROOT / "results/processed/trace_sizes.csv"
EVENT_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/event_sufficiency.csv"
ABLATIONS_CSV = REPO_ROOT / "results/processed/ablations.csv"
RTL_SMOKE_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/rtl_smoke_event_sufficiency.csv"
RTL_ALIGNMENT_CSV = REPO_ROOT / "results/processed/rtl_firmware_alignment.csv"
RTL_CLASSES_CSV = REPO_ROOT / "results/processed/rtl_capsule_event_classes.csv"
FORMAL_COVERAGE_CSV = REPO_ROOT / "results/processed/formal_coverage.csv"
PROOF_OBLIGATIONS_CSV = REPO_ROOT / "results/processed/proof_obligations.csv"
PAPER_FIGURES = REPO_ROOT / "paper/figures"

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
    outputs = {
        "table01_synthesis_resources.md": _render_synthesis_table(
            _ordered_synthesis_rows(_read_rows(SYNTHESIS_CSV)),
            _read_rows(SYNTHESIS_OVERHEAD_CSV),
        ),
        "table02_replay_evidence.md": _render_replay_table(
            _read_rows(REPLAY_CSV),
            _read_rows(RTL_ALIGNMENT_CSV),
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
    }
    for name, content in outputs.items():
        (PAPER_FIGURES / name).write_text(content, encoding="utf-8")
    print(f"WROTE {len(outputs)} paper table(s) under {PAPER_FIGURES}")
    return 0


def _render_synthesis_table(synthesis_rows: list[dict[str, str]], overhead_rows: list[dict[str, str]]) -> str:
    lines = [
        "# Table 1. Synthesis Resource Status",
        "",
        "Generated from `../../results/processed/synthesis.csv` and "
        "`../../results/processed/synthesis_overhead.csv`.",
        "",
        "Generic Yosys cell counts are measured from real local reports. "
        "Mapped FPGA LUT/FF/BRAM/Fmax fields remain `NA` until a mapped flow exists.",
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
    return "\n".join(lines) + "\n"


def _render_replay_table(replay_rows: list[dict[str, str]], alignment_rows: list[dict[str, str]]) -> str:
    lines = [
        "# Table 2. Replay Evidence Status",
        "",
        "Generated from `../../results/processed/replay_experiments.csv` and "
        "`../../results/processed/rtl_firmware_alignment.csv`.",
        "",
        "Model and firmware-sim rows are commit-index replay checks. RTL-smoke rows are "
        "property/key-event alignment checks, not full benchmark-wide RTL replay.",
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
    rtl_suite = _find_row(replay_rows, experiment="firmware_running_rtl_suite")
    lines.append(
        "| Full firmware-running RTL suite | {status} | {status} | NA | NA | {notes} |".format(
            status=_status_cell(rtl_suite.get("status", "TODO"), rtl_suite.get("evidence_level", "rtl")),
            notes=_escape_cell(rtl_suite.get("notes", "requires unavailable local toolchain")),
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
