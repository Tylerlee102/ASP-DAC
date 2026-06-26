#!/usr/bin/env python3
"""Generate a theorem proof-obligation matrix from current evidence artifacts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPLAY_CSV = REPO_ROOT / "results/processed/replay_experiments.csv"
REPLAY_NEGATIVE_CSV = REPO_ROOT / "results/processed/replay_negative_tests.csv"
RTL_EXPORTS_CSV = REPO_ROOT / "results/processed/rtl_capsule_exports.csv"
RTL_ALIGNMENT_CSV = REPO_ROOT / "results/processed/rtl_firmware_alignment.csv"
RANDOMIZED_IRQ_CSV = REPO_ROOT / "results/processed/randomized_interrupt_campaign.csv"
EVENT_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/event_sufficiency.csv"
RTL_SMOKE_SUFFICIENCY_CSV = REPO_ROOT / "results/processed/rtl_smoke_event_sufficiency.csv"
FORMAL_COVERAGE_CSV = REPO_ROOT / "results/processed/formal_coverage.csv"
OUT_CSV = REPO_ROOT / "results/processed/proof_obligations.csv"
OUT_DOC = REPO_ROOT / "docs/proof_obligation_matrix.md"

FIELDNAMES = [
    "obligation_id",
    "theorem_assumption",
    "claim",
    "evidence_status",
    "evidence_level",
    "evidence_artifacts",
    "current_limit",
]


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    theorem_assumption: str
    claim: str
    evidence_status: str
    evidence_level: str
    evidence_artifacts: str
    current_limit: str


def main() -> int:
    data = EvidenceData.load()
    obligations = _build_obligations(data)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows([obligation.__dict__ for obligation in obligations])
    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(_render_doc(obligations), encoding="utf-8")
    print(f"WROTE {OUT_CSV} and {OUT_DOC}")
    return 0


class EvidenceData:
    def __init__(self) -> None:
        self.replay = _read_rows(REPLAY_CSV)
        self.replay_negative = _read_rows(REPLAY_NEGATIVE_CSV)
        self.rtl_exports = _read_rows(RTL_EXPORTS_CSV)
        self.rtl_alignment = _read_rows(RTL_ALIGNMENT_CSV)
        self.randomized_irq = _read_rows(RANDOMIZED_IRQ_CSV)
        self.event_sufficiency = _read_rows(EVENT_SUFFICIENCY_CSV)
        self.rtl_smoke_sufficiency = _read_rows(RTL_SMOKE_SUFFICIENCY_CSV)
        self.formal_coverage = _read_rows(FORMAL_COVERAGE_CSV)

    @classmethod
    def load(cls) -> "EvidenceData":
        return cls()

    def firmware_images_present(self) -> bool:
        return len(list((REPO_ROOT / "firmware/build").glob("*/*.*"))) >= 36

    def all_status(self, rows: list[dict[str, str]], status: str = "PASS") -> bool:
        return bool(rows) and all(row.get("status") == status for row in rows)

    def replay_passes(self, evidence_level: str) -> int:
        return sum(1 for row in self.replay if row.get("status") == "PASS" and row.get("evidence_level") == evidence_level)

    def negative_passes(self, test_name: str, mode: str | None = None) -> int:
        return sum(
            1
            for row in self.replay_negative
            if row.get("test") == test_name
            and row.get("status") == "PASS"
            and (mode is None or row.get("mode") == mode)
        )

    def formal_family_passes(self, *families: str) -> bool:
        by_family = {row.get("module_family"): row for row in self.formal_coverage}
        return all(by_family.get(family, {}).get("status") == "PASS" for family in families)


def _build_obligations(data: EvidenceData) -> list[Obligation]:
    summary_ready = data.firmware_images_present()
    replay_model = data.replay_passes("model")
    replay_firmware = data.replay_passes("firmware-sim")
    rtl_exports_pass = data.all_status(data.rtl_exports)
    rtl_alignment_pass = data.all_status(data.rtl_alignment)
    randomized_irq_pass = data.all_status(data.randomized_irq)
    event_sufficiency_rows = len(data.event_sufficiency)
    rtl_smoke_sufficiency_rows = len(data.rtl_smoke_sufficiency)
    checked_modes = ("commit-index", "cycle-index")
    order_negative_passes = min(
        data.negative_passes("swap_strict_event_order_tags", mode) for mode in checked_modes
    )
    missing_negative_passes = min(
        data.negative_passes("missing_first_replay_event", mode) for mode in checked_modes
    )
    duplicate_negative_passes = min(
        data.negative_passes("duplicate_first_replay_event", mode) for mode in checked_modes
    )
    payload_negative_passes = min(data.negative_passes("corrupt_first_payload", mode) for mode in checked_modes)
    commit_shift_passes = data.negative_passes("shift_first_commit_index", "commit-index")
    cycle_shift_passes = data.negative_passes("shift_first_cycle_index", "cycle-index")

    return [
        Obligation(
            "PO-01",
            "A0/A2 platform and firmware identity",
            "Replay uses the same platform profile and byte-identical firmware image identity as the recorded run.",
            "PARTIAL" if summary_ready else "TODO",
            "documentation+firmware-artifact",
            "formal/assumptions.md; docs/capsule_format.md; firmware/build/; results/processed/summary.csv",
            "Identity fields are specified and generated firmware artifacts exist, but there is no external compiler or full RTL replay identity check.",
        ),
        Obligation(
            "PO-02",
            "A1/A3 deterministic architectural state and core step",
            "For equal platform, firmware, state, and boundary input, the replay model produces the same next architectural state and observation.",
            "PARTIAL" if replay_model == 6 and replay_firmware == 6 else "TODO",
            "model+firmware-sim",
            "results/processed/replay_experiments.csv; results/raw/firmware_sim_traces.json; scripts/rv32i_firmware_sim.py",
            "The local interpreter and model are deterministic for the six workloads; this is not a mechanized RV32I ISA proof.",
        ),
        Obligation(
            "PO-03",
            "A4 boundary event completeness",
            "Replay capsules retain every nondeterministic boundary event needed by the scoped benchmark failures.",
            "PARTIAL" if event_sufficiency_rows == 6 and rtl_smoke_sufficiency_rows == 6 and rtl_exports_pass else "TODO",
            "model+rtl-smoke",
            "results/processed/event_sufficiency.csv; results/processed/rtl_smoke_event_sufficiency.csv; results/processed/rtl_capsule_exports.csv; results/processed/rtl_capsule_event_classes.csv",
            "Completeness is exercised for six model benchmarks and twelve RTL-smoke capsules, not for arbitrary firmware or full benchmark-wide RTL traces.",
        ),
        Obligation(
            "PO-04",
            "A5 commit-index and same-index ordering",
            "Replay comparison rejects missing, duplicate, shifted cycle/commit indices, and same-index reordered events.",
            "PASS_LOCAL" if min(
                order_negative_passes,
                missing_negative_passes,
                duplicate_negative_passes,
                commit_shift_passes,
                cycle_shift_passes,
            ) == 6 and rtl_exports_pass else "TODO",
            "model+rtl-smoke",
            "results/processed/replay_negative_tests.csv; results/processed/rtl_capsule_exports.csv",
            "Comparator/order checks are generated cycle-index and commit-index fixtures plus RTL-smoke export checks; full firmware-running RTL replay remains pending.",
        ),
        Obligation(
            "PO-05",
            "A6 precise interrupt delivery",
            "Interrupt timing is represented at commit-index boundaries and reproduced in seeded RTL-smoke schedules.",
            "PARTIAL" if randomized_irq_pass and rtl_alignment_pass else "TODO",
            "rtl-smoke+firmware-sim",
            "results/processed/randomized_interrupt_campaign.csv; results/processed/rtl_firmware_alignment.csv; results/processed/event_sufficiency.csv",
            "Seeded interrupt evidence covers RTL-smoke interrupt-race schedules; there is no full interrupt-controller proof or benchmark-wide randomized campaign.",
        ),
        Obligation(
            "PO-06",
            "A7 MMIO read/write contract",
            "MMIO read values, write observations, and corruption of MMIO payloads are replay-visible and checked.",
            "PASS_LOCAL" if payload_negative_passes == 6 and data.formal_family_passes("mmio_interrupt_loggers", "replay_control", "replay_mismatch_guards") else "TODO",
            "model+formal-bmc+rtl-smoke",
            "results/processed/replay_negative_tests.csv; results/processed/formal_coverage.csv; results/processed/rtl_firmware_alignment.csv",
            "Current checks cover local logger/control contracts and benchmark fixtures, not a complete bus-protocol proof.",
        ),
        Obligation(
            "PO-07",
            "A8 external memory mutation contract",
            "External architectural mutations must be captured as ordered boundary events when present.",
            "ASSUMPTION_ONLY",
            "documentation",
            "formal/assumptions.md; docs/event_model.md; docs/capsule_format.md",
            "The current six workloads do not include DMA or external RAM mutation RTL tests; the contract is specified but not exercised.",
        ),
        Obligation(
            "PO-08",
            "A9 deterministic safety property checker",
            "The property checker emits deterministic failure IDs/signatures over equal trace observations.",
            "PASS_LOCAL" if data.formal_family_passes("property_checker", "hash_signature") and rtl_alignment_pass else "TODO",
            "formal-bmc+rtl-smoke+firmware-sim",
            "results/processed/formal_coverage.csv; results/processed/rtl_firmware_alignment.csv; results/processed/replay_experiments.csv",
            "Checks cover local property/signature RTL contracts and smoke alignment, not every future safety property.",
        ),
        Obligation(
            "PO-09",
            "A10 finite prefix sufficiency",
            "Capsules and replay comparisons target the finite prefix through the selected property failure.",
            "PASS_LOCAL" if replay_model == 6 and data.formal_family_passes("capsule_buffer", "replay_capsule_top") else "TODO",
            "model+formal-bmc+rtl-smoke",
            "results/processed/replay_experiments.csv; results/processed/formal_coverage.csv; results/processed/rtl_capsule_exports.csv",
            "Prefix behavior is checked for model/firmware-sim workloads and bounded recorder contracts, not a full processor/replay theorem.",
        ),
        Obligation(
            "PO-10",
            "A11 recorder noninterference separate from sufficiency theorem",
            "The theorem applies to the recorded execution and does not itself prove instrumentation noninterference.",
            "ASSUMPTION_ONLY",
            "documentation",
            "formal/assumptions.md; docs/replay_sufficiency_theorem.md; paper/limitations.md",
            "No perturbation or runtime-overhead proof exists yet; mapped and benchmark-wide hardware results are pending.",
        ),
    ]


def _render_doc(obligations: list[Obligation]) -> str:
    lines = [
        "# Proof Obligation Matrix",
        "",
        "Generated by `scripts/summarize_proof_obligations.py` from theorem",
        "assumptions and current result artifacts.",
        "",
        "Status meanings:",
        "",
        "- `PASS_LOCAL`: local generated checks directly exercise the scoped obligation.",
        "- `PARTIAL`: current generated evidence supports the obligation for the scoped workloads or smoke paths, but not end to end.",
        "- `ASSUMPTION_ONLY`: the obligation is specified as a theorem assumption and still lacks executable evidence.",
        "- `TODO`: required evidence is missing from the current generated artifacts.",
        "",
        "| ID | Theorem assumption | Current status | Evidence level | Evidence artifacts | Current limit |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for obligation in obligations:
        lines.append(
            "| {obligation_id} | {assumption}: {claim} | {status} | {level} | {artifacts} | {limit} |".format(
                obligation_id=_escape_md(obligation.obligation_id),
                assumption=_escape_md(obligation.theorem_assumption),
                claim=_escape_md(obligation.claim),
                status=_escape_md(obligation.evidence_status),
                level=_escape_md(obligation.evidence_level),
                artifacts=_escape_md(obligation.evidence_artifacts),
                limit=_escape_md(obligation.current_limit),
            )
        )
    lines.extend(
        [
            "",
            "This matrix is deliberately conservative. It links the written",
            "replay-sufficiency theorem to current generated evidence, but it does not",
            "turn the theorem into a mechanized end-to-end proof.",
            "",
        ]
    )
    return "\n".join(lines)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
