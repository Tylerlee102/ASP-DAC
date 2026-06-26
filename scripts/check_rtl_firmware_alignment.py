#!/usr/bin/env python3
"""Check semantic alignment between RTL-smoke capsules and firmware-sim runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
RTL_CAPSULE_DIR = REPO_ROOT / "results/raw/rtl_capsules"
OUT_CSV = REPO_ROOT / "results/processed/rtl_firmware_alignment.csv"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from replaycapsule_model import (  # noqa: E402
    ACTUATOR_ADDR,
    ACTUATOR_UNSAFE,
    BENCHMARKS,
    COMMAND_ADDR,
    EventType,
    SENSOR_ADDR,
    SENSOR_HIGH,
    STACK_PROTECTED_ADDR,
)
from rv32i_firmware_sim import run_firmware  # noqa: E402


def main() -> int:
    rows: list[dict[str, str]] = []
    failed = False

    for benchmark in BENCHMARKS:
        for failing in (True, False):
            variant = "failing" if failing else "fixed"
            firmware = run_firmware(benchmark, failing=failing)
            try:
                rtl = _load_rtl_capsule(benchmark, variant)
                property_alignment = _property_alignment(rtl, firmware.property_id)
                if failing:
                    key_event_alignment, checked_events = _required_event_alignment(benchmark, rtl, firmware.events)
                else:
                    key_event_alignment = "NA"
                    checked_events = "fixed variant checks property absence only"
                status = "PASS" if property_alignment == "PASS" and key_event_alignment in {"PASS", "NA"} else "FAIL"
                notes = _notes(failing, property_alignment, key_event_alignment)
            except Exception as exc:  # noqa: BLE001 - collect all alignment errors in the CSV
                status = "FAIL"
                property_alignment = "FAIL"
                key_event_alignment = "FAIL"
                checked_events = "NA"
                rtl = {"property_id": "NA"}
                notes = str(exc)

            failed = failed or status != "PASS"
            rows.append(
                {
                    "benchmark": benchmark,
                    "variant": variant,
                    "status": status,
                    "property_alignment": property_alignment,
                    "key_event_alignment": key_event_alignment,
                    "rtl_property_id": _normalized_property_id(rtl.get("property_id")),
                    "firmware_property_id": firmware.property_id or "NONE",
                    "checked_events": checked_events,
                    "notes": notes,
                }
            )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "benchmark",
                "variant",
                "status",
                "property_alignment",
                "key_event_alignment",
                "rtl_property_id",
                "firmware_property_id",
                "checked_events",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"WROTE {OUT_CSV}")
    return 1 if failed else 0


def _load_rtl_capsule(benchmark: str, variant: str) -> dict[str, object]:
    path = RTL_CAPSULE_DIR / f"{benchmark}_{variant}.json"
    if not path.exists():
        raise FileNotFoundError(f"missing RTL smoke capsule {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _property_alignment(rtl: dict[str, object], firmware_property_id: str | None) -> str:
    rtl_property_id = _normalized_property_id(rtl.get("property_id"))
    expected = firmware_property_id or "NONE"
    return "PASS" if rtl_property_id == expected else "FAIL"


def _required_event_alignment(benchmark: str, rtl: dict[str, object], firmware_events: tuple[object, ...]) -> tuple[str, str]:
    checks = {
        "sensor_threshold_bug": (
            ("mmio_read_sensor_high", _has_rtl_mmio(rtl, "read", SENSOR_ADDR, SENSOR_HIGH), _has_fw_event(firmware_events, EventType.EV_MMIO_READ, SENSOR_ADDR, SENSOR_HIGH)),
        ),
        "interrupt_race_bug": (
            ("mmio_write_command_one", _has_rtl_mmio(rtl, "write", COMMAND_ADDR, 1), _has_fw_event(firmware_events, EventType.EV_MMIO_WRITE, COMMAND_ADDR, 1)),
            ("interrupt_taken", _has_rtl_interrupt(rtl, "taken"), _has_fw_event(firmware_events, EventType.EV_INTERRUPT_ENTER, data=1)),
        ),
        "mmio_ordering_bug": (
            ("mmio_write_actuator_25", _has_rtl_mmio(rtl, "write", ACTUATOR_ADDR, 25), _has_fw_event(firmware_events, EventType.EV_MMIO_WRITE, ACTUATOR_ADDR, 25)),
        ),
        "stack_corruption_bug": (
            ("store_protected_stack", _has_rtl_store(rtl, STACK_PROTECTED_ADDR, 0xDEAD_BEEF), _has_fw_event(firmware_events, EventType.EV_STORE, STACK_PROTECTED_ADDR, 0xDEAD_BEEF)),
        ),
        "uart_command_bug": (
            ("mmio_read_command_unsafe", _has_rtl_mmio(rtl, "read", COMMAND_ADDR, 0x55), _has_fw_event(firmware_events, EventType.EV_MMIO_READ, COMMAND_ADDR, 0x55)),
            ("mmio_write_actuator_unsafe", _has_rtl_mmio(rtl, "write", ACTUATOR_ADDR, ACTUATOR_UNSAFE), _has_fw_event(firmware_events, EventType.EV_MMIO_WRITE, ACTUATOR_ADDR, ACTUATOR_UNSAFE)),
        ),
        "watchdog_timeout_bug": (
            ("mmio_read_sensor_high", _has_rtl_mmio(rtl, "read", SENSOR_ADDR, SENSOR_HIGH), _has_fw_event(firmware_events, EventType.EV_MMIO_READ, SENSOR_ADDR, SENSOR_HIGH)),
        ),
    }[benchmark]

    checked = []
    for name, rtl_ok, firmware_ok in checks:
        checked.append(f"{name}:rtl={_flag(rtl_ok)};firmware={_flag(firmware_ok)}")
    status = "PASS" if all(rtl_ok and firmware_ok for _, rtl_ok, firmware_ok in checks) else "FAIL"
    return status, "|".join(checked)


def _normalized_property_id(value: object) -> str:
    if value is None:
        return "NONE"
    text = str(value)
    if text in {"", "NA", "NONE"}:
        return "NONE"
    return text


def _has_rtl_mmio(rtl: dict[str, object], direction: str, addr: int, value: int) -> bool:
    return any(
        _event_field(event, "kind") == "mmio"
        and _event_field(event, "direction") == direction
        and _int_field(event, "addr") == addr
        and _int_field(event, "value") == value
        for event in _events(rtl)
    )


def _has_rtl_store(rtl: dict[str, object], addr: int, value: int) -> bool:
    return any(
        _event_field(event, "kind") == "store"
        and _int_field(event, "addr") == addr
        and _int_field(event, "value") == value
        for event in _events(rtl)
    )


def _has_rtl_interrupt(rtl: dict[str, object], state: str) -> bool:
    return any(
        _event_field(event, "kind") == "interrupt" and _event_field(event, "state") == state
        for event in _events(rtl)
    )


def _events(rtl: dict[str, object]) -> tuple[dict[str, object], ...]:
    events = rtl.get("events", ())
    if not isinstance(events, list):
        return ()
    return tuple(event for event in events if isinstance(event, dict))


def _has_fw_event(
    firmware_events: tuple[object, ...],
    event_type: EventType,
    addr: int | None = None,
    data: int | None = None,
) -> bool:
    for event in firmware_events:
        if getattr(event, "event_type") != event_type:
            continue
        if addr is not None and getattr(event, "addr") != addr:
            continue
        if data is not None and getattr(event, "data") != data:
            continue
        return True
    return False


def _event_field(event: dict[str, object], field_name: str) -> str | None:
    value = event.get(field_name)
    return str(value) if value is not None else None


def _int_field(event: dict[str, object], field_name: str) -> int | None:
    value = event.get(field_name)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    return None


def _flag(value: bool) -> str:
    return "yes" if value else "no"


def _notes(failing: bool, property_alignment: str, key_event_alignment: str) -> str:
    if property_alignment != "PASS":
        return "RTL-smoke and firmware-sim property IDs disagree"
    if key_event_alignment == "FAIL":
        return "required replay-visible event evidence is missing from either RTL-smoke or firmware-sim"
    if failing:
        return "RTL-smoke failing capsule aligns with firmware-sim property and required event evidence; not full replay"
    return "RTL-smoke fixed capsule and firmware-sim fixed run both avoid property failure"


if __name__ == "__main__":
    raise SystemExit(main())
