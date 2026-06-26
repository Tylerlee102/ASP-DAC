#!/usr/bin/env python3
"""Run a seeded RTL-smoke interrupt timing campaign with Icarus Verilog."""

from __future__ import annotations

import csv
import hashlib
import os
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "results/raw/randomized_interrupt_campaign"
OUT_CSV = REPO_ROOT / "results/processed/randomized_interrupt_campaign.csv"
BUILD_DIR = REPO_ROOT / ".tools/randomized_interrupt_campaign"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from run_hdl_checks import (  # noqa: E402
    PICORV32_INCLUDE_DIRS,
    PICORV32_WRAPPER_SOURCES,
    _clean_log,
    _find_tool,
    _run,
)


AFTER_COMMAND_SEEDS = (1101, 1103, 1109, 1117, 1123, 1129)
FIXED_WINDOW_CASES = (
    (2101, 20, 50),
    (2103, 30, 60),
    (2109, 40, 70),
    (2111, 50, 80),
    (2113, 60, 90),
    (2129, 70, 100),
    (2131, 80, 110),
)
BEGIN_RE = re.compile(
    r"RC_CAPSULE_BEGIN\s+count=(?P<count>\d+)\s+property=(?P<property>\d+)\s+"
    r"signature=(?P<signature>[0-9a-fA-F]+)\s+frozen=(?P<frozen>[01])\s+overflow=(?P<overflow>[01])"
)
EVENT_RE = re.compile(r"RC_CAPSULE_EVENT\s+index=(?P<index>\d+)\s+packet=(?P<packet>[0-9a-fA-F]+)")


@dataclass(frozen=True)
class CampaignCase:
    seed: int
    family: str
    irq_after_command: int
    irq_pulse_cycles: int
    irq_start_cycle: int
    irq_end_cycle: int


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    failures: list[str] = []
    iverilog = _find_tool("iverilog")
    vvp = _find_tool("vvp")
    if not iverilog or not vvp:
        for case in _campaign_cases():
            rows.append(_todo_row(case, "Icarus Verilog or vvp not available"))
        _write_rows(rows)
        print(f"WROTE {OUT_CSV}")
        return 0

    output_path = BUILD_DIR / "tb_picorv32_interrupt_campaign.vvp"
    compile_log = RAW_DIR / "compile_iverilog.txt"
    compile_cmd = [iverilog.command, "-g2012"]
    for include_dir in PICORV32_INCLUDE_DIRS:
        compile_cmd.extend(["-I", include_dir])
    compile_cmd.append("-DRC_IRQ_VECTOR_WORD_INDEX=12")
    compile_cmd.extend(["-o", os.path.relpath(output_path, REPO_ROOT / "tb/system"), *PICORV32_WRAPPER_SOURCES])
    compile_result = _run(compile_cmd, cwd=REPO_ROOT / "tb/system", env=iverilog.env)
    compile_log.write_text(_clean_log(compile_result.stdout) or "compile passed without output\n", encoding="utf-8")
    if compile_result.returncode != 0:
        for case in _campaign_cases():
            rows.append(_fail_row(case, "compile failed", str(compile_log.relative_to(REPO_ROOT))))
        _write_rows(rows)
        print(f"WROTE {OUT_CSV}")
        return 1

    for case in _campaign_cases():
        first = _run_seed(vvp.command, vvp.env, output_path, case, 1)
        second = _run_seed(vvp.command, vvp.env, output_path, case, 2)
        status = "PASS" if _same_successful_capsule(first, second) else "FAIL"
        if status != "PASS":
            failures.append(f"seed {case.seed} did not reproduce deterministic capsule digest")
        rows.append(
            {
                "seed": str(case.seed),
                "family": case.family,
                "benchmark": "interrupt_race_bug",
                "status": status,
                "evidence_level": "rtl-smoke",
                "irq_after_command": str(case.irq_after_command),
                "irq_pulse_cycles": str(case.irq_pulse_cycles),
                "irq_start_cycle": _optional_int(case.irq_start_cycle),
                "irq_end_cycle": _optional_int(case.irq_end_cycle),
                "expected_property": "2",
                "property_run1": first.get("property", "NA"),
                "property_run2": second.get("property", "NA"),
                "capsule_count_run1": first.get("count", "NA"),
                "capsule_count_run2": second.get("count", "NA"),
                "digest_run1": first.get("digest", "NA"),
                "digest_run2": second.get("digest", "NA"),
                "raw_log_run1": first.get("raw_log", "NA"),
                "raw_log_run2": second.get("raw_log", "NA"),
                "notes": _notes(status, first, second),
            }
        )

    _write_rows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if failures else 0


def _campaign_cases() -> tuple[CampaignCase, ...]:
    cases: list[CampaignCase] = []
    for seed in AFTER_COMMAND_SEEDS:
        rng = random.Random(seed)
        cases.append(
            CampaignCase(
                seed=seed,
                family="irq_after_command",
                irq_after_command=1,
                irq_pulse_cycles=rng.randint(18, 48),
                irq_start_cycle=-1,
                irq_end_cycle=-1,
            )
        )
    for seed, start, end in FIXED_WINDOW_CASES:
        cases.append(
            CampaignCase(
                seed=seed,
                family="fixed_irq_window",
                irq_after_command=0,
                irq_pulse_cycles=24,
                irq_start_cycle=start,
                irq_end_cycle=end,
            )
        )
    return tuple(cases)


