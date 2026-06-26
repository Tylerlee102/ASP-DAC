# ReplayCapsule-RV

Event-sufficient hardware failure capsules for deterministic replay of embedded RV32I systems.

This repository is a research prototype scaffold. It is intentionally honest about what is implemented now versus what requires external tools or later phases.

Current status:

- Phase 0 repository plan and research-lab ownership scaffold: present.
- Phase 1 minimal SoC/event simulation: six-benchmark Python model and RV32I firmware interpreter present.
- PicoRV32 integration: upstream source vendored, wrapper source present, fifteen firmware smokes pass through the wrapper, and the Verilator harness under `tb/verilator` builds and runs full record/replay rows; current evaluated full RTL replay evidence is 45/45 PASS.
- Phase 2 event-stream RTL: synthesizable SystemVerilog source files, static RTL checks, directed Icarus simulations, Verilator lint, bounded formal checks, and generic Yosys synthesis evidence present.
- Phase 3/4 property checking and capsule generation: record-side RTL modules present; fifteen firmware-running wrapper smokes validate failing, fixed, and no-failure edge images; evaluated host-driven full RTL record/replay rows pass.
- Phase 5/6/7/8 replay, bug suite, baselines, and ablations: model-level results generated for six benchmarks; RTL smoke capsule export self-compare, missing/duplicate-event, metadata/payload/order-corruption, and PC-context checks plus RTL/firmware-sim alignment rows present; full RTL replay metrics are generated with 45/45 PASS rows.
- Firmware-running RTL simulation: the local Verilator simulator builds and executes with verified firmware HEX fallback images, not compiler-backed firmware. The evaluated host-driven full RTL record/replay suite passes all 45 benchmark/variant/seed rows.
- Mapped FPGA synthesis: Yosys + nextpnr-ice40 is attempted by script; scoped tiny iCE40 rows place and route for `replaycapsule_tiny_baseline` and `replaycapsule_recorder_tiny`. The recorder tiny configuration reports 372 LUT, 205 FF, and 77.40 MHz Fmax; the tiny baseline reports 46 LUT, 32 FF, and 157.51 MHz Fmax. PicoRV32/full-recorder/wrapper rows still fail placement, so no full-core mapped overhead is claimed.
- Paper results: no fabricated numbers; result files are generated only by scripts.

## Quick Start

Preferred on CI, Docker, or a machine with `make`:

```sh
make reproduce
```

The strict final CI source-of-truth path is:

```text
.github/workflows/final-reproduce.yml
```

That workflow installs the RISC-V compiler and LaTeX packages on Ubuntu,
requires compiler-backed firmware (`REQUIRE_COMPILER=1`), disables fallback
firmware for full RTL replay (`ALLOW_FALLBACK=0`), builds the paper, runs
audits, packages the artifact, and uploads `results/`, `paper/main.pdf`, and
`dist/replaycapsule-rv-artifact.zip`.

On this Windows workspace, if `make` is unavailable:

```powershell
.\scripts\reproduce_all.ps1
```

On Unix-like shells:

```sh
python3 scripts/run_all_tests.py
```

The submission-readiness gate dashboard is the authority for what is measured
and what remains blocked:

```text
docs/conference_readiness_dashboard.md
```

The local gate checks repository structure, event definitions, firmware benchmark pairs, static RTL contracts, directed HDL checks including fifteen PicoRV32 wrapper smokes with generated log-level capsule sanity summaries, a seeded RTL-smoke interrupt reproducibility campaign with generated summary/coverage/corruption ledgers and MMIO wait-state cases, bounded formal event-tap, event-classifier/slicer, property-checker, hash-signature, MMIO/interrupt loggers, registers, replay-control, replay-mismatch, capsule-buffer, and recorder proof/cover targets when local SMTBMC tools are available, a generated formal coverage matrix, a bounded overflow contract ledger, replay parsing/comparison, six model-level bug capsules, replay-comparator negative fixtures, full RTL replay ledgers, baseline trace sizes, ablations, generic Yosys synthesis and derived generic cell-overhead context when available, an attempted iCE40 mapped-flow ledger, SVG figure generation, and a hash manifest for the main generated artifacts. Evaluated host-driven full benchmark RTL replay/export/compare simulation is all-PASS.

## Research Claim

ReplayCapsule-RV defines and implements an event-sufficiency model for deterministic replay of embedded RV32I failures caused by asynchronous interrupts and memory-mapped I/O. The same lightweight hardware event stream drives runtime safety checking and compact replay-capsule generation without relying on full instruction traces or full-system snapshots.

The project does not claim novelty for generic runtime monitors, trace compression, post-silicon debug tracing, snapshots, or deterministic replay in general.

## Main Directories

