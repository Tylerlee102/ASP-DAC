# ReplayCapsule-RV

ReplayCapsule-RV captures event-sufficient hardware failure capsules for replaying scoped single-hart RV32I interrupt/MMIO bugs.

## Current Evidence

- Compiler-backed firmware: `15/15` PASS in `results/processed/firmware_build.csv`.
- Full RTL replay: `45/45` PASS in `results/processed/full_rtl_replay.csv`.
- v2 full RTL replay: `135/135` PASS across core, hashed, and full recorder configs with RTL consumer checks in `results/processed/full_rtl_replay_v2.csv`.
- Focused standalone self-replay matrix: reusable RTL self-replay SoC shell plus 42 Icarus rows record 14 PicoRV32 v2 base, expanded, profile2, and realistic-control MMIO/interrupt/watchdog failures across core, hashed, and full recorder configs, reset the core, launch captured-store replay, and require captured/source-sent/consumer-consumed word counts to match in `results/processed/standalone_self_replay_smokes.csv`; the IRQ-triggered rows also require matching nonzero PicoRV32 interrupt-handler entry counts in record and replay.
- v2 zero-fail measured gate: empty bug inventory in `results/processed/v2_zero_fail_bug_inventory.csv`; see `docs/v2_zero_fail_status.md`.
- v2 workload/buffer/runtime/mapped evidence: `1125/1125` workload replay PASS rows, `1125/1125` v2 measured buffer rows at the measured depth, `25/25` runtime rows, a same-target ECP5 selected minimal-recorder overhead claim, and measured core/hashed diagnostic comparison rows in the `*_v2_measured.csv` files.
- v2 expanded benchmark coverage: `144/144` PASS rows for eight compiler-backed firmware families across three seeds and three recorder configs in `results/processed/expanded_benchmark_replay_measured.csv`, including two alternate-MMIO-profile families and two realistic-control families.
- Second-core breadth: FemtoRV32 Quark is vendored with BSD-3-Clause license metadata, has ReplayCapsule v1/v2 wrappers, passes wrapper lint plus generic Yosys synthesis, runs one compiler-built capture smoke, adds a v1 RTL packet checker plus a scoped v1 MMIO replay driver, runs 56 focused capsule-derived replay smokes over 14 base/expanded benchmark families and four v1 capture profiles in `results/processed/second_core_replay_smokes.csv`, and adds 126/126 scoped seeded v2 MMIO replay-consumer rows over 14 benchmark families, 3 seeds, and core/hashed/full configs with replay-side host perturbations and property-signature equality in `results/processed/second_core_v2_smokes.csv`; this is not a true CPU interrupt/ISR or full v2 MMIO+IRQ replay-consumer claim.
- Interrupt-capable second-core candidate: Hazard3 is vendored and pinned under `third_party/hazard3` with Apache-2.0 license metadata, external/software/timer IRQ ports, machine CSR/MRET support markers, a passing Verilator frontend probe in `results/processed/second_core_irq_candidate.csv`, a focused RV32I+Zicsr true-ISR firmware smoke in `results/processed/hazard3_irq_smoke.csv`, and a 48-row seeded v2 MMIO+IRQ ReplayCapsule replay-consumer benchmark matrix in `results/processed/hazard3_v2_replay_smoke.csv` across 8 Hazard3 workload families, 2 recorder configs, and 3 seeds.
- ASIC/open-PDK evidence: Nangate45 Yosys+ABC area rows plus 5/5 OpenROAD placed/global-routed rows PASS for baseline plus minimal/core/hashed/full v2 configurations in `results/processed/asic_openpdk.csv`; these are OpenROAD global-route physical-flow rows, not detailed-route signoff, tapeout, or energy results.
- Full RTL negative replay: `10` replay-critical corruptions rejected, `0` unexpected accepts, `2` not-applicable rows in `results/processed/full_rtl_replay_negative.csv`.
- Runtime overhead: measured for the fixed workload set in `results/processed/runtime_overhead.csv` and `results/processed/runtime_overhead_summary.csv`.
- Full-core mapped overhead: PASS for same-target ECP5 claim-allowed points in `results/processed/full_core_mapped_summary.csv`; mapped scaling has 9 PASS rows and 1 visible P&R timeout row in `results/processed/mapped_scaling.csv`.
- Paper: `paper/main.pdf` builds, with audits in `results/processed/claim_audit.csv`, `results/processed/paper_number_audit.csv`, and `results/processed/todo_audit.csv`.
- Artifact: `dist/replaycapsule-rv-artifact.zip` and `dist/replaycapsule-rv-topconf-artifact.zip`.

## Evidence Quick Links

