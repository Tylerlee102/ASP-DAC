#!/usr/bin/env python3
"""Run firmware-running RTL record/replay experiments when the harness exists."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("REPLAYCAPSULE_REPO_ROOT", Path(__file__).resolve().parents[1]))
SIM = REPO_ROOT / "build/verilator/replaycapsule_sim"
OUT_CSV = REPO_ROOT / "results/processed/full_rtl_replay.csv"
FIRMWARE_BUILD_CSV = REPO_ROOT / "results/processed/firmware_build.csv"
FIRMWARE_COMPARISON_CSV = REPO_ROOT / "results/processed/firmware_source_comparison.csv"
CAPSULE_DIR = REPO_ROOT / "results/raw/rtl_capsules"
SIGNATURE_DIR = REPO_ROOT / "results/raw/rtl_signatures"
DEBUG_DIR = REPO_ROOT / "results/debug/pass7"
LOCAL_WINLIBS_BIN = REPO_ROOT / ".tools/winlibs/mingw64/bin"
OSS_CAD_SUITE = Path(os.environ.get("REPLAYCAPSULE_OSS_CAD_SUITE", REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"))
LOCAL_BUILD_ROOT = Path(os.environ.get("REPLAYCAPSULE_LOCAL_BUILD_ROOT", Path.home() / ".cache/replaycapsule-rv/verilator"))

BENCHMARKS = (
    "sensor_threshold_bug",
    "interrupt_race_bug",
    "mmio_ordering_bug",
    "stack_corruption_bug",
    "uart_command_bug",
    "watchdog_timeout_bug",
)

VARIANTS = {
    "sensor_threshold_bug": ("failing", "fixed", "no_failure_edge"),
    "interrupt_race_bug": ("failing", "fixed"),
    "mmio_ordering_bug": ("failing", "fixed"),
    "stack_corruption_bug": ("failing", "fixed"),
    "uart_command_bug": ("failing", "fixed", "no_failure_edge"),
    "watchdog_timeout_bug": ("failing", "fixed", "no_failure_edge"),
}

VERILATOR_SOURCE_PATHS = (
    "tb/verilator/replaycapsule_verilator_top.sv",
    "third_party/picorv32/picorv32.v",
    "rtl/event_pkg.sv",
    "rtl/event_tap.sv",
    "rtl/event_classifier.sv",
    "rtl/capsule_buffer.sv",
    "rtl/property_checker.sv",
    "rtl/event_slicer.sv",
    "rtl/hash_signature.sv",
    "rtl/replay_capsule_top.sv",
    "rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv",
    "tb/verilator/main.cpp",
    "tb/verilator/rtl_harness.cpp",
    "tb/verilator/capsule_io.cpp",
)

VERILATOR_DEPENDENCY_PATHS = VERILATOR_SOURCE_PATHS + (
    "tb/verilator/rtl_harness.h",
    "tb/verilator/capsule_io.h",
    "Makefile",
)

FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "rtl_record_status",
    "capsule_export_status",
    "replay_status",
    "property_id_record",
    "property_id_replay",
    "commit_match",
    "event_match",
    "final_signature_match",
    "capsule_bytes",
    "cycles_to_failure",
    "commits_to_failure",
    "firmware_source",
    "firmware_sha256",
    "compiler_backed",
    "notes",
]

COMPARISON_FIELDS = [
    "benchmark",
    "variant",
    "seed",
    "fallback_status",
    "compiler_status",
    "fallback_property_id",
    "compiler_property_id",
    "fallback_cycles_to_failure",
    "compiler_cycles_to_failure",
    "fallback_commits_to_failure",
    "compiler_commits_to_failure",
    "fallback_event_count",
    "compiler_event_count",
    "same_property",
    "same_event_count",
    "first_divergence",
    "likely_root_cause",
    "notes",
]

EXPECTED_PROPERTIES = {
    "sensor_threshold_bug": 3,
    "interrupt_race_bug": 2,
    "mmio_ordering_bug": 5,
    "stack_corruption_bug": 4,
    "uart_command_bug": 1,
    "watchdog_timeout_bug": 6,
}


def main() -> int:
    reexec_code = _maybe_reexec_without_space(sys.argv[1:])
    if reexec_code is not None:
        return reexec_code

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="run seed 1 only")
    parser.add_argument("--full", action="store_true", help="run default seed set 1,2,3")
    parser.add_argument("--benchmark", choices=BENCHMARKS, help="run one benchmark only")
    parser.add_argument("--variant", help="run one variant only; requires --benchmark")
    parser.add_argument("--seed", type=int, help="run one seed only")
    parser.add_argument("--max-cycles", type=int, default=100000)
    parser.add_argument("--debug-events", action="store_true", help="write record/replay event debug logs")
    parser.add_argument("--dump-mmio", action="store_true", help="write live MMIO traces for debug runs")
    parser.add_argument("--dump-property", action="store_true", help="write property-checker input/output traces")
    parser.add_argument("--dump-pc", action="store_true", help="write instruction fetch PC traces")
    parser.add_argument("--dump-disasm-context", action="store_true", help="write firmware disassembly or HEX context")
    parser.add_argument("--debug-dir", default=str(DEBUG_DIR), help="directory for --debug-events outputs")
    parser.add_argument("--allow-fallback", action="store_true", help="permit non-compiler fallback HEX rows")
    args = parser.parse_args()
    if args.variant and not args.benchmark:
        parser.error("--variant requires --benchmark")
    if args.benchmark and args.variant and args.variant not in VARIANTS[args.benchmark]:
        parser.error(f"{args.variant} is not a known variant for {args.benchmark}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    SIGNATURE_DIR.mkdir(parents=True, exist_ok=True)

    seeds = [args.seed] if args.seed is not None else [1] if args.quick else [1, 2, 3]
    benchmarks = [args.benchmark] if args.benchmark else list(BENCHMARKS)
    variants = {benchmark: (args.variant,) if args.variant else VARIANTS[benchmark] for benchmark in benchmarks}
    allow_fallback = args.allow_fallback or _truthy_env("REPLAYCAPSULE_ALLOW_FALLBACK") or _truthy_env("ALLOW_FALLBACK")
    blocker = _ensure_simulator()
    rows: list[dict[str, str]] = []
    if blocker:
        for benchmark in benchmarks:
            for variant in variants[benchmark]:
                for seed in seeds:
                    rows.append(_blocked_row(benchmark, variant, seed, blocker))
        _write_rows(rows)
        _write_firmware_source_comparison(rows)
        print(f"WROTE {_rel(OUT_CSV)}")
        print(f"BLOCKED full RTL replay: {blocker}")
        return 1 if _strict_ci() else 0

    for benchmark in benchmarks:
        for variant in variants[benchmark]:
            for seed in seeds:
                rows.append(
                    _run_case(
                        benchmark,
                        variant,
                        seed,
                        args.max_cycles,
                        allow_fallback,
                        args.debug_events,
                        Path(args.debug_dir),
                        args.dump_mmio,
                        args.dump_property,
                        args.dump_pc,
                        args.dump_disasm_context,
                    )
                )

    _write_rows(rows)
    _write_firmware_source_comparison(rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    if _strict_ci() and rows and all(row.get("rtl_record_status") == "BLOCKED" for row in rows):
        print("BLOCKED full RTL replay: all rows are blocked in strict CI")
        return 1
    return 0


def _maybe_reexec_without_space(argv: list[str]) -> int | None:
    if os.name != "nt" or os.environ.get("REPLAYCAPSULE_NO_SUBST") == "1":
        return None
    if " " not in str(REPO_ROOT):
        return None

    for letter in ("R", "X", "Y", "Z"):
        drive = f"{letter}:"
        if not Path(drive + "\\").exists():
            break
    else:
        return None

    created = subprocess.run(["subst", drive, str(REPO_ROOT)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if created.returncode != 0:
        return None
    env = dict(os.environ)
    env["REPLAYCAPSULE_NO_SUBST"] = "1"
    env["REPLAYCAPSULE_ORIGINAL_REPO_ROOT"] = str(REPO_ROOT)
    env["REPLAYCAPSULE_REPO_ROOT"] = drive + "\\"
    env["REPLAYCAPSULE_OSS_CAD_SUITE"] = drive + "\\.tools\\oss-cad-suite\\oss-cad-suite"
    try:
        completed = subprocess.run(
            [sys.executable, drive + "\\scripts\\run_full_rtl_replay.py", *argv],
            cwd=drive + "\\",
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(_clean(completed.stdout), end="")
        return completed.returncode
    finally:
        subprocess.run(["subst", drive, "/D"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _ensure_simulator() -> str | None:
    log = REPO_ROOT / "results/raw/verilator/build.log"
    if _sim_path().exists() and not _sim_needs_rebuild():
        _sanitize_file(log)
        return None
    make = _find_make()
    gxx = _find_cxx()
    verilator = _find_verilator()
    missing = []
    if not make:
        missing.append("make/gmake")
    if not gxx:
        missing.append("g++/c++/clang++")
    if not verilator:
        missing.append("verilator")
    if missing:
        return "missing " + ", ".join(missing) + "; build/verilator/replaycapsule_sim not available"

    cache_sim = LOCAL_BUILD_ROOT / "replaycapsule_sim.exe"
    build_args = [
        make,
        "verilator-harness",
        f"PYTHON={Path(sys.executable).as_posix()}",
        f"VERILATOR={Path(verilator).name}",
        "VERILATOR_ENV=",
    ]
    if os.name == "nt":
        shutil.rmtree(LOCAL_BUILD_ROOT / "obj_dir", ignore_errors=True)
        if cache_sim.exists():
            cache_sim.unlink()
        LOCAL_BUILD_ROOT.mkdir(parents=True, exist_ok=True)
        build_args.extend(
            [
                f"VERILATOR_MDIR={LOCAL_BUILD_ROOT.as_posix()}/obj_dir",
                f"VERILATOR_OUTPUT={cache_sim.as_posix()}",
                f"VERILATOR_CFLAGS=-std=c++17 -O2 -I{(REPO_ROOT / 'tb/verilator').as_posix()}",
                "VERILATOR_SOURCES=" + " ".join((REPO_ROOT / path).as_posix() for path in VERILATOR_SOURCE_PATHS),
            ]
        )
    completed = subprocess.run(
        build_args,
        cwd=REPO_ROOT,
        env=_tool_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    existing = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if completed.returncode != 0:
        separator = "\n\n# make invocation output\n" if existing else ""
        existing = existing + separator + completed.stdout
    elif not existing:
        existing = completed.stdout
    log.write_text(_clean(existing), encoding="utf-8")
    if os.name == "nt" and cache_sim.exists():
        target = SIM.with_suffix(".exe")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cache_sim, target)
    if completed.returncode != 0 or not _sim_path().exists():
        return f"verilator harness build failed; see {_rel(log)}"
    return None


def _run_case(
    benchmark: str,
    variant: str,
    seed: int,
    max_cycles: int,
    allow_fallback: bool,
    debug_events: bool = False,
    debug_dir: Path = DEBUG_DIR,
    dump_mmio: bool = False,
    dump_property: bool = False,
    dump_pc: bool = False,
    dump_disasm_context: bool = False,
) -> dict[str, str]:
    firmware, firmware_meta, firmware_blocker = _select_firmware(benchmark, variant, allow_fallback)
    if firmware_blocker is not None or firmware is None:
        return _blocked_row(benchmark, variant, seed, firmware_blocker or "compiler-backed firmware unavailable")

    base = f"{benchmark}_{variant}_seed{seed}"
    capsule = CAPSULE_DIR / f"{base}.json"
    record_sig = SIGNATURE_DIR / f"{base}_record.json"
    replay_sig = SIGNATURE_DIR / f"{base}_replay.json"

    record = _run_sim(
        "record",
        benchmark,
        variant,
        firmware,
        capsule,
        record_sig,
        seed,
        max_cycles,
        debug_events,
        debug_dir,
        dump_mmio,
        dump_property,
        dump_pc,
        dump_disasm_context,
    )
    debug_requested = debug_events or dump_mmio or dump_property or dump_pc or dump_disasm_context
    if record.returncode != 0:
        if debug_requested:
            _write_debug_analysis(benchmark, variant, seed, debug_dir, replay_ran=False)
            _write_run_debug_context(
                benchmark,
                variant,
                seed,
                firmware,
                firmware_meta,
                record,
                record_sig,
                debug_dir,
                dump_disasm_context,
                replay=None,
                replay_sig=None,
            )
        return _failed_row(benchmark, variant, seed, "FAIL", "NA", record.stdout, firmware_meta, record_sig, capsule)

    replay = _run_sim(
        "replay",
        benchmark,
        variant,
        firmware,
        capsule,
        replay_sig,
        seed,
        max_cycles,
        debug_events,
        debug_dir,
        dump_mmio,
        dump_property,
        dump_pc,
        dump_disasm_context,
    )
    record_payload = _read_json(record_sig)
    replay_payload = _read_json(replay_sig)
    if debug_requested:
        _write_debug_analysis(benchmark, variant, seed, debug_dir, replay_ran=True)
        _write_run_debug_context(
            benchmark,
            variant,
            seed,
            firmware,
            firmware_meta,
            record,
            record_sig,
            debug_dir,
            dump_disasm_context,
            replay=replay,
            replay_sig=replay_sig,
        )
    event_match = "PASS" if replay.returncode == 0 else "FAIL"
    final_match = "PASS" if _sig(record_payload) == _sig(replay_payload) else "FAIL"
    property_match = "PASS" if str(record_payload.get("property_id")) == str(replay_payload.get("property_id")) else "FAIL"
    replay_status = "PASS" if replay.returncode == 0 and final_match == "PASS" and property_match == "PASS" else "FAIL"
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": str(seed),
        "rtl_record_status": "PASS",
        "capsule_export_status": "PASS" if capsule.exists() else "FAIL",
        "replay_status": replay_status,
        "property_id_record": str(record_payload.get("property_id", "NA")),
        "property_id_replay": str(replay_payload.get("property_id", "NA")),
        "commit_match": "PASS" if str(record_payload.get("commits_to_failure")) == str(replay_payload.get("commits_to_failure")) else "FAIL",
        "event_match": event_match,
        "final_signature_match": final_match,
        "capsule_bytes": str(record_payload.get("capsule_bytes", "NA")),
        "cycles_to_failure": str(record_payload.get("cycles_to_failure", "NA")),
        "commits_to_failure": str(record_payload.get("commits_to_failure", "NA")),
        "firmware_source": firmware_meta["firmware_source"],
        "firmware_sha256": firmware_meta["firmware_sha256"],
        "compiler_backed": firmware_meta["compiler_backed"],
        "notes": _clean(replay.stdout).splitlines()[-1] if replay.stdout.splitlines() else "record/replay complete",
    }


def _run_sim(
    mode: str,
    benchmark: str,
    variant: str,
    firmware: Path,
    capsule: Path,
    signature: Path,
    seed: int,
    max_cycles: int,
    debug_events: bool = False,
    debug_dir: Path = DEBUG_DIR,
    dump_mmio: bool = False,
    dump_property: bool = False,
    dump_pc: bool = False,
    dump_disasm_context: bool = False,
) -> subprocess.CompletedProcess[str]:
    command = [
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
        str(max_cycles),
    ]
    if debug_events:
        command.extend(["--debug-events", "--debug-dir", _rel(debug_dir)])
    elif dump_mmio or dump_property or dump_pc or dump_disasm_context:
        command.extend(["--debug-dir", _rel(debug_dir)])
    if dump_mmio:
        command.append("--dump-mmio")
    if dump_property:
        command.append("--dump-property")
    if dump_pc:
        command.append("--dump-pc")
    if dump_disasm_context:
        command.append("--dump-disasm-context")
    return subprocess.run(command, cwd=REPO_ROOT, env=_tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def _write_debug_analysis(benchmark: str, variant: str, seed: int, debug_dir: Path, replay_ran: bool) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    base = f"{benchmark}_{variant}_seed{seed}"
    record_path = debug_dir / f"{base}_record_events.json"
    replay_path = debug_dir / f"{base}_replay_events.json"
    if not replay_ran and not replay_path.exists():
        _write_json(replay_path, {"benchmark": benchmark, "variant": variant, "seed": seed, "mode": "replay", "events": [], "notes": "replay not run because record failed"})
    record = _read_json(record_path)
    replay = _read_json(replay_path)
    _write_event_diff(debug_dir / f"{base}_event_diff.txt", record, replay, replay_ran)
    _write_trace(debug_dir / f"{base}_property_trace.txt", record, replay, {10}, "property")
    _write_trace(debug_dir / f"{base}_mmio_trace.txt", record, replay, {5, 6}, "mmio")
    _write_trace(debug_dir / f"{base}_interrupt_trace.txt", record, replay, {7, 8}, "interrupt")


def _write_run_debug_context(
    benchmark: str,
    variant: str,
    seed: int,
    firmware: Path,
    firmware_meta: dict[str, str],
    record: subprocess.CompletedProcess[str],
    record_sig: Path,
    debug_dir: Path,
    dump_disasm_context: bool,
    replay: subprocess.CompletedProcess[str] | None,
    replay_sig: Path | None,
) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    base = f"{benchmark}_{variant}_seed{seed}"
    record_payload = _read_json(record_sig)
    replay_payload = _read_json(replay_sig) if replay_sig is not None else {}
    build_row = _firmware_build_row(benchmark, variant)
    expected_property = _expected_property(benchmark, variant)
    observed_property = record_payload.get("property_id", "NA")
    cycles = record_payload.get("cycles_to_failure", "NA")
    commits = record_payload.get("commits_to_failure", "NA")
    error_code = _extract_error_code(record.stdout)
    first_divergence = _first_divergence_note(expected_property, observed_property, record, replay, record_payload, replay_payload)

    log_lines = [
        f"benchmark={benchmark}",
        f"variant={variant}",
        f"seed={seed}",
        f"firmware_hex={_rel(firmware)}",
        f"firmware_sha256={firmware_meta.get('firmware_sha256', 'NA')}",
        f"firmware_source={firmware_meta.get('firmware_source', 'NA')}",
        f"compiler_backed={firmware_meta.get('compiler_backed', 'false')}",
        f"compiler={build_row.get('compiler', 'NA')}",
        f"compiler_version={build_row.get('compiler_version', 'NA')}",
        "compiler_flags=-march=rv32i -mabi=ilp32 -O2 -ffreestanding -fno-builtin -nostdlib -nostartfiles -Wall -Wextra",
        f"expected_property_id={expected_property}",
        f"observed_property_id={observed_property}",
        f"record_returncode={record.returncode}",
        f"replay_returncode={replay.returncode if replay is not None else 'NA'}",
        f"error_code={error_code}",
        f"cycles_reached={cycles}",
        f"commits_reached={commits}",
        "main_returned=unknown_from_current_symbol_set",
        "post_main_infinite_loop=inspect_pc_trace",
        "interrupt_events=inspect_property_trace_and_interrupt_trace",
        "mmio_accesses=inspect_mmio_trace",
        "property_checker_io=inspect_property_trace",
        "record_stdout=" + _clean(record.stdout).replace("\n", "\\n"),
    ]
    if replay is not None:
        log_lines.append("replay_stdout=" + _clean(replay.stdout).replace("\n", "\\n"))
    (debug_dir / f"{base}_record.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    if record_sig.exists():
        shutil.copy2(record_sig, debug_dir / f"{base}_signature.json")
    (debug_dir / f"{base}_first_divergence.txt").write_text(first_divergence + "\n", encoding="utf-8")
    if dump_disasm_context:
        _write_disasm_context(debug_dir / f"{base}_firmware_disasm.txt", firmware, build_row)


def _write_disasm_context(path: Path, firmware: Path, build_row: dict[str, str]) -> None:
    elf_value = build_row.get("elf_path", "")
    elf = REPO_ROOT / elf_value if elf_value and elf_value != "NA" else Path()
    elf_available = bool(elf_value and elf_value != "NA" and elf.exists() and elf.is_file())
    compiler = build_row.get("compiler", "")
    objdump_names = []
    if compiler and compiler != "NA" and compiler.endswith("gcc"):
        objdump_names.append(compiler[:-3] + "objdump")
    objdump_names.extend(["riscv64-unknown-elf-objdump", "riscv-none-elf-objdump", "riscv32-unknown-elf-objdump"])
    objdump = next((tool for name in objdump_names if (tool := shutil.which(name))), None)
    lines = [
        f"firmware_hex={_rel(firmware)}",
        f"firmware_elf={_rel(elf) if elf_available else 'NA'}",
    ]
    if objdump and elf_available:
        completed = subprocess.run([objdump, "-d", str(elf)], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        lines.append(f"objdump={Path(objdump).name}")
        lines.append(_clean(completed.stdout))
    else:
        lines.append("objdump=NA")
        lines.append("# HEX words")
        if firmware.exists():
            lines.extend(firmware.read_text(encoding="utf-8", errors="replace").splitlines())
        else:
            lines.append("firmware HEX missing")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _firmware_build_row(benchmark: str, variant: str) -> dict[str, str]:
    for row in _firmware_build_rows():
        if row.get("benchmark") == benchmark and row.get("variant") == variant:
            return row
    return {}


def _expected_property(benchmark: str, variant: str) -> int:
    if variant in {"fixed", "no_failure_edge"}:
        return 0
    return EXPECTED_PROPERTIES.get(benchmark, 0)


def _extract_error_code(output: str) -> str:
    for line in _clean(output).splitlines():
        if line.startswith("error_code="):
            return line.split("=", 1)[1].strip()
    return "NA"


def _first_divergence_note(
    expected_property: int,
    observed_property: object,
    record: subprocess.CompletedProcess[str],
    replay: subprocess.CompletedProcess[str] | None,
    record_payload: dict[str, object],
    replay_payload: dict[str, object],
) -> str:
    lines = [
        f"expected_property_id={expected_property}",
        f"observed_record_property_id={observed_property}",
        f"record_returncode={record.returncode}",
    ]
    if record.returncode != 0:
        lines.append(f"first_divergence=record_failed_before_replay:{_extract_error_code(record.stdout)}")
        lines.append("likely_root_cause=firmware execution did not produce the expected property event before max_cycles")
        return "\n".join(lines)
    if replay is None:
        lines.append("first_divergence=replay_not_run")
        return "\n".join(lines)
    lines.append(f"replay_returncode={replay.returncode}")
    if str(record_payload.get("property_id")) != str(replay_payload.get("property_id")):
        lines.append("first_divergence=property_id_mismatch")
    elif str(record_payload.get("property_signature")) != str(replay_payload.get("property_signature")):
        lines.append("first_divergence=property_signature_mismatch")
    elif replay.returncode != 0:
        lines.append(f"first_divergence=replay_failed:{_extract_error_code(replay.stdout)}")
    else:
        lines.append("first_divergence=none")
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_event_diff(path: Path, record: dict[str, object], replay: dict[str, object], replay_ran: bool) -> None:
    record_events = _events(record)
    replay_events = _events(replay)
    lines = [
        f"record_property_id={record.get('property_id', 'NA')}",
        f"replay_property_id={replay.get('property_id', 'NA')}",
        f"record_property_signature={record.get('property_signature', 'NA')}",
        f"replay_property_signature={replay.get('property_signature', 'NA')}",
        f"record_event_count={len(record_events)}",
        f"replay_event_count={len(replay_events)}",
    ]
    if not replay_ran:
        lines.append("first_divergence=replay_not_run_record_failed")
    else:
        limit = min(len(record_events), len(replay_events))
        first = None
        for index in range(limit):
            if record_events[index].get("packet") != replay_events[index].get("packet"):
                first = index
                break
        if first is None and len(record_events) != len(replay_events):
            first = limit
        if first is None:
            lines.append("first_divergence=none")
        else:
            lines.append(f"first_divergence_event_index={first}")
            lines.append("record_event=" + json.dumps(record_events[first] if first < len(record_events) else None, sort_keys=True))
            lines.append("replay_event=" + json.dumps(replay_events[first] if first < len(replay_events) else None, sort_keys=True))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_trace(path: Path, record: dict[str, object], replay: dict[str, object], event_types: set[int], label: str) -> None:
    lines = [f"# {label} trace"]
    for mode, payload in (("record", record), ("replay", replay)):
        lines.append(f"[{mode}]")
        found = False
        for event in _events(payload):
            if int(event.get("event_type", -1)) not in event_types:
                continue
            found = True
            lines.append(json.dumps(event, sort_keys=True))
        if not found:
            lines.append("no matching events")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _events(payload: dict[str, object]) -> list[dict[str, object]]:
    events = payload.get("events", [])
    if isinstance(events, list):
        return [event for event in events if isinstance(event, dict)]
    return []


def _blocked_row(benchmark: str, variant: str, seed: int, notes: str) -> dict[str, str]:
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": str(seed),
        "rtl_record_status": "BLOCKED",
        "capsule_export_status": "BLOCKED",
        "replay_status": "BLOCKED",
        "property_id_record": "NA",
        "property_id_replay": "NA",
        "commit_match": "NA",
        "event_match": "NA",
        "final_signature_match": "NA",
        "capsule_bytes": "NA",
        "cycles_to_failure": "NA",
        "commits_to_failure": "NA",
        "firmware_source": "NA",
        "firmware_sha256": "NA",
        "compiler_backed": "false",
        "notes": notes,
    }


def _failed_row(
    benchmark: str,
    variant: str,
    seed: int,
    record_status: str,
    replay_status: str,
    notes: str,
    firmware_meta: dict[str, str] | None = None,
    record_sig: Path | None = None,
    capsule: Path | None = None,
) -> dict[str, str]:
    firmware_meta = firmware_meta or _empty_firmware_metadata()
    record_payload = _read_json(record_sig) if record_sig is not None else {}
    return {
        "benchmark": benchmark,
        "variant": variant,
        "seed": str(seed),
        "rtl_record_status": record_status,
        "capsule_export_status": "FAIL",
        "replay_status": replay_status,
        "property_id_record": str(record_payload.get("property_id", "NA")),
        "property_id_replay": "NA",
        "commit_match": "NA",
        "event_match": "NA",
        "final_signature_match": "NA",
        "capsule_bytes": str(record_payload.get("capsule_bytes", "NA")),
        "cycles_to_failure": str(record_payload.get("cycles_to_failure", "NA")),
        "commits_to_failure": str(record_payload.get("commits_to_failure", "NA")),
        "firmware_source": firmware_meta.get("firmware_source", "NA"),
        "firmware_sha256": firmware_meta.get("firmware_sha256", "NA"),
        "compiler_backed": firmware_meta.get("compiler_backed", "false"),
        "notes": _clean(notes).splitlines()[-1] if _clean(notes).splitlines() else "RTL run failed",
    }


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _sig(payload: dict[str, object]) -> tuple[object, object]:
    return payload.get("property_id"), payload.get("property_signature")


def _write_rows(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_firmware_source_comparison(rows: list[dict[str, str]]) -> None:
    FIRMWARE_COMPARISON_CSV.parent.mkdir(parents=True, exist_ok=True)
    comparison_rows = [_comparison_row(row) for row in rows]
    with FIRMWARE_COMPARISON_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPARISON_FIELDS)
        writer.writeheader()
        writer.writerows(comparison_rows)


def _comparison_row(row: dict[str, str]) -> dict[str, str]:
    status = _case_status(row)
    compiler_property = row.get("property_id_record", "NA")
    compiler_cycles = row.get("cycles_to_failure", "NA")
    compiler_commits = row.get("commits_to_failure", "NA")
    compiler_events = _event_count_from_row(row)
    expected_property = str(_expected_property(row["benchmark"], row["variant"]))
    first_divergence = "NA"
    likely_root_cause = "NA"
    if status != "PASS":
        first_divergence = row.get("notes", "compiler-backed row did not pass")
        likely_root_cause = _likely_root_cause(row)
    if row.get("compiler_backed") == "true":
        return {
            "benchmark": row["benchmark"],
            "variant": row["variant"],
            "seed": row["seed"],
            "fallback_status": "NOT_RUN",
            "compiler_status": status,
            "fallback_property_id": expected_property if row["variant"] not in {"fixed", "no_failure_edge"} else "0",
            "compiler_property_id": compiler_property,
            "fallback_cycles_to_failure": "NOT_RUN",
            "compiler_cycles_to_failure": compiler_cycles,
            "fallback_commits_to_failure": "NOT_RUN",
            "compiler_commits_to_failure": compiler_commits,
            "fallback_event_count": "NOT_RUN",
            "compiler_event_count": compiler_events,
            "same_property": "PASS" if compiler_property == expected_property else "FAIL",
            "same_event_count": "NA",
            "first_divergence": first_divergence,
            "likely_root_cause": likely_root_cause,
            "notes": "compiler-backed firmware row; fallback comparison not run in this invocation",
        }
    return {
        "benchmark": row["benchmark"],
        "variant": row["variant"],
        "seed": row["seed"],
        "fallback_status": status if row.get("firmware_source") == "fallback_hex" else "NA",
        "compiler_status": "BLOCKED",
        "fallback_property_id": row.get("property_id_record", "NA"),
        "compiler_property_id": "NA",
        "fallback_cycles_to_failure": row.get("cycles_to_failure", "NA"),
        "compiler_cycles_to_failure": "NA",
        "fallback_commits_to_failure": row.get("commits_to_failure", "NA"),
        "compiler_commits_to_failure": "NA",
        "fallback_event_count": _event_count_from_row(row),
        "compiler_event_count": "NA",
        "same_property": "NA",
        "same_event_count": "NA",
        "first_divergence": "compiler-backed firmware unavailable",
        "likely_root_cause": "compiler-backed firmware unavailable",
        "notes": "run used fallback HEX because compiler-backed firmware was unavailable and fallback was explicitly allowed",
    }


def _event_count_from_row(row: dict[str, str]) -> str:
    value = row.get("capsule_bytes", "NA")
    try:
        return str(int(value) // 21)
    except (TypeError, ValueError):
        return "NA"


def _likely_root_cause(row: dict[str, str]) -> str:
    notes = row.get("notes", "")
    if "NO_EXPECTED_FAILURE" in notes or row.get("property_id_record") in {"0", "NA"}:
        return "expected property did not fire during compiler-backed record run"
    if row.get("replay_status") == "FAIL":
        return "record/replay divergence"
    if row.get("final_signature_match") == "FAIL":
        return "final signature mismatch"
    return "row did not satisfy full replay pass criteria"


def _case_status(row: dict[str, str]) -> str:
    if (
        row.get("rtl_record_status") == "PASS"
        and row.get("replay_status") == "PASS"
        and row.get("final_signature_match") == "PASS"
    ):
        return "PASS"
    if "BLOCKED" in {row.get("rtl_record_status"), row.get("replay_status")}:
        return "BLOCKED"
    return "FAIL"


def _select_firmware(benchmark: str, variant: str, allow_fallback: bool) -> tuple[Path | None, dict[str, str], str | None]:
    rows = [row for row in _firmware_build_rows() if row.get("benchmark") == benchmark and row.get("variant") == variant]
    compiler_rows = [row for row in rows if row.get("build_status") == "PASS" and row.get("firmware_source") == "compiler_c"]
    if compiler_rows:
        firmware = _row_hex_path(compiler_rows[0], benchmark, variant)
        if firmware.exists():
            return firmware, _metadata_from_row(compiler_rows[0], firmware, True), None
        return None, _empty_firmware_metadata(), f"compiler-backed firmware row exists but HEX is missing: {_rel(firmware)}"

    fallback_rows = [row for row in rows if row.get("build_status") == "FALLBACK" and row.get("firmware_source") == "fallback_hex"]
    if fallback_rows:
        firmware = _row_hex_path(fallback_rows[0], benchmark, variant)
        if not firmware.exists() and variant == "no_failure_edge":
            firmware = REPO_ROOT / "firmware/build" / benchmark / "failing.hex"
        if allow_fallback and firmware.exists():
            return firmware, _metadata_from_row(fallback_rows[0], firmware, False), None
        if firmware.exists():
            return None, _empty_firmware_metadata(), "fallback HEX available but fallback was not explicitly allowed; compiler-backed firmware unavailable"
        return None, _empty_firmware_metadata(), f"fallback firmware row exists but HEX is missing: {_rel(firmware)}"

    failed_rows = [row for row in rows if row.get("build_status") == "FAIL"]
    if failed_rows:
        return None, _empty_firmware_metadata(), "compiler-backed firmware build failed: " + failed_rows[0].get("notes", "see firmware_build.csv")

    firmware = REPO_ROOT / "firmware/build" / benchmark / f"{variant}.hex"
    if allow_fallback and firmware.exists():
        return firmware, {
            "firmware_source": "untracked_fallback_hex",
            "firmware_sha256": _sha256(firmware),
            "compiler_backed": "false",
        }, None
    return None, _empty_firmware_metadata(), f"missing compiler-backed firmware metadata for {benchmark}/{variant}"


def _row_hex_path(row: dict[str, str], benchmark: str, variant: str) -> Path:
    hex_path = row.get("hex_path", "")
    if hex_path and hex_path != "NA":
        return REPO_ROOT / hex_path
    return REPO_ROOT / "firmware/build" / benchmark / f"{variant}.hex"


def _metadata_from_row(row: dict[str, str], firmware: Path, compiler_backed: bool) -> dict[str, str]:
    return {
        "firmware_source": row.get("firmware_source") or ("compiler_c" if compiler_backed else "fallback_hex"),
        "firmware_sha256": row.get("sha256_hex") or _sha256(firmware),
        "compiler_backed": "true" if compiler_backed else "false",
    }


def _empty_firmware_metadata() -> dict[str, str]:
    return {
        "firmware_source": "NA",
        "firmware_sha256": "NA",
        "compiler_backed": "false",
    }


def _firmware_metadata(benchmark: str, variant: str, firmware: Path) -> dict[str, str]:
    for row in _firmware_build_rows():
        if row.get("benchmark") != benchmark or row.get("variant") != variant:
            continue
        source = row.get("firmware_source") or ("compiler_c" if row.get("build_status") == "PASS" else "fallback_hex" if row.get("build_status") == "FALLBACK" else row.get("build_status", "unknown").lower())
        digest = row.get("sha256_hex") or _sha256(firmware)
        return {
            "firmware_source": source,
            "firmware_sha256": digest,
            "compiler_backed": "true" if row.get("build_status") == "PASS" else "false",
        }
    return {
        "firmware_source": "untracked_hex",
        "firmware_sha256": _sha256(firmware) if firmware.exists() else "NA",
        "compiler_backed": "false",
    }


def _firmware_build_rows() -> list[dict[str, str]]:
    if not FIRMWARE_BUILD_CSV.exists():
        return []
    with FIRMWARE_BUILD_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clean(text: str) -> str:
    cleaned = text
    replacements = [str(REPO_ROOT), str(REPO_ROOT).replace("\\", "/")]
    original_root = os.environ.get("REPLAYCAPSULE_ORIGINAL_REPO_ROOT")
    if original_root:
        replacements.extend([original_root, original_root.replace("\\", "/")])
    home = str(Path.home())
    replacements.extend([home, home.replace("\\", "/")])
    for value in replacements:
        if value:
            cleaned = cleaned.replace(value, ".")
    cleaned = re.sub(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+", ".", cleaned)
    return cleaned


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _strict_ci() -> bool:
    return _truthy_env("REPLAYCAPSULE_STRICT_CI") or _truthy_env("CI")


def _sanitize_file(path: Path) -> None:
    if path.exists():
        path.write_text(_clean(path.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")


def _find_make() -> str | None:
    for path in (LOCAL_WINLIBS_BIN / "make.exe", LOCAL_WINLIBS_BIN / "mingw32-make.exe"):
        if path.exists():
            return str(path)
    return shutil.which("make") or shutil.which("gmake") or shutil.which("mingw32-make")


def _sim_needs_rebuild() -> bool:
    sim = _sim_path()
    if not sim.exists():
        return True
    sim_mtime = sim.stat().st_mtime
    for rel_path in VERILATOR_DEPENDENCY_PATHS:
        path = REPO_ROOT / rel_path
        if path.exists() and path.stat().st_mtime > sim_mtime:
            return True
    return False


def _find_cxx() -> str | None:
    for path in (LOCAL_WINLIBS_BIN / "g++.exe", LOCAL_WINLIBS_BIN / "c++.exe", LOCAL_WINLIBS_BIN / "clang++.exe"):
        if path.exists():
            return str(path)
    return shutil.which("g++") or shutil.which("c++") or shutil.which("clang++")


def _find_verilator() -> str | None:
    for path in _existing_oss_paths("bin/verilator_bin.exe", "bin/verilator.exe", "bin/verilator"):
        if path.exists():
            return str(path)
    return shutil.which("verilator")


def _tool_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in ("VERILATOR_ROOT", "VERILATOR_BIN", "OSS_CAD_SUITE"):
        env.pop(key, None)
    parts = []
    if LOCAL_WINLIBS_BIN.exists():
        parts.append(str(LOCAL_WINLIBS_BIN))
    if OSS_CAD_SUITE.exists():
        for path in (OSS_CAD_SUITE / "bin", OSS_CAD_SUITE / "lib"):
            if path.exists():
                parts.append(str(path))
        verilator_root = OSS_CAD_SUITE / "share" / "verilator"
        if verilator_root.exists():
            env["VERILATOR_ROOT"] = verilator_root.as_posix()
    git_usr_bin = _git_usr_bin()
    if git_usr_bin is not None:
        parts.append(str(git_usr_bin))
    parts.append(env.get("PATH", ""))
    env["PATH"] = os.pathsep.join(parts)
    return env


def _existing_oss_paths(*relative_paths: str) -> tuple[Path, ...]:
    if not OSS_CAD_SUITE.exists():
        return tuple()
    return tuple(OSS_CAD_SUITE / relative for relative in relative_paths)


def _git_usr_bin() -> Path | None:
    git = shutil.which("git")
    if not git:
        return None
    path = Path(git)
    for parent in path.parents:
        candidate = parent / "usr/bin"
        if (candidate / "uname.exe").exists():
            return candidate
    return None


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
