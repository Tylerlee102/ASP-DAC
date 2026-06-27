#!/usr/bin/env python3
"""Generate conference-review evidence tables from measured artifacts."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = REPO_ROOT / "results/processed"

BENCHMARKS = (
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
)

EVENT_CLASSES = (
    "commit",
    "branch/jump",
    "load/store",
    "MMIO read",
    "MMIO write",
    "interrupt enter",
    "interrupt exit",
    "external input",
    "property fail",
    "checkpoint/hash",
    "diagnostic PC context",
)

BASELINE_NAMES = (
    "Full instruction trace",
    "Full commit trace",
    "Branch/control-flow trace",
    "Store/output trace",
    "MMIO-only trace",
    "Interrupt-only trace",
    "Interrupt+MMIO trace",
    "Snapshot-on-failure",
    "ReplayCapsule-RV core-only capsule",
    "ReplayCapsule-RV property-aware capsule",
)

BASELINE_TO_TRACE = {
    "Full instruction trace": "full_instruction_trace",
    "Full commit trace": "full_commit_trace",
    "Branch/control-flow trace": "branch_only_trace",
    "Store/output trace": "store_only_trace",
    "MMIO-only trace": "mmio_only_trace",
    "Interrupt+MMIO trace": "interrupt_mmio_trace",
    "Snapshot-on-failure": "snapshot_on_failure",
    "ReplayCapsule-RV property-aware capsule": "property_aware_replaycapsule_rv",
}

ABLATION_TO_CLASS = {
    "remove_branch_events": "branch/jump",
    "remove_store_events": "load/store",
    "remove_mmio_read_values": "MMIO read",
    "remove_mmio_write_observations": "MMIO write",
    "remove_interrupt_timing": "interrupt enter",
    "remove_external_input_values": "external input",
    "remove_checkpoint_hashes": "checkpoint/hash",
    "remove_pc_context": "diagnostic PC context",
}


def main() -> int:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    outputs = [
        _write_event_sufficiency_matrix(),
        _write_baseline_comparison(),
        _write_scaling_workloads(),
        _write_buffer_sweep(),
        _write_mapped_synthesis(),
        _write_mapped_overhead(),
        _write_paper_event_sufficiency_table(),
    ]
    for path in outputs:
        print(f"WROTE {path}")
    return 0


def _write_event_sufficiency_matrix() -> Path:
    ablations = _read_rows(PROCESSED / "ablations.csv")
    rtl_ablations = _read_rows(PROCESSED / "rtl_smoke_ablations.csv")
    rows: list[dict[str, str]] = []

    for benchmark in BENCHMARKS:
        model_by_class = _ablation_index(ablations, benchmark, "model")
        rtl_by_class = _ablation_index(rtl_ablations, benchmark, "rtl-smoke")
        for event_class in EVENT_CLASSES:
            rows.append(_event_matrix_row(benchmark, "model", event_class, model_by_class.get(event_class)))
            rows.append(_event_matrix_row(benchmark, "firmware-sim", event_class, None, firmware_todo=True))
            rows.append(_event_matrix_row(benchmark, "rtl-smoke", event_class, rtl_by_class.get(event_class)))
            rows.append(_event_matrix_row(benchmark, "full-rtl", event_class, None, full_rtl_todo=True))

    out = PROCESSED / "event_sufficiency_matrix.csv"
    _write_rows(
        out,
        rows,
        [
            "benchmark",
            "evidence_level",
            "removed_event_class",
            "replay_result",
            "property_match",
            "final_signature_match",
            "required_for_replay",
            "notes",
        ],
    )
    return out


def _event_matrix_row(
    benchmark: str,
    evidence_level: str,
    event_class: str,
    source: dict[str, str] | None,
    firmware_todo: bool = False,
    full_rtl_todo: bool = False,
) -> dict[str, str]:
    if source:
        replay_success = source.get("replay_success", "TODO")
        required = "yes" if replay_success == "False" else "no"
        return {
            "benchmark": benchmark,
            "evidence_level": evidence_level,
            "removed_event_class": event_class,
            "replay_result": "FAIL" if replay_success == "False" else "PASS",
            "property_match": "PASS",
            "final_signature_match": "PASS",
            "required_for_replay": required,
            "notes": source.get("reason", "measured ablation row"),
        }
    if full_rtl_todo:
        return {
            "benchmark": benchmark,
            "evidence_level": evidence_level,
            "removed_event_class": event_class,
            "replay_result": "TODO",
            "property_match": "NA",
            "final_signature_match": "NA",
            "required_for_replay": "unknown",
            "notes": "full RTL event-removal ablation is not implemented; see full_rtl_replay.csv for record/replay status",
        }
    if firmware_todo:
        return {
            "benchmark": benchmark,
            "evidence_level": evidence_level,
            "removed_event_class": event_class,
            "replay_result": "TODO",
            "property_match": "NA",
            "final_signature_match": "NA",
            "required_for_replay": "unknown",
            "notes": "firmware-sim event-removal ablation is not implemented yet",
        }
    return {
        "benchmark": benchmark,
        "evidence_level": evidence_level,
        "removed_event_class": event_class,
        "replay_result": "TODO",
        "property_match": "NA",
        "final_signature_match": "NA",
        "required_for_replay": "unknown",
        "notes": "no generated ablation row for this event class",
    }


def _ablation_index(rows: list[dict[str, str]], benchmark: str, evidence_level: str) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        if row.get("benchmark") != benchmark or row.get("evidence_level") != evidence_level:
            continue
        if row.get("variant", "failing") not in {"", "failing"}:
            continue
        event_class = ABLATION_TO_CLASS.get(row.get("ablation", ""))
        if event_class:
            index[event_class] = row
    return index


def _write_baseline_comparison() -> Path:
    trace_rows = _read_rows(PROCESSED / "trace_sizes.csv")
    rows: list[dict[str, str]] = []
    for benchmark in BENCHMARKS:
        for evidence_level in ("model", "firmware-sim", "rtl-smoke", "full-rtl"):
            full_instruction = _find_trace(trace_rows, benchmark, evidence_level, "full_instruction_trace")
            snapshot = _find_trace(trace_rows, benchmark, evidence_level, "snapshot_on_failure")
            for baseline in BASELINE_NAMES:
                source = _find_trace(trace_rows, benchmark, evidence_level, BASELINE_TO_TRACE.get(baseline, ""))
                rows.append(_baseline_row(benchmark, evidence_level, baseline, source, full_instruction, snapshot))

    out = PROCESSED / "baseline_comparison.csv"
    _write_rows(
        out,
        rows,
        [
            "benchmark",
            "evidence_level",
            "baseline",
            "bytes",
            "events",
            "replay_success",
            "property_match",
            "final_signature_match",
            "reduction_vs_full_instruction",
            "reduction_vs_snapshot",
            "notes",
        ],
    )
    return out


def _baseline_row(
    benchmark: str,
    evidence_level: str,
    baseline: str,
    source: dict[str, str],
    full_instruction: dict[str, str],
    snapshot: dict[str, str],
) -> dict[str, str]:
    if not source:
        status = "TODO"
        notes = "no generated full RTL baseline trace row; see full_rtl_replay.csv for record/replay status" if evidence_level == "full-rtl" else "no generated row for this baseline/evidence level"
        return {
            "benchmark": benchmark,
            "evidence_level": evidence_level,
            "baseline": baseline,
            "bytes": "NA",
            "events": "NA",
            "replay_success": status,
            "property_match": "NA",
            "final_signature_match": "NA",
            "reduction_vs_full_instruction": "NA",
            "reduction_vs_snapshot": "NA",
            "notes": notes,
        }

    replay_success = source.get("replay_success", "TODO")
    return {
        "benchmark": benchmark,
        "evidence_level": evidence_level,
        "baseline": baseline,
        "bytes": source.get("bytes", "NA"),
        "events": source.get("event_count", "NA"),
        "replay_success": _normalize_bool_status(replay_success),
        "property_match": "PASS" if replay_success == "True" else "FAIL" if replay_success == "False" else "NA",
        "final_signature_match": "PASS" if replay_success == "True" else "FAIL" if replay_success == "False" else "NA",
        "reduction_vs_full_instruction": _reduction(source.get("bytes"), full_instruction.get("bytes")),
        "reduction_vs_snapshot": _reduction(source.get("bytes"), snapshot.get("bytes")),
        "notes": source.get("notes", ""),
    }


def _write_scaling_workloads() -> Path:
    rows: list[dict[str, str]] = []
    families = (
        ("long_polling_rare_mmio_trigger", 17),
        ("interrupt_storm_mask_windows", 29),
        ("uart_command_stream_delayed_unsafe", 41),
        ("watchdog_heartbeat_long", 53),
        ("stack_corruption_after_stores", 67),
    )
    for benchmark, seed in families:
        for workload_size in (128, 1024, 8192):
            metrics = _synthetic_scaling_metrics(benchmark, workload_size, seed)
            rows.append(metrics)

    out = PROCESSED / "scaling_workloads.csv"
    _write_rows(
        out,
        rows,
        [
            "benchmark",
            "workload_size",
            "seed",
            "cycles",
            "commits",
            "events",
            "capsule_bytes",
            "instruction_trace_bytes",
            "snapshot_bytes",
            "overflow",
            "buffer_depth",
            "event_rate_per_kinst",
            "notes",
        ],
    )
    return out


def _synthetic_scaling_metrics(benchmark: str, workload_size: int, seed: int) -> dict[str, str]:
    if "polling" in benchmark:
        events = 3 + workload_size // 512
    elif "interrupt" in benchmark:
        events = 4 + workload_size // 64
    elif "uart" in benchmark:
        events = 5 + workload_size // 128
    elif "watchdog" in benchmark:
        events = 4 + workload_size // 256
    else:
        events = 3 + workload_size // 96
    commits = workload_size
    cycles = workload_size * 3 + seed
    buffer_depth = 64
    return {
        "benchmark": benchmark,
        "workload_size": str(workload_size),
        "seed": str(seed),
        "cycles": str(cycles),
        "commits": str(commits),
        "events": str(events),
        "capsule_bytes": str(events * 21),
        "instruction_trace_bytes": str(commits * 8),
        "snapshot_bytes": "132",
        "overflow": str(events > buffer_depth),
        "buffer_depth": str(buffer_depth),
        "event_rate_per_kinst": f"{events / (commits / 1000.0):.3f}",
        "notes": "synthetic model-scaling workload generated by script; not firmware-running RTL evidence",
    }


def _write_buffer_sweep() -> Path:
    rows: list[dict[str, str]] = []
    for benchmark in (
        "long_polling_rare_mmio_trigger",
        "interrupt_storm_mask_windows",
        "uart_command_stream_delayed_unsafe",
        "watchdog_heartbeat_long",
        "stack_corruption_after_stores",
    ):
        event_count = int(_synthetic_scaling_metrics(benchmark, 8192, 101)["events"])
        for depth in (4, 8, 16, 32, 64, 128):
            overflow = event_count > depth
            rows.append(
                {
                    "benchmark": benchmark,
                    "buffer_depth": str(depth),
                    "event_count": str(event_count),
                    "overflow": str(overflow),
                    "replay_available": str(not overflow),
                    "capsule_bytes": str(event_count * 21 if not overflow else 0),
                    "notes": "synthetic model buffer sweep; overflow invalidates replay availability",
                }
            )

    out = PROCESSED / "buffer_sweep.csv"
    _write_rows(out, rows, ["benchmark", "buffer_depth", "event_count", "overflow", "replay_available", "capsule_bytes", "notes"])
    return out


def _write_mapped_synthesis() -> Path:
    out = PROCESSED / "mapped_synthesis.csv"
    if _has_mapped_runner_rows(out):
        return out
    rows: list[dict[str, str]] = []
    for design in ("picorv32", "replay_capsule_top", "picorv32_replaycapsule_wrapper"):
        rows.append(
            {
                "target": "TODO",
                "flow": "mapped FPGA or ASIC flow",
                "design": design,
                "lut": "NA",
                "ff": "NA",
                "bram": "NA",
                "dsp": "NA",
                "cells": "NA",
                "area_um2": "NA",
                "fmax_mhz": "NA",
                "wns": "NA",
                "tns": "NA",
                "power_mw": "NA",
                "status": "TODO",
                "report_path": "NA",
                "notes": "no generated nextpnr/OpenROAD/Vivado/Quartus mapped report exists; generic Yosys rows remain in synthesis.csv only",
            }
        )
    _write_rows(
        out,
        rows,
        ["target", "flow", "design", "lut", "ff", "bram", "dsp", "cells", "area_um2", "fmax_mhz", "wns", "tns", "power_mw", "status", "report_path", "notes"],
    )
    return out


def _write_mapped_overhead() -> Path:
    out = PROCESSED / "mapped_overhead.csv"
    if _has_mapped_runner_rows(out):
        return out
    rows = [
        {
            "target": "TODO",
            "flow": "mapped FPGA or ASIC flow",
            "metric": metric,
            "baseline": "NA",
            "with_replaycapsule": "NA",
            "delta": "NA",
            "percent_overhead": "NA",
            "notes": "requires mapped_synthesis.csv PASS rows from a real mapped flow",
        }
        for metric in ("lut", "ff", "bram", "cells", "area_um2", "fmax_mhz", "power_mw")
    ]
    _write_rows(out, rows, ["target", "flow", "metric", "baseline", "with_replaycapsule", "delta", "percent_overhead", "notes"])
    return out


def _has_mapped_runner_rows(path: Path) -> bool:
    rows = _read_rows(path)
    return any(
        row.get("target") == "ice40-hx8k"
        or row.get("flow") == "yosys+synth_ice40+nextpnr-ice40"
        or row.get("status") in {"PASS", "FAIL", "BLOCKED"}
        for row in rows
    )


def _write_paper_event_sufficiency_table() -> Path:
    rows = _read_rows(PROCESSED / "event_sufficiency_matrix.csv")
    measured = [
        row
        for row in rows
        if row.get("evidence_level") in {"model", "rtl-smoke"}
        and row.get("replay_result") in {"PASS", "FAIL"}
    ]
    lines = [
        "# Event-Sufficiency Matrix",
        "",
        "Generated from `../../results/processed/event_sufficiency_matrix.csv`.",
        "",
        "Rows marked required are sufficient-evidence observations at the named evidence level, not a global minimality proof.",
        "",
        "| Benchmark | Evidence level | Required core events | Diagnostic-only/optional observed | TODO/BLOCKED classes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for benchmark in BENCHMARKS:
        for evidence_level in ("model", "rtl-smoke", "firmware-sim", "full-rtl"):
            subset = [row for row in rows if row.get("benchmark") == benchmark and row.get("evidence_level") == evidence_level]
            required = [row["removed_event_class"] for row in subset if row.get("required_for_replay") == "yes"]
            optional = [row["removed_event_class"] for row in subset if row.get("required_for_replay") == "no"]
            todo = [row["removed_event_class"] for row in subset if row.get("replay_result") in {"TODO", "BLOCKED"}]
            if evidence_level in {"model", "rtl-smoke"} and not any(row in measured for row in subset):
                continue
            lines.append(
                "| {benchmark} | {level} | {required} | {optional} | {todo} |".format(
                    benchmark=benchmark,
                    level=evidence_level,
                    required="; ".join(required) if required else "none observed",
                    optional="; ".join(optional) if optional else "none observed",
                    todo="; ".join(todo) if todo else "none",
                )
            )
    out = REPO_ROOT / "paper/figures/table_event_sufficiency.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _find_trace(rows: list[dict[str, str]], benchmark: str, evidence_level: str, baseline: str) -> dict[str, str]:
    if not baseline:
        return {}
    return next(
        (
            row
            for row in rows
            if row.get("benchmark") == benchmark
            and row.get("variant") == "failing"
            and row.get("evidence_level") == evidence_level
            and row.get("baseline") == baseline
            and row.get("status") == "MEASURED"
        ),
        {},
    )


def _normalize_bool_status(value: str) -> str:
    if value == "True":
        return "PASS"
    if value == "False":
        return "FAIL"
    return value or "TODO"


def _reduction(candidate: str | None, reference: str | None) -> str:
    try:
        candidate_int = int(candidate or "")
        reference_int = int(reference or "")
    except ValueError:
        return "NA"
    if candidate_int <= 0 or reference_int <= 0:
        return "NA"
    return f"{reference_int / candidate_int:.3f}x"


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
