#!/usr/bin/env python3
"""Compile a tiny SystemVerilog design with Verilator and record the result."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/verilator_compile_smoke.csv"
FIELDNAMES = ["tool", "status", "verilator_path", "version", "output", "notes"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verilator", default="verilator")
    args = parser.parse_args()

    verilator = shutil.which(args.verilator) if not Path(args.verilator).exists() else args.verilator
    if not verilator:
        _write_row(args.verilator, "FAIL", "NA", "NA", "NA", "Verilator command not found")
        return 1

    env = _clean_env()
    version = _version(verilator, env)
    with tempfile.TemporaryDirectory(prefix="replaycapsule-verilator-smoke-") as tmp:
        tmp_path = Path(tmp)
        sv = tmp_path / "tiny_smoke.sv"
        sv.write_text(
            "\n".join(
                [
                    "module tiny_smoke(input logic clk, output logic seen);",
                    "  always_ff @(posedge clk) begin",
                    "    seen <= 1'b1;",
                    "  end",
                    "endmodule",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        cpp = tmp_path / "main.cpp"
        cpp.write_text(
            "\n".join(
                [
                    '#include "Vtiny_smoke.h"',
                    "#include \"verilated.h\"",
                    "int main(int argc, char **argv) {",
                    "  Verilated::commandArgs(argc, argv);",
                    "  Vtiny_smoke top;",
                    "  top.clk = 0;",
                    "  top.eval();",
                    "  top.clk = 1;",
                    "  top.eval();",
                    "  return top.seen ? 0 : 1;",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        obj_dir = tmp_path / "obj_dir"
        exe_name = "tiny_smoke.exe" if os.name == "nt" else "tiny_smoke"
        command = [
            verilator,
            "--cc",
            "--exe",
            "--build",
            "--sv",
            "--top-module",
            "tiny_smoke",
            "--Mdir",
            str(obj_dir),
            "-o",
            exe_name,
            str(sv),
            str(cpp),
        ]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=120,
        )
        log = REPO_ROOT / "results/raw/verilator/compile_smoke.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(_clean(completed.stdout), encoding="utf-8")
        exe = obj_dir / exe_name
        if completed.returncode == 0 and exe.exists():
            _write_row("verilator", "PASS", _clean(str(Path(verilator).resolve())), version, _rel(log), "tiny SystemVerilog compile/build succeeded")
            return 0
        note = _last_line(completed.stdout) or "tiny SystemVerilog compile/build failed"
        _write_row("verilator", "FAIL", _clean(str(Path(verilator).resolve())), version, _rel(log), _clean(note))
        return 1


def _clean_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in ("VERILATOR_ROOT", "VERILATOR_BIN", "OSS_CAD_SUITE"):
        env.pop(key, None)
    return env


def _version(verilator: str, env: dict[str, str]) -> str:
    completed = subprocess.run(
        [verilator, "--version"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=30,
    )
    return _clean(_last_line(completed.stdout) or "version probe produced no output")


def _write_row(tool: str, status: str, path: str, version: str, output: str, notes: str) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(
            {
                "tool": tool,
                "status": status,
                "verilator_path": path,
                "version": version,
                "output": output,
                "notes": notes,
            }
        )
    print(f"{status}: {tool} - {notes}")
    print(f"WROTE {_rel(OUT_CSV)}")


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def _clean(text: str) -> str:
    cleaned = text.replace(str(REPO_ROOT), ".").replace(str(REPO_ROOT).replace("\\", "/"), ".")
    home = str(Path.home())
    return cleaned.replace(home, ".").replace(home.replace("\\", "/"), ".")


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
