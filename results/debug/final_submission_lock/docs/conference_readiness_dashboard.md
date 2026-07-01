# Conference Readiness Dashboard

Last updated from locked evidence: CI run latest successful final-reproduce run on master, commit `current master commit`.

Current status: SUBMISSION-READY CANDIDATE.

| Gate | Status | Evidence |
| --- | --- | --- |
| Compiler-backed firmware | PASS | 15/15 rows in `results/processed/firmware_build.csv` |
| Full RTL replay | PASS | 45/45 rows in `results/processed/full_rtl_replay.csv` |
| Negative replay | PASS | 10 rejects, 0 unexpected accepts, 2 NA in `results/processed/full_rtl_replay_negative.csv` |
| Runtime overhead | PASS | baseline, disabled-recorder, and enabled-recorder rows in `results/processed/runtime_overhead_summary.csv` |
| Full-core mapped overhead | PASS | same-target ECP5 rows in `results/processed/mapped_synthesis.csv`, `results/processed/mapped_overhead.csv`; selected v2 minimal overhead plus measured core/hashed comparisons in `results/processed/mapped_scaling_v2_measured.csv` |
| ASIC/open-PDK physical flow | PASS-SCOPE-LIMITED | 5/5 OpenROAD placed/global-routed Nangate45 rows in `results/processed/asic_openpdk.csv` with parsed area, WNS/TNS, and power; not detailed-route signoff, tapeout, silicon, or energy |
| Minimal recorder fidelity | PASS | `tb_rcv2_minimal_recorder` row in `results/processed/hdl_checks.csv` |
| Focused standalone self-replay matrix | PASS-SCOPE-LIMITED | 42/42 rows in `results/processed/standalone_self_replay_smokes.csv` use `rtl_self_replay_soc` with captured/source-sent/consumer-consumed count agreement, including 3 IRQ rows with matching nonzero PicoRV32 record/replay interrupt-handler entry counts, plus `tb_picorv32_standalone_self_replay_smoke`, `verilator_lint_replaycapsule_v2_self_replay_top`, and `verilator_lint_replaycapsule_v2_self_replay_soc` rows in `results/processed/hdl_checks.csv`; not a board/silicon replay flow |
| Recorder presence | PASS | `results/processed/mapped_recorder_presence.csv` |
| Second-core wrapper/replay-smoke breadth | PASS-SCOPE-LIMITED | FemtoRV32 Quark source, license, pin, ReplayCapsule wrapper lint/synthesis, one compiler-built capture smoke, a v1 RTL packet checker, a scoped v1 MMIO replay driver, 56/56 focused capsule-derived replay rows across v1 capture profiles in `results/processed/second_core_replay_smokes.csv`, and 126/126 scoped seeded v2 MMIO replay-consumer rows across 14 benchmark families and 3 seeds with replay-side host perturbations and property-signature equality in `results/processed/second_core_v2_smokes.csv`; no true CPU interrupt/ISR or full v2 MMIO+IRQ second-core replay claim |
| Interrupt-capable second-core candidate | PASS-SCOPE-LIMITED | Hazard3 is vendored and pinned with Apache-2.0 license metadata; 11 PASS checks plus 1 scope-boundary row in `results/processed/second_core_irq_candidate.csv`, including external/software/timer IRQ ports, machine CSR/MRET support, and Verilator frontend lint |
| Hazard3 true ISR firmware smoke | PASS-SCOPE-LIMITED | 1/1 focused Icarus row in `results/processed/hazard3_irq_smoke.csv` builds RV32I+Zicsr firmware, asserts a machine external interrupt, observes one ISR marker, one IRQ ack, `mret` return to foreground done, and final IRQ deassertion |
| Hazard3 v2 MMIO+IRQ replay benchmark matrix | PASS-SCOPE-LIMITED | 48/48 seeded Icarus rows in `results/processed/hazard3_v2_replay_smoke.csv` wrap Hazard3 with the selected v2 recorder and RTL replay consumer across 8 workload families, 2 recorder configs, and 3 seeds; rows perturb replay-side host sensor input, keep replay external IRQ deasserted, drive MMIO and IRQ from the capsule stream, and reproduce the recorded property signature |
| Paper build | PASS | `results/processed/paper_build_status.csv` |
| Claim/number/TODO audits | PASS | `results/processed/claim_audit.csv`, `paper_number_audit.csv`, `todo_audit.csv` |
| Artifact package | PASS | `dist/replaycapsule-rv-artifact.zip` and `results/processed/artifact_manifest.csv` |

## Allowed Claims

- Event-sufficient capsules for scoped single-hart RV32I interrupt/MMIO failures.
- Compiler-backed full RTL replay for the generated benchmark rows.
- v2 RTL capsule-source plus replay-consumer checks for measured MMIO/IRQ replay stimulus.
- v2 replay-mode-controller captured-store self-replay handoff rows.
- Reusable v2 RTL self-replay SoC shell plus a 42/42 focused Icarus standalone self-replay matrix, with IRQ rows checking matching nonzero PicoRV32 interrupt-handler entries in record and replay.
- Full RTL corrupted-capsule rejection for replay-critical corruption classes.
- Nangate45 OpenROAD placed/global-routed area, WNS/TNS, and power rows, plus Yosys+ABC synthesis-only standard-cell area rows; explicitly not detailed-route signoff, tapeout, silicon, or energy.
- FemtoRV32 wrapper lint/synthesis plus one firmware capture smoke, a v1 RTL packet checker, a scoped v1 MMIO replay driver, a focused capsule-derived replay-smoke matrix across v1 capture profiles, and scoped seeded v2 MMIO replay-consumer benchmark/config rows with replay-side host perturbations and property-signature equality, explicitly not true CPU interrupt/ISR or full v2 MMIO+IRQ replay on FemtoRV32.
- A pinned Hazard3 interrupt-capable second-core candidate with license metadata, IRQ/CSR/MRET source markers, Verilator frontend lint, a focused RV32I+Zicsr firmware smoke that executes a real machine external interrupt handler and returns through `mret`, and a seeded v2 ReplayCapsule MMIO+IRQ replay-consumer benchmark matrix across multiple Hazard3 firmware workload families and core/hashed recorder configs.
- Measured runtime summaries and same-target full-core ECP5 mapped overhead for the selected v2 minimal recorder profile, with core/hashed retained as diagnostic comparisons.

## Forbidden Claims

- Detailed-route ASIC signoff, tapeout, silicon, or energy.
- Standalone board/silicon replay engine.
- Full operating-system or application-suite ReplayCapsule coverage on a second RV32I core.
- Full v2 MMIO+IRQ replay-consumer stimulus on FemtoRV32.
- Hazard3 full-diagnostic `full` recorder-config replay with all-commit IRQ lookahead.
- Multicore, DMA, cache-coherent, or broad platform support.
- Do not claim replacement for RISC-V trace/debug standards.
- Do not claim globally smallest trace or universal deterministic replay.
