# Paper Figures

This directory is the landing zone for final paper-ready figure and table
assets. It mirrors generated SVG status figures from `../../results/figures/`
and includes generated Markdown table sources derived from `../../results/`.

Do not manually type measurement values into paper figures or tables. Numeric
content must come from generated CSV, JSON, SVG, or synthesis-report artifacts.

## Current Generated Sources

| Source | Generated today? | Role |
| --- | --- | --- |
| `../../results/raw/phase12_sensor_threshold_trace.json` | Yes | Smoke event timeline for model and replay-flow figures. |
| `../../results/processed/replay_experiments.csv` | Yes | Replay-flow status source. |
| `../../results/processed/rtl_capsule_exports.csv` | Yes | RTL-smoke capsule export, missing-event, duplicate-event, metadata-corruption, payload-corruption, order-corruption, and PC-context source. |
| `../../results/processed/rtl_capsule_event_classes.csv` | Yes | RTL-smoke capsule packet-class source. |
| `../../results/processed/rtl_firmware_alignment.csv` | Yes | RTL-smoke versus firmware-sim property/key-event alignment source. |
| `../../results/processed/randomized_interrupt_campaign.csv` | Yes | Seeded RTL-smoke interrupt campaign source. |
| `../../results/processed/trace_sizes.csv` | Yes | Baseline trace-size data source. |
| `../../results/figures/trace_size_status.svg` | Yes | Existing generated trace-size status figure; not final paper styling. |
| `../../results/figures/rtl_capsule_event_classes.svg` | Yes | Existing generated RTL-smoke capsule class figure; not final paper styling. |
| `../../results/figures/randomized_interrupt_campaign.svg` | Yes | Existing generated seeded interrupt campaign figure; not final paper styling. |
| `../../results/processed/ablations.csv` | Yes | Ablation heatmap data source. |
| `../../results/processed/hdl_checks.csv` | Yes | Directed HDL and PicoRV32 wrapper smoke verification source with nine directed module rows and twelve wrapper smoke rows. |
| `../../results/processed/formal_checks.csv` | Yes | Bounded event-tap, event-classifier/slicer, property-checker, hash-signature, MMIO/interrupt logger, register, replay-control, replay-mismatch, capsule-buffer, and recorder formal status source. |
| `../../results/processed/formal_coverage.csv` | Yes | Reviewer-facing mapping from formal BMC/cover targets to RTL contract families and explicit limits. |
| `../../results/raw/yosys_picorv32.txt` | Yes | Yosys generic synthesis report for the baseline PicoRV32 core. |
| `../../results/raw/yosys_replay_capsule_top.txt` | Yes | Yosys generic synthesis report for the record-side top. |
| `../../results/raw/yosys_picorv32_replaycapsule_wrapper.txt` | Yes | Yosys generic synthesis report for the integrated wrapper. |
| `../../results/processed/synthesis.csv` | Yes | Synthesis/resource table source with generic cells measured and mapped resource/timing fields TODO/NA. |
| `../../results/processed/synthesis_overhead.csv` | Yes | Derived generic cell-overhead context with mapped fields kept as NA. |
| `table01_synthesis_resources.md` | Yes | Generated Markdown source for the synthesis/resource table. |
| `table02_replay_evidence.md` | Yes | Generated Markdown source for replay evidence status. |
| `table03_trace_baselines.md` | Yes | Generated Markdown source for trace-size baselines. |
| `table04_event_sufficiency.md` | Yes | Generated Markdown source for event-sufficiency ablations. |
| `table05_formal_coverage.md` | Yes | Generated Markdown source for bounded formal coverage. |
| `../../results/processed/summary.csv` | Yes | Provenance and missing-tool status ledger. |

## Planned Assets

| Output | Status | Source of truth | Missing gate |
| --- | --- | --- | --- |
| `fig01_architecture.svg` / `.pdf` | Not generated | `../../docs/architecture.md`, `../../docs/event_interface.md`, `../../rtl/*.sv` | None for record-side diagram; PicoRV32 artifact required before claiming completed SoC integration. |
| `fig02_event_model.svg` / `.pdf` | Partial source generated | `../../docs/event_model.md`, `../../results/raw/phase12_sensor_threshold_trace.json` | Full benchmark timeline requires RTL/PicoRV32 traces. |
| `fig03_replay_flow.svg` / `.pdf` | Partial source generated | `../../results/processed/replay_experiments.csv`, replay testbench scripts | Full benchmark replay requires RTL/PicoRV32 traces. |
| `fig04_baseline_trace_sizes.svg` / `.pdf` | Status SVG generated today | `../../results/processed/trace_sizes.csv`, `../../results/figures/trace_size_status.svg` | Missing baselines and replay-success fields require simulator/RTL/PicoRV32 artifacts. |
| `fig05_ablation_heatmap.svg` / `.pdf` | CSV generated today; heatmap not generated | `../../results/processed/ablations.csv` | Full-suite rows require firmware-running RTL/PicoRV32 traces. |
| `fig06_rtl_capsule_event_classes.svg` / `.pdf` | Status SVG generated today | `../../results/processed/rtl_capsule_event_classes.csv`, `../../results/figures/rtl_capsule_event_classes.svg` | Full benchmark-wide RTL traces required before treating this as complete baseline coverage. |
| `fig07_randomized_interrupt_campaign.svg` / `.pdf` | Status SVG generated today | `../../results/processed/randomized_interrupt_campaign.csv`, `../../results/figures/randomized_interrupt_campaign.svg` | Full record/replay randomized RTL campaign remains pending. |
| `table01_synthesis_resources.md` | Generated partial table today | `../../results/processed/synthesis.csv`, `../../results/processed/synthesis_overhead.csv` | Mapped FPGA flow for LUT/FF/BRAM/Fmax and mapped core-relative overhead. |
| `table02_replay_evidence.md` | Generated partial table today | `../../results/processed/replay_experiments.csv`, `../../results/processed/rtl_firmware_alignment.csv` | Full firmware-running RTL replay suite. |
| `table03_trace_baselines.md` | Generated partial table today | `../../results/processed/trace_sizes.csv`, `../../results/processed/rtl_capsule_event_classes.csv` | Full benchmark-wide RTL trace-size rows and mapped/replay-backed reductions. |
| `table04_event_sufficiency.md` | Generated partial table today | `../../results/processed/event_sufficiency.csv`, `../../results/processed/ablations.csv` | RTL-backed ablations. |
| `table05_formal_coverage.md` | Generated table today | `../../results/processed/formal_coverage.csv` | End-to-end proof remains outside current bounded checks. |

## Rendering Rules

- Keep final plot data in `../../results/processed/*`.
- Keep raw logs and traces in `../../results/raw/*`.
- Treat `TODO` and `NA` as first-class paper states until the missing tool or
  RTL artifact exists.
- Captions may describe the measurement method, but must not introduce numbers
  that are absent from the source artifacts.
- If a final figure is restyled for publication, record the exact source CSV or
  JSON path in its caption notes or adjacent metadata.

## Required Before Submission

| Requirement | Applies to |
| --- | --- |
| Firmware-running PicoRV32 traces for all listed benchmarks | Replay flow, baseline sizes, ablation heatmap. |
| Full Verilator or cocotb RTL simulation outputs | Replay success, cycles to failure, overflow behavior. |
| Yosys reports parsed into `synthesis.csv` and `synthesis_overhead.csv` | Synthesis/resource table. |
| Mapped FPGA report for both baseline and ReplayCapsule builds | LUT/FF/BRAM/Fmax and overhead fields. |