- Paper PDF: `paper/main.pdf`
- Main artifact: `dist/replaycapsule-rv-artifact.zip`
- Top-conference artifact: `dist/replaycapsule-rv-topconf-artifact.zip`
- Firmware evidence: `results/processed/firmware_build.csv`
- Full RTL replay evidence: `results/processed/full_rtl_replay.csv`
- v2 zero-fail status: `docs/v2_zero_fail_status.md`
- v2 full RTL replay evidence: `results/processed/full_rtl_replay_v2.csv`
- v2 measured workload scaling: `results/processed/workload_scaling_v2_measured.csv`
- v2 measured buffer sensitivity: `results/processed/buffer_sensitivity_v2_measured.csv`
- v2 measured runtime scaling: `results/processed/runtime_scaling_v2_measured.csv`
- v2 measured mapped overhead: `results/processed/mapped_scaling_v2_measured.csv` and `results/processed/mapped_scaling_overhead_v2_measured.csv`
- v2 new benchmark replay: `results/processed/expanded_benchmark_replay_measured.csv`
- Second-core breadth evidence: `docs/second_core_breadth.md`, `docs/second_core_replay_smokes.md`, `docs/second_core_v2_smokes.md`, `docs/second_core_irq_candidate.md`, `docs/hazard3_irq_smoke.md`, `docs/hazard3_v2_replay_smoke.md`, `results/processed/second_core_breadth.csv`, `results/processed/second_core_replay_smokes.csv`, `results/processed/second_core_v2_smokes.csv`, `results/processed/second_core_irq_candidate.csv`, `results/processed/hazard3_irq_smoke.csv`, and `results/processed/hazard3_v2_replay_smoke.csv`
- Standalone self-replay matrix: `docs/standalone_self_replay_smokes.md` and `results/processed/standalone_self_replay_smokes.csv`
- Scope-limited ASIC/open-PDK evidence: `docs/asic_openpdk_evidence.md`, `results/processed/asic_openpdk.csv`, `results/processed/asic_openpdk_overhead.csv`, `results/processed/asic_openpdk_yosys_area.csv`, and `results/processed/asic_openpdk_yosys_area_overhead.csv`
- Negative replay evidence: `results/processed/full_rtl_replay_negative.csv`
- Workload scaling: `results/processed/workload_scaling.csv`
- Capsule baselines: `results/processed/capsule_baseline_comparison.csv` and `results/processed/capsule_baseline_summary.csv`
- Buffer sensitivity: `results/processed/buffer_sensitivity.csv` and `results/processed/buffer_sensitivity_summary.csv`
- Runtime scaling: `results/processed/runtime_scaling.csv` and `results/processed/runtime_scaling_summary.csv`
- Event ablation scaling: `results/processed/event_ablation_scaling.csv`
- Mapped ECP5 evidence: `results/processed/mapped_scaling.csv`, `results/processed/mapped_scaling_overhead.csv`, `results/processed/mapped_scaling_summary.csv`, `results/processed/mapped_recorder_presence.csv`, and `results/processed/full_core_mapped_summary.csv`
- Artifact manifest: `results/processed/artifact_manifest.csv`
- Reviewer audit: `docs/top_conference_reviewer_audit.md`

## GitHub Actions

The top-conference CI entry point is `.github/workflows/topconf-full.yml`. It installs the RISC-V compiler, Verilator, Yosys, nextpnr ECP5/iCE40 tools, and LaTeX, then runs:

```sh
make check-toolchain
make firmware
make full-rtl-replay
make full-rtl-negative
make workload-scaling-full
make capsule-baselines-full
make buffer-sensitivity-full
make runtime-scaling-full
make event-ablation-scaling-full
make mapped-scaling-full
make paper
make paper-audit
make artifact
```

The workflow uploads `replaycapsule-rv-topconf-full-evidence`. Package installation is accounted for in `results/processed/apt_install_status.csv`; any required package failure exits the workflow directly. The previous exit-code-2 annotation was an installer-loop issue in the older reproduction workflow and is not used as evidence.

## Local Reproduction

Full checked-in reproduction:

```sh
make reproduce
```

On Windows, use the checked-in wrapper so the repo can find a real Python 3
runtime even when `python` is a Microsoft Store alias:

```powershell
.\scripts\reproduce_all.ps1
```

Top-conference evaluation package:

```sh
make topconf-full
```

Focused commands:

```sh
make mapped-synth
make mapped-scaling-full
make topconf-tables
make topconf-figures
make paper
make paper-audit
make artifact
make topconf-artifact
```

Measured v2 zero-fail evidence:

```sh
make topconf-v2-measured
make replay-consumer-v2
```

The measured v2 path runs the full v2 workload/buffer/runtime/mapped evidence,
the expanded benchmark families, and the zero-fail inventory audit. On Windows
shells, prefer `.\scripts\reproduce_all.ps1` or pass `PYTHON=/path/to/python`.

## Mapped FPGA Evidence

