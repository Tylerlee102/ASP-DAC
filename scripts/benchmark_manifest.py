#!/usr/bin/env python3
"""Write benchmark diversity manifest and explicitly scoped replay coverage."""

from __future__ import annotations

from topconf_eval_common import REPO_ROOT, read_csv, write_csv


MANIFEST_CSV = REPO_ROOT / "results/processed/benchmark_manifest.csv"
EXPANDED_REPLAY_CSV = REPO_ROOT / "results/processed/expanded_benchmark_replay.csv"

MANIFEST_FIELDS = [
    "benchmark",
    "benchmark_family",
    "new_or_existing",
    "variants",
    "deterministic_seed_support",
    "compiler_backed_firmware",
    "property_id",
    "model_support",
    "rtl_replay_support",
    "notes",
]

REPLAY_FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "benchmark_family",
    "new_or_existing",
    "firmware_status",
    "rtl_replay_status",
    "property_match",
    "event_match",
    "final_signature_match",
    "notes",
]

EXISTING = {
    "sensor_threshold_bug": ("sensor_threshold", "3"),
    "interrupt_race_bug": ("interrupt_race", "2"),
    "mmio_ordering_bug": ("mmio_ordering", "5"),
    "stack_corruption_bug": ("stack_corruption", "4"),
    "uart_command_bug": ("uart_command", "1"),
    "watchdog_timeout_bug": ("watchdog_timeout", "6"),
}

CANDIDATES = {
    "timer_jitter_bug": ("timer_jitter_bug", "7"),
    "nested_interrupt_bug": ("nested_interrupt_bug", "8"),
    "multi_mmio_peripheral_bug": ("multi_mmio_peripheral_bug", "9"),
    "dma_like_mmio_burst_bug_without_real_dma": ("dma_like_mmio_burst_bug_without_real_dma", "10"),
}

MEASURED_EXPANSION = {
    "commanded_actuator_limit_bug": ("commanded_actuator_limit", "1"),
    "late_config_sequence_bug": ("late_config_sequence", "5"),
    "sensor_debounce_bug": ("sensor_debounce", "3"),
    "status_clear_on_read_bug": ("status_clear_on_read", "1"),
    "platform2_status_window_bug": ("platform2_status_window", "1"),
    "platform2_config_order_bug": ("platform2_config_order", "5"),
    "environmental_controller_bug": ("environmental_controller", "1"),
    "power_rail_sequencer_bug": ("power_rail_sequencer", "5"),
}


def main() -> int:
    write_csv(MANIFEST_CSV, MANIFEST_FIELDS, _manifest_rows())
    write_csv(EXPANDED_REPLAY_CSV, REPLAY_FIELDS, _replay_rows())
    print("WROTE results/processed/benchmark_manifest.csv")
    print("WROTE results/processed/expanded_benchmark_replay.csv")
    return 0


def _manifest_rows() -> list[dict[str, object]]:
    rows = []
    for benchmark, (family, prop) in EXISTING.items():
        rows.append(
            {
                "benchmark": benchmark,
                "benchmark_family": family,
                "new_or_existing": "existing",
                "variants": "failing;fixed" + (";no_failure_edge" if benchmark in {"sensor_threshold_bug", "uart_command_bug", "watchdog_timeout_bug"} else ""),
                "deterministic_seed_support": "true",
                "compiler_backed_firmware": "true",
                "property_id": prop,
                "model_support": "true",
                "rtl_replay_support": "true",
                "notes": "existing benchmark family with current replay evidence",
            }
        )
    for benchmark, (family, prop) in MEASURED_EXPANSION.items():
        rows.append(
            {
                "benchmark": benchmark,
                "benchmark_family": family,
                "new_or_existing": "new_measured",
                "variants": "failing;fixed",
                "deterministic_seed_support": "true",
                "compiler_backed_firmware": "true",
                "property_id": prop,
                "model_support": "not_claimed",
                "rtl_replay_support": "true",
                "notes": "new compiler-backed firmware family with measured v2 full RTL replay evidence",
            }
        )
    for benchmark, (family, prop) in CANDIDATES.items():
        rows.append(
            {
                "benchmark": benchmark,
                "benchmark_family": family,
                "new_or_existing": "candidate",
                "variants": "failing;fixed",
                "deterministic_seed_support": "planned",
                "compiler_backed_firmware": "not_integrated",
                "property_id": prop,
                "model_support": "not_integrated",
                "rtl_replay_support": "not_integrated",
                "notes": "candidate added to diversity plan; not counted as replay evidence until property checker, firmware build, and RTL harness support land",
            }
        )
    return rows


def _replay_rows() -> list[dict[str, object]]:
    replay = read_csv(REPO_ROOT / "results/processed/full_rtl_replay.csv")
    expanded = read_csv(REPO_ROOT / "results/processed/expanded_benchmark_replay_measured.csv")
    rows = []
    for row in replay:
        family, _ = EXISTING.get(row.get("benchmark", ""), ("unknown", "NA"))
        rows.append(
            {
                "benchmark": row.get("benchmark", "NA"),
                "variant": row.get("variant", "NA"),
                "seed": row.get("seed", "NA"),
                "benchmark_family": family,
                "new_or_existing": "existing",
                "firmware_status": row.get("rtl_record_status", "NA"),
                "rtl_replay_status": row.get("replay_status", "NA"),
                "property_match": "PASS" if row.get("property_id_record") == row.get("property_id_replay") else "FAIL",
                "event_match": row.get("event_match", "NA"),
                "final_signature_match": row.get("final_signature_match", "NA"),
                "notes": "existing measured full RTL replay row",
            }
        )
    for row in expanded:
        family, _ = MEASURED_EXPANSION.get(row.get("benchmark", ""), ("unknown", "NA"))
        rows.append(
            {
                "benchmark": row.get("benchmark", "NA"),
                "variant": row.get("variant", "NA"),
                "seed": row.get("seed", "NA"),
                "benchmark_family": family,
                "new_or_existing": "new_measured",
                "firmware_status": row.get("rtl_record_status", "NA"),
                "rtl_replay_status": row.get("replay_status", "NA"),
                "property_match": "PASS" if row.get("property_id_record") == row.get("property_id_replay") else "FAIL",
                "event_match": row.get("event_match", "NA"),
                "final_signature_match": row.get("final_signature_match", "NA"),
                "notes": "new measured v2 full RTL replay row",
            }
        )
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
