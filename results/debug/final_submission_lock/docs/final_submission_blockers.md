# Final Submission Blockers

Generated from locked evidence: CI run latest successful final-reproduce run on master.

## Fatal Before Submission

No fatal evidence blocker remains in the locked CI artifact.

## Serious Limitations To State Clearly

| Limitation | Required handling |
| --- | --- |
| Full replay matrix still uses Verilator orchestration | Claim the measured RTL source/consumer, captured-store checks, and focused Icarus standalone matrix; do not claim a board/silicon replay engine. |
| Single-hart RV32I scope | Do not claim multicore, DMA, or cache-coherence support. |
| Second-core breadth is still focused | FemtoRV32 Quark is vendored, wrapped, linted, generically synthesized, run through one capture smoke, checked with a v1 RTL packet checker, uses a scoped v1 MMIO replay driver for replay reads, runs focused capsule-derived replay rows across v1 capture profiles, and has scoped seeded v2 MMIO replay-consumer benchmark/config rows with replay-side host perturbations and property-signature equality. Hazard3 now has a focused true-ISR smoke plus a seeded v2 MMIO+IRQ replay-consumer matrix across core/hashed recorder configs. Do not claim OS/application-suite coverage or full-diagnostic all-commit Hazard3 replay. |
| ECP5 diagnostic overhead is not optimized | Report the selected v2 minimal recorder profile separately from diagnostic-rich core/hashed and legacy mapped rows. |
| ASIC flow is OpenROAD global-route only | Claim generated Nangate45 placed/global-routed area, timing, and power rows; do not claim detailed-route signoff, tapeout, silicon, or energy. |
| Benchmark scope | Present the generated base and expanded families as evaluation evidence, not complete embedded coverage. |

## Submission Decision

SUBMISSION-READY CANDIDATE, assuming the paper keeps the limitations above explicit and the artifact is submitted with the locked evidence bundle.
