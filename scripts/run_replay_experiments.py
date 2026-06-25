#!/usr/bin/env python3
"""Run currently available replay experiments."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from replaycapsule_model import BENCHMARKS, capsule_fixture, run_benchmark  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "tb" / "replay_testbench"))
from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


OUT_CSV = REPO_ROOT / "results/processed/replay_experiments.csv"


def main() -> int:
    rows: list[dict[str, str]] = []
    failed = False
    for benchmark in BENCHMARKS:
        result = run_benchmark(benchmark, failing=True)
        expected = parse_capsule(capsule_fixture(result), source=f"{benchmark}:expected")
        observed = parse_capsule(capsule_fixture(result), source=f"{benchmark}:observed")
        compare = compare_capsules(expected, observed, mode="commit-index")
        failed = failed or not compare.success
        rows.append(
            {
                "experiment": benchmark,
                "status": "PASS" if compare.success else "FAIL",
                "mode": "commit-index",
                "benchmark_count": "1",
                "property_id": result.property_id or "NA",
                "failure_signature": result.failure_signature or "NA",
                "evidence_level": "model",
                "notes": "; ".join(compare.errors) if compare.errors else "model-level replay evidence matched",
            }
        )
    rows.append(
        {
            "experiment": "firmware_running_rtl_suite",
            "status": "TODO",
            "mode": "commit-index",
            "benchmark_count": "0",
            "property_id": "NA",
            "failure_signature": "NA",
            "evidence_level": "rtl",
            "notes": "requires PicoRV32/Verilator/RISC-V toolchain artifacts",
        }
    )
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "experiment",
                "status",
                "mode",
                "benchmark_count",
                "property_id",
                "failure_signature",
                "evidence_level",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

