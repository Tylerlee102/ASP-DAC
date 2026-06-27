#!/usr/bin/env python3
"""Run parameterized full-core mapped FPGA scaling sweeps."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import run_mapped_synthesis
from topconf_eval_common import MAPPED_BUFFER_DEPTHS, MAPPED_CONFIGS, MAPPED_MEMORY_WORDS, RECORDER_CONFIGS, REPO_ROOT, pct_delta, rel, safe_float, write_csv


OUT_CSV = REPO_ROOT / "results/processed/mapped_scaling.csv"
OVERHEAD_CSV = REPO_ROOT / "results/processed/mapped_scaling_overhead.csv"
PRESENCE_CSV = REPO_ROOT / "results/processed/mapped_recorder_presence.csv"
RAW_DIR = REPO_ROOT / "results/raw/mapped_scaling"

FIELDS = [
    "target",
    "flow",
    "design",
    "memory_words",
    "buffer_depth",
    "recorder_config",
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
    "target",
    "flow",
    "memory_words",
    "buffer_depth",
    "recorder_config",
    "metric",
    "baseline",
    "with_replaycapsule",
    "delta",
    "percent_overhead",
    "claim_allowed",
    "notes",
]

PRESENCE_FIELDS = [
    "design",
    "target",
    "flow",
    "memory_words",
    "buffer_depth",
    "recorder_config",
    "recorder_present",
    "evidence",
    "status",
    "notes",
]

TARGET = run_mapped_synthesis.FULL_CORE_TARGETS[0]
BASELINE_DESIGN = run_mapped_synthesis.DESIGNS["full_core_baseline_board"]
REPLAY_DESIGN = run_mapped_synthesis.DESIGNS["full_core_replaycapsule_board"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full", "representative"), default="quick")
    parser.add_argument("--max-replay-points", type=int, default=0, help="optional cap for full/representative debugging")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    yosys = run_mapped_synthesis._find_tool("yosys")
    nextpnr = run_mapped_synthesis._find_tool(TARGET.nextpnr_name)
    rows: list[dict[str, object]] = []
    cache: dict[tuple[object, ...], dict[str, object]] = {}

    for memory_words, buffer_depth, config in _points(args.mode, args.max_replay_points):
        baseline_key = ("baseline", memory_words)
        if baseline_key not in cache:
            cache[baseline_key] = _run_or_block(BASELINE_DESIGN, memory_words, buffer_depth, config, yosys, nextpnr, baseline_independent=True)
        baseline = dict(cache[baseline_key])
        baseline["buffer_depth"] = buffer_depth
        baseline["recorder_config"] = config
        if baseline.get("notes"):
            baseline["notes"] = str(baseline["notes"]) + "; baseline RTL independent of recorder buffer/config"
        rows.append(baseline)
        rows.append(_run_or_block(REPLAY_DESIGN, memory_words, buffer_depth, config, yosys, nextpnr, baseline_independent=False))

    presence_rows = [_presence(row) for row in rows if row["design"] == "full_core_replaycapsule_board"]
    overhead_rows = _overheads(rows, presence_rows)
    write_csv(OUT_CSV, FIELDS, rows)
    write_csv(OVERHEAD_CSV, OVERHEAD_FIELDS, overhead_rows)
    write_csv(PRESENCE_CSV, PRESENCE_FIELDS, presence_rows)
    print("WROTE results/processed/mapped_scaling.csv")
    print("WROTE results/processed/mapped_scaling_overhead.csv")
    print("WROTE results/processed/mapped_recorder_presence.csv")
    return 0


def _points(mode: str, max_replay_points: int) -> list[tuple[int, int, str]]:
    if mode == "quick":
        return [(2048, 32, "full")]
    if mode == "representative":
        points = [
            (1024, 16, "core"),
            (2048, 16, "core"),
            (2048, 32, "full"),
            (4096, 32, "full"),
            (2048, 64, "hashed"),
        ]
    else:
        points = [(memory, depth, config) for memory in MAPPED_MEMORY_WORDS for depth in MAPPED_BUFFER_DEPTHS for config in MAPPED_CONFIGS]
    return points[:max_replay_points] if max_replay_points else points


def _run_or_block(
    design: run_mapped_synthesis.Design,
    memory_words: int,
    buffer_depth: int,
    config: str,
    yosys: str | None,
    nextpnr: str | None,
    baseline_independent: bool,
) -> dict[str, object]:
    if not yosys:
        return _blocked(design.name, memory_words, buffer_depth, config, "missing yosys")
    if not nextpnr:
        return _blocked(design.name, memory_words, buffer_depth, config, f"missing {TARGET.nextpnr_name}")
    return _run_design(design, memory_words, buffer_depth, config, yosys, nextpnr, baseline_independent)


def _run_design(
    design: run_mapped_synthesis.Design,
    memory_words: int,
    buffer_depth: int,
    config: str,
    yosys: str,
    nextpnr: str,
    baseline_independent: bool,
) -> dict[str, object]:
    safe_config = config.replace("-", "_")
    stem = f"{design.name}_mem{memory_words}_buf{buffer_depth}_{safe_config}_{TARGET.suffix}"
    json_path = RAW_DIR / f"{stem}.json"
    bitstream_path = RAW_DIR / f"{stem}.{TARGET.output_ext}"
    yosys_log = RAW_DIR / f"{stem}_yosys.txt"
    nextpnr_log = RAW_DIR / f"{stem}_nextpnr.txt"
    for stale in (json_path, bitstream_path):
        if stale.exists():
            stale.unlink()
    y = run_mapped_synthesis._run_tool([yosys, "-p", _yosys_script(design, memory_words, buffer_depth, config, json_path)], run_mapped_synthesis.YOSYS_TIMEOUT_SECONDS)
    yosys_log.write_text(run_mapped_synthesis._clean(y.stdout), encoding="utf-8")
    if y.returncode != 0 or not json_path.exists():
        return _failed(design.name, memory_words, buffer_depth, config, yosys_log, "SYNTH_FAIL")

    command = [nextpnr, *TARGET.nextpnr_args, "--json", rel(json_path), "--textcfg", rel(bitstream_path)]
    if run_mapped_synthesis.ECP5_LPF.exists():
        command.extend(["--lpf", rel(run_mapped_synthesis.ECP5_LPF)])
    n = run_mapped_synthesis._run_tool(command, run_mapped_synthesis.NEXTPNR_TIMEOUT_SECONDS)
    nextpnr_log.write_text(run_mapped_synthesis._clean(n.stdout), encoding="utf-8")
    if n.returncode != 0 or not bitstream_path.exists():
        return _failed(design.name, memory_words, buffer_depth, config, nextpnr_log, "P&R_FAIL")
    text = yosys_log.read_text(encoding="utf-8", errors="replace") + "\n" + nextpnr_log.read_text(encoding="utf-8", errors="replace")
    metrics = run_mapped_synthesis._ecp5_metrics(text)
    notes = "real ECP5 85K place-and-route completed"
    if baseline_independent:
        notes += "; baseline has no recorder parameter"
    return {
        "target": TARGET.name,
        "flow": TARGET.flow,
        "design": design.name,
        "memory_words": memory_words,
        "buffer_depth": buffer_depth,
        "recorder_config": config,
        "lut": metrics.get("lut", "NA"),
        "ff": metrics.get("ff", "NA"),
        "bram": metrics.get("bram", "NA"),
        "dsp": metrics.get("dsp", "NA"),
        "cells": metrics.get("cells", "NA"),
        "area_um2": "NA",
        "fmax_mhz": metrics.get("fmax_mhz", "NA"),
        "wns": "NA",
        "tns": "NA",
        "power_mw": "NA",
        "status": "PASS",
        "report_path": rel(nextpnr_log),
        "notes": notes,
    }


def _yosys_script(design: run_mapped_synthesis.Design, memory_words: int, buffer_depth: int, config: str, json_path: Path) -> str:
    read = "read_verilog -sv -Irtl -Irtl/mapped -Irtl/rv32i_integration -Ithird_party/picorv32 " + " ".join(design.sources)
    commands = [read, f"chparam -set MEM_WORDS {memory_words} {design.top}"]
    if design.name == "full_core_replaycapsule_board":
        addr_w = max(1, math.ceil(math.log2(buffer_depth)))
        capture_mode = RECORDER_CONFIGS.get(config, RECORDER_CONFIGS["full"])["capture_mode"]
        commands.extend(
            [
                f"chparam -set CAPSULE_DEPTH {buffer_depth} {design.top}",
                f"chparam -set CAPSULE_ADDR_W {addr_w} {design.top}",
                f"chparam -set CAPTURE_MODE {capture_mode} {design.top}",
            ]
        )
    commands.append(f"synth_ecp5 -top {design.top} -json {rel(json_path)}")
    return "; ".join(commands)


def _blocked(design: str, memory_words: int, buffer_depth: int, config: str, notes: str) -> dict[str, object]:
    return {
        "target": TARGET.name,
        "flow": TARGET.flow,
        "design": design,
        "memory_words": memory_words,
        "buffer_depth": buffer_depth,
        "recorder_config": config,
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
        "notes": notes,
    }


def _failed(design: str, memory_words: int, buffer_depth: int, config: str, report: Path, stage: str) -> dict[str, object]:
    row = _blocked(design, memory_words, buffer_depth, config, f"{stage}: {run_mapped_synthesis._last_error_line(report)}")
    row["status"] = "FAIL"
    row["report_path"] = rel(report)
    return row


def _presence(row: dict[str, object]) -> dict[str, object]:
    report = REPO_ROOT / str(row.get("report_path", ""))
    json_path = Path(str(report).replace("_nextpnr.txt", ".json"))
    yosys_path = Path(str(report).replace("_nextpnr.txt", "_yosys.txt"))
    json_text = json_path.read_text(encoding="utf-8", errors="replace") if json_path.exists() else ""
    yosys_text = yosys_path.read_text(encoding="utf-8", errors="replace") if yosys_path.exists() else ""
    report_text = report.read_text(encoding="utf-8", errors="replace") if report.exists() else ""
    combined = json_text + "\n" + yosys_text + "\n" + report_text
    present = row.get("status") == "PASS" and all(token in combined for token in ("replay_capsule_top", "capsule_buffer")) and "recorder_status" in combined
    evidence = rel(yosys_path) if yosys_path.exists() else rel(json_path) if json_path.exists() else str(row.get("report_path", "NA"))
    return {
        "design": row["design"],
        "target": row["target"],
        "flow": row["flow"],
        "memory_words": row["memory_words"],
        "buffer_depth": row["buffer_depth"],
        "recorder_config": row["recorder_config"],
        "recorder_present": "yes" if present else "no",
        "evidence": evidence,
        "status": "PASS" if present else "FAIL" if row.get("status") == "PASS" else "NA",
        "notes": "recorder hierarchy/status evidence found" if present else "recorder presence not claimable for this row",
    }


def _overheads(rows: list[dict[str, object]], presence_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    keys = sorted({(row["memory_words"], row["buffer_depth"], row["recorder_config"]) for row in rows})
    for memory_words, buffer_depth, config in keys:
        baseline = _find(rows, "full_core_baseline_board", memory_words, buffer_depth, config)
        replay = _find(rows, "full_core_replaycapsule_board", memory_words, buffer_depth, config)
        presence = next((row for row in presence_rows if row["memory_words"] == memory_words and row["buffer_depth"] == buffer_depth and row["recorder_config"] == config), None)
        claim = bool(baseline and replay and presence and baseline["status"] == "PASS" and replay["status"] == "PASS" and presence["status"] == "PASS")
        for metric in ("lut", "ff", "bram", "fmax_mhz"):
            b = baseline.get(metric, "NA") if baseline else "NA"
            r = replay.get(metric, "NA") if replay else "NA"
            delta = _delta(b, r)
            out.append(
                {
                    "target": TARGET.name,
                    "flow": TARGET.flow,
                    "memory_words": memory_words,
                    "buffer_depth": buffer_depth,
                    "recorder_config": config,
                    "metric": metric,
                    "baseline": b,
                    "with_replaycapsule": r,
                    "delta": delta,
                    "percent_overhead": pct_delta(b, r),
                    "claim_allowed": "yes" if claim and b != "NA" and r != "NA" else "no",
                    "notes": "same-target mapped overhead" if claim else "requires same-target PASS rows and recorder presence PASS",
                }
            )
    return out


def _find(rows: list[dict[str, object]], design: str, memory_words: object, buffer_depth: object, config: object) -> dict[str, object] | None:
    return next((row for row in rows if row["design"] == design and row["memory_words"] == memory_words and row["buffer_depth"] == buffer_depth and row["recorder_config"] == config), None)


def _delta(left: object, right: object) -> str:
    l = safe_float(left)
    r = safe_float(right)
    if l is None or r is None:
        return "NA"
    return f"{(r - l):.2f}"


if __name__ == "__main__":
    raise SystemExit(main())
