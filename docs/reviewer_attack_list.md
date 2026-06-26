# Reviewer Attack List

## 1. "This is just trace compression."

Likely wording: The paper appears to choose a smaller trace, not introduce a new replay model.

Required evidence: formal event-sufficiency model, ablations showing which missing events break replay, and comparison to full traces.

Current weakness: only the smoke ablation is executable locally.

Fix plan: run all six firmware benchmarks on RTL traces and show per-bug minimal event sets.

## 2. "This is just runtime monitoring."

Required evidence: same events drive both checking and replay capsules; replay must reproduce failures, not only detect them.

Current weakness: property checker RTL exists, but full firmware replay is pending.

Fix plan: connect replay driver to RTL-generated capsules.

## 3. "This is just deterministic replay."

Required evidence: narrowed embedded RV32I interrupt/MMIO boundary and minimal event model.

Current weakness: the replay-sufficiency theorem is still a written proof sketch. Bounded SMTBMC checks cover local recorder, classifier/slicer, checker, logger, register, buffer, hash, replay-control, and replay-mismatch contracts, but not the end-to-end theorem.

Fix plan: connect the written theorem to the checked local contracts and add broader stream-level replay proofs.

## 4. "The novelty is only integration."

Required evidence: novelty matrix and theorem that identify event sufficiency as the contribution.

Current weakness: PicoRV32 has twelve wrapper smokes, not benchmark-wide replay/export evidence.

Fix plan: scale the PicoRV32 wrapper harness across the benchmark suite and keep the same event interface.

## 5. "The benchmarks are toy examples."

Required evidence: realistic embedded bug mechanics, failing/fixed firmware, randomized interrupt/input campaigns.

Current weakness: twelve firmware-running RTL smokes exist; the full RTL replay/export suite is not running yet.

Fix plan: implement all six failing/fixed firmware images.

## 6. "The proof is too weak."

Required evidence: explicit assumptions, equivalence definition, induction over commit-index time.

Current weakness: no mechanized end-to-end proof. Current bounded evidence is summarized in `docs/formal_coverage_matrix.md` and `results/processed/formal_checks.csv`.

Fix plan: strengthen theorem with invariants linked to the checked formal/SVA contracts and add broader stream-level replay proof families.

## 7. "The hardware overhead is too high."

Required evidence: LUT/FF/BRAM/Fmax from a real synthesis flow.

Current weakness: generic Yosys cell counts exist, but mapped FPGA resources and timing do not.

Fix plan: run at least one mapped FPGA flow and report LUT/FF/BRAM/Fmax from generated reports.

## 8. "The capsule is not actually minimal."

Required evidence: ablations and per-bug minimum event set table.

Current weakness: default capture currently includes property context beyond strict nondeterminism.

Fix plan: distinguish sufficiency core from diagnostic context and quantify both.

## 9. "The method does not scale."

Required evidence: buffer overflow rates, event rates, and scaling discussion.

Current weakness: no long-running firmware workloads yet.

Fix plan: add longer seeded workloads and vary buffer/window sizes.

## 10. "Existing RISC-V trace could do this."

Required evidence: compare against E-Trace/N-Trace-style baselines and explain missing MMIO value/interrupt replay semantics.

Current weakness: standards comparison is documentation-only.

Fix plan: implement trace-size baselines and discuss adapter feasibility.

## 11. "Snapshot systems already solve this."

Required evidence: snapshot-on-failure baseline showing inability to replay pre-failure nondeterministic path without event history.

Current weakness: model-level and firmware-sim snapshot sizes are measured, but RTL replay-success and RTL snapshot comparisons are still pending.

Fix plan: implement RTL snapshot-size and replay-success baseline rows once firmware-running RTL traces are available.

## 12. "Why does this need hardware?"

Required evidence: hardware sees exact interrupt/MMIO timing and can freeze on failure with low perturbation.

Current weakness: runtime-overhead numbers missing.

Fix plan: quantify software-only instrumentation perturbation versus RTL capture.

## 13. "Why should ASP-DAC/DATE/ICCAD care?"

Required evidence: formal model, synthesizable design, FPGA/synthesis evaluation, and reproducible artifact.

Current weakness: the artifact has local RTL, formal, firmware-sim, and generic synthesis evidence, but still lacks benchmark-wide RTL replay and mapped hardware measurements.

Fix plan: complete gates before making a venue-ready claim.
