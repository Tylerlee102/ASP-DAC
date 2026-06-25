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

Current weakness: proof is a sketch, not machine-checked.

Fix plan: add SV assertions and bounded formal checks for recorder invariants.

## 4. "The novelty is only integration."

Required evidence: novelty matrix and theorem that identify event sufficiency as the contribution.

Current weakness: top-level integration still uses a scaffold, not PicoRV32.

Fix plan: replace scaffold with PicoRV32 and keep the same event interface.

## 5. "The benchmarks are toy examples."

Required evidence: realistic embedded bug mechanics, failing/fixed firmware, randomized interrupt/input campaigns.

Current weakness: benchmark READMEs exist; actual firmware-running tests are pending.

Fix plan: implement all six failing/fixed firmware images.

## 6. "The proof is too weak."

Required evidence: explicit assumptions, equivalence definition, induction over commit-index time.

Current weakness: no mechanized proof.

Fix plan: strengthen theorem with invariants linked to formal/SVA checks.

## 7. "The hardware overhead is too high."

Required evidence: LUT/FF/BRAM/Fmax from a real synthesis flow.

Current weakness: Yosys and FPGA tools are not available locally.

Fix plan: run Yosys and at least one mapped FPGA flow.

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

Current weakness: snapshot baseline is currently planned, not measured.

Fix plan: implement snapshot-size and replay-success baseline.

## 12. "Why does this need hardware?"

Required evidence: hardware sees exact interrupt/MMIO timing and can freeze on failure with low perturbation.

Current weakness: runtime-overhead numbers missing.

Fix plan: quantify software-only instrumentation perturbation versus RTL capture.

## 13. "Why should ASP-DAC/DATE/ICCAD care?"

Required evidence: formal model, synthesizable design, FPGA/synthesis evaluation, and reproducible artifact.

Current weakness: early prototype stage.

Fix plan: complete gates before making a venue-ready claim.

