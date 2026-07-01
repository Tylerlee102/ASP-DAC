# Reviewer Attack List

## 1. "This is just trace compression."

Likely wording: The paper appears to choose a smaller trace, not introduce a new replay model.

Required evidence: formal event-sufficiency model, ablations showing which missing events break replay, and comparison to full traces.

Current weakness: only the smoke ablation is executable locally.

Fix plan: run all six firmware benchmarks on RTL traces and show per-bug minimal event sets.

## 2. "This is just runtime monitoring."

Required evidence: same events drive both checking and replay capsules; replay must reproduce failures, not only detect them.

Current weakness: the broad full-core replay matrix still depends on Verilator reset orchestration and a modeled memory/peripheral shell rather than a deployed board/silicon replay flow.

Fix plan: emphasize the completed RTL capsule source, replay-mode controller, captured-store self-replay rows, and MMIO/IRQ replay consumer, while avoiding a board/silicon replay-engine claim.

## 3. "This is just deterministic replay."

Required evidence: narrowed embedded RV32I interrupt/MMIO boundary and minimal event model.

Current weakness: the replay-sufficiency theorem is still a written proof sketch. `docs/proof_obligation_matrix.md` now maps assumptions to current evidence and limits. Bounded SMTBMC checks cover local recorder, classifier/slicer, checker, logger, register, buffer, hash, replay-control, and replay-mismatch contracts, but not the end-to-end theorem.

Fix plan: connect the written theorem to the checked local contracts and add broader stream-level replay proofs.

## 4. "The novelty is only integration."

Required evidence: novelty matrix and theorem that identify event sufficiency as the contribution.

Current weakness: the novelty argument must stay focused on event sufficiency, not broad trace replacement.

Fix plan: keep the event interface and same-target mapped evidence tied to the scoped contribution.

## 5. "The benchmarks are toy examples."

Required evidence: realistic embedded bug mechanics, failing/fixed firmware, randomized interrupt/input campaigns.

Current weakness: the benchmark suite is generated and scoped, even though compiler-backed full RTL replay, expanded v2 rows, FemtoRV32 breadth, and Hazard3 MMIO+IRQ replay rows now pass.

Fix plan: present the generated base, expanded, FemtoRV32, and Hazard3 families as focused embedded bug mechanics, not complete embedded-system coverage.

## 6. "The proof is too weak."

Required evidence: explicit assumptions, equivalence definition, induction over commit-index time.

Current weakness: no mechanized end-to-end proof. Current bounded evidence is summarized in `docs/formal_coverage_matrix.md`, `docs/proof_obligation_matrix.md`, `results/processed/formal_checks.csv`, and `results/processed/proof_obligations.csv`.

Fix plan: strengthen theorem with invariants linked to the checked formal/SVA contracts and add broader stream-level replay proof families.

## 7. "The hardware overhead is too high."

Required evidence: LUT/FF/BRAM/Fmax from a real synthesis flow.

Current weakness: full-core mapped ECP5 overhead is high.

Fix plan: report the same-target ECP5 LUT/FF/BRAM/Fmax rows exactly, separate the v2 minimal recorder profile from diagnostic-rich core/hashed rows, and state that the diagnostic prototype is not area-optimized.

## 8. "The capsule is not actually minimal."

Required evidence: ablations and per-bug minimum event set table.

Current weakness: default capture includes property context beyond strict nondeterminism. Model-level and exported RTL-smoke event-class ablations now exist; full RTL ablation variants are future work.

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

Current weakness: model-level and firmware-sim snapshot sizes are measured, while RTL snapshot-size baselines remain future work.

Fix plan: implement RTL snapshot-size and replay-success baseline rows once firmware-running RTL traces are available.

## 12. "Why does this need hardware?"

Required evidence: hardware sees exact interrupt/MMIO timing and can freeze on failure with low perturbation.

Current weakness: runtime-overhead numbers are measured in the current harness, but software-only perturbation is not fully quantified.

Fix plan: quantify software-only instrumentation perturbation versus RTL capture.

## 13. "Why should ASP-DAC/DATE/ICCAD care?"

Required evidence: formal model, synthesizable design, FPGA/synthesis evaluation, and reproducible artifact.

Current weakness: the artifact now has full RTL replay and mapped hardware measurements; the main risk is overclaiming beyond the scoped prototype.

Fix plan: complete gates before making a venue-ready claim.
