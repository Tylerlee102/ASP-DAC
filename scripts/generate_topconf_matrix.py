#!/usr/bin/env python3
"""Create the top-conference evaluation matrix before running experiments."""

from __future__ import annotations

from pathlib import Path

from topconf_eval_common import (
    BENCHMARKS,
    FULL_SCALES,
    MAPPED_BUFFER_DEPTHS,
    MAPPED_CONFIGS,
    MAPPED_MEMORY_WORDS,
    QUICK_SCALES,
    RECORDER_CONFIGS,
    SEEDS,
    VARIANTS,
    WORKLOAD_SCALES,
    processed_path,
    write_csv,
)


FIELDS = [
    "experiment_group",
    "experiment_id",
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "memory_words",
    "buffer_depth",
    "recorder_config",
    "target",
    "flow",
    "required_for_top_conference",
    "expected_output",
    "status",
    "notes",
]

DOC_PATH = Path(__file__).resolve().parents[1] / "docs/top_conference_evaluation_matrix.md"


def main() -> int:
    rows = _rows()
    write_csv(processed_path("evaluation_matrix.csv"), FIELDS, rows)
    _write_doc(rows)
    print("WROTE results/processed/evaluation_matrix.csv")
    print("WROTE docs/top_conference_evaluation_matrix.md")
    return 0


def _rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for mode, scales, seeds in (("quick", QUICK_SCALES, (1,)), ("full", FULL_SCALES, SEEDS)):
        for benchmark in BENCHMARKS:
            for variant in VARIANTS[benchmark]:
                for seed in seeds:
                    for scale in scales:
                        rows.append(_row("Replay correctness", f"{mode}_replay", benchmark, variant, seed, scale, "results/processed/workload_scaling.csv", "yes", mode))
                        rows.append(_row("Runtime overhead", f"{mode}_runtime", benchmark, variant, seed, scale, "results/processed/runtime_scaling.csv", "yes", mode))
                        rows.append(_row("Capsule-size baseline comparison", f"{mode}_capsule_baseline", benchmark, variant, seed, scale, "results/processed/capsule_baseline_comparison.csv", "yes", mode))
        for benchmark in BENCHMARKS:
            rows.append(_row("Negative/corruption replay", f"{mode}_negative", benchmark, "failing", 1, scales[0], "results/processed/full_rtl_replay_negative.csv", "yes", mode))
        for scale in scales:
            rows.append(_row("Workload scaling", f"{mode}_workload_{scale}", "all", "all", "all", scale, "results/processed/workload_scaling.csv", "yes", WORKLOAD_SCALES[scale]["notes"]))
            rows.append(_row("Buffer-depth sensitivity", f"{mode}_buffer_{scale}", "all", "all", "all", scale, "results/processed/buffer_sensitivity.csv", "yes", mode))
            rows.append(_row("Event-sufficiency ablation at scale", f"{mode}_event_ablation_{scale}", "all", "all", "all", scale, "results/processed/event_ablation_scaling.csv", "yes", mode))
        for config in RECORDER_CONFIGS:
            rows.append(_row("Recorder-configuration sensitivity", f"{mode}_recorder_{config}", "all", "all", "all", "all", "results/processed/recorder_config_replay.csv", "yes", RECORDER_CONFIGS[config]["notes"], recorder_config=config))

    for mode in ("quick", "full"):
        memory_values = (2048,) if mode == "quick" else MAPPED_MEMORY_WORDS
        buffer_values = (32,) if mode == "quick" else MAPPED_BUFFER_DEPTHS
        configs = ("full",) if mode == "quick" else MAPPED_CONFIGS
        for memory_words in memory_values:
            for buffer_depth in buffer_values:
                for config in configs:
                    for design in ("full_core_baseline_board", "full_core_replaycapsule_board"):
                        rows.append(
                            _row(
                                "Full-core mapped FPGA scaling",
                                f"{mode}_mapped_{design}",
                                "NA",
                                design,
                                "NA",
                                "NA",
                                "results/processed/mapped_scaling.csv",
                                "yes",
                                mode,
                                memory_words=memory_words,
                                buffer_depth=buffer_depth,
                                recorder_config=config,
                                target="ecp5-85k",
                                flow="yosys+synth_ecp5+nextpnr-ecp5",
                            )
                        )
                    rows.append(
                        _row(
                            "Recorder presence after mapping",
                            f"{mode}_presence",
                            "NA",
                            "full_core_replaycapsule_board",
                            "NA",
                            "NA",
                            "results/processed/mapped_recorder_presence.csv",
                            "yes",
                            mode,
                            memory_words=memory_words,
                            buffer_depth=buffer_depth,
                            recorder_config=config,
                            target="ecp5-85k",
                            flow="yosys+synth_ecp5+nextpnr-ecp5",
                        )
                    )
                    rows.append(
                        _row(
                            "Failure diagnosis for failed mapped rows",
                            f"{mode}_mapped_diagnosis",
                            "NA",
                            "all",
                            "NA",
                            "NA",
                            "results/processed/mapped_failure_diagnosis.csv",
                            "yes",
                            mode,
                            memory_words=memory_words,
                            buffer_depth=buffer_depth,
                            recorder_config=config,
                            target="ecp5-85k",
                            flow="yosys+synth_ecp5+nextpnr-ecp5",
                        )
                    )

    rows.append(_row("Paper figure/table generation", "topconf_tables", "all", "all", "all", "all", "paper/tables/*.tex", "yes", "generated after CSV evidence"))
    rows.append(_row("Paper figure/table generation", "topconf_figures", "all", "all", "all", "all", "paper/figures/fig_*.pdf", "yes", "generated after CSV evidence"))
    return rows


def _row(
    group: str,
    experiment_id: str,
    benchmark: object,
    variant: object,
    seed: object,
    scale: object,
    expected_output: str,
    required: str,
    notes: str,
    memory_words: object = "NA",
    buffer_depth: object = "NA",
    recorder_config: object = "NA",
    target: object = "NA",
    flow: object = "NA",
) -> dict[str, object]:
    return {
        "experiment_group": group,
        "experiment_id": experiment_id,
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "workload_scale": scale,
        "memory_words": memory_words,
        "buffer_depth": buffer_depth,
        "recorder_config": recorder_config,
        "target": target,
        "flow": flow,
        "required_for_top_conference": required,
        "expected_output": expected_output,
        "status": "DEFINED",
        "notes": notes,
    }


def _write_doc(rows: list[dict[str, object]]) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    group_counts: dict[str, int] = {}
    for row in rows:
        group = str(row["experiment_group"])
        group_counts[group] = group_counts.get(group, 0) + 1
    lines = [
        "# Top-Conference Evaluation Matrix",
        "",
        "This matrix defines the quick and full evaluation space before results are marked PASS. Result-producing scripts update separate evidence CSVs; this file is a plan, not a pass list.",
        "",
        "| Experiment group | Defined rows | Evidence output |",
        "|---|---:|---|",
    ]
    for group, count in sorted(group_counts.items()):
        outputs = sorted({str(row["expected_output"]) for row in rows if row["experiment_group"] == group})
        lines.append(f"| {group} | {count} | {', '.join(outputs)} |")
    lines.extend(
        [
            "",
            "Quick mode covers all six benchmark families with a small seed/scale subset for local debugging.",
            "Full mode expands seeds, workload scales, memory sizes, buffer depths, and recorder configurations when CI time permits.",
            "Rows remain `DEFINED` here until their corresponding processed CSV contains measured, estimated, blocked, timeout, or failed evidence.",
        ]
    )
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
