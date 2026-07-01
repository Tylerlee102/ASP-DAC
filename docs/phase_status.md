# ReplayCapsule-RV Phase Status

Last inspected: 2026-06-27.

This file is a current evidence snapshot. The locked Linux CI run is the
authority for compiler-backed firmware, full RTL replay, mapped ECP5
place-and-route, paper build, audits, and artifact packaging. Local Windows
shells may need the bundled Python/runtime wrappers documented in
`README.md` and `artifact_evaluation.md`.

## Status Vocabulary

- Complete: the phase has generated evidence at the claimed scope.
- Scoped complete: the phase is complete for the current single-hart RV32I
  interrupt/MMIO prototype, with explicit out-of-scope limits.
- Future work: the item is not claimed by the paper or artifact.

## Phase Matrix

| Phase | Scope | Status | Evidence | Remaining limitation |
| --- | --- | --- | --- | --- |
| 0 | Repository plan and research scaffold | Complete | `docs/research_plan.md`, ownership docs, README, artifact notes, honesty rules | None for packaging |
| 1 | RV32I benchmark and firmware scaffold | Complete | Six firmware bug families, compiler-backed firmware rows in `results/processed/firmware_build.csv`, model and firmware-sim traces | Benchmark suite is generated and scoped |
| 2 | Record-side and replay-side RTL modules | Complete | Event tap, classifier/slicer, property checker, hash/signature, MMIO/interrupt loggers, registers, replay-control, replay-mismatch, recorder, capsule buffer, v2 capsule source, replay-mode controller, and replay consumer RTL plus HDL/formal rows | No board/silicon replay engine is claimed |
| 3 | Replay model and proof obligations | Scoped complete | `docs/event_model.md`, `formal/replay_sufficiency_theorem.md`, `docs/proof_obligation_matrix.md`, `results/processed/proof_obligations.csv` | Written theorem and evidence mapping, not a mechanized end-to-end processor proof |
| 4 | RTL replay drive and corruption rejection | Complete | `results/processed/full_rtl_replay.csv` reports 45/45 PASS; `results/processed/full_rtl_replay_v2.csv` reports 135/135 rows with RTL MMIO/IRQ replay drive; `results/processed/self_replay_handoff_v2.csv` reports captured-store self-replay handoff rows; `results/processed/full_rtl_replay_negative.csv` reports 10 rejects, 0 unexpected accepts, 2 not-applicable rows | Broad full-core replay remains harness-orchestrated, not board/silicon replay |
| 5 | Verification harnesses and assertions | Complete | `results/processed/hdl_checks.csv`, `formal_checks.csv`, `formal_coverage.csv`, `overflow_contracts.csv`, randomized interrupt rows, and full RTL replay rows | Broader randomized full RTL campaigns are future work |
| 6 | Runtime overhead | Complete | `results/processed/runtime_overhead.csv` and `runtime_overhead_summary.csv` | Measurements are harness-level, not an ASIC or deployment proof |
| 7 | Synthesis and mapped overhead | Complete | `results/processed/mapped_synthesis.csv`, `mapped_overhead.csv`, `mapped_recorder_presence.csv`, `full_core_mapped_summary.csv`, and `asic_openpdk.csv` | ECP5 prototype is not area-optimized; ASIC context is OpenROAD global-routed Nangate45 evidence, not detailed-route signoff or energy |
| 8 | Baselines and ablations | Scoped complete | `trace_sizes.csv`, `baseline_comparison.csv`, `ablations.csv`, `event_sufficiency.csv`, `rtl_smoke_ablations.csv`, and `rtl_smoke_event_sufficiency.csv` | Full RTL trace-size reductions and full RTL ablation variants are future work |
| 9 | Paper and audits | Complete | `paper/main.pdf`, `paper_build_status.csv`, `claim_audit.csv`, `paper_number_audit.csv`, and `todo_audit.csv` | Claims must remain scoped to generated evidence |
| 10 | Artifact and final CI package | Complete | `dist/replaycapsule-rv-artifact.zip`, `results/processed/artifact_manifest.csv`, `results/processed/final_ci_verification.csv`, and `docs/final_evidence_lock.md` | Artifact depends on standard Linux reproduction tools or the locked CI bundle |

## Bottom Line

The final package is a submission-ready candidate for a scoped systems/hardware
artifact: compiler-backed firmware, full RTL replay, corrupted-capsule
rejection, runtime measurements, same-target ECP5 mapped overhead, paper build,
claim audits, and artifact packaging are present. The paper must keep the
limits explicit: single-hart RV32I interrupt/MMIO scope, harness-orchestrated
reset/peripheral replay environment, ASIC evidence limited to OpenROAD global-routed Nangate45 rows,
and high prototype overhead.
