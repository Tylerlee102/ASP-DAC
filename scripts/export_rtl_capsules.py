#!/usr/bin/env python3
"""Decode RTL smoke capsule dumps and self-check them with the replay comparator."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "results/raw"
CAPSULE_DIR = RAW_DIR / "rtl_capsules"
OUT_CSV = REPO_ROOT / "results/processed/rtl_capsule_exports.csv"

sys.path.insert(0, str(REPO_ROOT / "tb" / "replay_testbench"))
from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


SMOKE_LOGS = (
    ("sensor_threshold_bug", "failing", RAW_DIR / "tb_picorv32_sensor_threshold_smoke_vvp_run.txt"),
    ("interrupt_race_bug", "failing", RAW_DIR / "tb_picorv32_interrupt_race_smoke_vvp_run.txt"),
    ("mmio_ordering_bug", "failing", RAW_DIR / "tb_picorv32_mmio_ordering_smoke_vvp_run.txt"),
    ("stack_corruption_bug", "failing", RAW_DIR / "tb_picorv32_stack_corruption_smoke_vvp_run.txt"),
    ("uart_command_bug", "failing", RAW_DIR / "tb_picorv32_uart_command_smoke_vvp_run.txt"),
    ("watchdog_timeout_bug", "failing", RAW_DIR / "tb_picorv32_watchdog_timeout_smoke_vvp_run.txt"),
    ("sensor_threshold_bug", "fixed", RAW_DIR / "tb_picorv32_sensor_threshold_fixed_smoke_vvp_run.txt"),
    ("interrupt_race_bug", "fixed", RAW_DIR / "tb_picorv32_interrupt_race_fixed_smoke_vvp_run.txt"),
    ("mmio_ordering_bug", "fixed", RAW_DIR / "tb_picorv32_mmio_ordering_fixed_smoke_vvp_run.txt"),
    ("stack_corruption_bug", "fixed", RAW_DIR / "tb_picorv32_stack_corruption_fixed_smoke_vvp_run.txt"),
    ("uart_command_bug", "fixed", RAW_DIR / "tb_picorv32_uart_command_fixed_smoke_vvp_run.txt"),
    ("watchdog_timeout_bug", "fixed", RAW_DIR / "tb_picorv32_watchdog_timeout_fixed_smoke_vvp_run.txt"),
)

PROPERTY_NAMES = {
    1: "P1_ACTUATOR_LIMIT",
    2: "P2_INTERRUPT_CRITICAL",
    3: "P3_SENSOR_DEADLINE",
    4: "P4_STACK_PROTECT",
    5: "P5_MMIO_ORDERING",
    6: "P6_WATCHDOG_TIMEOUT",
}

EVENT_RE = re.compile(r"RC_CAPSULE_EVENT\s+index=(?P<index>\d+)\s+packet=(?P<packet>[0-9a-fA-F]+)")


def main() -> int:
    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    failed = False
    for benchmark, variant, log_path in SMOKE_LOGS:
        try:
            packets = _read_packets(log_path)
            payload = _capsule_payload(benchmark, variant, log_path, packets)
            json_path = CAPSULE_DIR / f"{benchmark}_{variant}.json"
            json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            parsed = parse_capsule(json.dumps(payload), source=f"{benchmark}:rtl")
            compare = compare_capsules(parsed, parsed, mode="commit-index")
            negative_check = _negative_check(parsed, payload, benchmark)
            metadata_corruption_check = _metadata_corruption_check(parsed, payload, benchmark)
            payload_corruption_check = _payload_corruption_check(parsed, payload, benchmark)
            pc_context_check = _pc_context_check(packets)
            status = (
                "PASS"
                if compare.success
                and negative_check in {"PASS", "NA"}
                and metadata_corruption_check == "PASS"
                and payload_corruption_check in {"PASS", "NA"}
                and pc_context_check in {"PASS", "NA"}
                else "FAIL"
            )
            if status == "PASS":
                if negative_check == "PASS" and payload_corruption_check == "PASS":
                    notes = "RTL smoke capsule export parsed, self-compared, and rejected missing-event, metadata-corruption, and payload-corruption negatives; PC context checked; not full replay"
                else:
                    notes = "RTL smoke capsule export parsed and self-compared; metadata corruption rejected; PC context checked; no replay-relevant event available for one negative check"
            elif compare.success:
                if negative_check == "FAIL":
                    notes = "missing-event negative check unexpectedly matched"
                elif metadata_corruption_check == "FAIL":
                    notes = "metadata-corruption negative check unexpectedly matched"
                elif payload_corruption_check == "FAIL":
                    notes = "payload-corruption negative check unexpectedly matched"
                else:
                    notes = "memory event PC context unexpectedly points into the MMIO aperture"
            else:
                notes = "; ".join(compare.errors)
        except Exception as exc:  # noqa: BLE001 - report all export failures in the CSV
            failed = True
            rows.append(
                {
                    "benchmark": benchmark,
                    "variant": variant,
                    "status": "FAIL",
                    "mode": "commit-index",
                    "rtl_packet_count": "0",
                    "replay_event_count": "0",
                    "property_id": "NA",
                    "failure_signature": "NA",
                    "negative_check": "NA",
                    "metadata_corruption_check": "NA",
                    "payload_corruption_check": "NA",
                    "pc_context_check": "NA",
                    "raw_log": str(log_path.relative_to(REPO_ROOT)),
                    "capsule_json": "NA",
                    "notes": str(exc),
                }
            )
            continue

        failed = failed or status != "PASS"
        rows.append(
            {
                "benchmark": benchmark,
                "variant": variant,
                "status": status,
                "mode": "commit-index",
                "rtl_packet_count": str(len(packets)),
                "replay_event_count": str(len(payload["events"])),
                "property_id": str(payload["property_id"]),
                "failure_signature": str(payload["failure_signature"]),
                "negative_check": negative_check,
                "metadata_corruption_check": metadata_corruption_check,
                "payload_corruption_check": payload_corruption_check,
                "pc_context_check": pc_context_check,
                "raw_log": str(log_path.relative_to(REPO_ROOT)),
                "capsule_json": str(json_path.relative_to(REPO_ROOT)),
                "notes": notes,
            }
        )

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "benchmark",
                "variant",
                "status",
                "mode",
                "rtl_packet_count",
                "replay_event_count",
                "property_id",
                "failure_signature",
                "negative_check",
                "metadata_corruption_check",
                "payload_corruption_check",
                "pc_context_check",
                "raw_log",
                "capsule_json",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"WROTE {OUT_CSV}")
    return 1 if failed else 0


def _read_packets(log_path: Path) -> list[dict[str, int]]:
    if not log_path.exists():
        raise FileNotFoundError(f"{log_path} does not exist; run HDL checks first")

    packets: list[dict[str, int]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        match = EVENT_RE.search(line)
        if not match:
            continue
        packets.append(_decode_packet(int(match.group("packet"), 16), int(match.group("index"))))

    if not packets:
        raise ValueError(f"{log_path} contains no RC_CAPSULE_EVENT lines")
    return packets


def _decode_packet(packet: int, index: int) -> dict[str, int]:
    return {
        "index": index,
        "event_type": (packet >> 164) & 0xF,
        "flags": (packet >> 160) & 0xF,
        "event_id": (packet >> 128) & 0xFFFF_FFFF,
        "commit": (packet >> 96) & 0xFFFF_FFFF,
        "pc": (packet >> 64) & 0xFFFF_FFFF,
        "addr": (packet >> 32) & 0xFFFF_FFFF,
        "data": packet & 0xFFFF_FFFF,
        "packet": packet,
    }


def _capsule_payload(benchmark: str, variant: str, log_path: Path, packets: list[dict[str, int]]) -> dict[str, object]:
    property_packet = next((packet for packet in packets if packet["event_type"] == 0xA), None)
    if variant == "failing" and property_packet is None:
        raise ValueError(f"{log_path} has no property-fail packet")

    if property_packet is not None:
        property_number = property_packet["addr"] & 0xFF
        property_id = PROPERTY_NAMES.get(property_number, f"P{property_number}")
        failure_signature = f"0x{property_packet['data']:08x}"
    else:
        property_id = "NONE"
        failure_signature = "NA"

    events: list[dict[str, object]] = []
    for packet in packets:
        order = packet["event_id"]
        commit = packet["commit"]
        pc = packet["pc"]
        events.append({"kind": "pc", "commit": commit, "order": order, "pc": f"0x{pc:08x}"})
        kind_event = _event_payload(packet)
        if kind_event is not None:
            events.append(kind_event)

    return {
        "benchmark": benchmark,
        "variant": variant,
        "evidence_level": "rtl-smoke",
        "source_log": str(log_path.relative_to(REPO_ROOT)),
        "property_id": property_id,
        "failure_signature": failure_signature,
        "rtl_packet_count": len(packets),
        "events": events,
    }


def _event_payload(packet: dict[str, int]) -> dict[str, object] | None:
    base: dict[str, object] = {
        "commit": packet["commit"],
        "order": packet["event_id"],
        "pc": f"0x{packet['pc']:08x}",
    }
    event_type = packet["event_type"]
    if event_type == 0x1:
        return {**base, "kind": "branch", "value": f"0x{packet['data']:08x}"}
    if event_type == 0x3:
        return {
            **base,
            "kind": "store",
            "addr": f"0x{packet['addr']:08x}",
            "value": f"0x{packet['data']:08x}",
        }
    if event_type == 0x5:
        return {
            **base,
            "kind": "mmio",
            "direction": "read",
            "addr": f"0x{packet['addr']:08x}",
            "value": f"0x{packet['data']:08x}",
        }
    if event_type == 0x6:
        return {
            **base,
            "kind": "mmio",
            "direction": "write",
            "addr": f"0x{packet['addr']:08x}",
            "value": f"0x{packet['data']:08x}",
        }
    if event_type == 0x7:
        return {**base, "kind": "interrupt", "irq": "line0", "state": "taken", "value": packet["data"]}
    if event_type == 0x8:
        return {**base, "kind": "interrupt", "irq": "line0", "state": "return", "value": packet["data"]}
    if event_type == 0x9:
        return {
            **base,
            "kind": "input",
            "input_id": f"input{packet['addr']}",
            "value": f"0x{packet['data']:08x}",
        }
    if event_type == 0xB:
        return {**base, "kind": "checkpoint", "value": f"0x{packet['data']:08x}"}
    return None


def _pc_context_check(packets: list[dict[str, int]]) -> str:
    checked = 0
    for packet in packets:
        if packet["event_type"] not in {0x3, 0x5, 0x6}:
            continue
        checked += 1
        if (packet["pc"] & 0xFFFF_0000) == 0x4000_0000:
            return "FAIL"
    return "PASS" if checked else "NA"


def _drop_one_replay_event(payload: dict[str, object]) -> dict[str, object]:
    events = list(payload["events"])  # type: ignore[arg-type]
    for index, event in enumerate(events):
        if isinstance(event, dict) and event.get("kind") != "pc":
            corrupted = dict(payload)
            corrupted["events"] = events[:index] + events[index + 1 :]
            return corrupted
    raise ValueError("cannot build negative check without a replay-relevant event")


def _negative_check(parsed, payload: dict[str, object], benchmark: str) -> str:
    try:
        negative_payload = _drop_one_replay_event(payload)
    except ValueError:
        return "NA"

    negative = compare_capsules(
        parsed,
        parse_capsule(json.dumps(negative_payload), source=f"{benchmark}:negative"),
        mode="commit-index",
    )
    return "PASS" if not negative.success else "FAIL"


def _metadata_corruption_check(parsed, payload: dict[str, object], benchmark: str) -> str:
    corrupted = dict(payload)
    property_id = str(corrupted.get("property_id", ""))
    if property_id:
        corrupted["property_id"] = f"{property_id}__CORRUPTED"
    else:
        failure_signature = str(corrupted.get("failure_signature", ""))
        corrupted["failure_signature"] = f"{failure_signature}__CORRUPTED"

    negative = compare_capsules(
        parsed,
        parse_capsule(json.dumps(corrupted), source=f"{benchmark}:metadata-corruption"),
        mode="commit-index",
    )
    return "PASS" if not negative.success else "FAIL"


def _payload_corruption_check(parsed, payload: dict[str, object], benchmark: str) -> str:
    try:
        corrupted = _corrupt_one_replay_payload(payload)
    except ValueError:
        return "NA"

    negative = compare_capsules(
        parsed,
        parse_capsule(json.dumps(corrupted), source=f"{benchmark}:payload-corruption"),
        mode="commit-index",
    )
    return "PASS" if not negative.success else "FAIL"


def _corrupt_one_replay_payload(payload: dict[str, object]) -> dict[str, object]:
    events = list(payload["events"])  # type: ignore[arg-type]
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        field_name = _first_payload_field_to_corrupt(event)
        if field_name is None:
            continue

        corrupted_event = dict(event)
        corrupted_event[field_name] = _corrupt_scalar(corrupted_event[field_name])
        corrupted = dict(payload)
        corrupted["events"] = events[:index] + [corrupted_event] + events[index + 1 :]
        return corrupted
    raise ValueError("cannot build payload corruption check without a replay-relevant field")


def _first_payload_field_to_corrupt(event: dict[str, object]) -> str | None:
    fields_by_kind = {
        "mmio": ("value", "addr", "direction"),
        "store": ("value", "addr", "pc"),
        "branch": ("value", "pc"),
        "interrupt": ("value", "state", "irq"),
        "input": ("value", "input_id", "addr"),
        "checkpoint": ("value",),
    }
    kind = event.get("kind")
    for field_name in fields_by_kind.get(str(kind), ()):
        if field_name in event and event[field_name] is not None:
            return field_name
    return None


def _corrupt_scalar(value: object) -> object:
    if isinstance(value, int):
        return value ^ 1
    if isinstance(value, str):
        if value in {"read", "write"}:
            return "write" if value == "read" else "read"
        try:
            return f"0x{(int(value, 0) ^ 1):08x}"
        except ValueError:
            return f"{value}__CORRUPTED"
    raise ValueError(f"cannot corrupt scalar value {value!r}")


if __name__ == "__main__":
    raise SystemExit(main())
