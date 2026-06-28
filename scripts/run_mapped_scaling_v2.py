#!/usr/bin/env python3
"""Write v2 mapped-scaling comparison tables with full-core v2 integration status explicit."""

from __future__ import annotations

from topconf_eval_common import REPO_ROOT, read_csv, write_csv


OUT_CSV = REPO_ROOT / "results/processed/mapped_scaling_v2.csv"
OVERHEAD_CSV = REPO_ROOT / "results/processed/mapped_scaling_overhead_v2.csv"
PRESENCE_CSV = REPO_ROOT / "results/processed/mapped_recorder_presence_v2.csv"

FIELDS = [
    "architecture",
    "recorder_config",
    "target",
    "flow",
    "design",
    "memory_words",
    "buffer_depth",
    "lut",
    "ff",
    "bram",
    "dsp",
    "cells",
    "area_um2",
    "fmax_mhz",
    "wns",
    "tns",
    "power_mw",
    "status",
    "report_path",
    "notes",
]

OVERHEAD_FIELDS = [
    "architecture",
    "recorder_config",
    "target",
    "flow",
    "memory_words",
    "buffer_depth",
    "metric",
    "baseline",
    "with_replaycapsule",
    "delta",
    "percent_overhead",
    "claim_allowed",
    "notes",
]

PRESENCE_FIELDS = [
    "architecture",
    "recorder_config",
    "design",
    "target",
    "flow",
    "memory_words",
    "buffer_depth",
    "recorder_present",
    "evidence",
    "status",
    "notes",
]


def main() -> int:
    rows = _mapped_rows()
    overhead = _overhead_rows()
    presence = _presence_rows()
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(OVERHEAD_CSV, OVERHEAD_FIELDS, overhead)
    write_csv(PRESENCE_CSV, PRESENCE_FIELDS, presence)
    print("WROTE results/processed/mapped_scaling_v2.csv")
    print("WROTE results/processed/mapped_scaling_overhead_v2.csv")
    print("WROTE results/processed/mapped_recorder_presence_v2.csv")
    return 0


def _mapped_rows() -> list[dict[str, object]]:
    out = []
    for row in read_csv(REPO_ROOT / "results/processed/mapped_scaling.csv"):
        out.append(
            {
                "architecture": "v1",
                "recorder_config": row.get("recorder_config", "full"),
                "target": row.get("target", "NA"),
                "flow": row.get("flow", "NA"),
                "design": row.get("design", "NA"),
                "memory_words": row.get("memory_words", "NA"),
                "buffer_depth": row.get("buffer_depth", "NA"),
                "lut": row.get("lut", "NA"),
                "ff": row.get("ff", "NA"),
                "bram": row.get("bram", "NA"),
                "dsp": row.get("dsp", "NA"),
                "cells": row.get("cells", "NA"),
                "area_um2": row.get("area_um2", "NA"),
                "fmax_mhz": row.get("fmax_mhz", "NA"),
                "wns": row.get("wns", "NA"),
                "tns": row.get("tns", "NA"),
                "power_mw": row.get("power_mw", "NA"),
                "status": row.get("status", "NA"),
                "report_path": row.get("report_path", "NA"),
                "notes": "measured v1 mapped scaling row",
            }
        )
    for config in ("core", "hashed", "full"):
        for memory_words in (1024, 2048, 4096):
            for buffer_depth in (128, 256, 512, 1024):
                out.append(_blocked_v2_row(config, memory_words, buffer_depth))
    return out


def _blocked_v2_row(config: str, memory_words: int, buffer_depth: int) -> dict[str, object]:
    return {
        "architecture": "v2",
        "recorder_config": config,
        "target": "ecp5-85k",
        "flow": "yosys+synth_ecp5+nextpnr-ecp5",
        "design": "full_core_replaycapsule_v2_board",
        "memory_words": memory_words,
        "buffer_depth": buffer_depth,
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
        "status": "BLOCKED",
        "report_path": "NA",
        "notes": "full-core v2 mapped overhead blocked: v2 recorder is not integrated into the full-core board wrapper; do not compare standalone prototype against full-core v1",
    }


def _overhead_rows() -> list[dict[str, object]]:
    out = []
    for row in read_csv(REPO_ROOT / "results/processed/mapped_scaling_overhead.csv"):
        out.append(
            {
                "architecture": "v1",
                "recorder_config": row.get("recorder_config", "full"),
                "target": row.get("target", "NA"),
                "flow": row.get("flow", "NA"),
                "memory_words": row.get("memory_words", "NA"),
                "buffer_depth": row.get("buffer_depth", "NA"),
                "metric": row.get("metric", "NA"),
                "baseline": row.get("baseline", "NA"),
                "with_replaycapsule": row.get("with_replaycapsule", "NA"),
                "delta": row.get("delta", "NA"),
                "percent_overhead": row.get("percent_overhead", "NA"),
                "claim_allowed": row.get("claim_allowed", "NA"),
                "notes": row.get("notes", "measured v1 overhead row"),
            }
        )
    for config in ("core", "hashed", "full"):
        for metric in ("lut", "ff", "bram", "fmax_mhz"):
            out.append(
                {
                    "architecture": "v2",
                    "recorder_config": config,
                    "target": "ecp5-85k",
                    "flow": "yosys+synth_ecp5+nextpnr-ecp5",
                    "memory_words": "2048",
                    "buffer_depth": "512",
                    "metric": metric,
                    "baseline": "NA",
                    "with_replaycapsule": "NA",
                    "delta": "NA",
                    "percent_overhead": "NA",
                    "claim_allowed": "no",
                    "notes": "blocked until same-target full-core v2 board mapping exists",
                }
            )
    return out


def _presence_rows() -> list[dict[str, object]]:
    out = []
    for row in read_csv(REPO_ROOT / "results/processed/mapped_recorder_presence.csv"):
        out.append(
            {
                "architecture": "v1",
                "recorder_config": row.get("recorder_config", "full"),
                "design": row.get("design", "NA"),
                "target": row.get("target", "NA"),
                "flow": row.get("flow", "NA"),
                "memory_words": row.get("memory_words", "NA"),
                "buffer_depth": row.get("buffer_depth", "NA"),
                "recorder_present": row.get("recorder_present", "NA"),
                "evidence": row.get("evidence", "NA"),
                "status": row.get("status", "NA"),
                "notes": row.get("notes", "measured v1 recorder-presence row"),
            }
        )
    for config in ("core", "hashed", "full"):
        out.append(
            {
                "architecture": "v2",
                "recorder_config": config,
                "design": "full_core_replaycapsule_v2_board",
                "target": "ecp5-85k",
                "flow": "yosys+synth_ecp5+nextpnr-ecp5",
                "memory_words": "2048",
                "buffer_depth": "512",
                "recorder_present": "NA",
                "evidence": "NA",
                "status": "BLOCKED",
                "notes": "full-core v2 board wrapper not integrated yet",
            }
        )
    return out


if __name__ == "__main__":
    raise SystemExit(main())