The full-core mapped rows use realistic board-level I/O and do not expose internal debug buses as top-level FPGA pins. The allowed top-level pins are `clk`, `rst_n`, `uart_rx`, `uart_tx`, `gpio_in[3:0]`, `gpio_out[7:0]`, `status_led[3:0]`, `capsule_event_seen`, `recorder_overflow_seen`, and `recorder_status_xor`.

The checked-in ECP5 scaling evidence preserves same-target PASS rows and the visible P&R timeout row. Overhead claims are allowed only for rows where both baseline and ReplayCapsule place-and-route pass on the same target and recorder presence is confirmed.

Claim-allowed ECP5 overhead ranges are reported in `results/processed/mapped_scaling_summary.csv`: LUT `+124.66%` to `+182.55%`, FF `+341.79%` to `+646.43%`, BRAM `+0.00%`, and Fmax `-25.70%` to `-17.53%`. These are high area overheads, not low-overhead results.

For v2, same-target full-core ECP5 measured rows are in
`results/processed/mapped_scaling_v2_measured.csv` at memory 128. The selected
minimal recorder profile passes at buffer depth 8 with `+8.26%` LUT, `+3.77%`
FF, `+0.00%` BRAM, and `-0.04%` Fmax. The core and hashed configs remain
measured diagnostic comparison rows at the same depth, not the selected area
claim: `+68.00%` and `+67.69%` LUT, respectively, with `+81.49%` FF.

## Scope And Limitations

Allowed claims:

- Event-sufficient capsules for scoped single-hart RV32I interrupt/MMIO failures.
- Compiler-backed full RTL replay for the generated benchmark suite.
- v2 RTL capsule-source plus replay-consumer checks for the measured v2 replay rows; the RTL source streams capsule words and the consumer drives MMIO/IRQ replay stimulus.
- v2 replay-mode-controller self-replay handoff from the captured RTL store without harness-preloaded capsule words in `results/processed/self_replay_handoff_v2.csv`.
- Reusable v2 RTL self-replay SoC shell plus a 42-row focused Icarus standalone self-replay matrix with explicit IRQ-entry equality on the IRQ rows.
- Pinned Hazard3 interrupt-capable second-core candidate with license/source metadata, frontend lint, a focused true-ISR firmware smoke, and a 48-row seeded v2 MMIO+IRQ ReplayCapsule replay-consumer benchmark matrix across 8 workload families, 2 recorder configs, and 3 seeds.
- FemtoRV32 Quark wrapper/replay-smoke breadth only: a second RV32I core is vendored, wrapped, linted, generically synthesized, run through one compiler-built capture smoke, checked with a v1 RTL packet checker, given a scoped v1 MMIO replay driver, run through 56 focused capsule-derived replay smokes over base/expanded benchmark families and four v1 capture profiles, and checked with 126 scoped seeded v2 MMIO replay-consumer benchmark/config rows that perturb replay-side host MMIO inputs and reproduce the property signature.
- Full RTL corrupted-capsule rejection for replay-critical corruption classes.
- Runtime overhead for the fixed workload set.
- Same-target ECP5 mapped overhead for the selected v2 minimal recorder profile, with diagnostic rows reported separately.
- OpenROAD Nangate45 placed/global-routed area, timing, and power rows for baseline plus v2 minimal/core/hashed/full configurations, with detailed-route/signoff/tapeout/energy explicitly out of scope.
- Measured v2 zero-fail evidence for the scoped v2 benchmark, scaling, runtime,
  mapped, and expanded-benchmark rows listed in `docs/v2_zero_fail_status.md`.

Forbidden claims:

- Area overhead minimization.
- Detailed-routed ASIC signoff, tapeout, silicon, or energy results.
- Standalone board/silicon replay engine independent of testbench reset orchestration and the focused reusable memory/MMIO/IRQ/watchdog shell.
- True CPU interrupt/ISR replay or full v2 MMIO+IRQ replay-consumer stimulus on FemtoRV32.
- Hazard3 full-diagnostic `full` recorder-config replay with all-commit IRQ lookahead.
- ASIC claims beyond the generated OpenROAD global-routed Nangate45 area/timing/power rows.
- Multicore, DMA, cache-coherent, or broad platform support.
- Do not claim replacement for RISC-V trace/debug standards.
- Globally smallest trace or deterministic replay outside the stated RV32I interrupt/MMIO scope.

## Main Directories

- `rtl/`: ReplayCapsule RTL modules and mapped board wrappers.
- `third_party/`: vendored PicoRV32, FemtoRV32, and Hazard3 source snapshots with license metadata.
- `firmware/`: compiler-built firmware benchmarks.
- `tb/`: Verilator and replay-comparator harnesses.
- `scripts/`: reproduction, audit, table, figure, synthesis, and packaging scripts.
- `paper/`: ACM/ASP-DAC-style paper source and generated table/figure assets.
- `docs/`: reviewer-facing model, evidence, limitation, and submission docs.
- `results/processed/`: generated CSV evidence.
