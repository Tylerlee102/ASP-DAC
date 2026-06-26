# ReplayCapsule-RV Figure and Table Plan

Status date: 2026-06-25.

This plan is a paper-facing manifest for figures and tables. Numeric values must
flow from generated artifacts under `results/`; do not type measurements by
hand into captions, plots, or tables.

## Status Vocabulary

| Status | Meaning |
| --- | --- |
| Generated today | A real artifact exists in `results/` with today's run output and can be used as source evidence. |
| Partial today | A source artifact exists today, but the final paper figure/table has not been rendered or the artifact only covers the smoke path. |
| Requires RTL/PicoRV32 | Needs firmware-running RTL traces from the PicoRV32 integration, Verilator/cocotb, and a RISC-V toolchain before paper claims can be filled. |
| Requires mapped FPGA flow | Needs OpenROAD or vendor mapping for LUT/FF/BRAM/Fmax fields. |
| Spec only | The figure can be drawn from the architecture/model docs, but no generated paper asset exists yet. |

## Generated Artifact Snapshot

| Artifact | Generated today? | Used by | Current honesty status |
| --- | --- | --- | --- |
| `results/raw/model_suite_traces.json` | Yes | Event model, replay flow, trace-size baselines | Six benchmark model-level traces. |
| `results/processed/replay_experiments.csv` | Yes | Replay flow | Six model-level replay rows pass; firmware-running RTL suite is TODO. |
| `results/processed/trace_sizes.csv` | Yes | Baseline trace-size figure | Contains model-level and firmware-sim rows for six benchmarks, plus RTL-smoke capsule-byte rows for exported failing/fixed capsules. Full benchmark-wide RTL rows remain TODO/NA where unavailable. |
| `results/figures/baseline_trace_sizes.svg` | Yes | Baseline trace-size figure | Generated from `trace_sizes.csv`. |
| `results/figures/ablation_heatmap.svg` | Yes | Ablation heatmap | Generated from model-level ablation rows. |
| `results/processed/ablations.csv` | Yes | Ablation heatmap | Model-level ablations are available; RTL-backed rows require firmware-running traces. |
| `results/processed/hdl_checks.csv` | Yes | Verification status | Eight directed Icarus module simulations, twelve PicoRV32 wrapper smokes, and Verilator lint-only checks pass. |
| `results/processed/formal_checks.csv` | Yes | Verification status | Depth-12 capsule-buffer and depth-16 recorder SMTBMC BMC/cover targets pass. |
| `results/processed/rtl_capsule_exports.csv` | Yes | RTL capsule export status | Failing and fixed RTL smoke capsules decode to JSON, self-compare, and fail missing-event negative checks through the replay comparator. |
| `results/raw/yosys_replay_capsule_top.txt` | Yes | Synthesis/resource table | Real Yosys generic synthesis report for the record-side top. |
| `results/raw/yosys_picorv32_replaycapsule_wrapper.txt` | Yes | Synthesis/resource table | Real Yosys generic synthesis report for the integrated wrapper. |
| `results/processed/synthesis.csv` | Yes | Synthesis/resource table | Contains measured generic cell counts plus TODO/NA mapped resource and timing fields. |
| `results/processed/summary.csv` | Yes | All figure/table provenance | One-command status ledger for generated artifacts and missing tools. |

## Paper Figure and Table Manifest

| ID | Asset | Paper role | Target output | Generated today? | Requires RTL/PicoRV32/Yosys artifacts? |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 | Architecture diagram | Show the record-side ReplayCapsule-RV path: core/fabric observations, event tap, classifier, slicer, capsule buffer, hash/signature, registers, and replay-control boundary. | `paper/figures/architecture_overview.svg` | Yes. Generated from script-level diagram specification. | No for current record-side diagram. Yes if the diagram claims a completed PicoRV32 SoC integration. |
| Fig. 2 | Replay flow | Show record, freeze, export, replay, compare, and property-signature verification using the replay comparator path. | `paper/figures/replay_flow.svg` | Yes. Generated from script-level diagram specification. | Yes for full firmware-running replay across the benchmark suite. |
| Fig. 3 | Baseline trace sizes | Compare available baseline trace/capsule sizes and mark unavailable baselines as TODO/NA without estimating them. | `paper/figures/baseline_trace_sizes.svg` | Yes. Generated from `results/processed/trace_sizes.csv`. | Yes for full-instruction trace and snapshot-on-failure baselines. |
| Fig. 4 | Ablation heatmap | Show which omitted event classes break replay for each benchmark and which omissions are benign for the observed fixture. | `paper/figures/ablation_heatmap.svg` | Yes. Generated from `results/processed/ablations.csv`. | Yes for buffer-size sweeps, last-K context-window sweeps, and RTL-backed ablations. |
| Table 1 | Synthesis/resource table | Report monitor/resource cost and timing only from generated synthesis outputs. | `paper/figures/table01_synthesis_resources.md` or paper-native table source | Partial today. `results/processed/synthesis.csv` contains measured generic Yosys cell counts. | Requires mapped FPGA flow for LUT/FF/BRAM/Fmax. Requires a matching baseline core build for core-relative overhead. |

## Figure Details

### Fig. 1: Architecture Diagram

Caption draft:
ReplayCapsule-RV records firmware-visible nondeterminism at the RV32I boundary
instead of storing a full instruction trace. The record path normalizes core,
MMIO, interrupt, and external-input observations into typed events, keeps the
events required by the selected capture policy, freezes a capsule on failure,
and exposes the capsule plus a replay signature to software.

