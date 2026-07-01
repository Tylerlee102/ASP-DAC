#!/usr/bin/env python3
"""Build and run the Hazard3 v2 MMIO+IRQ ReplayCapsule benchmark matrix."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import ctypes
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = REPO_ROOT / "build" / "hazard3_replay_smoke"
RAW_DIR = REPO_ROOT / "results" / "raw" / "hazard3_v2_replay_smoke"
OUT_CSV = REPO_ROOT / "results" / "processed" / "hazard3_v2_replay_smoke.csv"
OUT_MD = REPO_ROOT / "docs" / "hazard3_v2_replay_smoke.md"
FIRMWARE = REPO_ROOT / "firmware" / "hazard3_replay_smoke" / "hazard3_replay_smoke.S"
LINKER = REPO_ROOT / "firmware" / "hazard3_replay_smoke" / "linker.ld"
TB = REPO_ROOT / "tb" / "system" / "tb_hazard3_v2_replay_smoke.sv"
HDL = REPO_ROOT / "third_party" / "hazard3" / "hdl"

FIELDS = [
    "check",
    "benchmark",
    "scenario",
    "variant",
    "seed",
    "status",
    "cycles",
    "config",
    "config_select",
    "expected_property",
    "property",
    "words",
    "consumed",
    "record_signature",
    "replay_signature",
    "signature_match",
    "record_irq_entries",
    "replay_irq_entries",
    "record_mmio_reads",
    "replay_mmio_reads",
    "replay_mmio_drives",
    "replay_irq_drives",
    "external_irq_replay",
    "sensor_value",
    "replay_sensor_value",
    "changed_sensor",
    "watchdog_enable",
    "raw_log",
    "notes",
]

PASS_RE = re.compile(
    r"RC_HAZARD3_V2_REPLAY_SMOKE_PASS cycles=(?P<cycles>\d+) "
    r"config=(?P<config>\d+) property=(?P<property>\d+) words=(?P<words>\d+) consumed=(?P<consumed>\d+) "
    r"record_signature=(?P<record_signature>[0-9a-fA-F]+) replay_signature=(?P<replay_signature>[0-9a-fA-F]+) "
    r"signature_match=(?P<signature_match>\d+) record_irq_entries=(?P<record_irq_entries>\d+) "
    r"replay_irq_entries=(?P<replay_irq_entries>\d+) record_mmio_reads=(?P<record_mmio_reads>\d+) "
    r"replay_mmio_reads=(?P<replay_mmio_reads>\d+) replay_mmio_drives=(?P<replay_mmio_drives>\d+) "
    r"replay_irq_drives=(?P<replay_irq_drives>\d+) external_irq_replay=(?P<external_irq_replay>\d+) "
    r"sensor_value=(?P<sensor_value>\d+) replay_sensor_value=(?P<replay_sensor_value>\d+)"
)


@dataclass(frozen=True)
class Hazard3Workload:
    benchmark: str
    workload_id: int
    expected_property: int
    sensor_base: int
    watchdog_enable: int = 0
    max_cycles: int = 5000
    variant: str = "failing"


@dataclass(frozen=True)
class V2Config:
    name: str
    select: int


@dataclass(frozen=True)
class SeedCase:
    seed: int
    sensor_delta: int
    replay_sensor_value: int


WORKLOADS = (
    Hazard3Workload("actuator_limit_bug", 1, 1, 650),
    Hazard3Workload("interrupt_critical_bug", 2, 2, 650),
    Hazard3Workload("stack_protect_bug", 4, 4, 650),
    Hazard3Workload("mmio_ordering_bug", 5, 5, 650),
    Hazard3Workload("profile2_actuator_limit_bug", 7, 1, 650),
    Hazard3Workload("profile2_interrupt_critical_bug", 8, 2, 650),
    Hazard3Workload("profile2_mmio_ordering_bug", 9, 5, 650),
    Hazard3Workload("post_config_actuator_limit_bug", 10, 1, 650),
)

CONFIGS = (
    V2Config("core", 0),
    V2Config("hashed", 1),
)

SEEDS = (
    SeedCase(1, 0, 0),
    SeedCase(2, 17, 123),
    SeedCase(3, 33, 698),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1), help="parallel simulator jobs")
    args = parser.parse_args()

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    cases = [(workload, config, seed) for workload in WORKLOADS for config in CONFIGS for seed in SEEDS]
    rows = [_blocked_row("not run", workload, config, seed) for workload, config, seed in cases]
    tools = _find_tools()
    missing = [name for name, value in tools.items() if not value]
    if missing:
        rows = [_blocked_row(f"missing tools: {', '.join(missing)}", workload, config, seed) for workload, config, seed in cases]
    else:
        build_results = {workload.benchmark: _build_firmware(tools, workload) for workload in WORKLOADS}
        failed_builds = {name: result for name, result in build_results.items() if result.returncode != 0}
        if failed_builds:
            rows = [
                _blocked_row(f"firmware build failed; see {_rel(RAW_DIR / f'firmware_build_{workload.benchmark}.txt')}", workload, config, seed)
                for workload, config, seed in cases
            ]
        else:
            for workload in WORKLOADS:
                _convert_verilog_hex_to_mem(
                    BUILD_DIR / f"{workload.benchmark}.hex",
                    BUILD_DIR / f"{workload.benchmark}.mem",
                )
            compile_result = _compile_sim(tools)
            if compile_result.returncode != 0:
                rows = [
                    _blocked_row(f"Icarus compile failed; see {_rel(RAW_DIR / 'iverilog_compile.txt')}", workload, config, seed)
                    for workload, config, seed in cases
                ]
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
                    rows = list(executor.map(lambda case: _run_sim(tools, case[0], case[1], case[2]), cases))
    _write_csv(rows)
    _write_doc(rows)
    bad = [row for row in rows if row["status"] != "PASS"]
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OUT_MD)}")
    print(f"HAZARD3_V2_REPLAY_MATRIX rows={len(rows)} bad={len(bad)}")
    return 1 if bad else 0


def _find_tools() -> dict[str, str | None]:
    bin_dirs = [path for path in (REPO_ROOT / ".tools" / "toolchains").glob("**/bin") if path.is_dir()]
    gcc = _find_named_tool(("riscv-none-elf-gcc.exe", "riscv64-unknown-elf-gcc.exe"), bin_dirs)
    objcopy = _find_named_tool(("riscv-none-elf-objcopy.exe", "riscv64-unknown-elf-objcopy.exe"), bin_dirs)
    oss_bin = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite" / "bin"
    iverilog = _first_existing([oss_bin / "iverilog.exe"]) or shutil.which("iverilog")
    vvp = _first_existing([oss_bin / "vvp.exe"]) or shutil.which("vvp")
    return {"gcc": gcc, "objcopy": objcopy, "iverilog": iverilog, "vvp": vvp}


def _build_firmware(tools: dict[str, str | None], workload: Hazard3Workload) -> subprocess.CompletedProcess[str]:
    elf = BUILD_DIR / f"{workload.benchmark}.elf"
    hex_path = BUILD_DIR / f"{workload.benchmark}.hex"
    map_path = BUILD_DIR / f"{workload.benchmark}.map"
    cmd = [
        tools["gcc"] or "",
        "-march=rv32i_zicsr",
        "-mabi=ilp32",
        "-ffreestanding",
        "-fno-builtin",
        "-nostdlib",
        "-nostartfiles",
        "-Wall",
        "-Wextra",
        f"-DWORKLOAD_ID={workload.workload_id}",
        str(FIRMWARE),
        "-T",
        str(LINKER),
        f"-Wl,-Map,{map_path}",
        "-o",
        str(elf),
    ]
    completed = _run(cmd, RAW_DIR / f"firmware_build_{workload.benchmark}.txt", env=_tool_env(tools["gcc"]))
    if completed.returncode == 0:
        objcopy_cmd = [tools["objcopy"] or "", "-O", "verilog", "--verilog-data-width=4", str(elf), str(hex_path)]
        objcopy_result = _run(objcopy_cmd, RAW_DIR / f"firmware_objcopy_{workload.benchmark}.txt", env=_tool_env(tools["objcopy"]))
        if objcopy_result.returncode != 0:
            return objcopy_result
    return completed


def _compile_sim(tools: dict[str, str | None]) -> subprocess.CompletedProcess[str]:
    hazard3_files = [
        str((HDL / line.split(maxsplit=1)[1]).relative_to(REPO_ROOT))
        for line in _read(HDL / "hazard3.f").splitlines()
        if line.startswith("file ")
    ]
    replay_sources = [
        "rtl/hash_signature.sv",
        "rtl/event_tap.sv",
        "rtl/event_classifier.sv",
        "rtl/property_checker.sv",
        "rtl/event_slicer.sv",
        "rtl/replaycapsule_v2/rcv2_payload_hasher.sv",
        "rtl/replaycapsule_v2/rcv2_address_dictionary.sv",
        "rtl/replaycapsule_v2/rcv2_adaptive_window.sv",
        "rtl/replaycapsule_v2/rcv2_event_packer.sv",
        "rtl/replaycapsule_v2/rcv2_event_fifo_bram.sv",
        "rtl/replaycapsule_v2/rcv2_event_stream_fifo.sv",
        "rtl/replaycapsule_v2/rcv2_recorder.sv",
        "rtl/replaycapsule_v2/rcv2_mmio_replay_driver.sv",
        "rtl/replaycapsule_v2/rcv2_irq_replay_driver.sv",
        "rtl/replaycapsule_v2/rcv2_replay_consumer.sv",
        "rtl/rv32i_integration/hazard3_replaycapsule_v2_wrapper.sv",
    ]
    cmd = [
        tools["iverilog"] or "",
        "-g2012",
        "-I",
        "rtl",
        "-I",
        "rtl/replaycapsule_v2",
        "-I",
        "rtl/rv32i_integration",
        "-I",
        "third_party/hazard3/hdl",
        "-o",
        str(BUILD_DIR / "tb_hazard3_v2_replay_smoke.vvp"),
        str(TB.relative_to(REPO_ROOT)),
        *replay_sources,
        *hazard3_files,
    ]
    return _run(cmd, RAW_DIR / "iverilog_compile.txt", env=_tool_env(tools["iverilog"]))


def _run_sim(
    tools: dict[str, str | None],
    workload: Hazard3Workload,
    config: V2Config,
    seed: SeedCase,
) -> dict[str, str]:
    scenario = f"{workload.benchmark}_{config.name}_seed{seed.seed}"
    sensor_value = workload.sensor_base + seed.sensor_delta
    log = RAW_DIR / f"vvp_run_{scenario}.txt"
    cmd = [
        tools["vvp"] or "",
        str(BUILD_DIR / "tb_hazard3_v2_replay_smoke.vvp"),
        f"+MEMFILE={_rel(BUILD_DIR / f'{workload.benchmark}.mem')}",
        f"+EXPECTED_PROPERTY={workload.expected_property}",
        f"+SENSOR_VALUE={sensor_value}",
        f"+REPLAY_SENSOR_VALUE={seed.replay_sensor_value}",
        f"+RECORDER_CONFIG_SELECT={config.select}",
        f"+WATCHDOG_ENABLE={workload.watchdog_enable}",
        "+REQUIRE_SIGNATURE_MATCH=1",
        f"+MAX_CYCLES={workload.max_cycles}",
    ]
    completed = _run(cmd, log, env=_tool_env(tools["vvp"]))
    text = _read(log)
    match = PASS_RE.search(text)
    if not match:
        return _fail_row(log, _last_line(text), workload, config, seed, sensor_value)
    status = (
        "PASS"
        if completed.returncode == 0
        and match.group("config") == str(config.select)
        and match.group("property") == str(workload.expected_property)
        and match.group("words") == match.group("consumed")
        and match.group("signature_match") == "1"
        and int(match.group("record_irq_entries")) > 0
        and int(match.group("replay_irq_entries")) > 0
        and int(match.group("record_mmio_reads")) > 0
        and int(match.group("replay_mmio_reads")) > 0
        and int(match.group("replay_mmio_drives")) > 0
        and int(match.group("replay_irq_drives")) > 0
        and match.group("external_irq_replay") == "0"
        and match.group("sensor_value") != match.group("replay_sensor_value")
        else "FAIL"
    )
    return {
        "check": "hazard3_v2_mmio_irq_replay_matrix",
        "benchmark": workload.benchmark,
        "scenario": scenario,
        "variant": workload.variant,
        "seed": str(seed.seed),
        "status": status,
        "cycles": match.group("cycles"),
        "config": config.name,
        "config_select": str(config.select),
        "expected_property": str(workload.expected_property),
        "property": match.group("property"),
        "words": match.group("words"),
        "consumed": match.group("consumed"),
        "record_signature": match.group("record_signature").lower(),
        "replay_signature": match.group("replay_signature").lower(),
        "signature_match": match.group("signature_match"),
        "record_irq_entries": match.group("record_irq_entries"),
        "replay_irq_entries": match.group("replay_irq_entries"),
        "record_mmio_reads": match.group("record_mmio_reads"),
        "replay_mmio_reads": match.group("replay_mmio_reads"),
        "replay_mmio_drives": match.group("replay_mmio_drives"),
        "replay_irq_drives": match.group("replay_irq_drives"),
        "external_irq_replay": match.group("external_irq_replay"),
        "sensor_value": match.group("sensor_value"),
        "replay_sensor_value": match.group("replay_sensor_value"),
        "changed_sensor": "PASS" if match.group("sensor_value") != match.group("replay_sensor_value") else "FAIL",
        "watchdog_enable": str(workload.watchdog_enable),
        "raw_log": _rel(log),
        "notes": (
            "Hazard3 is ReplayCapsule-wrapped for a seeded v2 MMIO+IRQ replay row: "
            "record captures an MMIO read plus true ISR marker/ack events, replay perturbs host sensor/IRQ, "
            "the selected RTL recorder config streams the capsule, and the RTL consumer drives core-facing MMIO and IRQ."
        ),
    }


def _convert_verilog_hex_to_mem(source: Path, dest: Path) -> None:
    words: dict[int, int] = {}
    byte_buffer: dict[int, int] = {}
    address = 0
    for raw in source.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split()
        if not parts:
            continue
        if parts[0].startswith("@"):
            address = int(parts[0][1:], 16)
            parts = parts[1:]
        for token in parts:
            value = int(token, 16)
            if len(token) <= 2:
                byte_buffer[address] = value
                address += 1
            else:
                words[address] = value
                address += 1
    for byte_addr, value in byte_buffer.items():
        index = byte_addr // 4
        shift = (byte_addr % 4) * 8
        words[index] = (words.get(index, 0) & ~(0xFF << shift)) | (value << shift)
    lines = [f"@{index:08x} {words[index]:08x}" for index in sorted(words)]
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run(cmd: list[str], log: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text((completed.stdout or "").strip() + "\n", encoding="utf-8")
    return completed


def _tool_env(tool: str | None) -> dict[str, str]:
    env = os.environ.copy()
    if tool:
        env["PATH"] = str(Path(tool).parent) + os.pathsep + env.get("PATH", "")
    oss = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite"
    if oss.exists():
        suite = _short_path(oss)
        env["PATH"] = os.pathsep.join([str(suite / "bin"), str(suite / "lib"), env.get("PATH", "")])
    return env


def _write_csv(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_doc(rows: list[dict[str, str]]) -> None:
    pass_rows = sum(1 for row in rows if row["status"] == "PASS")
    benchmarks = sorted({row["benchmark"] for row in rows})
    configs = sorted({row["config"] for row in rows})
    seeds = sorted({row["seed"] for row in rows})
    properties = sorted({row["property"] for row in rows if row["property"] not in {"", "NA"}})
    status = "PASS" if rows and pass_rows == len(rows) else "FAIL"
    lines = [
        "# Hazard3 v2 Replay Benchmark Matrix",
        "",
        f"Status: `{status}` ({pass_rows}/{len(rows)} rows PASS).",
        "",
        "These Icarus rows wrap the vendored Hazard3 core with the v2 ReplayCapsule recorder and RTL replay consumer. Each row runs compiler-built RV32I+Zicsr firmware, records a firmware MMIO read plus true machine external interrupt handler marker/ack events, resets the core, perturbs replay-side host sensor input while keeping host replay IRQ deasserted, and requires the RTL replay consumer to drive core-facing MMIO data and IRQ stimulus while reproducing the recorded property signature.",
        "",
        f"- Benchmarks covered: `{len(benchmarks)}` ({', '.join(benchmarks)}).",
        f"- Recorder configs covered: `{len(configs)}` ({', '.join(configs)}).",
        f"- Seeds covered: `{len(seeds)}` ({', '.join(seeds)}).",
        f"- Property IDs covered: `{len(properties)}` ({', '.join(properties)}).",
        "",
        "| Benchmark | Seed | Config | Status | Property | Words | Consumed | IRQ record/replay | MMIO drives | IRQ drives | Sensor -> replay host | Evidence |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['benchmark']}` | {row['seed']} | `{row['config']}` | `{row['status']}` | {row['property']} | "
            f"{row['words']} | {row['consumed']} | {row['record_irq_entries']}/{row['replay_irq_entries']} | "
            f"{row['replay_mmio_drives']} | {row['replay_irq_drives']} | "
            f"{row['sensor_value']} -> {row['replay_sensor_value']} | `{row['raw_log']}` |"
        )
    lines.extend([
        "",
        "Allowed from this evidence:",
        "",
        "- Hazard3 has a seeded ReplayCapsule v2 MMIO+IRQ replay-consumer matrix across multiple firmware bug classes and selected v2 recorder configurations.",
        "- The replay phase uses the RTL replay consumer to drive core-facing MMIO read data and IRQ stimulus while host-side replay IRQ remains deasserted.",
        "- The observed interrupt-enter event is tied to firmware execution of the Hazard3 ISR marker write.",
        "",
        "Do not claim from this evidence:",
        "",
        "- ASIC implementation-cost claims; use `results/processed/asic_openpdk.csv` for those.",
        "- Board/silicon replay.",
        "- Multicore, DMA, cache/coherence, or arbitrary peripheral replay.",
        "- Full operating-system or application-suite coverage beyond these scoped firmware benchmark rows.",
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _blocked_row(notes: str, workload: Hazard3Workload, config: V2Config, seed: SeedCase) -> dict[str, str]:
    sensor_value = workload.sensor_base + seed.sensor_delta
    return {
        "check": "hazard3_v2_mmio_irq_replay_matrix",
        "benchmark": workload.benchmark,
        "scenario": f"{workload.benchmark}_{config.name}_seed{seed.seed}",
        "variant": workload.variant,
        "seed": str(seed.seed),
        "status": "BLOCKED",
        "cycles": "NA",
        "config": config.name,
        "config_select": str(config.select),
        "expected_property": str(workload.expected_property),
        "property": "NA",
        "words": "NA",
        "consumed": "NA",
        "record_signature": "NA",
        "replay_signature": "NA",
        "signature_match": "NA",
        "record_irq_entries": "NA",
        "replay_irq_entries": "NA",
        "record_mmio_reads": "NA",
        "replay_mmio_reads": "NA",
        "replay_mmio_drives": "NA",
        "replay_irq_drives": "NA",
        "external_irq_replay": "NA",
        "sensor_value": str(sensor_value),
        "replay_sensor_value": str(seed.replay_sensor_value),
        "changed_sensor": "NA",
        "watchdog_enable": str(workload.watchdog_enable),
        "raw_log": "",
        "notes": notes,
    }


def _fail_row(
    log: Path,
    notes: str,
    workload: Hazard3Workload,
    config: V2Config,
    seed: SeedCase,
    sensor_value: int,
) -> dict[str, str]:
    row = _blocked_row(notes, workload, config, seed)
    row["status"] = "FAIL"
    row["sensor_value"] = str(sensor_value)
    row["raw_log"] = _rel(log)
    return row


def _find_named_tool(names: tuple[str, ...], bin_dirs: list[Path]) -> str | None:
    for bin_dir in bin_dirs:
        for name in names:
            candidate = bin_dir / name
            if candidate.exists():
                return str(candidate)
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def _first_existing(paths: list[Path]) -> str | None:
    for path in paths:
        if path.exists():
            return str(_short_path(path))
    return None


def _short_path(path: Path) -> Path:
    if os.name != "nt":
        return path
    try:
        buffer = ctypes.create_unicode_buffer(1024)
        result = ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, len(buffer))
        if result:
            return Path(buffer.value)
    except Exception:
        pass
    return path


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "no output"


if __name__ == "__main__":
    raise SystemExit(main())
