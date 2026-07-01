#!/usr/bin/env python3
"""Probe the vendored interrupt-capable second-core candidate."""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR = REPO_ROOT / "third_party" / "hazard3"
HDL = VENDOR / "hdl"
RAW_DIR = REPO_ROOT / "results" / "raw" / "second_core_irq_candidate"
OUT_CSV = REPO_ROOT / "results" / "processed" / "second_core_irq_candidate.csv"
OUT_MD = REPO_ROOT / "docs" / "second_core_irq_candidate.md"
EXPECTED_COMMIT = "8af992930f71a69b0e06c38734c1094f41a05ca0"
FIELDS = ["check", "status", "evidence", "notes"]


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    lint_status, lint_note, lint_log = _run_lint()
    rows = _build_rows(lint_status, lint_note, lint_log)
    _write_csv(rows)
    _write_doc(rows)
    bad = [row for row in rows if row["status"] == "FAIL"]
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OUT_MD)}")
    print(f"SECOND_CORE_IRQ_CANDIDATE rows={len(rows)} bad={len(bad)}")
    return 1 if bad else 0


def _build_rows(lint_status: str, lint_note: str, lint_log: Path) -> list[dict[str, str]]:
    readme = _read(VENDOR / "Readme.md")
    license_text = _read(VENDOR / "LICENSE")
    vendored = _read(VENDOR / "VENDORED.md")
    filelist = _read(HDL / "hazard3.f")
    top = _read(HDL / "hazard3_cpu_1port.v")
    config = _read(HDL / "hazard3_config.vh")
    csr = _read(HDL / "hazard3_csr.v")
    decode = _read(HDL / "hazard3_decode.v")
    irq_ctrl = _read(HDL / "hazard3_irq_ctrl.v")
    hdl_files = sorted(HDL.rglob("*.v")) + sorted(HDL.rglob("*.vh"))
    filelist_sources = [line.split(maxsplit=1)[1] for line in filelist.splitlines() if line.startswith("file ")]
    return [
        _row(
            "hazard3_source_present",
            "PASS" if (HDL / "hazard3_cpu_1port.v").exists() and (HDL / "hazard3_core.v").exists() else "FAIL",
            "third_party/hazard3/hdl",
            f"Vendored Hazard3 HDL is present with {len(hdl_files)} Verilog/include files.",
        ),
        _row(
            "hazard3_filelist_present",
            "PASS" if len(filelist_sources) >= 18 and "hazard3_irq_ctrl.v" in filelist else "FAIL",
            "third_party/hazard3/hdl/hazard3.f",
            f"Filelist names {len(filelist_sources)} core source files including the IRQ controller.",
        ),
        _row(
            "hazard3_license_tracked",
            "PASS" if "Apache License" in license_text and "Version 2.0" in license_text else "FAIL",
            "third_party/hazard3/LICENSE",
            "Apache-2.0 license is vendored with the candidate core.",
        ),
        _row(
            "hazard3_source_pinned",
            "PASS" if EXPECTED_COMMIT in vendored else "FAIL",
            "third_party/hazard3/VENDORED.md",
            f"Vendored metadata pins upstream commit {EXPECTED_COMMIT}.",
        ),
        _row(
            "hazard3_declares_rv32i",
            "PASS" if "RV32I" in readme and "Zicsr" in readme else "FAIL",
            "third_party/hazard3/Readme.md",
            "README declares RV32I/RV32E scope and CSR support.",
        ),
        _row(
            "hazard3_external_irq_ports",
            "PASS" if "input wire [NUM_IRQS-1:0] irq" in top and "soft_irq" in top and "timer_irq" in top else "FAIL",
            "third_party/hazard3/hdl/hazard3_cpu_1port.v",
            "Top-level candidate exposes external, software, and timer interrupt inputs.",
        ),
        _row(
            "hazard3_irq_configurable",
            "PASS" if "parameter NUM_IRQS" in config and "MTVEC_INIT" in config and "MTVEC_WMASK" in config else "FAIL",
            "third_party/hazard3/hdl/hazard3_config.vh",
            "Candidate has configurable external IRQ count and trap-vector reset/writability parameters.",
        ),
        _row(
            "hazard3_csr_interrupt_support",
            "PASS" if all(token in csr for token in ("MTVEC", "MSTATUS", "MIE", "MIP", "MEPC", "MCAUSE")) else "FAIL",
            "third_party/hazard3/hdl/hazard3_csr.v",
            "CSR block implements standard machine trap/interrupt CSRs needed for true ISR replay work.",
        ),
        _row(
            "hazard3_mret_decode_present",
            "PASS" if "MRET" in decode or "mret" in readme.lower() else "FAIL",
            "third_party/hazard3/hdl/hazard3_decode.v",
            "Candidate decodes or documents MRET, enabling real interrupt-return firmware instead of wrapper-only IRQ pulses.",
        ),
        _row(
            "hazard3_irq_controller_present",
            "PASS" if "module hazard3_irq_ctrl" in irq_ctrl and "external_irq_pending" in irq_ctrl else "FAIL",
            "third_party/hazard3/hdl/hazard3_irq_ctrl.v",
            "Candidate includes an IRQ controller module with external interrupt pending logic.",
        ),
        _row(
            "hazard3_frontend_lint",
            lint_status,
            _rel(lint_log),
            lint_note,
        ),
        _row(
            "hazard3_replay_scope_boundary",
            "INFO",
            "docs/second_core_irq_candidate.md",
            "This source/frontend probe is not itself a ReplayCapsule wrapper or replay result; the separate Hazard3 ISR smoke is tracked in docs/hazard3_irq_smoke.md and the seeded v2 ReplayCapsule MMIO+IRQ benchmark matrix is tracked in docs/hazard3_v2_replay_smoke.md.",
        ),
    ]


