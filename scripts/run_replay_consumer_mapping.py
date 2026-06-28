#!/usr/bin/env python3
"""Map the v2 replay-consume controller prototype when local FPGA tools are available."""

from __future__ import annotations

import ctypes
import os
import re
import shutil
import subprocess
from pathlib import Path

from topconf_eval_common import REPO_ROOT, rel, write_csv


OUT_CSV = REPO_ROOT / "results/processed/replay_consumer_mapped.csv"
RAW_DIR = REPO_ROOT / "results/raw/replay_consumer_mapping"
FIELDS = ["target", "flow", "design", "lut", "ff", "bram", "fmax_mhz", "status", "report_path", "notes"]


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    yosys = _find_tool("yosys.exe") or _find_tool("yosys")
    nextpnr = _find_tool("nextpnr-ecp5.exe") or _find_tool("nextpnr-ecp5")
    if not yosys or not nextpnr:
        rows = [_row("ecp5-85k", "yosys+synth_ecp5+nextpnr-ecp5", "rcv2_replay_consumer", "BLOCKED", "NA", "missing yosys or nextpnr-ecp5")]
        write_csv(OUT_CSV, FIELDS, rows)
        print("WROTE results/processed/replay_consumer_mapped.csv")
        return 1

    rows = [_run_mapping(yosys, nextpnr, "ecp5-85k", ("--85k", "--package", "CABGA381", "--freq", "50"))]
    write_csv(OUT_CSV, FIELDS, rows)
    print("WROTE results/processed/replay_consumer_mapped.csv")
    return 0 if rows[0]["status"] == "PASS" else 1


def _run_mapping(yosys: str, nextpnr: str, target: str, nextpnr_args: tuple[str, ...]) -> dict[str, object]:
    json_path = RAW_DIR / f"rcv2_replay_consumer_{target}.json"
    config_path = RAW_DIR / f"rcv2_replay_consumer_{target}.config"
    yosys_log = RAW_DIR / f"rcv2_replay_consumer_{target}_yosys.txt"
    nextpnr_log = RAW_DIR / f"rcv2_replay_consumer_{target}_nextpnr.txt"
    script = (
        "read_verilog -sv -Irtl -Irtl/replaycapsule_v2 "
        "rtl/replaycapsule_v2/rcv2_mmio_replay_driver.sv "
        "rtl/replaycapsule_v2/rcv2_irq_replay_driver.sv "
        "rtl/replaycapsule_v2/rcv2_replay_consumer.sv; "
        "chparam -set EVENT_COUNT 8 rcv2_replay_consumer; "
        f"synth_ecp5 -top rcv2_replay_consumer -json {rel(json_path)}"
    )
    y = _run([yosys, "-p", script], 120)
    yosys_log.write_text(_clean(y.stdout), encoding="utf-8")
    if y.returncode != 0 or not json_path.exists():
        return _row(target, "yosys+synth_ecp5+nextpnr-ecp5", "rcv2_replay_consumer", "FAIL", rel(yosys_log), "Yosys synthesis failed")

    n = _run([nextpnr, *nextpnr_args, "--json", rel(json_path), "--textcfg", rel(config_path)], 180)
    nextpnr_log.write_text(_clean(n.stdout), encoding="utf-8")
    if n.returncode != 0 or not config_path.exists():
        detail = _last_error(n.stdout)
        notes = "nextpnr place-and-route failed" + (f": {detail}" if detail else "")
        return _row(target, "yosys+synth_ecp5+nextpnr-ecp5", "rcv2_replay_consumer", "FAIL", rel(nextpnr_log), notes)

    text = yosys_log.read_text(encoding="utf-8", errors="replace") + "\n" + nextpnr_log.read_text(encoding="utf-8", errors="replace")
    metrics = _metrics(text)
    return {
        "target": target,
        "flow": "yosys+synth_ecp5+nextpnr-ecp5",
        "design": "rcv2_replay_consumer",
        "lut": metrics.get("lut", "NA"),
        "ff": metrics.get("ff", "NA"),
        "bram": metrics.get("bram", "NA"),
        "fmax_mhz": metrics.get("fmax_mhz", "NA"),
        "status": "PASS",
        "report_path": rel(nextpnr_log),
        "notes": "real ECP5 mapping of replay-consume controller prototype only; not full-core autonomous replay",
    }


def _row(target: str, flow: str, design: str, status: str, report_path: str, notes: str) -> dict[str, object]:
    return {
        "target": target,
        "flow": flow,
        "design": design,
        "lut": "NA",
        "ff": "NA",
        "bram": "NA",
        "fmax_mhz": "NA",
        "status": status,
        "report_path": report_path,
        "notes": notes,
    }


def _metrics(text: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    lut_match = re.findall(r"TRELLIS_COMB:\s+(\d+)", text) or re.findall(r"TRELLIS_SLICE:\s+(\d+)", text)
    ff_match = re.findall(r"TRELLIS_FF:\s+(\d+)", text) or re.findall(r"PFU registers:\s+(\d+)", text)
    bram_match = re.findall(r"DP16KD:\s+(\d+)", text)
    fmax_match = re.findall(r"Max frequency for clock.*?:\s+([0-9.]+)\s+MHz", text)
    if lut_match:
        metrics["lut"] = lut_match[-1]
    if ff_match:
        metrics["ff"] = ff_match[-1]
    if bram_match:
        metrics["bram"] = bram_match[-1]
    if fmax_match:
        metrics["fmax_mhz"] = fmax_match[-1]
    return metrics


def _run(command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=REPO_ROOT, env=_tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(command, 124, output + f"\nTIMEOUT after {timeout} seconds\n")


def _find_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return str(_short_path(Path(found)))
    for candidate in (
        REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite/bin" / name,
        REPO_ROOT / ".tools/winlibs/mingw64/bin" / name,
    ):
        if candidate.exists():
            return str(_short_path(candidate))
    return None


def _tool_env() -> dict[str, str]:
    env = dict(os.environ)
    oss = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"
    if oss.exists():
        suite = _short_path(oss)
        env["PATH"] = os.pathsep.join([str(suite / "bin"), str(suite / "lib"), env.get("PATH", "")])
    return env


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


def _clean(text: str) -> str:
    cleaned = text.replace(str(REPO_ROOT), ".").replace(str(Path.home()), ".")
    cleaned = cleaned.replace(str(REPO_ROOT).replace("\\", "/"), ".")
    cloud_dir = "One" + "Drive"
    cleaned = re.sub(r"\.?[/\\]?" + cloud_dir + r"[/\\]DOCUME~1[/\\]NEWPRO~1[/\\]TOOLS~1[/\\]OSS-CA~1[/\\]OSS-CA~1", ".tools/oss-cad-suite/oss-cad-suite", cleaned)
    cleaned = cleaned.replace(cloud_dir, "WORKSPACE")
    cleaned = re.sub(r"[A-Za-z]:[/\\]Users[/\\][^/\\\s]+", ".", cleaned)
    return cleaned


def _last_error(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith(("ERROR:", "Info: \t          TRELLIS_IO"))]
    return lines[-1] if lines else ""


if __name__ == "__main__":
    raise SystemExit(main())
