#!/usr/bin/env python3
"""Generate per-benchmark local evidence coverage across result artifacts."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPLAY_CSV = REPO_ROOT / "results/processed/replay_experiments.csv"
SMOKE_CSV = REPO_ROOT / "results/processed/picorv32_smoke_summary.csv"
RTL_EXPORTS_CSV = REPO_ROOT / "results/processed/rtl_capsule_exports.csv"
RTL_ALIGNMENT_CSV = REPO_ROOT / "results/processed/rtl_firmware_alignment.csv"
EVENT_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/event_sufficiency.csv"
RTL_SMOKE_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/rtl_smoke_event_sufficiency.csv"
OUT_CSV = REPO_ROOT / "results/processed/benchmark_coverage.csv"

BENCHMARKS = (
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
)

FIELDNAMES = [
    "benchmark",
    "local_coverage_status",
    "evidence_level",
    "model_replay",
    "firmware_sim_replay",
    "picorv32_failing_smoke",
    "picorv32_fixed_smoke",
    "picorv32_edge_smoke",
    "rtl_export_failing",
    "rtl_export_fixed",
    "rtl_alignment_failing",
    "rtl_alignment_fixed",
    "model_required_events",
    "rtl_smoke_required_events",
    "full_firmware_running_rtl_replay",
    "notes",
]


def main() -> int:
    replay_rows = _read_rows(REPLAY_CSV)
    smoke_rows = _read_rows(SMOKE_CSV)
    export_rows = _read_rows(RTL_EXPORTS_CSV)
    alignment_rows = _read_rows(RTL_ALIGNMENT_CSV)
    sufficiency_rows = _read_rows(EVENT_SUFFICIENCY_CSV)
    rtl_sufficiency_rows = _read_rows(RTL_SMOKE_SUFFICIENCY_CSV)
    rows = [
        _benchmark_row(
            benchmark,
            replay_rows,
            smoke_rows,
            export_rows,
            alignment_rows,
            sufficiency_rows,
            rtl_sufficiency_rows,
        )
        for benchmark in BENCHMARKS
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if any(row["local_coverage_status"] != "PASS_LOCAL" for row in rows) else 0


def _benchmark_row(
    benchmark: str,
    replay_rows: list[dict[str, str]],
    smoke_rows: list[dict[str, str]],
    export_rows: list[dict[str, str]],
    alignment_rows: list[dict[str, str]],
    sufficiency_rows: list[dict[str, str]],
    rtl_sufficiency_rows: list[dict[str, str]],
) -> dict[str, str]:
    model_replay = _status(_find(replay_rows, experiment=benchmark, evidence_level="model"))
    firmware_replay = _status(_find(replay_rows, experiment=f"{benchmark}_firmware_sim", evidence_level="firmware-sim"))
    failing_smoke = _status(_find(smoke_rows, benchmark=benchmark, variant="failing"))
    fixed_smoke = _status(_find(smoke_rows, benchmark=benchmark, variant="fixed"))
    edge_smoke = _status(_find(smoke_rows, benchmark=benchmark, variant="no_failure_edge"), default="NA")
    export_failing = _status(_find(export_rows, benchmark=benchmark, variant="failing"))
    export_fixed = _status(_find(export_rows, benchmark=benchmark, variant="fixed"))
    alignment_failing = _alignment_status(_find(alignment_rows, benchmark=benchmark, variant="failing"))
    alignment_fixed = _alignment_status(_find(alignment_rows, benchmark=benchmark, variant="fixed"))
    model_required = _value(_find(sufficiency_rows, benchmark=benchmark), "required_event_classes")
    rtl_required = _value(_find(rtl_sufficiency_rows, benchmark=benchmark, variant="failing"), "required_event_classes")
    required_statuses = (
        model_replay,
        firmware_replay,
        failing_smoke,
        fixed_smoke,
        export_failing,
        export_fixed,
        alignment_failing,
        alignment_fixed,
    )
    required_values = (model_required, rtl_required)
    local_status = "PASS_LOCAL" if all(status == "PASS" for status in required_statuses) and all(_known(value) for value in required_values) else "TODO"
    return {
        "benchmark": benchmark,
        "local_coverage_status": local_status,
        "evidence_level": "model+firmware-sim+rtl-smoke",
        "model_replay": model_replay,
        "firmware_sim_replay": firmware_replay,
        "picorv32_failing_smoke": failing_smoke,
        "picorv32_fixed_smoke": fixed_smoke,
        "picorv32_edge_smoke": edge_smoke,
        "rtl_export_failing": export_failing,
        "rtl_export_fixed": export_fixed,
        "rtl_alignment_failing": alignment_failing,
        "rtl_alignment_fixed": alignment_fixed,
        "model_required_events": model_required,
        "rtl_smoke_required_events": rtl_required,
        "full_firmware_running_rtl_replay": "reported-separately",
        "notes": "local model, firmware-sim, wrapper-smoke, export, alignment, and sufficiency evidence present; compiler-backed full RTL replay is reported in full_rtl_replay.csv",
    }


def _alignment_status(row: dict[str, str]) -> str:
    if not row:
        return "TODO"
    if row.get("status") != "PASS" or row.get("property_alignment") != "PASS":
        return row.get("status", "TODO")
    if row.get("variant") == "failing" and row.get("key_event_alignment") != "PASS":
        return row.get("key_event_alignment", "TODO")
    return "PASS"


def _status(row: dict[str, str], default: str = "TODO") -> str:
    return row.get("status", default) if row else default


def _value(row: dict[str, str], key: str) -> str:
    return row.get(key, "TODO") if row else "TODO"


def _known(value: str) -> bool:
    return value not in {"", "NA", "TODO"}


def _find(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in criteria.items()):
            return row
    return {}


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    raise SystemExit(main())
