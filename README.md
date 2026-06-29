# ReplayCapsule-RV

ReplayCapsule-RV captures event-sufficient hardware failure capsules for replaying scoped single-hart RV32I interrupt/MMIO bugs.

## Current Evidence

- Compiler-backed firmware: `15/15` PASS in `results/processed/firmware_build.csv`.
- Full RTL replay: `45/45` PASS in `results/processed/full_rtl_replay.csv`.
- v2 full RTL replay: `135/135` PASS across core, hashed, and full recorder configs in `results/processed/full_rtl_replay_v2.csv`.
- v2 zero-fail measured gate: empty bug inventory in `results/processed/v2_zero_fail_bug_inventory.csv`; see `docs/v2_zero_fail_status.md`.
- v2 workload/buffer/runtime/mapped evidence: `1125/1125` workload replay PASS rows, `6750/6750` v2 measured buffer rows, `25/25` runtime rows, and same-target ECP5 full-core mapped PASS rows in the `*_v2_measured.csv` files.
- v2 new benchmark coverage: `12/12` PASS rows for two added compiler-backed firmware families in `results/processed/expanded_benchmark_replay_measured.csv`.
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
the two added benchmark families, and the zero-fail inventory audit. On Windows
shells where `python3` is a Store alias, pass `PYTHON=/path/to/python`.

## Mapped FPGA Evidence

The full-core mapped rows use realistic board-level I/O and do not expose internal debug buses as top-level FPGA pins. The allowed top-level pins are `clk`, `rst_n`, `uart_rx`, `uart_tx`, `gpio_in[3:0]`, `gpio_out[7:0]`, `status_led[3:0]`, `capsule_event_seen`, `recorder_overflow_seen`, and `recorder_status_xor`.

The checked-in ECP5 scaling evidence preserves same-target PASS rows and the visible P&R timeout row. Overhead claims are allowed only for rows where both baseline and ReplayCapsule place-and-route pass on the same target and recorder presence is confirmed.

Claim-allowed ECP5 overhead ranges are reported in `results/processed/mapped_scaling_summary.csv`: LUT `+124.66%` to `+182.55%`, FF `+341.79%` to `+646.43%`, BRAM `+0.00%`, and Fmax `-25.70%` to `-17.53%`. These are high area overheads, not low-overhead results.

For v2, same-target full-core ECP5 measured rows are in
`results/processed/mapped_scaling_v2_measured.csv` at memory 128 and buffer
depth 16. The companion overhead table
`results/processed/mapped_scaling_overhead_v2_measured.csv` marks all v2
core/hashed/full overhead comparisons as claim-allowed.

## Scope And Limitations

Allowed claims:

- Event-sufficient capsules for scoped single-hart RV32I interrupt/MMIO failures.
- Compiler-backed host-driven full RTL replay for the generated benchmark suite.
- Full RTL corrupted-capsule rejection for replay-critical corruption classes.
- Runtime overhead for the fixed workload set.
- Same-target ECP5 mapped overhead for claim-allowed PASS comparison points.
- Measured v2 zero-fail evidence for the scoped v2 benchmark, scaling, runtime,
  mapped, and expanded-benchmark rows listed in `docs/v2_zero_fail_status.md`.

Forbidden claims:

- Area overhead minimization.
- ASIC implementation, timing, or energy results.
- Autonomous hardware replay-consume datapath.
- Multicore, DMA, cache-coherent, or broad platform support.
- Replacement for RISC-V trace/debug standards.
- Globally smallest trace or deterministic replay outside the stated RV32I interrupt/MMIO scope.

## Main Directories

- `rtl/`: ReplayCapsule RTL modules and mapped board wrappers.
- `firmware/`: compiler-built firmware benchmarks.
- `tb/`: Verilator and replay-comparator harnesses.
- `scripts/`: reproduction, audit, table, figure, synthesis, and packaging scripts.
- `paper/`: ACM/ASP-DAC-style paper source and generated table/figure assets.
- `docs/`: reviewer-facing model, evidence, limitation, and submission docs.
- `results/processed/`: generated CSV evidence.
