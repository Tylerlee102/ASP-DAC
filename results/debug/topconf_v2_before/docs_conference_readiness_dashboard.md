# Conference Readiness Dashboard

Last updated from locked evidence: CI run latest successful final-reproduce run on master, commit `current master commit`.

Current status: SUBMISSION-READY CANDIDATE.

| Gate | Status | Evidence |
| --- | --- | --- |
| Compiler-backed firmware | PASS | 15/15 rows in `results/processed/firmware_build.csv` |
| Full RTL replay | PASS | 45/45 rows in `results/processed/full_rtl_replay.csv` |
| Negative replay | PASS | 10 rejects, 0 unexpected accepts, 2 NA in `results/processed/full_rtl_replay_negative.csv` |
| Runtime overhead | PASS | baseline, disabled-recorder, and enabled-recorder rows in `results/processed/runtime_overhead_summary.csv` |
| Full-core mapped overhead | PASS | same-target ECP5 rows in `results/processed/mapped_synthesis.csv` and `results/processed/mapped_overhead.csv` |
| Recorder presence | PASS | `results/processed/mapped_recorder_presence.csv` |
| Paper build | PASS | `results/processed/paper_build_status.csv` |
| Claim/number/TODO audits | PASS | `results/processed/claim_audit.csv`, `paper_number_audit.csv`, `todo_audit.csv` |
| Artifact package | PASS | `dist/replaycapsule-rv-artifact.zip` and `results/processed/artifact_manifest.csv` |

## Allowed Claims

- Event-sufficient capsules for scoped single-hart RV32I interrupt/MMIO failures.
- Compiler-backed host-driven full RTL replay for the generated benchmark rows.
- Full RTL corrupted-capsule rejection for replay-critical corruption classes.
- Measured runtime summaries and same-target full-core ECP5 mapped overhead.

## Forbidden Claims

- ASIC area or power.
- Hardware replay-consume datapath.
- Multicore, DMA, cache-coherent, or broad platform support.
- Replacement for RISC-V trace/debug standards.
- Globally smallest trace or universal deterministic replay.
