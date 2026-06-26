# ReplayCapsule-RV

Event-sufficient hardware failure capsules for deterministic replay of embedded RV32I systems.

This repository is a research prototype scaffold. It is intentionally honest about what is implemented now versus what requires external tools or later phases.

Current status:

- Phase 0 repository plan and research-lab ownership scaffold: present.
- Phase 1 minimal SoC/event simulation: six-benchmark Python model and RV32I firmware interpreter present.
- PicoRV32 integration: upstream source vendored, wrapper source present, and twelve firmware smokes pass through the wrapper; full replay/export/compare simulation remains pending.
- Phase 2 event-stream RTL: synthesizable SystemVerilog source files, static RTL checks, directed Icarus simulations, Verilator lint, bounded formal checks, and generic Yosys synthesis evidence present.
- Phase 3/4 property checking and capsule generation: record-side RTL modules present; twelve firmware-running wrapper smokes validate failing and fixed images; full validation pending.
- Phase 5/6/7/8 replay, bug suite, baselines, and ablations: model-level results generated for six benchmarks; RTL smoke capsule export self-compare, missing/duplicate-event, metadata/payload/order-corruption, and PC-context checks plus RTL/firmware-sim alignment rows present; full RTL replay metrics pending.
- Firmware-running RTL simulation and mapped FPGA synthesis: pending local `make`/C++ build support, RISC-V compiler, and mapped flow.
- Paper results: no fabricated numbers; result files are generated only by scripts.

## Quick Start

```powershell
.\scripts\reproduce_all.ps1
```

On Unix-like shells:

```sh
python3 scripts/run_all_tests.py
```

The local gate checks repository structure, event definitions, firmware benchmark pairs, static RTL contracts, directed HDL checks including twelve PicoRV32 wrapper smokes, a seeded RTL-smoke interrupt reproducibility campaign, bounded formal event-tap, event-classifier/slicer, property-checker, hash-signature, MMIO/interrupt loggers, registers, replay-control, replay-mismatch, capsule-buffer, and recorder proof/cover targets when local SMTBMC tools are available, a generated formal coverage matrix, replay parsing/comparison, six model-level bug capsules, replay-comparator negative fixtures, baseline trace sizes, ablations, generic Yosys synthesis and derived generic cell-overhead context when available, and SVG figure generation. Full benchmark RTL replay/export/compare simulation and mapped FPGA synthesis are reported as unavailable when the required tools are not installed.

## Research Claim

ReplayCapsule-RV defines and implements a minimal event-sufficiency model for deterministic replay of embedded RV32I failures caused by asynchronous interrupts and memory-mapped I/O. The same lightweight hardware event stream drives runtime safety checking and compact replay-capsule generation without relying on full instruction traces or full-system snapshots.

The project does not claim novelty for generic runtime monitors, trace compression, post-silicon debug tracing, snapshots, or deterministic replay in general.

## Main Directories

- `rtl/`: Replay capsule hardware modules.
- `rtl/rv32i_integration/`: SoC integration scaffold.
- `firmware/`: Embedded firmware examples and bug benchmark descriptions.
- `tb/`: System, replay, and future Verilator/cocotb tests.
- `formal/`: assumptions, theorem, SVA checks, and bounded SMTBMC harnesses.
- `scripts/`: reproducible experiment and test drivers.
- `docs/`: architecture, model, novelty, methodology, and reviewer materials.
- `paper/`: paper draft package.

## Current Evidence

- Model-level replay: `results/processed/replay_experiments.csv`
- Replay comparator negative tests: `results/processed/replay_negative_tests.csv`
- Firmware-sim replay: `results/processed/firmware_sim_replay.csv`
- RTL smoke capsule exports: `results/processed/rtl_capsule_exports.csv`
- RTL smoke capsule event classes: `results/processed/rtl_capsule_event_classes.csv`
- RTL/firmware-sim alignment: `results/processed/rtl_firmware_alignment.csv`
- Seeded RTL-smoke interrupt campaign: `results/processed/randomized_interrupt_campaign.csv`
- Firmware images: `firmware/build/`
- Baseline sizes and replay success: `results/processed/trace_sizes.csv`
- Ablations: `results/processed/ablations.csv`
- Static RTL check summary: `scripts/static_rtl_checks.py`
- Directed HDL checks: `results/processed/hdl_checks.csv`
- Bounded formal checks: `results/processed/formal_checks.csv`
- Formal coverage matrix: `results/processed/formal_coverage.csv` and `docs/formal_coverage_matrix.md`
- Generic Yosys synthesis: `results/processed/synthesis.csv`
- Generic cell-overhead context: `results/processed/synthesis_overhead.csv`
- Generated figures: `results/figures/` and `paper/figures/`

Rows marked `model` are executable event-model evidence. Rows marked `firmware-sim` execute RV32I instruction words in the local interpreter. The current HDL rows include directed module simulations, Verilator lint, and twelve PicoRV32 wrapper smokes, but not the full six-benchmark RTL replay suite.
