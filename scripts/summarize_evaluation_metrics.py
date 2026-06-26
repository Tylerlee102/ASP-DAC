#!/usr/bin/env python3
"""Summarize headline evaluation metrics from generated artifacts."""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
REPLAY_CSV = REPO_ROOT / "results/processed/replay_experiments.csv"
NEGATIVE_CSV = REPO_ROOT / "results/processed/replay_negative_tests.csv"
TRACE_CSV = REPO_ROOT / "results/processed/trace_sizes.csv"
HDL_CSV = REPO_ROOT / "results/processed/hdl_checks.csv"
RTL_EXPORTS_CSV = REPO_ROOT / "results/processed/rtl_capsule_exports.csv"
RTL_ALIGNMENT_CSV = REPO_ROOT / "results/processed/rtl_firmware_alignment.csv"
RANDOMIZED_IRQ_CSV = REPO_ROOT / "results/processed/randomized_interrupt_campaign.csv"
RANDOMIZED_IRQ_COVERAGE_CSV = REPO_ROOT / "results/processed/randomized_interrupt_coverage.csv"
SYNTH_OVERHEAD_CSV = REPO_ROOT / "results/processed/synthesis_overhead.csv"
MODEL_TRACE_JSON = REPO_ROOT / "results/raw/model_suite_traces.json"
FIRMWARE_TRACE_JSON = REPO_ROOT / "results/raw/firmware_sim_traces.json"
OUT_CSV = REPO_ROOT / "results/processed/evaluation_metrics.csv"

FIELDNAMES = ["metric", "status", "value", "unit", "evidence_level", "source", "notes"]


def main() -> int:
    rows: list[dict[str, str]] = []
    replay_rows = _read_rows(REPLAY_CSV)
    trace_rows = _read_rows(TRACE_CSV)
    rows.extend(_replay_success_metrics(replay_rows))
    rows.extend(_negative_fixture_metrics(_read_rows(NEGATIVE_CSV)))
    rows.extend(_hdl_frontend_metrics(_read_rows(HDL_CSV)))
    rows.extend(_rtl_smoke_metrics(_read_rows(RTL_EXPORTS_CSV), _read_rows(RTL_ALIGNMENT_CSV)))
    rows.extend(_randomized_interrupt_metrics(_read_rows(RANDOMIZED_IRQ_CSV), _read_rows(RANDOMIZED_IRQ_COVERAGE_CSV)))
    rows.extend(_trace_size_metrics(trace_rows))
    rows.extend(_failure_prefix_metrics(MODEL_TRACE_JSON, "model"))
    rows.extend(_failure_prefix_metrics(FIRMWARE_TRACE_JSON, "firmware-sim"))
    rows.extend(_synthesis_metrics(_read_rows(SYNTH_OVERHEAD_CSV)))
    rows.extend(_hardware_todo_metrics())

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {OUT_CSV}")
    return 0


def _replay_success_metrics(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        _rate_row(
            "model_replay_success_rate",
            [row for row in rows if row.get("evidence_level") == "model"],
            "model",
            "results/processed/replay_experiments.csv",
            "Model-level commit-index replay rows.",
        ),
        _rate_row(
            "firmware_sim_replay_success_rate",
            [row for row in rows if row.get("evidence_level") == "firmware-sim"],
            "firmware-sim",
            "results/processed/replay_experiments.csv",
            "RV32I firmware-sim commit-index replay rows.",
        ),
        _todo_row(
            "firmware_running_rtl_replay_success_rate",
            "percent",
            "rtl",
            "results/processed/replay_experiments.csv",
            "Benchmark-wide firmware-running RTL replay remains blocked by missing make/C++/RISC-V compiler support.",
        ),
    ]


def _negative_fixture_metrics(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        _rate_row(
            "replay_negative_fixture_pass_rate",
            rows,
            "model",
            "results/processed/replay_negative_tests.csv",
            "Benchmark-derived positive and negative comparator fixtures across commit-index and cycle-index modes.",
        )
    ]


