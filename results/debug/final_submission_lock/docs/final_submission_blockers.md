# Final Submission Blockers

Generated from locked evidence: CI run latest successful final-reproduce run on master.

## Fatal Before Submission

No fatal evidence blocker remains in the locked CI artifact.

## Serious Limitations To State Clearly

| Limitation | Required handling |
| --- | --- |
| Host-driven replay consume path | Claim only the measured host-streamed full-core consumer check; do not claim autonomous hardware replay. |
| Single-hart RV32I scope | Do not claim multicore, DMA, or cache-coherence support. |
| ECP5 overhead is not optimized | Report the measured overhead and state that replay fidelity and auditability were prioritized over area minimization. |
| No ASIC flow | Do not claim ASIC area, timing, or power. |
| Benchmark scope | Present the six generated families as evaluation evidence, not complete embedded coverage. |

## Submission Decision

SUBMISSION-READY CANDIDATE, assuming the paper keeps the limitations above explicit and the artifact is submitted with the locked evidence bundle.