def _run_seed(
    vvp_command: str,
    env: dict[str, str],
    output_path: Path,
    case: CampaignCase,
    run_index: int,
) -> dict[str, str]:
    run_log = RAW_DIR / f"seed_{case.seed}_run{run_index}.txt"
    cmd = [
        vvp_command,
        os.path.relpath(output_path, REPO_ROOT),
        "+MEMFILE=firmware/build/interrupt_race_bug/failing.mem",
        "+EXPECTED_PROPERTY=2",
        "+SENSOR_VALUE=850",
        "+COMMAND_VALUE=0",
        "+MAX_CYCLES=900",
        f"+IRQ_AFTER_COMMAND={case.irq_after_command}",
        f"+IRQ_PULSE_CYCLES={case.irq_pulse_cycles}",
        "+DUMP_CAPSULE=1",
    ]
    if case.irq_start_cycle >= 0:
        cmd.append(f"+IRQ_START_CYCLE={case.irq_start_cycle}")
    if case.irq_end_cycle >= 0:
        cmd.append(f"+IRQ_END_CYCLE={case.irq_end_cycle}")
    result = _run(cmd, cwd=REPO_ROOT, env=env)
    run_log.write_text(_clean_log(result.stdout), encoding="utf-8")
    parsed = _parse_run_log(run_log)
    parsed["returncode"] = str(result.returncode)
    parsed["raw_log"] = str(run_log.relative_to(REPO_ROOT))
    return parsed


def _parse_run_log(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    begin = BEGIN_RE.search(text)
    packets = [match.group("packet").lower() for match in EVENT_RE.finditer(text)]
    digest = hashlib.sha256("\n".join(packets).encode("ascii")).hexdigest() if packets else "NA"
    property_packet = _property_packet(packets)
    property_id = str((property_packet >> 32) & 0xFF) if property_packet is not None else "NA"
    signature = f"{property_packet & 0xFFFF_FFFF:08x}" if property_packet is not None else "NA"
    if not begin:
        return {
            "count": "NA",
            "property": property_id,
            "signature": signature,
            "frozen": "NA",
            "overflow": "NA",
            "digest": digest,
        }
    return {
        "count": begin.group("count"),
        "property": property_id,
        "signature": signature,
        "frozen": begin.group("frozen"),
        "overflow": begin.group("overflow"),
        "digest": digest,
    }


def _property_packet(packets: list[str]) -> int | None:
    for packet_hex in packets:
        packet = int(packet_hex, 16)
        if ((packet >> 164) & 0xF) == 0xA:
            return packet
    return None


def _same_successful_capsule(first: dict[str, str], second: dict[str, str]) -> bool:
    required = (
        first.get("returncode") == "0",
        second.get("returncode") == "0",
        first.get("property") == "2",
        second.get("property") == "2",
        first.get("frozen") == "1",
        second.get("frozen") == "1",
        first.get("overflow") == "0",
        second.get("overflow") == "0",
        first.get("count") not in {"0", "NA"},
        first.get("count") == second.get("count"),
        first.get("digest") == second.get("digest"),
        first.get("signature") == second.get("signature"),
    )
    return all(required)


def _notes(status: str, first: dict[str, str], second: dict[str, str]) -> str:
    if status == "PASS":
        return "same seeded interrupt schedule reproduced identical frozen RTL-smoke capsule digest across two simulator invocations"
    return (
        "seeded interrupt rerun mismatch: "
        f"rc=({first.get('returncode')},{second.get('returncode')}) "
        f"property=({first.get('property')},{second.get('property')}) "
        f"digest=({first.get('digest')},{second.get('digest')})"
    )


def _optional_int(value: int) -> str:
    return str(value) if value >= 0 else "NA"


def _todo_row(case: CampaignCase, notes: str) -> dict[str, str]:
    return {
        "seed": str(case.seed),
        "family": case.family,
        "benchmark": "interrupt_race_bug",
        "status": "TODO",
        "evidence_level": "rtl-smoke",
        "irq_after_command": str(case.irq_after_command),
        "irq_pulse_cycles": str(case.irq_pulse_cycles),
        "irq_start_cycle": _optional_int(case.irq_start_cycle),
        "irq_end_cycle": _optional_int(case.irq_end_cycle),
        "expected_property": "2",
        "property_run1": "NA",
        "property_run2": "NA",
        "capsule_count_run1": "NA",
        "capsule_count_run2": "NA",
        "digest_run1": "NA",
        "digest_run2": "NA",
        "raw_log_run1": "NA",
        "raw_log_run2": "NA",
        "notes": notes,
    }


def _fail_row(case: CampaignCase, notes: str, raw_log: str) -> dict[str, str]:
    row = _todo_row(case, notes)
    row["status"] = "FAIL"
    row["raw_log_run1"] = raw_log
    return row


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "seed",
                "family",
                "benchmark",
                "status",
                "evidence_level",
                "irq_after_command",
                "irq_pulse_cycles",
                "irq_start_cycle",
                "irq_end_cycle",
                "expected_property",
                "property_run1",
                "property_run2",
                "capsule_count_run1",
                "capsule_count_run2",
                "digest_run1",
                "digest_run2",
                "raw_log_run1",
                "raw_log_run2",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