def _hdl_frontend_metrics(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    directed = [row for row in rows if row.get("check", "").startswith("tb_") and not row.get("check", "").startswith("tb_picorv32")]
    wrapper = [row for row in rows if row.get("check", "").startswith("tb_picorv32")]
    verilator = [row for row in rows if row.get("check", "").startswith("verilator_lint_")]
    return [
        _rate_row(
            "hdl_frontend_pass_rate",
            rows,
            "rtl-smoke",
            "results/processed/hdl_checks.csv",
            "Directed Icarus simulations, PicoRV32 wrapper smokes, and Verilator lint-only frontend checks.",
        ),
        _rate_row(
            "directed_icarus_module_pass_rate",
            directed,
            "rtl-smoke",
            "results/processed/hdl_checks.csv",
            "Standalone directed Icarus module simulations excluding PicoRV32 wrapper smoke rows.",
        ),
        _rate_row(
            "picorv32_wrapper_smoke_pass_rate",
            wrapper,
            "rtl-smoke",
            "results/processed/hdl_checks.csv",
            "Firmware-running PicoRV32 wrapper smokes, including failing/fixed images and selected no-failure edge cases.",
        ),
        _rate_row(
            "verilator_lint_pass_rate",
            verilator,
            "rtl-smoke",
            "results/processed/hdl_checks.csv",
            "Verilator lint-only frontend checks for top-level integration and property assertion sources.",
        ),
    ]


def _rtl_smoke_metrics(exports: list[dict[str, str]], alignment: list[dict[str, str]]) -> list[dict[str, str]]:
    fixed = [row for row in alignment if row.get("variant") == "fixed"]
    failing = [row for row in alignment if row.get("variant") == "failing"]
    false_failures = sum(
        1
        for row in fixed
        if not (
            row.get("status") == "PASS"
            and row.get("property_alignment") == "PASS"
            and row.get("rtl_property_id") == "NONE"
            and row.get("firmware_property_id") == "NONE"
        )
    )
    missed_failures = sum(
        1
        for row in failing
        if not (
            row.get("status") == "PASS"
            and row.get("property_alignment") == "PASS"
            and row.get("rtl_property_id") not in {"", "NONE", "NA"}
        )
    )
    return [
        _rate_row(
            "rtl_smoke_capsule_export_pass_rate",
            exports,
            "rtl-smoke",
            "results/processed/rtl_capsule_exports.csv",
            "Exported RTL-smoke capsules parse and pass self/negative checks; not benchmark-wide RTL replay.",
        ),
        _count_row(
            "rtl_smoke_false_property_failures",
            false_failures,
            len(fixed),
            "rtl-smoke",
            "results/processed/rtl_firmware_alignment.csv",
            "Fixed RTL-smoke and firmware-sim variants both avoid property failures.",
        ),
        _count_row(
            "rtl_smoke_missed_property_failures",
            missed_failures,
            len(failing),
            "rtl-smoke",
            "results/processed/rtl_firmware_alignment.csv",
            "Failing RTL-smoke and firmware-sim variants align on property IDs.",
        ),
    ]


def _randomized_interrupt_metrics(
    campaign: list[dict[str, str]],
    coverage: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        _rate_row(
            "seeded_rtl_smoke_interrupt_reproducibility_rate",
            campaign,
            "rtl-smoke",
            "results/processed/randomized_interrupt_campaign.csv",
            "Seeded interrupt-race RTL-smoke cases rerun in fresh simulator invocations and compare frozen capsule digests.",
        ),
        _rate_row(
            "seeded_randomized_interrupt_coverage_item_pass_rate",
            coverage,
            "rtl-smoke",
            "results/processed/randomized_interrupt_coverage.csv",
            "Generated checklist over current seeded interrupt coverage and stronger randomized RTL cases still marked TODO.",
        ),
    ]


def _trace_size_metrics(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        _median_bytes_row(
            "median_firmware_sim_replaycapsule_bytes",
            rows,
            "firmware-sim",
            "property_aware_replaycapsule_rv",
            "ReplayCapsule bytes over firmware-sim failing runs.",
        ),
        _median_bytes_row(
            "median_firmware_sim_full_instruction_trace_bytes",
            rows,
            "firmware-sim",
            "full_instruction_trace",
            "Full instruction-trace bytes over firmware-sim failing runs.",
        ),
        _median_bytes_row(
            "median_firmware_sim_snapshot_bytes",
            rows,
            "firmware-sim",
            "snapshot_on_failure",
            "Architectural snapshot bytes over firmware-sim failing runs.",
        ),
        _median_ratio_row(
            "median_firmware_sim_reduction_vs_full_instruction",
            rows,
            "firmware-sim",
            "full_instruction_trace",
            "property_aware_replaycapsule_rv",
            "Full-instruction bytes divided by ReplayCapsule bytes; less than 1.0 means the capsule is larger for these tiny workloads.",
        ),
        _median_ratio_row(
            "median_firmware_sim_reduction_vs_snapshot",
            rows,
            "firmware-sim",
            "snapshot_on_failure",
            "property_aware_replaycapsule_rv",
            "Snapshot bytes divided by ReplayCapsule bytes.",
        ),
        _median_ratio_row(
            "median_model_reduction_vs_full_commit",
            rows,
            "model",
            "full_commit_trace",
            "property_aware_replaycapsule_rv",
            "Model full-commit bytes divided by model ReplayCapsule bytes using fixed record-size estimates.",
        ),
    ]


def _failure_prefix_metrics(trace_path: Path, evidence_level: str) -> list[dict[str, str]]:
    cycles: list[float] = []
    commits: list[float] = []
    for run in _read_runs(trace_path):
        fail_event = next((event for event in run.get("events", []) if event.get("event_type") == "EV_PROPERTY_FAIL"), None)
        if not isinstance(fail_event, dict):
            continue
        cycle = _as_float(fail_event.get("cycle"))
        commit = _as_float(fail_event.get("commit"))
        if cycle is not None:
            cycles.append(cycle)
        if commit is not None:
            commits.append(commit)

    source = _source_path(trace_path)
    return [
        _median_value_row(
            f"median_{evidence_level.replace('-', '_')}_cycles_to_failure",
            cycles,
            "cycles",
            evidence_level,
            source,
            "Median cycle index of EV_PROPERTY_FAIL in generated failing traces.",
        ),
        _median_value_row(
            f"median_{evidence_level.replace('-', '_')}_commits_to_failure",
            commits,
            "commits",
            evidence_level,
            source,
            "Median commit index of EV_PROPERTY_FAIL in generated failing traces.",
        ),
    ]


def _synthesis_metrics(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    measured = next((row for row in rows if row.get("status") == "MEASURED"), None)
    if measured is None:
        return [
            _todo_row(
                "generic_yosys_cell_delta",
                "cells",
                "generic-yosys",
                "results/processed/synthesis_overhead.csv",
                "Generic Yosys synthesis-overhead row is missing.",
            ),
            _todo_row(
                "generic_yosys_cell_overhead_percent",
                "percent",
                "generic-yosys",
                "results/processed/synthesis_overhead.csv",
                "Generic Yosys synthesis-overhead row is missing.",
            ),
        ]
    return [
        _metric_row(
            "generic_yosys_cell_delta",
            "MEASURED",
            measured.get("generic_cell_delta", "NA"),
            "cells",
            "generic-yosys",
            "results/processed/synthesis_overhead.csv",
            "Generic unmapped cell-count delta; not LUT/FF/BRAM/Fmax.",
        ),
        _metric_row(
            "generic_yosys_cell_overhead_percent",
            "MEASURED",
            measured.get("generic_cell_overhead_percent", "NA"),
            "percent",
            "generic-yosys",
            "results/processed/synthesis_overhead.csv",
            "Generic unmapped cell-count overhead; mapped FPGA overhead remains TODO.",
        ),
    ]


def _hardware_todo_metrics() -> list[dict[str, str]]:
    return [
        _todo_row(
            "mapped_lut_overhead_percent",
            "percent",
            "mapped-fpga",
            "results/processed/synthesis_overhead.csv",
            "Requires mapped FPGA LUT reports.",
        ),
        _todo_row(
            "mapped_ff_overhead_percent",
            "percent",
            "mapped-fpga",
            "results/processed/synthesis_overhead.csv",
            "Requires mapped FPGA FF reports.",
        ),
        _todo_row(
            "bram_overhead",
            "brams",
            "mapped-fpga",
            "results/processed/synthesis_overhead.csv",
            "Requires mapped FPGA BRAM reports.",
        ),
        _todo_row(
            "fmax_loss_percent",
            "percent",
            "mapped-fpga",
            "results/processed/synthesis_overhead.csv",
            "Requires timing reports from OpenROAD or vendor FPGA flow.",
        ),
        _todo_row(
            "runtime_slowdown_percent",
            "percent",
            "rtl",
            "results/processed/replay_experiments.csv",
            "Requires benchmark-wide firmware-running RTL or hardware execution timing.",
        ),
        _todo_row(
            "buffer_overflow_rate",
            "percent",
            "rtl",
            "results/processed/rtl_capsule_exports.csv",
            "Requires benchmark-wide runtime overflow counters; bounded buffer checks exist separately.",
        ),
    ]


def _rate_row(
    metric: str,
    rows: list[dict[str, str]],
    evidence_level: str,
    source: str,
    notes: str,
) -> dict[str, str]:
    total = len(rows)
    if total == 0:
        return _todo_row(metric, "percent", evidence_level, source, "No rows available. " + notes)
    passes = sum(1 for row in rows if row.get("status") == "PASS")
    return _metric_row(
        metric,
        "MEASURED",
        f"{passes}/{total} ({100.0 * passes / total:.1f}%)",
        "percent",
        evidence_level,
        source,
        notes,
    )


def _count_row(
    metric: str,
    count: int,
    total: int,
    evidence_level: str,
    source: str,
    notes: str,
) -> dict[str, str]:
    if total == 0:
        return _todo_row(metric, "count", evidence_level, source, "No rows available. " + notes)
    return _metric_row(metric, "MEASURED", f"{count}/{total}", "count", evidence_level, source, notes)


def _median_bytes_row(
    metric: str,
    rows: list[dict[str, str]],
    evidence_level: str,
    baseline: str,
    notes: str,
) -> dict[str, str]:
    values = [
        int(row["bytes"])
        for row in rows
        if row.get("status") == "MEASURED"
        and row.get("evidence_level") == evidence_level
        and row.get("baseline") == baseline
        and row.get("bytes", "").isdigit()
    ]
    return _median_value_row(metric, values, "bytes", evidence_level, "results/processed/trace_sizes.csv", notes)


def _median_ratio_row(
    metric: str,
    rows: list[dict[str, str]],
    evidence_level: str,
    numerator_baseline: str,
    denominator_baseline: str,
    notes: str,
) -> dict[str, str]:
    by_key: dict[tuple[str, str], dict[str, int]] = {}
    for row in rows:
        if row.get("status") != "MEASURED" or row.get("evidence_level") != evidence_level:
            continue
        baseline = row.get("baseline")
        if baseline not in {numerator_baseline, denominator_baseline}:
            continue
        value = row.get("bytes", "")
        if not value.isdigit():
            continue
        key = (row.get("benchmark", ""), row.get("variant", ""))
        by_key.setdefault(key, {})[baseline] = int(value)

    ratios = []
    for values in by_key.values():
        numerator = values.get(numerator_baseline)
        denominator = values.get(denominator_baseline)
        if numerator is not None and denominator:
            ratios.append(numerator / denominator)
    return _median_value_row(metric, ratios, "x", evidence_level, "results/processed/trace_sizes.csv", notes)


def _median_value_row(
    metric: str,
    values: Iterable[float],
    unit: str,
    evidence_level: str,
    source: str,
    notes: str,
) -> dict[str, str]:
    value_list = list(values)
    if not value_list:
        return _todo_row(metric, unit, evidence_level, source, "No measured values available. " + notes)
    median = statistics.median(value_list)
    if unit in {"bytes", "cycles", "commits"}:
        value = str(int(median)) if float(median).is_integer() else f"{median:.1f}"
    else:
        value = f"{median:.3f}"
    return _metric_row(metric, "MEASURED", value, unit, evidence_level, source, notes)


def _metric_row(
    metric: str,
    status: str,
    value: str,
    unit: str,
    evidence_level: str,
    source: str,
    notes: str,
) -> dict[str, str]:
    return {
        "metric": metric,
        "status": status,
        "value": value,
        "unit": unit,
        "evidence_level": evidence_level,
        "source": source,
        "notes": notes,
    }


def _todo_row(metric: str, unit: str, evidence_level: str, source: str, notes: str) -> dict[str, str]:
    return _metric_row(metric, "TODO", "TODO", unit, evidence_level, source, notes)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_runs(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    runs = payload.get("runs") if isinstance(payload, dict) else None
    if isinstance(runs, list):
        return [run for run in runs if isinstance(run, dict)]
    return [payload] if isinstance(payload, dict) else []


def _as_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(int(value, 0))
        except ValueError:
            return None
    return None


def _source_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
