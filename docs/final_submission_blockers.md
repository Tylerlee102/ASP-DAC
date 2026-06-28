# Final Submission Blockers

Generated from locked evidence: CI run latest successful final-reproduce run on master.

## Fatal Before Submission

No fatal evidence blocker remains in the locked CI artifact.

## Serious Limitations To State Clearly

| Limitation | Required handling |
| --- | --- |
| Host-driven replay consume path | Do not claim a synthesizable replay-consume datapath. |
| Single-hart RV32I scope | Do not claim multicore, DMA, or cache-coherence support. |
| ECP5 overhead is not optimized | Report the measured overhead and state that replay fidelity and auditability were prioritized over area minimization. |
| No ASIC flow | Do not claim ASIC area, timing, or power. |
| Benchmark scope | Present the original six generated families plus the two v2 expansion families as scoped evaluation evidence, not complete embedded coverage. |
| v2 replay-consume scope | The v2 replay-consume controller is tested RTL, but the full-core replay flow is still host-driven. Do not claim autonomous full-core hardware replay. |

## Submission Decision

SUBMISSION-READY CANDIDATE for the scoped v2 zero-fail gate as well, assuming the paper keeps the limitations above explicit and the artifact is submitted with the measured evidence bundle.
