#!/usr/bin/env python3
"""Generate a hash manifest for the main local evidence artifacts."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/artifact_manifest.csv"

FIELDNAMES = [
    "artifact",
    "status",
    "bytes",
    "sha256",
    "producer",
    "role",
    "required_for_local_gate",
    "notes",
]


@dataclass(frozen=True)
class ArtifactSpec:
    path: str
    producer: str
    role: str
    required: bool = True
    notes: str = ""


ARTIFACTS = (
    ArtifactSpec("results/processed/replay_experiments.csv", "scripts/run_replay_experiments.py", "model and firmware-sim replay status"),
    ArtifactSpec("results/processed/replay_negative_tests.csv", "scripts/run_replay_negative_tests.py", "replay comparator positive and negative fixtures"),
    ArtifactSpec("results/processed/firmware_sim_replay.csv", "scripts/rv32i_firmware_sim.py", "RV32I interpreter replay rows"),
    ArtifactSpec("results/processed/rtl_capsule_exports.csv", "scripts/export_rtl_capsules.py", "RTL-smoke capsule export and corruption checks"),
    ArtifactSpec("results/processed/rtl_capsule_event_classes.csv", "scripts/summarize_rtl_capsule_classes.py", "RTL-smoke capsule event-class counts"),
    ArtifactSpec("results/processed/rtl_firmware_alignment.csv", "scripts/check_rtl_firmware_alignment.py", "RTL-smoke versus firmware-sim alignment"),
    ArtifactSpec("results/processed/randomized_interrupt_campaign.csv", "scripts/run_randomized_interrupt_campaign.py", "seeded RTL-smoke interrupt campaign rows"),
    ArtifactSpec("results/processed/randomized_interrupt_summary.csv", "scripts/summarize_randomized_interrupt_campaign.py", "seeded interrupt campaign summary"),
    ArtifactSpec("results/processed/randomized_interrupt_coverage.csv", "scripts/summarize_randomized_interrupt_campaign.py", "seeded interrupt coverage and TODO checklist"),
    ArtifactSpec("results/processed/randomized_interrupt_corruption.csv", "scripts/summarize_randomized_interrupt_campaign.py", "seeded interrupt corruption-rejection checks"),
    ArtifactSpec("results/processed/trace_sizes.csv", "scripts/collect_trace_sizes.py", "baseline trace-size rows"),
    ArtifactSpec("results/processed/ablations.csv", "scripts/run_ablations.py", "model-level ablation rows"),
    ArtifactSpec("results/processed/event_sufficiency.csv", "scripts/run_ablations.py", "model event-sufficiency summary"),
    ArtifactSpec("results/processed/rtl_smoke_ablations.csv", "scripts/run_rtl_smoke_ablations.py", "RTL-smoke event-class ablations"),
    ArtifactSpec("results/processed/rtl_smoke_event_sufficiency.csv", "scripts/run_rtl_smoke_ablations.py", "RTL-smoke required event-class summary"),
    ArtifactSpec("results/processed/hdl_checks.csv", "scripts/run_hdl_checks.py", "directed HDL simulation and lint rows"),
    ArtifactSpec("results/processed/picorv32_smoke_summary.csv", "scripts/summarize_picorv32_smokes.py", "PicoRV32 wrapper smoke observed capsule summary"),
    ArtifactSpec("results/processed/picorv32_smoke_coverage.csv", "scripts/summarize_picorv32_smokes.py", "PicoRV32 wrapper smoke log-level coverage checks"),
    ArtifactSpec("results/processed/benchmark_coverage.csv", "scripts/summarize_benchmark_coverage.py", "per-benchmark local evidence coverage ledger"),
    ArtifactSpec("results/processed/formal_checks.csv", "scripts/run_formal_checks.py", "bounded formal check rows"),
    ArtifactSpec("results/processed/formal_coverage.csv", "scripts/summarize_formal_coverage.py", "formal coverage matrix source"),
    ArtifactSpec("results/processed/proof_obligations.csv", "scripts/summarize_proof_obligations.py", "proof-obligation source"),
    ArtifactSpec("results/processed/synthesis.csv", "scripts/parse_synthesis_reports.py", "generic synthesis status"),
    ArtifactSpec("results/processed/synthesis_overhead.csv", "scripts/summarize_synthesis_overhead.py", "generic synthesis overhead context"),
    ArtifactSpec("results/processed/evaluation_metrics.csv", "scripts/summarize_evaluation_metrics.py", "headline metric rollup"),
    ArtifactSpec("results/processed/claim_audit.csv", "scripts/audit_claims.py", "claim honesty audit rows"),
    ArtifactSpec("results/processed/toolchain_status.csv", "scripts/run_all_tests.py", "local tool availability and blocker ledger"),
    ArtifactSpec("docs/formal_coverage_matrix.md", "scripts/summarize_formal_coverage.py", "reviewer-facing formal coverage table"),
    ArtifactSpec("docs/proof_obligation_matrix.md", "scripts/summarize_proof_obligations.py", "reviewer-facing proof-obligation matrix"),
    ArtifactSpec("results/raw/model_suite_traces.json", "scripts/replaycapsule_model.py", "model trace bundle"),
    ArtifactSpec("results/raw/firmware_sim_traces.json", "scripts/rv32i_firmware_sim.py", "firmware-sim trace bundle"),
    ArtifactSpec("results/raw/phase12_sensor_threshold_trace.json", "scripts/replaycapsule_model.py", "model smoke trace"),
)

GLOBS = (
    ("paper/figures/table*.md", "scripts/render_paper_tables.py", "generated paper table source"),
    ("paper/figures/*.svg", "scripts/make_figures.py", "paper SVG figure mirror"),
    ("results/figures/*.svg", "scripts/make_figures.py", "generated SVG figure source"),
    ("results/raw/tb_*_*.txt", "scripts/run_hdl_checks.py", "raw HDL compile/simulation log"),
    ("results/raw/verilator_lint_*.txt", "scripts/run_hdl_checks.py", "raw Verilator lint log"),
    ("results/raw/formal_*.txt", "scripts/run_formal_checks.py", "raw bounded formal log"),
    ("results/raw/randomized_interrupt_campaign/*.txt", "scripts/run_randomized_interrupt_campaign.py", "raw seeded interrupt campaign log"),
    ("results/raw/rtl_capsules/*.json", "scripts/export_rtl_capsules.py", "raw exported RTL-smoke capsule"),
    ("results/raw/yosys_*.txt", "scripts/synth_yosys.py", "raw generic synthesis report"),
)


def main() -> int:
    rows: list[dict[str, str]] = []
    seen: set[Path] = set()
    for spec in ARTIFACTS:
        path = REPO_ROOT / spec.path
        rows.append(_row(path, spec.producer, spec.role, spec.required, spec.notes))
        seen.add(path)
    for pattern, producer, role in GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if path in seen or path == OUT_CSV:
                continue
            rows.append(_row(path, producer, role, True, "discovered by manifest glob"))
            seen.add(path)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    missing = [row["artifact"] for row in rows if row["required_for_local_gate"] == "yes" and row["status"] == "MISSING"]
    print(f"WROTE {OUT_CSV}; present={len(rows) - len(missing)} missing={len(missing)}")
    if missing:
        for artifact in missing:
            print(f"MISSING {artifact}")
        return 1
    return 0


def _row(path: Path, producer: str, role: str, required: bool, notes: str) -> dict[str, str]:
    if not path.exists():
        return {
            "artifact": _rel(path),
            "status": "MISSING",
            "bytes": "NA",
            "sha256": "NA",
            "producer": producer,
            "role": role,
            "required_for_local_gate": "yes" if required else "no",
            "notes": notes,
        }
    data = path.read_bytes()
    return {
        "artifact": _rel(path),
        "status": "PRESENT",
        "bytes": str(len(data)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "producer": producer,
        "role": role,
        "required_for_local_gate": "yes" if required else "no",
        "notes": notes,
    }


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
