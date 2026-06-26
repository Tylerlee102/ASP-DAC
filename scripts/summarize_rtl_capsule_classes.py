#!/usr/bin/env python3
"""Summarize event-class composition of exported RTL-smoke capsules."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORT_CSV = REPO_ROOT / "results/processed/rtl_capsule_exports.csv"
OUT_CSV = REPO_ROOT / "results/processed/rtl_capsule_event_classes.csv"
EVENT_RE = re.compile(r"RC_CAPSULE_EVENT\s+index=(?P<index>\d+)\s+packet=(?P<packet>[0-9a-fA-F]+)")

EVENT_TYPE_NAMES = {
    0x0: "commit",
    0x1: "branch",
    0x2: "jump",
    0x3: "store",
    0x4: "load",
    0x5: "mmio_read",
    0x6: "mmio_write",
    0x7: "interrupt_enter",
    0x8: "interrupt_exit",
    0x9: "external_input",
    0xA: "property_fail",
    0xB: "checkpoint_hash",
}
REPLAY_RELEVANT_TYPES = {
    "branch",
    "jump",
    "store",
    "mmio_read",
    "mmio_write",
    "interrupt_enter",
    "interrupt_exit",
    "external_input",
    "checkpoint_hash",
}


def main() -> int:
    rows: list[dict[str, str]] = []
    failed = False
    if not EXPORT_CSV.exists():
        rows.append(_todo_row("suite", "NA", f"missing artifact: {EXPORT_CSV.relative_to(REPO_ROOT)}"))
    else:
        with EXPORT_CSV.open(newline="", encoding="utf-8") as handle:
            for export in csv.DictReader(handle):
                try:
                    rows.append(_summarize_export(export))
                except Exception as exc:  # noqa: BLE001 - preserve per-capsule failure rows
                    failed = True
                    rows.append(_failure_row(export, str(exc)))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "benchmark",
                "variant",
                "status",
                "evidence_level",
                "rtl_packet_count",
                "packet_bytes",
                "replay_relevant_packet_count",
                "pc_evidence_event_count",
                "commit",
                "branch",
                "jump",
                "store",
                "load",
                "mmio_read",
                "mmio_write",
                "interrupt_enter",
                "interrupt_exit",
                "external_input",
                "property_fail",
                "checkpoint_hash",
                "raw_log",
                "capsule_json",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if failed else 0


def _summarize_export(export: dict[str, str]) -> dict[str, str]:
    benchmark = export.get("benchmark", "unknown")
    variant = export.get("variant", "unknown")
    if export.get("status") != "PASS":
        return _todo_row(benchmark, variant, "source export row is not PASS")

    raw_log = export.get("raw_log", "")
    capsule_json = export.get("capsule_json", "")
    packets = _read_packets(REPO_ROOT / raw_log)
    capsule = json.loads((REPO_ROOT / capsule_json).read_text(encoding="utf-8"))
    pc_evidence_count = sum(1 for event in capsule.get("events", []) if isinstance(event, dict) and event.get("kind") == "pc")

    counts = {name: 0 for name in EVENT_TYPE_NAMES.values()}
    for packet in packets:
        event_type = EVENT_TYPE_NAMES.get((packet >> 164) & 0xF, "unknown")
        if event_type in counts:
            counts[event_type] += 1

    replay_relevant_count = sum(counts[name] for name in REPLAY_RELEVANT_TYPES)
    packet_count = len(packets)
    return {
        "benchmark": benchmark,
        "variant": variant,
        "status": "PASS",
        "evidence_level": "rtl-smoke",
        "rtl_packet_count": str(packet_count),
        "packet_bytes": str(packet_count * 21),
        "replay_relevant_packet_count": str(replay_relevant_count),
        "pc_evidence_event_count": str(pc_evidence_count),
        **{name: str(counts[name]) for name in EVENT_TYPE_NAMES.values()},
        "raw_log": raw_log,
        "capsule_json": capsule_json,
        "notes": "decoded exported RTL-smoke packet classes; not a full benchmark-wide trace baseline",
    }


def _read_packets(path: Path) -> list[int]:
    if not path.exists():
        raise FileNotFoundError(f"missing raw log {path.relative_to(REPO_ROOT)}")
    packets = [int(match.group("packet"), 16) for match in EVENT_RE.finditer(path.read_text(encoding="utf-8"))]
    if not packets:
        raise ValueError(f"{path.relative_to(REPO_ROOT)} contains no RC_CAPSULE_EVENT lines")
    return packets


def _todo_row(benchmark: str, variant: str, notes: str) -> dict[str, str]:
    return {
        "benchmark": benchmark,
        "variant": variant,
        "status": "TODO",
        "evidence_level": "rtl-smoke",
        "rtl_packet_count": "NA",
        "packet_bytes": "NA",
        "replay_relevant_packet_count": "NA",
        "pc_evidence_event_count": "NA",
        **{name: "NA" for name in EVENT_TYPE_NAMES.values()},
        "raw_log": "NA",
        "capsule_json": "NA",
        "notes": notes,
    }


def _failure_row(export: dict[str, str], notes: str) -> dict[str, str]:
    row = _todo_row(export.get("benchmark", "unknown"), export.get("variant", "unknown"), notes)
    row["status"] = "FAIL"
    row["raw_log"] = export.get("raw_log", "NA")
    row["capsule_json"] = export.get("capsule_json", "NA")
    return row


if __name__ == "__main__":
    raise SystemExit(main())