Source material:
- `docs/architecture.md`
- `docs/event_interface.md`
- `rtl/replay_capsule_top.sv`
- `rtl/event_tap.sv`
- `rtl/event_classifier.sv`
- `rtl/event_slicer.sv`
- `rtl/capsule_buffer.sv`
- `rtl/hash_signature.sv`
- `rtl/replay_control.sv`

Paper-readiness checks:
- Label the core side as "RV32I boundary" unless PicoRV32 integration artifacts
  are present.
- Show `replay_control` as present but not overclaim full end-to-end RTL replay
  until firmware-running traces exist.
- Avoid area/timing callouts in this figure.

### Fig. 2: Event Model

Caption draft:
Commit-index time gives ReplayCapsule-RV a logical replay clock. Boundary
events record the nondeterministic facts that firmware can observe, such as MMIO
read values and interrupt delivery points. Replaying the same firmware image and
the same ordered boundary events should reproduce the same architectural prefix
and property-failure signature under the stated assumptions.

Source material:
- `docs/event_model.md`
- `docs/capsule_format.md`
- `formal/replay_sufficiency_theorem.md`
- `results/raw/phase12_sensor_threshold_trace.json`

Paper-readiness checks:
- If the figure includes a concrete timeline, generate it from the JSON trace.
- Use TODO markers, not inferred data, for event families not exercised by the
  smoke trace.

### Fig. 3: Replay Flow

Caption draft:
The evaluation path records a capsule, freezes it at the target failure,
exports or parses the event stream, replays it against a controlled environment,
and compares property, MMIO, input, interrupt, and signature evidence.

Source material:
- `tb/replay_testbench/capsule_parser.py`
- `tb/replay_testbench/replay_compare.py`
- `tb/replay_testbench/replay_driver.py`
- `scripts/run_replay_experiments.py`
- `results/processed/replay_experiments.csv`

Paper-readiness checks:
- Distinguish the current Python smoke replay from future RTL replay.
- Full benchmark claims require firmware-running RTL/PicoRV32 artifacts.

### Fig. 4: Baseline Trace Sizes

Caption draft:
Trace-size baselines are reported only when the corresponding artifact exists.
Rows that require unavailable simulator, RTL, or replay outputs remain TODO/NA
rather than being estimated.

Source material:
- `docs/baselines.md`
- `scripts/collect_trace_sizes.py`
- `results/processed/trace_sizes.csv`
- `results/figures/trace_size_status.svg`

Paper-readiness checks:
- Render all values directly from `trace_sizes.csv`.
- Preserve TODO/NA rows for unavailable baselines.
- Do not compute trace reduction ratios until both numerator and denominator are
  generated artifacts from the same workload.

### Fig. 5: Ablation Heatmap

Caption draft:
Ablations remove one event class or capture policy feature at a time. The heatmap
shows whether replay still matches the expected capsule for each benchmark,
with unavailable benchmark rows marked TODO until firmware-running RTL traces
exist.

Source material:
- `docs/ablation_plan.md`
- `scripts/run_ablations.py`
- `results/processed/ablations.csv`

Paper-readiness checks:
- Use the CSV `status` field to separate measured smoke entries from TODO
  full-suite entries.
- Do not generalize smoke-only successes to all benchmarks.
- Full heatmap requires PicoRV32/RTL traces for every benchmark listed in
  `docs/experimental_methodology.md`.

### Table 1: Synthesis/Resource Table

Caption draft:
Resource and timing results are generated from synthesis reports. Generic Yosys
cell counts can be reported from the current local run. Mapped resource and
timing fields remain TODO/NA until the mapped tool flow exists.

Source material:
- `scripts/synth_yosys.py`
- `scripts/parse_synthesis_reports.py`
- `results/raw/yosys_replay_capsule_top.txt`
- `results/processed/synthesis.csv`

Paper-readiness checks:
- Yosys generic cells may be reported only after a real report is parsed.
- LUT/FF/BRAM/Fmax require a mapped FPGA flow, not the generic Yosys report.
- Core-relative overhead requires a PicoRV32-integrated top and matching
  baseline core build.

## Regeneration Order

Use the existing pipeline as the source of truth:

1. Run `scripts/run_all_tests.py` for the complete local status ledger.
2. Run `scripts/run_replay_experiments.py` for replay status.
3. Run `scripts/collect_trace_sizes.py` for baseline trace-size rows.
4. Run `scripts/run_ablations.py` for ablation rows.
5. Run `scripts/synth_yosys.py`; it uses system Yosys or workspace-local `yowasp-yosys` when available.
6. Run `scripts/parse_synthesis_reports.py` after synthesis.
7. Run `scripts/make_figures.py` or its paper-rendering successor.

## Missing Artifact Gates

| Gate | Needed artifacts | Unlocks |
| --- | --- | --- |
| PicoRV32 integration | Firmware-running record/replay traces for each benchmark | Full replay flow, full baseline comparison, full ablation heatmap, core-relative resource overhead. |
| Full Verilator/cocotb plus RISC-V toolchain | Reproducible RTL simulation traces and firmware images | Benchmark-wide event logs, replay success, cycles to failure, overflow checks. |
| Yosys | Real synthesis report for `replay_capsule_top` and integrated variants | Generic cell counts and synthesis status. Current local flow satisfies this with `yowasp-yosys`. |
| FPGA mapping flow | Device-mapped reports for baseline and ReplayCapsule builds | LUT, FF, BRAM, Fmax, and timing-overhead fields. |