def _run_lint() -> tuple[str, str, Path]:
    log = RAW_DIR / "verilator_lint_hazard3_cpu_1port.txt"
    tool_root = _oss_cad_suite_root()
    verilator = _find_verilator(tool_root)
    if not verilator:
        log.write_text("verilator not found\n", encoding="utf-8")
        return "FAIL", "Verilator was not found, so frontend lint could not run.", log
    if not (HDL / "hazard3.f").exists():
        log.write_text("missing third_party/hazard3/hdl/hazard3.f\n", encoding="utf-8")
        return "FAIL", "Hazard3 filelist is missing.", log
    files = [
        str((HDL / line.split(maxsplit=1)[1]).relative_to(REPO_ROOT))
        for line in _read(HDL / "hazard3.f").splitlines()
        if line.startswith("file ")
    ]
    cmd = [
        verilator,
        "--lint-only",
        "-Wall",
        "-Wno-fatal",
        "-Wno-UNUSEDPARAM",
        "-Wno-UNUSEDSIGNAL",
        "-Wno-PINCONNECTEMPTY",
        "--top-module",
        "hazard3_cpu_1port",
        "-Ithird_party/hazard3/hdl",
        *files,
    ]
    env = os.environ.copy()
    if tool_root:
        env["PATH"] = str(tool_root / "bin") + os.pathsep + env.get("PATH", "")
        env["VERILATOR_ROOT"] = str(tool_root / "share" / "verilator")
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    text = completed.stdout.strip()
    if not text:
        text = (
            "verilator lint passed without output"
            if completed.returncode == 0
            else f"verilator exited with code {completed.returncode} without output"
        )
    log.write_text(text + "\n", encoding="utf-8")
    if completed.returncode == 0:
        return "PASS", "Verilator frontend lint accepts the vendored Hazard3 single-port CPU top and filelist.", log
    return "FAIL", f"Verilator frontend lint failed with exit code {completed.returncode}.", log


def _oss_cad_suite_root() -> Path | None:
    local = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite"
    if not local.exists():
        return None
    if " " not in str(local):
        return local
    link = Path("C:/rc_tools")
    if not link.exists():
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(local)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if (link / "bin" / "verilator_bin.exe").exists() and (link / "share" / "verilator").exists():
        return link
    return local


def _find_verilator(tool_root: Path | None) -> str | None:
    if tool_root:
        local = tool_root / "bin" / "verilator_bin.exe"
        if local.exists():
            return str(local)
    local = REPO_ROOT / ".tools" / "oss-cad-suite" / "oss-cad-suite" / "bin" / "verilator_bin.exe"
    if local.exists():
        return str(local)
    return shutil.which("verilator") or shutil.which("verilator_bin.exe")


def _write_csv(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_doc(rows: list[dict[str, str]]) -> None:
    status = "PASS" if all(row["status"] in {"PASS", "INFO"} for row in rows) else "FAIL"
    lines = [
        "# Second-Core IRQ Candidate",
        "",
        f"Status: `{status}`.",
        "",
        "Hazard3 is vendored as a pinned interrupt-capable RV32 candidate. This source and frontend-readiness gate proves the candidate has real interrupt/CSR machinery and can be parsed by the local Verilator frontend, but it does not by itself prove firmware execution or ReplayCapsule record/replay on Hazard3. The separate focused ISR firmware smoke is tracked in `docs/hazard3_irq_smoke.md`, and the seeded v2 ReplayCapsule MMIO+IRQ replay-consumer benchmark matrix is tracked in `docs/hazard3_v2_replay_smoke.md`.",
        "",
        "| Check | Status | Evidence | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['check']}` | `{row['status']}` | `{row['evidence']}` | {row['notes']} |")
    lines.extend(
        [
            "",
            "Allowed from this evidence:",
            "",
            "- Hazard3 is a vendored, pinned, Apache-2.0 interrupt-capable second-core candidate.",
            "- The candidate exposes external, software, and timer IRQ inputs and contains machine trap/interrupt CSR support.",
            "- The candidate HDL filelist passes local Verilator frontend lint.",
            "",
            "Do not claim from this evidence:",
            "",
            "- Hazard3 firmware execution from this source/frontend probe alone; use `docs/hazard3_irq_smoke.md` for the separate focused ISR smoke.",
            "- Hazard3 ReplayCapsule replay from this source/frontend probe alone; use `docs/hazard3_v2_replay_smoke.md` for the separate seeded v2 replay matrix.",
            "- Cross-core behavioral equivalence or portability.",
            "",
            "Next step: broaden beyond the current scoped Hazard3 v2 matrix only if the paper needs OS/application-suite coverage or full-diagnostic all-commit replay.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _row(check: str, status: str, evidence: str, notes: str) -> dict[str, str]:
    return {"check": check, "status": status, "evidence": evidence, "notes": notes}


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


if __name__ == "__main__":
    raise SystemExit(main())
