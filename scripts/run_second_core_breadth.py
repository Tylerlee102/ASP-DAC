#!/usr/bin/env python3
"""Emit honest second-core breadth evidence for the vendored FemtoRV32 core."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CORE = REPO_ROOT / "third_party" / "femtorv32" / "femtorv32_quark.v"
WRAPPER = REPO_ROOT / "rtl" / "rv32i_integration" / "femtorv32_replaycapsule_wrapper.sv"
LICENSE = REPO_ROOT / "third_party" / "femtorv32" / "LICENSE"
VENDORED = REPO_ROOT / "third_party" / "femtorv32" / "VENDORED.md"
HDL_CSV = REPO_ROOT / "results" / "processed" / "hdl_checks.csv"
SYNTHESIS_CSV = REPO_ROOT / "results" / "processed" / "synthesis.csv"
SECOND_CORE_REPLAY_CSV = REPO_ROOT / "results" / "processed" / "second_core_replay_smokes.csv"
SECOND_CORE_V2_CSV = REPO_ROOT / "results" / "processed" / "second_core_v2_smokes.csv"
OUT_CSV = REPO_ROOT / "results" / "processed" / "second_core_breadth.csv"
OUT_MD = REPO_ROOT / "docs" / "second_core_breadth.md"
MIN_SECOND_CORE_REPLAY_BENCHMARKS = 14
MIN_SECOND_CORE_REPLAY_ROWS = 56
MIN_SECOND_CORE_V2_BENCHMARKS = 14
MIN_SECOND_CORE_V2_SEEDS = 3
MIN_SECOND_CORE_V2_ROWS = 126

FIELDS = ["check", "status", "evidence", "notes"]


def main() -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    _refresh_synthesis()
    rows = _build_rows()
    _write_csv(rows)
    _write_doc(rows)
    print(f"WROTE {_rel(OUT_CSV)}")
    print(f"WROTE {_rel(OUT_MD)}")
    return 1 if any(row["status"] == "FAIL" for row in rows) else 0


def _refresh_synthesis() -> None:
    subprocess.run([sys.executable, "scripts/synth_yosys.py", "--top", "FemtoRV32"], cwd=REPO_ROOT, check=False)
    subprocess.run([sys.executable, "scripts/synth_yosys.py", "--top", "femtorv32_replaycapsule_wrapper"], cwd=REPO_ROOT, check=False)
    subprocess.run([sys.executable, "scripts/parse_synthesis_reports.py"], cwd=REPO_ROOT, check=False)
    subprocess.run([sys.executable, "scripts/run_hdl_checks.py"], cwd=REPO_ROOT, check=False)
    subprocess.run([sys.executable, "scripts/run_second_core_replay_smokes.py"], cwd=REPO_ROOT, check=False)
    subprocess.run([sys.executable, "scripts/run_second_core_v2_smokes.py"], cwd=REPO_ROOT, check=False)


def _build_rows() -> list[dict[str, str]]:
    core_text = _read(CORE)
    wrapper_text = _read(WRAPPER)
    license_text = _read(LICENSE)
    vendored_text = _read(VENDORED)
    synthesis_rows = _read_csv(SYNTHESIS_CSV)
    hdl_rows = _read_csv(HDL_CSV)
    second_replay_rows = _read_csv(SECOND_CORE_REPLAY_CSV)
    second_v2_rows = _read_csv(SECOND_CORE_V2_CSV)
    second_replay_profiles = {row.get("capture_profile", "") for row in second_replay_rows if row.get("capture_profile")}
    second_v2_configs = {row.get("recorder_config", "") for row in second_v2_rows if row.get("status") == "PASS"}
    second_v2_benchmarks = {row.get("benchmark", "") for row in second_v2_rows if row.get("status") == "PASS"}
    second_v2_seeds = {row.get("seed", "") for row in second_v2_rows if row.get("status") == "PASS"}
    core_synthesis = _row_for(synthesis_rows, "FemtoRV32")
    wrapper_synthesis = _row_for(synthesis_rows, "femtorv32_replaycapsule_wrapper")
    wrapper_lint = next((row for row in hdl_rows if row.get("check") == "verilator_lint_femtorv32_wrapper"), {})
    wrapper_smoke = next((row for row in hdl_rows if row.get("check") == "tb_femtorv32_sensor_threshold_smoke"), {})
    wrapper_replay_smoke = next((row for row in hdl_rows if row.get("check") == "tb_femtorv32_capsule_derived_replay_smoke"), {})
    v2_wrapper_lint = next((row for row in hdl_rows if row.get("check") == "verilator_lint_femtorv32_v2_wrapper"), {})
    v2_replay_smoke = next((row for row in hdl_rows if row.get("check") == "tb_femtorv32_v2_replay_smoke"), {})
    v1_replay_checker = next((row for row in hdl_rows if row.get("check") == "tb_rcv1_capsule_replay_checker"), {})
    v1_mmio_driver = next((row for row in hdl_rows if row.get("check") == "tb_rcv1_mmio_replay_driver"), {})
    core_synthesis_cells = core_synthesis.get("cells", "NA") if core_synthesis else "NA"
    wrapper_synthesis_cells = wrapper_synthesis.get("cells", "NA") if wrapper_synthesis else "NA"
    second_replay_bad = [row for row in second_replay_rows if row.get("status") != "PASS"]
    second_replay_mmio_bad = [row for row in second_replay_rows if row.get("mmio_driver_hits") in {"", "NA", None}]
    second_replay_benchmarks = {row.get("benchmark", "") for row in second_replay_rows if row.get("status") == "PASS"}
    second_v2_bad = [
        row
        for row in second_v2_rows
        if row.get("status") != "PASS" or row.get("signature_match") != "PASS" or row.get("changed_input") != "PASS"
    ]

    rows = [
        _row(
            "femtorv32_source_present",
            "PASS" if CORE.exists() and "module FemtoRV32" in core_text else "FAIL",
            _rel(CORE),
            "Vendored FemtoRV32 Quark Verilog source is present.",
        ),
        _row(
            "femtorv32_declares_rv32i",
            "PASS" if "Instruction set: RV32I" in core_text and '`define NRV_ARCH     "rv32i"' in core_text else "FAIL",
            _rel(CORE),
            "Source declares RV32I architecture scope.",
        ),
        _row(
            "femtorv32_license_tracked",
            "PASS" if LICENSE.exists() and "BSD 3-Clause License" in license_text else "FAIL",
            _rel(LICENSE),
            "Upstream BSD-3-Clause license is vendored with the core.",
        ),
        _row(
            "femtorv32_source_pinned",
            "PASS" if "5c08c870315c09ccd9ec64ccde20ab3375b3f273" in vendored_text else "FAIL",
            _rel(VENDORED),
            "Vendored metadata pins the upstream commit used for this copy.",
        ),
        _row(
            "femtorv32_generic_synthesis",
            "PASS" if core_synthesis and core_synthesis.get("status") == "MEASURED" and core_synthesis_cells != "NA" else "FAIL",
            "results/processed/synthesis.csv",
            f"Yosys generic synthesis row for FemtoRV32 reports cells={core_synthesis_cells}.",
        ),
        _row(
            "femtorv32_replaycapsule_wrapper_present",
            "PASS" if WRAPPER.exists() and "FemtoRV32" in wrapper_text and "replay_capsule_top" in wrapper_text else "FAIL",
            _rel(WRAPPER),
            "ReplayCapsule wrapper around FemtoRV32 source is present.",
        ),
        _row(
            "femtorv32_replaycapsule_wrapper_lint",
            "PASS" if wrapper_lint.get("status") == "PASS" else "FAIL",
            wrapper_lint.get("raw_log", "results/processed/hdl_checks.csv"),
            "Verilator frontend lint accepts the FemtoRV32 ReplayCapsule wrapper.",
        ),
        _row(
            "femtorv32_replaycapsule_wrapper_synthesis",
            "PASS" if wrapper_synthesis and wrapper_synthesis.get("status") == "MEASURED" and wrapper_synthesis_cells != "NA" else "FAIL",
            "results/processed/synthesis.csv",
            f"Yosys generic synthesis row for the FemtoRV32 ReplayCapsule wrapper reports cells={wrapper_synthesis_cells}.",
        ),
        _row(
            "femtorv32_compiler_firmware_smoke",
            "PASS" if wrapper_smoke.get("status") == "PASS" else "FAIL",
            wrapper_smoke.get("raw_log", "results/processed/hdl_checks.csv"),
            "Icarus runs compiler-built sensor_threshold_bug firmware on the FemtoRV32 ReplayCapsule wrapper and captures the expected property-fail capsule.",
        ),
        _row(
            "femtorv32_v1_capsule_replay_checker",
            "PASS" if v1_replay_checker.get("status") == "PASS" else "FAIL",
            v1_replay_checker.get("raw_log", "results/processed/hdl_checks.csv"),
            "Reusable RTL checker for the 168-bit v1 capsule packet stream accepts matching replay packets and rejects mismatch/extra/truncated streams.",
        ),
        _row(
            "femtorv32_v1_mmio_replay_driver",
            "PASS" if v1_mmio_driver.get("status") == "PASS" else "FAIL",
            v1_mmio_driver.get("raw_log", "results/processed/hdl_checks.csv"),
            "Scoped v1 RTL MMIO replay driver stores captured 168-bit packets and returns replay MMIO-read values for matching observed addresses.",
        ),
        _row(
            "femtorv32_capsule_derived_replay_smoke",
            "PASS" if wrapper_replay_smoke.get("status") == "PASS" else "FAIL",
            wrapper_replay_smoke.get("raw_log", "results/processed/hdl_checks.csv"),
            "Icarus captures the compiler-built sensor-threshold failure capsule, resets the wrapped FemtoRV32 core, drives replay MMIO reads through the scoped v1 RTL replay driver, and routes replay packet comparison through the v1 RTL checker.",
        ),
        _row(
            "femtorv32_v2_mmio_replay_consumer_smoke",
            "PASS" if wrapper_replay_smoke.get("status") == "PASS" and v2_wrapper_lint.get("status") == "PASS" and v2_replay_smoke.get("status") == "PASS" else "FAIL",
            v2_replay_smoke.get("raw_log", "results/processed/hdl_checks.csv"),
            "A scoped FemtoRV32 v2 wrapper passes Verilator frontend lint and an Icarus smoke that records a v2 sensor-threshold stream, resets the wrapped core, changes the replay sensor input, and requires the v2 replay consumer to consume the captured MMIO replay stream and reproduce the property id and property signature.",
        ),
        _row(
            "femtorv32_v2_mmio_replay_consumer_config_matrix",
            "PASS"
            if second_v2_rows
            and not second_v2_bad
            and {"core", "hashed", "full"}.issubset(second_v2_configs)
            and len(second_v2_rows) >= MIN_SECOND_CORE_V2_ROWS
            and len(second_v2_benchmarks) >= MIN_SECOND_CORE_V2_BENCHMARKS
            and len(second_v2_seeds) >= MIN_SECOND_CORE_V2_SEEDS
            else "FAIL",
            "results/processed/second_core_v2_smokes.csv",
            f"Focused seeded FemtoRV32 v2 MMIO replay-consumer smokes pass for {len(second_v2_benchmarks)} benchmark families across {len(second_v2_configs)} recorder configs ({', '.join(sorted(second_v2_configs)) if second_v2_configs else 'none'}) and {len(second_v2_seeds)} seeds, perturbing replay-side host MMIO inputs while requiring captured-stream consumption and property-signature equality; true IRQ replay and full MMIO+IRQ replay are not claimed.",
        ),
        _row(
            "femtorv32_capsule_derived_replay_matrix",
            "PASS" if second_replay_rows and not second_replay_bad and not second_replay_mmio_bad and len(second_replay_rows) >= MIN_SECOND_CORE_REPLAY_ROWS and len(second_replay_benchmarks) >= MIN_SECOND_CORE_REPLAY_BENCHMARKS and len(second_replay_profiles) >= 4 else "FAIL",
            "results/processed/second_core_replay_smokes.csv",
            f"Focused FemtoRV32 capsule-derived replay rows pass for {len(second_replay_benchmarks)} base and expanded benchmark families across {len(second_replay_profiles)} v1 capture profiles with checker-consumed packet streams and v1 MMIO replay-driver hit accounting, including wrapper-level IRQ-boundary evidence; no true CPU interrupt/ISR or seeded matrix claim.",
        ),
        _row(
            "femtorv32_replay_scope_boundary",
            "INFO",
            "docs/second_core_breadth.md",
            "This is second-core wrapper lint/synthesis plus focused capsule-derived replay smokes across v1 capture profiles with scoped v1 MMIO replay reads and a seeded scoped v2 MMIO replay-consumer campaign; true CPU interrupt/ISR replay and full MMIO+IRQ replay are not claimed yet.",
        ),
    ]
    return rows


def _write_csv(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_doc(rows: list[dict[str, str]]) -> None:
    status = "PASS" if all(row["status"] in {"PASS", "INFO"} for row in rows) else "FAIL"
    second_replay_rows = _read_csv(SECOND_CORE_REPLAY_CSV)
    second_v2_rows = _read_csv(SECOND_CORE_V2_CSV)
    second_replay_benchmarks = sorted({row.get("benchmark", "") for row in second_replay_rows if row.get("status") == "PASS"})
    second_replay_profiles = sorted({row.get("capture_profile", "") for row in second_replay_rows if row.get("capture_profile")})
    second_v2_configs = sorted({row.get("recorder_config", "") for row in second_v2_rows if row.get("status") == "PASS"})
    second_v2_benchmarks = sorted({row.get("benchmark", "") for row in second_v2_rows if row.get("status") == "PASS"})
    second_v2_seeds = sorted({row.get("seed", "") for row in second_v2_rows if row.get("status") == "PASS"})
    benchmark_count = len(second_replay_benchmarks)
    profile_count = len(second_replay_profiles)
    v2_config_count = len(second_v2_configs)
    v2_benchmark_count = len(second_v2_benchmarks)
    v2_seed_count = len(second_v2_seeds)
    lines = [
        "# Second-Core Breadth Evidence",
        "",
        f"Status: `{status}`.",
        "",
        f"This folder now vendors FemtoRV32 Quark as a real second RV32I core candidate, adds ReplayCapsule wrappers around it, measures generic Yosys synthesis rows for both the core and wrapper, runs one compiler-built sensor-threshold firmware capture smoke through the wrapper, adds a reusable v1 RTL capsule replay checker plus a scoped v1 RTL MMIO replay driver, runs focused capsule-derived replay smokes that reset the wrapped core and reproduce captured capsule/property/signature evidence for {benchmark_count} base and expanded benchmark families across {profile_count} v1 capture profiles, and adds scoped seeded v2 MMIO replay-consumer smokes on FemtoRV32 for {v2_benchmark_count} benchmark families across {v2_config_count} recorder configs and {v2_seed_count} seeds. This evidence is useful for reducing PicoRV32-only integration risk, but it is deliberately not a true CPU interrupt/ISR or full MMIO+IRQ replay claim.",
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
            "- A second open-source RV32I core has been vendored with license metadata.",
            "- The second core has a measured generic Yosys synthesis row.",
            "- A ReplayCapsule wrapper around the second core passes Verilator frontend lint and generic Yosys synthesis.",
            "- One compiler-built sensor-threshold firmware smoke runs on the FemtoRV32 ReplayCapsule wrapper and captures the expected property-fail capsule.",
            "- A reusable v1 RTL capsule replay checker validates matching 168-bit packet streams and rejects mismatch/extra/truncated streams.",
            "- A scoped v1 RTL MMIO replay driver stores captured 168-bit packets and supplies replay MMIO-read values for matching observed addresses.",
            f"- Focused capsule-derived replay smokes on FemtoRV32 reproduce captured property, signature, checker-consumed capsule packets, and v1 MMIO replay-driver hit accounting after reset for {benchmark_count} base and expanded benchmark families across {profile_count} v1 capture profiles.",
            f"- Scoped seeded v2 FemtoRV32 replay-consumer smokes record a v2 MMIO/property stream, reset the wrapped core, perturb replay-side host MMIO inputs, and require the v2 consumer to consume the captured stream and reproduce the property id and property signature for {v2_benchmark_count} benchmark families across {v2_config_count} recorder configs ({', '.join(second_v2_configs) if second_v2_configs else 'none'}) and {v2_seed_count} seeds.",
            "",
            "Do not claim from this evidence:",
            "",
            "- v2 replay that drives both FemtoRV32 core-facing MMIO and IRQ inputs.",
            "- True CPU interrupt/ISR replay on FemtoRV32; the vendored Quark core has no external interrupt/CSR machinery.",
            "- Cross-core behavioral equivalence or portability.",
            "- ASIC, timing, power, or mapped FPGA results for FemtoRV32.",
            "",
            "Next step: add v2 IRQ stimulus on a core with true interrupt support.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _row(check: str, status: str, evidence: str, notes: str) -> dict[str, str]:
    return {"check": check, "status": status, "evidence": evidence, "notes": notes}


def _row_for(rows: list[dict[str, str]], top: str) -> dict[str, str] | None:
    return next((row for row in rows if row.get("top") == top), None)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
