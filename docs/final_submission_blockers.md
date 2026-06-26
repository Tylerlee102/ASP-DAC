# Final Submission Blockers

Generated blocker classification date: 2026-06-26.

Authoritative gate source: `docs/conference_readiness_dashboard.md`.

## Fatal Before Submission

| Blocker | Gate | Why fatal | Exact unblock |
| --- | --- | --- | --- |
| Firmware is not compiler-backed locally | G1/G5 | The RTL harness uses verified HEX fallback images, not a fresh local RISC-V compiler flow. | Run `.github/workflows/final-reproduce.yml`, which installs `riscv64-unknown-elf-gcc`/`objcopy`/`size`, requires compiler-backed `results/processed/firmware_build.csv` rows, disables fallback for full RTL replay, and uploads the generated evidence. |
| Full-core mapped overhead evidence is unavailable | G13 | A hardware/EDA venue will expect baseline-versus-ReplayCapsule mapped resource/timing numbers for overhead claims. The current evidence has scoped tiny iCE40 PASS rows, but PicoRV32 and wrapper mapped rows still fail placement. | Retarget or constrain the full-core Yosys + nextpnr flow, or use Vivado, Quartus, OpenROAD, or another documented mapped flow, then regenerate `results/processed/mapped_synthesis.csv` and `results/processed/mapped_overhead.csv` with comparable full-core PASS rows. |
| Runtime overhead / perturbation is blocked | G14 | Hardware replay instrumentation needs measured execution impact. Current-harness wall-clock rows exist, but there is no comparable baseline core wrapper or recorder-disabled top. | Add script-backed baseline-versus-recorder firmware-running RTL or hardware measurements, or remove runtime-overhead claims entirely. |
| Paper PDF build is not yet a PASS | G16 | A submission needs a compiled paper and audit-clean source. | Run `.github/workflows/final-reproduce.yml` or another LaTeX-equipped CI/container path and commit only generated build-status evidence, not fake PDFs. |

## Serious but Acceptable if Caveated

| Issue | Gate | Required caveat |
| --- | --- | --- |
| Formal theorem is a written proof sketch plus bounded local evidence | G11 | Do not claim a mechanized end-to-end proof. |
| Full RTL replay is host-driven | G5/G7 | State that replay is driven by the Verilator host harness and do not claim a synthesizable replay-consume datapath. |
| Full RTL negative tests have two NA cases | G8 | State that 10 replay-critical corruptions reject and 2 cases are not applicable in the current commit-index harness. |
| Synthetic scaling workloads are model-level | G10 | Do not use them as firmware-running or hardware scaling evidence. |
| Final CI is newly added | G1 | Treat `.github/workflows/final-reproduce.yml` as the source-of-truth path, but do not claim compiler-backed firmware or paper PDF until remote logs and uploaded artifacts prove them. |

## Nice-to-Have

| Item | Benefit |
| --- | --- |
| Convert generated SVG figures to PDF for direct LaTeX inclusion | Cleaner paper build and camera-ready figure quality. |
| Add a longer real firmware workload family | Stronger response to toy-benchmark criticism. |
| Add a core-only capsule implementation | Completes the baseline table without TODO rows. |
| Add script-level comparison against standard trace encodings | Better related-work and baseline defense. |

## Future Work

| Item | Scope |
| --- | --- |
| Multicore replay | Requires memory-interleaving and shared-state event model. |
| DMA and cache/coherence events | Requires platform-level event contracts beyond the current single-hart scope. |
| Peripheral-internal replay | Requires device-state modeling or richer replay-visible boundary events. |
| Deployment perturbation study | Requires hardware or high-fidelity firmware-running RTL timing setup. |

## Submission Decision

NOT READY.

The repository is much closer to an honest artifact package than before because full RTL replay is 45/45 PASS and scoped tiny iCE40 mapping now has baseline and recorder PASS rows. The final CI workflow now exists for the missing compiler/LaTeX evidence, but the precise reason not to submit yet is that remote CI still needs to prove compiler-backed firmware, paper-PDF output, and any stronger full-core/runtime evidence.
