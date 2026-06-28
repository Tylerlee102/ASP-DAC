#!/usr/bin/env python3
"""Compile and run the ReplayCapsule-RV v2 replay-consume RTL tests."""

from __future__ import annotations

import csv
import ctypes
import os
import shutil
import subprocess
from pathlib import Path

from topconf_eval_common import REPO_ROOT, rel, write_csv


OUT_CSV = REPO_ROOT / "results/processed/replay_consumer_tests.csv"
RAW_DIR = REPO_ROOT / "results/raw/replay_consumer"
FIELDS = [
    "test_name",
    "capsule_source",
    "expected_result",
    "actual_result",
    "passed",
    "error_code",
    "notes",
]


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    iverilog = _find_tool("iverilog.exe") or _find_tool("iverilog")
    vvp = _find_tool("vvp.exe") or _find_tool("vvp")
    rows: list[dict[str, object]]
    if not iverilog or not vvp:
        rows = [
            {
                "test_name": "replay_consumer_toolchain",
                "capsule_source": "tb/replay_consumer/tb_rcv2_replay_consumer.sv",
                "expected_result": "PASS",
                "actual_result": "BLOCKED",
                "passed": "false",
                "error_code": "NA",
                "notes": "missing iverilog or vvp; RTL test not executed",
            }
        ]
        write_csv(OUT_CSV, FIELDS, rows)
        print(f"WROTE {rel(OUT_CSV)}")
        return 1

    simv = RAW_DIR / "tb_rcv2_replay_consumer.vvp"
    compile_log = RAW_DIR / "compile.log"
    run_log = RAW_DIR / "run.log"
    sources = [
        "rtl/replaycapsule_v2/rcv2_mmio_replay_driver.sv",
        "rtl/replaycapsule_v2/rcv2_irq_replay_driver.sv",
        "rtl/replaycapsule_v2/rcv2_replay_consumer.sv",
        "tb/replay_consumer/tb_rcv2_replay_consumer.sv",
    ]
    compile_cmd = [
        iverilog,
        "-g2012",
        "-Irtl",
        "-Irtl/replaycapsule_v2",
        "-o",
        rel(simv),
        *sources,
    ]
    c = subprocess.run(compile_cmd, cwd=REPO_ROOT, env=_tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    compile_log.write_text(c.stdout, encoding="utf-8")
    if c.returncode != 0:
        rows = [_blocked_row("replay_consumer_compile", "COMPILE_FAIL", rel(compile_log))]
        write_csv(OUT_CSV, FIELDS, rows)
        print(f"WROTE {rel(OUT_CSV)}")
        return c.returncode

    r = subprocess.run([vvp, rel(simv)], cwd=REPO_ROOT, env=_tool_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    run_log.write_text(r.stdout, encoding="utf-8")
    rows = _parse_results(r.stdout)
    if not rows:
      rows = [_blocked_row("replay_consumer_run", "NO_RESULT_LINES", rel(run_log))]
    write_csv(OUT_CSV, FIELDS, rows)
    print(f"WROTE {rel(OUT_CSV)}")
    passed = sum(1 for row in rows if row["passed"] == "true")
    print(f"REPLAY_CONSUMER_TESTS passed={passed} total={len(rows)}")
    return 0 if r.returncode == 0 and passed == len(rows) else 1


def _parse_results(text: str) -> list[dict[str, object]]:
    rows = []
    for line in text.splitlines():
        if not line.startswith("RESULT,"):
            continue
        parts = next(csv.reader([line]))
        _, test_name, expected, actual, passed, error_code = parts[:6]
        rows.append(
            {
                "test_name": test_name,
                "capsule_source": "tb/replay_consumer/tb_rcv2_replay_consumer.sv",
                "expected_result": expected,
                "actual_result": actual,
                "passed": "true" if passed == "1" else "false",
                "error_code": error_code,
                "notes": "RTL testbench execution",
            }
        )
    return rows


def _blocked_row(test_name: str, actual: str, log_path: str) -> dict[str, object]:
    return {
        "test_name": test_name,
        "capsule_source": "tb/replay_consumer/tb_rcv2_replay_consumer.sv",
        "expected_result": "PASS",
        "actual_result": actual,
        "passed": "false",
        "error_code": "NA",
        "notes": f"see {log_path}",
    }


def _find_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return str(_short_path(Path(found)))
    candidates = [
        REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite/bin" / name,
        REPO_ROOT / ".tools/winlibs/mingw64/bin" / name,
    ]
    for candidate in candidates:
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


if __name__ == "__main__":
    raise SystemExit(main())