- `rtl/`: Replay capsule hardware modules.
- `rtl/rv32i_integration/`: SoC integration scaffold.
- `firmware/`: Embedded firmware examples and bug benchmark descriptions.
- `tb/`: System, replay, and Verilator harness tests.
- `formal/`: assumptions, theorem, SVA checks, and bounded SMTBMC harnesses.
- `scripts/`: reproducible experiment and test drivers.
- `docs/`: architecture, model, related-work, methodology, and reviewer materials.
- `paper/`: paper draft package.

## Current Evidence

- Model-level replay: `results/processed/replay_experiments.csv`
- Replay comparator negative tests: `results/processed/replay_negative_tests.csv`
- Firmware-sim replay: `results/processed/firmware_sim_replay.csv`
- Firmware build/fallback ledger: `results/processed/firmware_build.csv`
- RTL smoke capsule exports: `results/processed/rtl_capsule_exports.csv`
- RTL smoke capsule event classes: `results/processed/rtl_capsule_event_classes.csv`
- RTL/firmware-sim alignment: `results/processed/rtl_firmware_alignment.csv`
- Seeded RTL-smoke interrupt campaign: `results/processed/randomized_interrupt_campaign.csv`
- Seeded interrupt campaign summary/coverage: `results/processed/randomized_interrupt_summary.csv` and `results/processed/randomized_interrupt_coverage.csv`
- Seeded interrupt corruption checks: `results/processed/randomized_interrupt_corruption.csv`
- Firmware images: `firmware/build/`
- Baseline sizes and replay success: `results/processed/trace_sizes.csv`
- Model ablations: `results/processed/ablations.csv`
- RTL-smoke ablations: `results/processed/rtl_smoke_ablations.csv` and `results/processed/rtl_smoke_event_sufficiency.csv`
- Static RTL check summary: `scripts/static_rtl_checks.py`
- Directed HDL checks: `results/processed/hdl_checks.csv`
- PicoRV32 smoke log summaries: `results/processed/picorv32_smoke_summary.csv` and `results/processed/picorv32_smoke_coverage.csv`
- Bounded formal checks: `results/processed/formal_checks.csv`
- Formal coverage matrix: `results/processed/formal_coverage.csv` and `docs/formal_coverage_matrix.md`
- Overflow contract ledger: `results/processed/overflow_contracts.csv`
- Proof obligation matrix: `results/processed/proof_obligations.csv` and `docs/proof_obligation_matrix.md`
- Generic Yosys synthesis: `results/processed/synthesis.csv`
- Generic cell-overhead context: `results/processed/synthesis_overhead.csv`
- Evaluation metric rollup: `results/processed/evaluation_metrics.csv`
- Per-benchmark local coverage: `results/processed/benchmark_coverage.csv`
- Claim audit: `results/processed/claim_audit.csv`
- Toolchain status: `results/processed/toolchain_status.csv`
- Artifact hash manifest: `results/processed/artifact_manifest.csv`
- Full RTL replay status ledger: `results/processed/full_rtl_replay.csv`
- Full RTL negative replay status ledger: `results/processed/full_rtl_replay_negative.csv`
- Firmware source comparison ledger: `results/processed/firmware_source_comparison.csv`
- Final GitHub Actions source-of-truth workflow: `.github/workflows/final-reproduce.yml`
- Runtime overhead blocker/current-harness ledger, with no baseline overhead claim: `results/processed/runtime_overhead.csv` and `results/processed/runtime_overhead_summary.csv`
- Event-sufficiency matrix: `results/processed/event_sufficiency_matrix.csv`
- Baseline comparison: `results/processed/baseline_comparison.csv`
- Mapped synthesis status ledger: `results/processed/mapped_synthesis.csv`
- Mapped overhead status ledger: `results/processed/mapped_overhead.csv`
- Artifact package: `dist/replaycapsule-rv-artifact.zip`
- Paper synthesis/resource table: `paper/figures/table01_synthesis_resources.md`
- Paper replay/baseline/ablation/formal/proof/metrics tables: `paper/figures/table02_replay_evidence.md` through `paper/figures/table07_evaluation_metrics.md`
- Generated figures: `results/figures/` and `paper/figures/`

Rows marked `model` are executable event-model evidence. Rows marked `firmware-sim` execute RV32I instruction words in the local interpreter. The current HDL rows include directed module simulations, Verilator lint, fifteen PicoRV32 wrapper smokes, and a host-driven Verilator record/replay harness; the evaluated full six-benchmark RTL replay suite is generated and all-PASS. Local Windows rows remain fallback-backed until the final CI workflow produces compiler-backed firmware and replay rows. Mapped evidence is currently limited to scoped tiny iCE40 configurations, and runtime evidence measures current harness wall-clock rows but not baseline overhead.
