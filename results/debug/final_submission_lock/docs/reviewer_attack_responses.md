# Reviewer Attack Responses

Each answer cites generated evidence files rather than relying on unsupported prose.

## 1. Is this just trace compression?

No. ReplayCapsule-RV records commit-indexed replay-driving interrupt/MMIO boundary events for a scoped failure class. The replay evidence is `results/processed/full_rtl_replay.csv`; trace-size and baseline context is generated separately in `results/processed/baseline_comparison.csv`.

## 2. Why not use RISC-V trace?

RISC-V trace and debug standards provide broader observability. ReplayCapsule-RV targets a narrower replay object: the boundary events needed by the host-driven replay harness. The paper must state complementarity, not replacement.

## 3. Is the replay hardware synthesizable?

The record-side RTL and board wrappers are synthesized and placed. The replay-consume path is host-driven. Evidence: `results/processed/mapped_synthesis.csv`, `results/processed/full_core_mapped_summary.csv`, and `results/processed/full_rtl_replay.csv`.

## 4. Why is overhead high?

The prototype prioritizes replay fidelity and auditability over area minimization. Full-core ECP5 overhead is reported in `results/processed/mapped_overhead.csv`: LUT 143.75%, FF 341.79%, BRAM 0.00%, Fmax delta -20.12%.

## 5. Why only single-hart?

The model assumes deterministic single-hart RV32I execution between recorded boundary events. Multicore ordering, DMA, and cache-coherence effects require additional event contracts and are listed as limitations in the paper and docs.

## 6. Why host-driven replay?

Host-driven replay lets the artifact validate event sufficiency and corruption rejection without claiming a replay-consume datapath. Evidence: `results/processed/full_rtl_replay.csv` and `results/processed/full_rtl_replay_negative.csv`.

## 7. Does this generalize beyond toy benchmarks?

The current evidence covers six firmware bug families and 45/45 compiler-backed full RTL rows. Broader firmware suites are future work; the current claim should stay scoped to these generated benchmarks.

## 8. Can the recorder be optimized away?

Recorder presence is checked in mapped artifacts. Evidence: `results/processed/mapped_recorder_presence.csv`, which reports recorder hierarchy, capsule buffer, status logic, and top outputs as present for the passing ECP5 row.

## 9. Are the results compiler-backed?

Yes for the locked CI evidence: `results/processed/firmware_build.csv` has 15/15 compiler-C PASS rows, and `results/processed/full_rtl_replay.csv` marks the replay rows as compiler-backed.

## 10. Can corrupted capsules pass?

The full RTL corrupted-capsule ledger reports 10 rejected replay-critical corruptions, 0 unexpected accepts, and 2 not-applicable rows in `results/processed/full_rtl_replay_negative.csv`.
