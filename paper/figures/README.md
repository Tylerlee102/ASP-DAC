# Paper Figures

This directory is the landing zone for final paper-ready figure and table
assets. At the moment, the real generated outputs live under `../../results/`;
this directory contains only the manifest until camera-ready assets are rendered
from those sources.

Do not manually type measurement values into paper figures or tables. Numeric
content must come from generated CSV, JSON, SVG, or synthesis-report artifacts.

## Current Generated Sources

| Source | Generated today? | Role |
| --- | --- | --- |
| `../../results/raw/phase12_sensor_threshold_trace.json` | Yes | Smoke event timeline for model and replay-flow figures. |
| `../../results/processed/replay_experiments.csv` | Yes | Replay-flow status source. |
| `../../results/processed/trace_sizes.csv` | Yes | Baseline trace-size data source. |
| `../../results/figures/trace_size_status.svg` | Yes | Existing generated trace-size status figure; not final paper styling. |
| `../../results/processed/ablations.csv` | Yes | Ablation heatmap data source. |
| `../../results/raw/yosys_replay_capsule_top.txt` | Yes | Yosys availability probe. |
| `../../results/processed/synthesis.csv` | Yes | Synthesis/resource table source; currently TODO/NA until Yosys is available. |
| `../../results/processed/summary.csv` | Yes | Provenance and missing-tool status ledger. |

## Planned Assets

| Output | Status | Source of truth | Missing gate |
| --- | --- | --- | --- |
| `fig01_architecture.svg` / `.pdf` | Not generated | `../../docs/architecture.md`, `../../docs/event_interface.md`, `../../rtl/*.sv` | None for record-side diagram; PicoRV32 artifact required before claiming completed SoC integration. |
| `fig02_event_model.svg` / `.pdf` | Partial source generated | `../../docs/event_model.md`, `../../results/raw/phase12_sensor_threshold_trace.json` | Full benchmark timeline requires RTL/PicoRV32 traces. |
| `fig03_replay_flow.svg` / `.pdf` | Partial source generated | `../../results/processed/replay_experiments.csv`, replay testbench scripts | Full benchmark replay requires RTL/PicoRV32 traces. |
| `fig04_baseline_trace_sizes.svg` / `.pdf` | Status SVG generated today | `../../results/processed/trace_sizes.csv`, `../../results/figures/trace_size_status.svg` | Missing baselines and replay-success fields require simulator/RTL/PicoRV32 artifacts. |
| `fig05_ablation_heatmap.svg` / `.pdf` | CSV generated today; heatmap not generated | `../../results/processed/ablations.csv` | Full-suite rows require firmware-running RTL/PicoRV32 traces. |
| `table01_synthesis_resources.md` | TODO source generated today | `../../results/processed/synthesis.csv` | Yosys for cells; mapped FPGA flow for LUT/FF/BRAM/Fmax; PicoRV32 integration for core-relative overhead. |

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
| Verilator or cocotb RTL simulation outputs | Replay success, cycles to failure, overflow behavior. |
| Yosys report parsed into `synthesis.csv` | Synthesis/resource table. |
| Mapped FPGA report for both baseline and ReplayCapsule builds | LUT/FF/BRAM/Fmax and overhead fields. |

