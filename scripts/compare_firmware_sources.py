#!/usr/bin/env python3
"""Compare fallback firmware intent with compiler-backed RTL replay rows."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from rv32i_firmware_sim import RV32IFirmwareSim, build_program  # noqa: E402


FULL_REPLAY_CSV = REPO_ROOT / "results/processed/full_rtl_replay.csv"
OUT_CSV = REPO_ROOT / "results/processed/firmware_source_comparison.csv"
DEBUG_DIR = REPO_ROOT / "results/debug/pass7/source_compare"

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "fallback_status",
    "compiler_status",
    "fallback_property_id",
    "compiler_property_id",
    "fallback_cycles_to_failure",
    "compiler_cycles_to_failure",
    "fallback_commits_to_failure",
    "compiler_commits_to_failure",
    "fallback_event_count",
    "compiler_event_count",
    "same_property",
    "same_event_count",
    "first_divergence",
    "likely_root_cause",
    "notes",
]

DEFAULT_CASES = (
    ("interrupt_race_bug", "failing"),
    ("mmio_ordering_bug", "failing"),
    ("stack_corruption_bug", "failing"),
    ("uart_command_bug", "failing"),
)

PROPERTY_NUMBER_BY_NAME = {
    "P1_ACTUATOR_LIMIT": "1",
    "P2_INTERRUPT_CRITICAL": "2",
    "P3_SENSOR_DEADLINE": "3",
    "P4_STACK_PROTECT": "4",
    "P5_MMIO_ORDERING": "5",
    "P6_WATCHDOG_TIMEOUT": "6",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="append", help="benchmark to compare; may be repeated")
    parser.add_argument("--variant", default="failing", help="variant to compare when --benchmark is used")
    parser.add_argument("--seed", type=int, action="append", help="seed to compare; may be repeated")
    parser.add_argument("--full-replay-csv", type=Path, default=FULL_REPLAY_CSV)
    parser.add_argument("--out-csv", type=Path, default=OUT_CSV)
    parser.add_argument("--debug-dir", type=Path, default=DEBUG_DIR)
    args = parser.parse_args()

    replay_rows = _read_rows(args.full_replay_csv)
    selected = _select_rows(replay_rows, args.benchmark, args.variant, args.seed)
    rows = [_compare_row(row, args.debug_dir) for row in selected]

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {_rel(args.out_csv)}")
    return 0


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _select_rows(
    replay_rows: list[dict[str, str]],
    benchmarks: list[str] | None,
    variant: str,
    seeds: list[int] | None,
) -> list[dict[str, str]]:
    seed_values = seeds or [1, 2, 3]
    if benchmarks:
        wanted = {(benchmark, variant, str(seed)) for benchmark in benchmarks for seed in seed_values}
    else:
        wanted = {(benchmark, variant, str(seed)) for benchmark, variant in DEFAULT_CASES for seed in seed_values}
    rows_by_key = {
        (row.get("benchmark", ""), row.get("variant", ""), row.get("seed", "")): row
        for row in replay_rows
    }
    selected = []
    for benchmark, variant_name, seed in sorted(wanted):
        selected.append(rows_by_key.get((benchmark, variant_name, seed), _missing_row(benchmark, variant_name, seed)))
    return selected


def _missing_row(benchmark: str, variant: str, seed: str) -> dict[str, str]:
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "rtl_record_status": "MISSING",
        "replay_status": "MISSING",
        "final_signature_match": "MISSING",
        "property_id_record": "NA",
        "cycles_to_failure": "NA",
        "commits_to_failure": "NA",
        "capsule_bytes": "NA",
        "notes": "full RTL replay row missing",
    }


def _compare_row(row: dict[str, str], debug_dir: Path) -> dict[str, str]:
    benchmark = row["benchmark"]
    variant = row["variant"]
    seed = row["seed"]
    fallback = _run_fallback(benchmark, variant)
    compiler_backed = row.get("compiler_backed") == "true" and row.get("firmware_source") == "compiler_c"
    compiler_status = _case_status(row) if compiler_backed else "BLOCKED"
    compiler_property = row.get("property_id_record", "NA") if compiler_backed else "NA"
    compiler_events = _event_count_from_row(row) if compiler_backed else "NA"
    same_property = "PASS" if _property_number(fallback["property_id"]) == _property_number(compiler_property) else "FAIL"
    same_event_count = "PASS" if str(fallback["event_count"]) == str(compiler_events) else "FAIL"
    first_divergence = _first_divergence(fallback, row, same_property, same_event_count)
    likely_root_cause = _likely_root_cause(row, first_divergence)
    _write_source_compare_debug(debug_dir, benchmark, variant, seed, fallback, row, first_divergence)
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": seed,
        "fallback_status": fallback["status"],
        "compiler_status": compiler_status,
        "fallback_property_id": _property_number(fallback["property_id"]),
        "compiler_property_id": compiler_property,
        "fallback_cycles_to_failure": str(fallback["cycles_to_failure"]),
        "compiler_cycles_to_failure": row.get("cycles_to_failure", "NA") if compiler_backed else "NA",
        "fallback_commits_to_failure": str(fallback["commits_to_failure"]),
        "compiler_commits_to_failure": row.get("commits_to_failure", "NA") if compiler_backed else "NA",
        "fallback_event_count": str(fallback["event_count"]),
        "compiler_event_count": compiler_events,
        "same_property": same_property,
        "same_event_count": same_event_count,
        "first_divergence": first_divergence,
        "likely_root_cause": likely_root_cause,
        "notes": row.get("notes", ""),
    }


def _run_fallback(benchmark: str, variant: str) -> dict[str, object]:
    failing = variant != "fixed"
    sim = RV32IFirmwareSim(build_program(benchmark, failing=failing))
    result = sim.run()
    events = list(result.events)
    return {
        "status": "PASS" if (result.failed if failing else not result.failed) else "FAIL",
        "property_id": result.property_id or 0,
        "cycles_to_failure": events[-1].cycle if events else 0,
        "commits_to_failure": events[-1].commit if events else 0,
        "event_count": len(events),
        "events": [event.to_trace_dict() for event in events],
    }


def _case_status(row: dict[str, str]) -> str:
    if (
        row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
    ):
        return "PASS"
    if row.get("rtl_record_status") == "MISSING":
        return "MISSING"
    if "BLOCKED" in {row.get("rtl_record_status"), row.get("replay_status")}:
        return "BLOCKED"
    return "FAIL"


def _event_count_from_row(row: dict[str, str]) -> str:
    try:
        return str(int(row.get("capsule_bytes", "NA")) // 21)
    except (TypeError, ValueError):
        return "NA"


def _first_divergence(fallback: dict[str, object], row: dict[str, str], same_property: str, same_event_count: str) -> str:
    if not (row.get("compiler_backed") == "true" and row.get("firmware_source") == "compiler_c"):
        return "compiler-backed RTL row unavailable"
    if row.get("rtl_record_status") == "MISSING":
        return "compiler row missing"
    if same_property == "FAIL":
        return f"property_id fallback={_property_number(fallback['property_id'])} compiler={_property_number(row.get('property_id_record', 'NA'))}"
    if row.get("rtl_record_status") != "PASS":
        return row.get("notes", "compiler record did not pass")
    if same_event_count == "FAIL":
        return f"event_count fallback={fallback['event_count']} compiler={_event_count_from_row(row)}"
    if row.get("replay_status") != "PASS":
        return row.get("notes", "compiler replay did not pass")
    return "none"


def _likely_root_cause(row: dict[str, str], first_divergence: str) -> str:
    if first_divergence == "compiler-backed RTL row unavailable":
        return "compiler-backed firmware row unavailable in input replay CSV"
    if "compiler=0" in first_divergence or row.get("property_id_record") in {"0", "NA"}:
        return "compiler-backed firmware did not execute the expected failing action before stop"
    if row.get("rtl_record_status") == "MISSING":
        return "full RTL replay output missing"
    if row.get("replay_status") == "FAIL":
        return "record/replay mismatch after record"
    return "compiler and fallback behavior differ"


def _write_source_compare_debug(
    debug_dir: Path,
    benchmark: str,
    variant: str,
    seed: str,
    fallback: dict[str, object],
    row: dict[str, str],
    first_divergence: str,
) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    base = f"{benchmark}_{variant}_seed{seed}"
    fallback_events = [event for event in fallback["events"] if event.get("event_type") in {"EV_MMIO_READ", "EV_MMIO_WRITE"}]
    (debug_dir / f"{base}_fallback_mmio.txt").write_text(
        "\n".join(json.dumps(event, sort_keys=True) for event in fallback_events) + "\n",
        encoding="utf-8",
    )
    compiler_trace = REPO_ROOT / "results/debug/pass7" / f"{base}_mmio_trace.txt"
    if compiler_trace.exists():
        compiler_text = compiler_trace.read_text(encoding="utf-8", errors="replace")
    else:
        compiler_text = "compiler MMIO trace not available; rerun full RTL replay with --dump-mmio\n"
    (debug_dir / f"{base}_compiler_mmio.txt").write_text(compiler_text, encoding="utf-8")
    diff_lines = [
        f"fallback_property_id={_property_number(fallback['property_id'])}",
        f"compiler_property_id={_property_number(row.get('property_id_record', 'NA'))}",
        f"fallback_event_count={fallback['event_count']}",
        f"compiler_event_count={_event_count_from_row(row)}",
        f"first_divergence={first_divergence}",
    ]
    (debug_dir / f"{base}_diff.txt").write_text("\n".join(diff_lines) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _property_number(value: object) -> str:
    text = str(value)
    if text in PROPERTY_NUMBER_BY_NAME:
        return PROPERTY_NUMBER_BY_NAME[text]
    if text == "None":
        return "0"
    return text


if __name__ == "__main__":
    raise SystemExit(main())
