#!/usr/bin/env python3
"""Replay scaled capsules after removing/corrupting selected event classes."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import run_full_rtl_replay
from topconf_eval_common import REPO_ROOT, read_csv, read_json, rel, write_csv


OUT_CSV = REPO_ROOT / "results/processed/event_ablation_scaling.csv"
RAW_DIR = REPO_ROOT / "results/raw/event_ablation_scaling"
CAPSULE_DIR = REPO_ROOT / "results/raw/workload_scaling/capsules"

EVENT_CLASSES = (
    "commit_index",
    "interrupt_pending",
    "interrupt_taken",
    "mmio_read",
    "mmio_write",
    "mmio_address",
    "mmio_value",
    "payload_hash",
    "property_id",
    "pc_context",
    "diagnostic_context",
    "cycle_delta",
)

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "workload_scale",
    "removed_or_corrupted_event_class",
    "replay_status",
    "property_match",
    "final_signature_match",
    "event_match",
    "rejected",
    "required_for_replay",
    "diagnostic_only",
    "notes",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-sec", type=int, default=30)
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    blocker = run_full_rtl_replay._ensure_simulator()
    firmware = _firmware_index()
    rows = []
    for row in read_csv(REPO_ROOT / "results/processed/workload_scaling.csv"):
        if row.get("replay_status") != "PASS":
            continue
        for event_class in EVENT_CLASSES:
            rows.append(_run_ablation(row, event_class, firmware, blocker, args.timeout_sec))
    write_csv(OUT_CSV, FIELDS, rows)
    print("WROTE results/processed/event_ablation_scaling.csv")
    return 0


def _firmware_index() -> dict[tuple[str, str, str], str]:
    out = {}
    for row in read_csv(REPO_ROOT / "results/processed/scaled_firmware_build.csv"):
        if row.get("build_status") == "PASS":
            out[(row["benchmark"], row["variant"], row["workload_scale"])] = row["hex_path"]
    return out


def _run_ablation(row: dict[str, str], event_class: str, firmware: dict[tuple[str, str, str], str], blocker: str | None, timeout_sec: int) -> dict[str, object]:
    base = f"{row['benchmark']}_{row['variant']}_seed{row['seed']}_{row['workload_scale']}"
    capsule = read_json(CAPSULE_DIR / f"{base}.json")
    if not capsule:
        return _row(row, event_class, "NA", "NA", "NA", "NA", "NA", "NA", "capsule JSON missing")
    mutated, required, diagnostic, notes = _mutate(capsule, event_class)
    if mutated is None:
        return _row(row, event_class, "NA", "NA", "NA", "NA", "NA", diagnostic, notes)
    if blocker:
        return _row(row, event_class, "BLOCKED", "NA", "NA", "NA", "NA", diagnostic, blocker)
    fw = firmware.get((row["benchmark"], row["variant"], row["workload_scale"]))
    if not fw:
        return _row(row, event_class, "BLOCKED", "NA", "NA", "NA", "NA", diagnostic, "scaled firmware path missing")

    mutated_path = RAW_DIR / f"{base}_{event_class}.json"
    signature_path = RAW_DIR / f"{base}_{event_class}_signature.json"
    mutated_path.write_text(json.dumps(mutated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    command = [
        str(run_full_rtl_replay._sim_path()),
        "--mode",
        "replay",
        "--benchmark",
        row["benchmark"],
        "--variant",
        row["variant"],
        "--firmware",
        fw,
        "--capsule",
        rel(mutated_path),
        "--signature",
        rel(signature_path),
        "--seed",
        row["seed"],
        "--max-cycles",
        row.get("cycles", "100000"),
    ]
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, env=run_full_rtl_replay._tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        return _row(row, event_class, "TIMEOUT", "NA", "NA", "NA", "false", diagnostic, f"replay timeout after {timeout_sec} seconds")
    rejected = completed.returncode != 0
    sig = read_json(signature_path)
    property_match = str(sig.get("property_id", "NA")) == row.get("property_id", "NA") if sig else False
    final_match = property_match
    event_match = completed.returncode == 0
    status = "REJECT" if rejected else "ACCEPT"
    return _row(row, event_class, status, property_match, final_match, event_match, rejected, diagnostic, notes, required)


def _mutate(capsule: dict[str, object], event_class: str) -> tuple[dict[str, object] | None, bool, bool, str]:
    mutated = json.loads(json.dumps(capsule))
    events = mutated.get("events", [])
    if not isinstance(events, list):
        return None, False, False, "capsule has no events array"
    if event_class == "cycle_delta":
        return None, False, True, "cycle_delta is not encoded in current capsule JSON"
    if event_class == "property_id":
        mutated["property_id"] = int(mutated.get("property_id", 0)) ^ 0x1
        for event in events:
            if isinstance(event, dict) and "property_id" in event:
                event["property_id"] = int(event.get("property_id", 0)) ^ 0x1
        return mutated, True, False, "corrupted property_id metadata"
    if event_class == "payload_hash":
        event = _first(events, lambda item: True)
        if event is None:
            return None, False, False, "no event to corrupt payload_hash"
        event["payload_hash"] = "0x00000000" if event.get("payload_hash") != "0x00000000" else "0x00000001"
        return mutated, True, False, "corrupted payload_hash field"
    if event_class == "diagnostic_context":
        index = _first_index(events, lambda item: bool(item.get("diagnostic_only")))
        if index is None:
            return None, False, True, "no diagnostic-only event present"
        del events[index]
        return mutated, False, True, "removed first diagnostic-only event"
    if event_class == "pc_context":
        index = _first_index(events, lambda item: "pc" in item)
        if index is None:
            return None, False, True, "no pc context field present"
        _corrupt_packet_field(events[index], 18, "00000000")
        return mutated, False, True, "corrupted PC context bits in packet"

    event_type = {
        "mmio_read": 5,
        "mmio_write": 6,
        "interrupt_pending": 7,
        "interrupt_taken": 7,
    }.get(event_class)
    if event_type is not None:
        index = _first_index(events, lambda item: int(item.get("event_type", -1)) == event_type)
        if index is None:
            return None, event_class.startswith(("mmio", "interrupt")), False, f"{event_class} event absent in capsule"
        if event_class in {"mmio_read", "mmio_write", "interrupt_pending", "interrupt_taken"}:
            del events[index]
            return mutated, True, False, f"removed first {event_class} event"
    if event_class == "mmio_address":
        event = _first(events, lambda item: int(item.get("event_type", -1)) in (5, 6))
        if event is None:
            return None, True, False, "MMIO event absent in capsule"
        _corrupt_packet_field(event, 26, "00000000")
        return mutated, True, False, "corrupted MMIO address field in packet"
    if event_class == "mmio_value":
        event = _first(events, lambda item: int(item.get("event_type", -1)) in (5, 6))
        if event is None:
            return None, True, False, "MMIO event absent in capsule"
        _corrupt_packet_field(event, 34, "ffffffff")
        return mutated, True, False, "corrupted MMIO value field in packet"
    if event_class == "commit_index":
        event = _first(events, lambda item: True)
        if event is None:
            return None, True, False, "no event to corrupt commit index"
        _corrupt_packet_field(event, 10, "ffffffff")
        return mutated, True, False, "corrupted commit index bits in packet"
    return None, False, False, "unsupported event class"


def _first(events: list[object], predicate) -> dict[str, object] | None:
    index = _first_index(events, predicate)
    return events[index] if index is not None else None


def _first_index(events: list[object], predicate) -> int | None:
    for index, event in enumerate(events):
        if isinstance(event, dict) and predicate(event):
            return index
    return None


def _corrupt_packet_field(event: dict[str, object], offset: int, value: str) -> None:
    packet = str(event.get("packet", ""))
    if len(packet) < offset + len(value):
        return
    event["packet"] = packet[:offset] + value + packet[offset + len(value):]
    event["payload_hash"] = "0x00000000"


def _row(
    source: dict[str, str],
    event_class: str,
    replay_status: object,
    property_match: object,
    final_signature_match: object,
    event_match: object,
    rejected: object,
    diagnostic_only: object,
    notes: str,
    required: object = "NA",
) -> dict[str, object]:
    return {
        "benchmark": source.get("benchmark", "NA"),
        "variant": source.get("variant", "NA"),
        "seed": source.get("seed", "NA"),
        "workload_scale": source.get("workload_scale", "NA"),
        "removed_or_corrupted_event_class": event_class,
        "replay_status": replay_status,
        "property_match": property_match,
        "final_signature_match": final_signature_match,
        "event_match": event_match,
        "rejected": rejected,
        "required_for_replay": required,
        "diagnostic_only": diagnostic_only,
        "notes": notes,
    }


if __name__ == "__main__":
    raise SystemExit(main())
