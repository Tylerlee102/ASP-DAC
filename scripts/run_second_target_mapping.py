#!/usr/bin/env python3
"""Try a second FPGA target for the replay-consume prototype and report blockers."""

from __future__ import annotations

from pathlib import Path

import run_replay_consumer_mapping
from topconf_eval_common import REPO_ROOT, rel, write_csv


OUT_CSV = REPO_ROOT / "results/processed/second_target_mapping.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/second_target_mapping_summary.csv"
FIELDS = [
    "target",
    "flow",
    "architecture",
    "recorder_config",
    "design",
    "memory_words",
    "buffer_depth",
    "lut",
    "ff",
    "bram",
    "area_um2",
    "fmax_mhz",
    "status",
    "report_path",
    "notes",
]
SUMMARY_FIELDS = ["target", "flow", "attempted", "pass_count", "fail_count", "blocked_count", "notes"]


def main() -> int:
    yosys = run_replay_consumer_mapping._find_tool("yosys.exe") or run_replay_consumer_mapping._find_tool("yosys")
    nextpnr = run_replay_consumer_mapping._find_tool("nextpnr-ecp5.exe") or run_replay_consumer_mapping._find_tool("nextpnr-ecp5")
    if not yosys or not nextpnr:
        rows = [_blocked("missing yosys or nextpnr-ecp5")]
    else:
        mapped = run_replay_consumer_mapping._run_mapping(yosys, nextpnr, "ecp5-45k", ("--45k", "--package", "CABGA381", "--freq", "50"))
        rows = [
            {
                "target": mapped["target"],
                "flow": mapped["flow"],
                "architecture": "v2",
                "recorder_config": "replay_consumer",
                "design": mapped["design"],
                "memory_words": "NA",
                "buffer_depth": "NA",
                "lut": mapped["lut"],
                "ff": mapped["ff"],
                "bram": mapped["bram"],
                "area_um2": "NA",
                "fmax_mhz": mapped["fmax_mhz"],
                "status": mapped["status"],
                "report_path": mapped["report_path"],
                "notes": mapped["notes"] + "; second target is prototype-only, not full-core evidence",
            }
        ]
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(SUMMARY_CSV, SUMMARY_FIELDS, [_summary(rows)])
    print("WROTE results/processed/second_target_mapping.csv")
    print("WROTE results/processed/second_target_mapping_summary.csv")
    return 0 if any(row["status"] == "PASS" for row in rows) else 1


def _blocked(notes: str) -> dict[str, object]:
    return {
        "target": "ecp5-45k",
        "flow": "yosys+synth_ecp5+nextpnr-ecp5",
        "architecture": "v2",
        "recorder_config": "replay_consumer",
        "design": "rcv2_replay_consumer",
        "memory_words": "NA",
        "buffer_depth": "NA",
        "lut": "NA",
        "ff": "NA",
        "bram": "NA",
        "area_um2": "NA",
        "fmax_mhz": "NA",
        "status": "BLOCKED",
        "report_path": "NA",
        "notes": notes,
    }


def _summary(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "target": rows[0]["target"] if rows else "ecp5-45k",
        "flow": rows[0]["flow"] if rows else "yosys+synth_ecp5+nextpnr-ecp5",
        "attempted": len(rows),
        "pass_count": sum(1 for row in rows if row["status"] == "PASS"),
        "fail_count": sum(1 for row in rows if row["status"] == "FAIL"),
        "blocked_count": sum(1 for row in rows if row["status"] == "BLOCKED"),
        "notes": "second-target evidence is scoped to replay-consume prototype unless full-core row exists",
    }


if __name__ == "__main__":
    raise SystemExit(main())
