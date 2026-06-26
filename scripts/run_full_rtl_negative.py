#!/usr/bin/env python3
"""Run full RTL corrupted-capsule replay tests when the harness is available."""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM = REPO_ROOT / "build/verilator/replaycapsule_sim"
OUT_CSV = REPO_ROOT / "results/processed/full_rtl_replay_negative.csv"
RAW_DIR = REPO_ROOT / "results/raw/full_rtl_negative"
LOCAL_WINLIBS_BIN = REPO_ROOT / ".tools/winlibs/mingw64/bin"

CASES = (
    "missing event",
    "duplicate event",
    "reordered event",
    "metadata corruption",
    "payload corruption",
    "wrong interrupt cause",
    "wrong MMIO address",
    "wrong MMIO value",
    "shifted commit index",
    "shifted cycle delta",
    "truncated capsule",
    "overflowed incomplete capsule",
)

FIELDS = ["benchmark", "variant", "seed", "corruption_type", "expected_result", "actual_result", "rejected", "error_code", "notes"]


def main() -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    blocker = _sim_blocker()
    if blocker:
        rows = [_blocked_row(case, blocker) for case in CASES]
        _write_rows(rows)
        print(f"WROTE {_rel(OUT_CSV)}")
        print(f"BLOCKED full RTL negative tests: {blocker}")
        return 0

    benchmark = "sensor_threshold_bug"
    variant = "failing"
    seed = 1
    firmware = REPO_ROOT / "firmware/build" / benchmark / f"{variant}.hex"
    valid_capsule = RAW_DIR / "valid_capsule.json"
    record_sig = RAW_DIR / "valid_record_signature.json"
    record = _run_sim("record", benchmark, variant, firmware, valid_capsule, record_sig, seed)
    if record.returncode != 0:
        rows = [_blocked_row(case, "valid record run failed: " + _last(record.stdout)) for case in CASES]
        _write_rows(rows)
        return 0

    payload = json.loads(valid_capsule.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for case in CASES:
        mutated, notes = _mutate(payload, case)
        if mutated is None:
            rows.append(_na_row(case, notes))
            continue
        mutated_path = RAW_DIR / (case.replace(" ", "_") + ".json")
        mutated_path.write_text(json.dumps(mutated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        signature = RAW_DIR / (case.replace(" ", "_") + "_signature.json")
        replay = _run_sim("replay", benchmark, variant, firmware, mutated_path, signature, seed)
        rejected = replay.returncode != 0
        rows.append(
            {
                "benchmark": benchmark,
                "variant": variant,
                "seed": str(seed),
                "corruption_type": case,
                "expected_result": "REJECT",
                "actual_result": "REJECT" if rejected else "ACCEPT",
                "rejected": str(rejected),
                "error_code": _error_code(replay.stdout),
                "notes": notes if rejected else "corrupted capsule unexpectedly replayed",
            }
        )

    _write_rows(rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    return 0


def _sim_blocker() -> str | None:
    if _sim_path().exists():
        return None
    missing = []
    if not _find_make():
        missing.append("make/gmake")
    if not _find_cxx():
        missing.append("g++/c++/clang++")
    if not shutil.which("verilator") and not (REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite/bin/verilator_bin.exe").exists():
        missing.append("verilator")
    return "build/verilator/replaycapsule_sim missing; " + ("missing " + ", ".join(missing) if missing else "run make verilator-harness")


def _mutate(payload: dict[str, object], case: str) -> tuple[dict[str, object] | None, str]:
    mutated = json.loads(json.dumps(payload))
    events = mutated.get("events")
    if not isinstance(events, list) or not events:
        return None, "valid capsule has no events"
    if case == "missing event":
        events.pop(0)
        return mutated, "removed first event"
    if case == "duplicate event":
        events.insert(0, dict(events[0]))
        return mutated, "duplicated first event"
    if case == "reordered event":
        if len(events) < 2:
            return None, "not enough events to reorder"
        events[0], events[1] = events[1], events[0]
        return mutated, "swapped first two events"
    if case == "metadata corruption":
        mutated["property_id"] = int(mutated.get("property_id", 0)) ^ 1
        return mutated, "changed property_id"
    if case == "truncated capsule":
        del events[len(events) // 2 :]
        return mutated, "truncated event list"
    if case == "overflowed incomplete capsule":
        mutated["overflow"] = True
        events.pop()
        return mutated, "set overflow and removed final event"
    if case == "shifted cycle delta":
        return None, "current full RTL harness uses commit-index replay only"

    index = _find_event(events, case)
    if index is None:
        return None, f"no applicable event for {case}"
    event = dict(events[index])
    packet = str(event["packet"])
    if case == "wrong MMIO address":
        packet = _replace_field(packet, 26, 8, "40000010")
    elif case == "wrong MMIO value":
        packet = _xor_field(packet, 34, 8)
    elif case == "shifted commit index":
        packet = _xor_field(packet, 10, 8)
    elif case == "wrong interrupt cause":
        packet = _xor_field(packet, 34, 8)
    else:
        packet = _xor_field(packet, 34, 8)
    event["packet"] = packet
    events[index] = event
    return mutated, f"mutated packet for {case}"


def _find_event(events: list[object], case: str) -> int | None:
    preferred = {
        "wrong interrupt cause": {7, 8},
        "wrong MMIO address": {5, 6},
        "wrong MMIO value": {5, 6},
        "shifted commit index": {5, 6, 7, 8, 1, 3},
        "payload corruption": {5, 6, 7, 8, 1, 3},
    }.get(case, {5, 6, 7, 8, 1, 3})
    for index, item in enumerate(events):
        if isinstance(item, dict) and int(item.get("event_type", -1)) in preferred:
            return index
    return None


def _replace_field(packet: str, offset: int, count: int, value: str) -> str:
    packet = packet.rjust(42, "0")
    return packet[:offset] + value[-count:].rjust(count, "0") + packet[offset + count :]


def _xor_field(packet: str, offset: int, count: int) -> str:
    field = int(packet[offset : offset + count], 16) ^ 1
    return _replace_field(packet, offset, count, f"{field:0{count}x}")


def _run_sim(mode: str, benchmark: str, variant: str, firmware: Path, capsule: Path, signature: Path, seed: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(_sim_path()),
            "--mode",
            mode,
            "--benchmark",
            benchmark,
            "--variant",
            variant,
            "--firmware",
            _rel(firmware),
            "--capsule",
            _rel(capsule),
            "--signature",
            _rel(signature),
            "--seed",
            str(seed),
            "--max-cycles",
            "100000",
        ],
        cwd=REPO_ROOT,
        env=_tool_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _blocked_row(case: str, notes: str) -> dict[str, str]:
    return {
        "benchmark": "suite",
        "variant": "failing",
        "seed": "NA",
        "corruption_type": case,
        "expected_result": "REJECT",
        "actual_result": "BLOCKED",
        "rejected": "NA",
        "error_code": "BLOCKED",
        "notes": notes,
    }


def _na_row(case: str, notes: str) -> dict[str, str]:
    return {
        "benchmark": "sensor_threshold_bug",
        "variant": "failing",
        "seed": "1",
        "corruption_type": case,
        "expected_result": "NA",
        "actual_result": "NA",
        "rejected": "NA",
        "error_code": "NA",
        "notes": notes,
    }


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _error_code(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("error_code="):
            return line.split("=", 1)[1]
    return "NA"


def _last(output: str) -> str:
    lines = [line.strip() for line in _clean(output).splitlines() if line.strip()]
    return lines[-1] if lines else "no output"


def _clean(text: str) -> str:
    cleaned = text
    replacements = [str(REPO_ROOT), str(REPO_ROOT).replace("\\", "/")]
    home = str(Path.home())
    replacements.extend([home, home.replace("\\", "/")])
    for value in replacements:
        if value:
            cleaned = cleaned.replace(value, ".")
    cleaned = re.sub(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+", ".", cleaned)
    return cleaned


def _find_make() -> str | None:
    for path in (LOCAL_WINLIBS_BIN / "make.exe", LOCAL_WINLIBS_BIN / "mingw32-make.exe"):
        if path.exists():
            return str(path)
    return shutil.which("make") or shutil.which("gmake") or shutil.which("mingw32-make")


def _find_cxx() -> str | None:
    for path in (LOCAL_WINLIBS_BIN / "g++.exe", LOCAL_WINLIBS_BIN / "c++.exe", LOCAL_WINLIBS_BIN / "clang++.exe"):
        if path.exists():
            return str(path)
    return shutil.which("g++") or shutil.which("c++") or shutil.which("clang++")


def _tool_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(LOCAL_WINLIBS_BIN), env.get("PATH", "")])
    return env


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _sim_path() -> Path:
    if SIM.exists():
        return SIM
    exe = SIM.with_suffix(".exe")
    if exe.exists():
        return exe
    return SIM


if __name__ == "__main__":
    raise SystemExit(main())
