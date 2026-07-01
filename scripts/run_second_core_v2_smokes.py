#!/usr/bin/env python3
"""Run scoped FemtoRV32 v2 MMIO replay-consumer smokes."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import run_hdl_checks as hdl


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / ".tools/second_core_v2_smokes"
RAW_DIR = REPO_ROOT / "results/raw/second_core_v2_smokes"
OUT_CSV = REPO_ROOT / "results/processed/second_core_v2_smokes.csv"
OUT_MD = REPO_ROOT / "docs/second_core_v2_smokes.md"

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "recorder_config",
    "config_select",
    "expected_property",
    "sensor_value",
    "replay_sensor_value",
    "command_value",
    "replay_command_value",
    "watchdog_enable",
    "irq_after_command",
    "status",
    "property_id",
    "capsule_words",
    "consumed_count",
    "record_signature",
    "replay_signature",
    "signature_match",
    "changed_input",
    "changed_command",
    "require_signature_match",
    "raw_log",
    "notes",
]

PASS_RE = re.compile(
    r"RC_FEMTO_V2_REPLAY_SMOKE_PASS seed=(?P<seed>\d+) config=(?P<config>\d+) "
    r"property=(?P<property>\d+) words=(?P<words>\d+) consumed=(?P<consumed>\d+) "
    r"record_signature=(?P<record>[0-9a-fA-F]+) replay_signature=(?P<replay>[0-9a-fA-F]+) "
    r"signature_match=(?P<signature_match>[01]) replay_sensor_input=(?P<replay_sensor>\d+) "
    r"changed_input=(?P<changed_input>[01]) replay_command_input=(?P<replay_command>\d+) "
    r"changed_command=(?P<changed_command>[01]) require_signature_match=(?P<require_signature_match>\d+)"
)


@dataclass(frozen=True)
class V2Config:
    recorder_config: str
    config_select: int


@dataclass(frozen=True)
class BenchmarkCase:
    benchmark: str
    expected_property: int
    sensor_value: int
    command_value: int
    variant: str = "failing"
    mem_variant: str = "failing"
    build_root: str = "firmware/build"
    watchdog_enable: int = 0
    irq_after_command: int = 0
    irq_pulse_cycles: int = 24
    max_cycles: int = 1200


@dataclass(frozen=True)
class SeedCase:
    seed: int
    sensor_delta: int
    replay_sensor_value: int
    replay_command_value: int


CONFIGS = (
    V2Config("core", 0),
    V2Config("hashed", 1),
    V2Config("full", 2),
)

BENCHMARKS = (
    BenchmarkCase("sensor_threshold_bug", 3, 850, 0),
    BenchmarkCase(
        "interrupt_race_bug",
        2,
        850,
        0,
        variant="fixed_with_wrapper_irq",
        mem_variant="fixed",
        irq_after_command=1,
        max_cycles=900,
    ),
    BenchmarkCase("mmio_ordering_bug", 5, 850, 0),
    BenchmarkCase("stack_corruption_bug", 4, 850, 0),
    BenchmarkCase("uart_command_bug", 1, 850, 85),
    BenchmarkCase("watchdog_timeout_bug", 6, 850, 0, watchdog_enable=1, max_cycles=1600),
    BenchmarkCase("commanded_actuator_limit_bug", 1, 850, 85, build_root="firmware/build_expanded"),
    BenchmarkCase("late_config_sequence_bug", 5, 850, 0, build_root="firmware/build_expanded"),
    BenchmarkCase("sensor_debounce_bug", 3, 850, 0, build_root="firmware/build_expanded", max_cycles=1400),
    BenchmarkCase("status_clear_on_read_bug", 1, 850, 85, build_root="firmware/build_expanded"),
    BenchmarkCase("platform2_status_window_bug", 1, 850, 85, build_root="firmware/build_expanded"),
    BenchmarkCase("platform2_config_order_bug", 5, 850, 0, build_root="firmware/build_expanded"),
    BenchmarkCase("environmental_controller_bug", 1, 650, 85, build_root="firmware/build_expanded", max_cycles=1400),
    BenchmarkCase("power_rail_sequencer_bug", 5, 850, 85, build_root="firmware/build_expanded", max_cycles=1400),
)

SEEDS = (
    SeedCase(1, 0, 0, 0),
    SeedCase(2, 17, 1, 1),
    SeedCase(3, 33, 2, 2),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1), help="parallel simulator jobs")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    test = next(test for test in hdl.IVERILOG_TESTS if test.name == "tb_femtorv32_v2_replay_smoke")
    simv = BUILD_DIR / "tb_femtorv32_v2_replay_smoke.vvp"
    compile_log = RAW_DIR / "tb_femtorv32_v2_replay_smoke_compile.txt"
    compile_status = _compile(test, simv, compile_log)
    cases = [(benchmark, config, seed) for benchmark in BENCHMARKS for config in CONFIGS for seed in SEEDS]
    if compile_status != 0:
        rows = [_blocked_row(benchmark, config, seed, "compile failed") for benchmark, config, seed in cases]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
            rows = list(executor.map(lambda item: _run_case(test, simv, item[0], item[1], item[2]), cases))

    _write_csv(rows)
    _write_doc(rows)
    bad = [row for row in rows if row["status"] != "PASS"]
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OUT_MD)}")
    print(f"SECOND_CORE_V2_SMOKES rows={len(rows)} bad={len(bad)}")
    return 1 if bad else 0


def _compile(test: hdl.IverilogTest, simv: Path, compile_log: Path) -> int:
    iverilog = hdl._find_tool("iverilog")
    if not iverilog:
        compile_log.write_text("iverilog not found\n", encoding="utf-8")
        return 1

    cwd = REPO_ROOT / test.workdir
    cmd = [iverilog.command, "-g2012"]
    for include_dir in hdl._augment_picorv32_include_dirs(test.include_dirs, test.sources):
        cmd.extend(["-I", include_dir])
    for define in test.defines:
        cmd.append(f"-D{define}")
    cmd.extend(["-o", os.path.relpath(simv, cwd), *hdl._augment_picorv32_sources(test.sources)])
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        env=iverilog.env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    compile_log.write_text(_clean(completed.stdout) or "compile passed without output\n", encoding="utf-8")
    return completed.returncode


def _run_case(test: hdl.IverilogTest, simv: Path, benchmark: BenchmarkCase, config: V2Config, seed: SeedCase) -> dict[str, str]:
    vvp = hdl._find_tool("vvp")
    if not vvp:
        return _blocked_row(benchmark, config, seed, "vvp not found")

    raw_log = RAW_DIR / f"{benchmark.benchmark}_{config.recorder_config}_seed{seed.seed}.txt"
    memfile = f"{benchmark.build_root}/{benchmark.benchmark}/{benchmark.mem_variant}.hex"
    sensor_value = benchmark.sensor_value + seed.sensor_delta
    replay_command_value = seed.replay_command_value if benchmark.command_value != 0 else benchmark.command_value
    args = []
    for arg in test.run_args:
        if not (
            arg.startswith("+MEMFILE=")
            or arg.startswith("+EXPECTED_PROPERTY=")
            or arg.startswith("+SEED=")
            or arg.startswith("+SENSOR_VALUE=")
            or arg.startswith("+REPLAY_SENSOR_VALUE=")
            or arg.startswith("+COMMAND_VALUE=")
            or arg.startswith("+REPLAY_COMMAND_VALUE=")
            or arg.startswith("+WATCHDOG_ENABLE=")
            or arg.startswith("+IRQ_AFTER_COMMAND=")
            or arg.startswith("+IRQ_PULSE_CYCLES=")
            or arg.startswith("+RECORDER_CONFIG_SELECT=")
            or arg.startswith("+REQUIRE_SIGNATURE_MATCH=")
            or arg.startswith("+MAX_CYCLES=")
        ):
            args.append(arg)
    args.extend(
        [
            f"+MEMFILE={memfile}",
            f"+EXPECTED_PROPERTY={benchmark.expected_property}",
            f"+SEED={seed.seed}",
            f"+SENSOR_VALUE={sensor_value}",
            f"+REPLAY_SENSOR_VALUE={seed.replay_sensor_value}",
            f"+COMMAND_VALUE={benchmark.command_value}",
            f"+REPLAY_COMMAND_VALUE={replay_command_value}",
            f"+WATCHDOG_ENABLE={benchmark.watchdog_enable}",
            f"+IRQ_AFTER_COMMAND={benchmark.irq_after_command}",
            f"+IRQ_PULSE_CYCLES={benchmark.irq_pulse_cycles}",
            f"+RECORDER_CONFIG_SELECT={config.config_select}",
            "+REQUIRE_SIGNATURE_MATCH=1",
            f"+MAX_CYCLES={benchmark.max_cycles}",
        ]
    )
    completed = subprocess.run(
        [vvp.command, os.path.relpath(simv, REPO_ROOT), *args],
        cwd=REPO_ROOT,
        env=vvp.env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    text = _clean(completed.stdout)
    raw_log.write_text(text, encoding="utf-8")
    match = PASS_RE.search(text)
    status = (
        "PASS"
        if completed.returncode == 0
        and match
        and int(match.group("seed")) == seed.seed
        and int(match.group("config")) == config.config_select
        and int(match.group("property")) == benchmark.expected_property
        and match.group("words") == match.group("consumed")
        and match.group("signature_match") == "1"
        and match.group("changed_input") == "1"
        else "FAIL"
    )
    return {
        "benchmark": benchmark.benchmark,
        "variant": benchmark.variant,
        "seed": str(seed.seed),
        "recorder_config": config.recorder_config,
        "config_select": str(config.config_select),
        "expected_property": str(benchmark.expected_property),
        "sensor_value": str(sensor_value),
        "replay_sensor_value": match.group("replay_sensor") if match else "0",
        "command_value": str(benchmark.command_value),
        "replay_command_value": match.group("replay_command") if match else str(replay_command_value),
        "watchdog_enable": str(benchmark.watchdog_enable),
        "irq_after_command": str(benchmark.irq_after_command),
        "status": status,
        "property_id": match.group("property") if match else "NA",
        "capsule_words": match.group("words") if match else "NA",
        "consumed_count": match.group("consumed") if match else "NA",
        "record_signature": match.group("record").lower() if match else "NA",
        "replay_signature": match.group("replay").lower() if match else "NA",
        "signature_match": "PASS" if match and match.group("signature_match") == "1" else "FAIL",
        "changed_input": "PASS" if match and match.group("changed_input") == "1" else "FAIL",
        "changed_command": "PASS" if match and match.group("changed_command") == "1" else ("NA" if benchmark.command_value == 0 else "FAIL"),
        "require_signature_match": match.group("require_signature_match") if match else "1",
        "raw_log": _rel(raw_log),
        "notes": (
            "Scoped seeded v2 FemtoRV32 smoke resets the wrapped core, perturbs replay-side host MMIO inputs, requires the v2 replay consumer to consume the captured MMIO/property stream, and reproduces the recorded property signature."
            if status == "PASS"
            else _last_line(text)
        ),
    }


def _blocked_row(benchmark: BenchmarkCase, config: V2Config, seed: SeedCase, notes: str) -> dict[str, str]:
    return {
        "benchmark": benchmark.benchmark,
        "variant": benchmark.variant,
        "seed": str(seed.seed),
        "recorder_config": config.recorder_config,
        "config_select": str(config.config_select),
        "expected_property": str(benchmark.expected_property),
        "sensor_value": str(benchmark.sensor_value + seed.sensor_delta),
        "replay_sensor_value": str(seed.replay_sensor_value),
        "command_value": str(benchmark.command_value),
        "replay_command_value": str(seed.replay_command_value if benchmark.command_value != 0 else benchmark.command_value),
        "watchdog_enable": str(benchmark.watchdog_enable),
        "irq_after_command": str(benchmark.irq_after_command),
        "status": "BLOCKED",
        "property_id": "NA",
        "capsule_words": "NA",
        "consumed_count": "NA",
        "record_signature": "NA",
        "replay_signature": "NA",
        "signature_match": "NA",
        "changed_input": "NA",
        "changed_command": "NA",
        "require_signature_match": "1",
        "raw_log": "",
        "notes": notes,
    }


def _write_csv(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_doc(rows: list[dict[str, str]]) -> None:
    pass_rows = sum(1 for row in rows if row["status"] == "PASS")
    benchmarks = sorted({row["benchmark"] for row in rows})
    configs = sorted({row["recorder_config"] for row in rows})
    seeds = sorted({row["seed"] for row in rows})
    wrapper_irq_rows = sum(1 for row in rows if row["status"] == "PASS" and row.get("irq_after_command") == "1")
    watchdog_rows = sum(1 for row in rows if row["status"] == "PASS" and row.get("watchdog_enable") == "1")
    command_perturb_rows = sum(1 for row in rows if row["status"] == "PASS" and row.get("changed_command") == "PASS")
    lines = [
        "# Second-Core v2 Replay-Consumer Smokes",
        "",
        f"Status: `{pass_rows}/{len(rows)}` rows PASS.",
        "",
        "These scoped Icarus rows run the FemtoRV32 v2 wrapper on compiler-built base and expanded benchmark firmware, record a v2 MMIO/property stream, reset the wrapped core, perturb replay-side host MMIO inputs, and require the v2 replay consumer to consume the captured stream while reproducing the recorded property signature.",
        "",
        f"- Benchmarks covered: `{len(benchmarks)}` ({', '.join(benchmarks)}).",
        f"- Recorder configs covered: `{len(configs)}` ({', '.join(configs)}).",
        f"- Seeds covered: `{len(seeds)}` ({', '.join(seeds)}).",
        f"- Wrapper-level IRQ-boundary rows: `{wrapper_irq_rows}` PASS.",
        f"- Watchdog rows: `{watchdog_rows}` PASS.",
        f"- Replay command perturbation rows: `{command_perturb_rows}` PASS.",
        "- The full diagnostic v2 config uses the same strict-order replay consumer, with the FemtoRV32 core held until the first replay word is preloaded so startup diagnostic events are consumed in order.",
        "",
        "| Benchmark | Seed | Config | Status | Property | Words | Consumed | Signature match | Changed sensor | Changed command | Record signature | Replay signature |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['benchmark']}` | {row['seed']} | `{row['recorder_config']}` | `{row['status']}` | {row['property_id']} | {row['capsule_words']} | "
            f"{row['consumed_count']} | `{row['signature_match']}` | `{row['changed_input']}` | `{row['changed_command']}` | "
            f"`{row['record_signature']}` | `{row['replay_signature']}` |"
        )
    lines.extend(
        [
            "",
            "Allowed from this evidence:",
            "",
            f"- Scoped seeded FemtoRV32 v2 MMIO replay-consumer smokes reproduce the recorded property signature for {len(benchmarks)} benchmark families across {len(seeds)} seeds and core, hashed, and full recorder configurations while replay-side host MMIO inputs are perturbed.",
            "- The v2 consumer consumes the captured replay stream and supplies replay MMIO values at the core-facing wrapper boundary for these focused base/expanded cases.",
            "- The matrix includes wrapper-level IRQ-boundary and watchdog cases, but these remain wrapper/recorder stimuli rather than true FemtoRV32 CPU interrupt handling.",
            "",
            "Do not claim from this evidence:",
            "",
            "- v2 replay that drives both FemtoRV32 core-facing MMIO and IRQ inputs.",
            "- True CPU interrupt/ISR replay on FemtoRV32.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _clean(text: str) -> str:
    return hdl._clean_log(text)


def _last_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped[:240]
    return "no output"


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
