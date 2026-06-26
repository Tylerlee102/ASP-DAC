# ReplayCapsule-RV Figure and Table Plan

Status date: 2026-06-26.

This plan is a paper-facing manifest for figures and tables. Numeric values must
flow from generated artifacts under `results/`; do not type measurements by
hand into captions, plots, or tables.

## Status Vocabulary

| Status | Meaning |
| --- | --- |
| Generated today | A real artifact exists in `results/` or `paper/figures/` with today's run output and can be used as source evidence. |
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
| `results/processed/rtl_smoke_ablations.csv` | Yes | Ablation/sufficiency table | Removes event classes from exported RTL-smoke capsules and reruns the replay comparator. |
| `results/processed/rtl_smoke_event_sufficiency.csv` | Yes | Ablation/sufficiency table | Summarizes required event classes for failing RTL-smoke capsules. |
| `results/processed/rtl_capsule_event_classes.csv` | Yes | RTL capsule event-class figure | Decodes exported RTL-smoke capsules into packet class counts; not a full benchmark-wide trace baseline. |
| `results/figures/rtl_capsule_event_classes.svg` | Yes | RTL capsule event-class figure | Generated from `rtl_capsule_event_classes.csv`. |
| `results/processed/randomized_interrupt_campaign.csv` | Yes | Seeded interrupt campaign figure | RTL-smoke interrupt-race seeds reproduce expected property IDs and capsule digests across fresh simulator invocations. |
| `results/figures/randomized_interrupt_campaign.svg` | Yes | Seeded interrupt campaign figure | Generated from `randomized_interrupt_campaign.csv`. |
| `results/processed/hdl_checks.csv` | Yes | Verification status | Nine directed Icarus module simulations, fifteen PicoRV32 wrapper smokes, and Verilator lint-only checks pass. |
| `results/processed/picorv32_smoke_summary.csv` | Yes | Wrapper smoke observations | Parses PicoRV32 smoke logs for property IDs, capsule counts, freeze state, and overflow state. |
| `results/processed/picorv32_smoke_coverage.csv` | Yes | Wrapper smoke coverage | Summarizes failing-image, fixed-image, no-failure edge, and benchmark-family wrapper coverage. |
| `results/processed/benchmark_coverage.csv` | Yes | Benchmark coverage | Joins model, firmware-sim, wrapper-smoke, export, alignment, and sufficiency evidence by benchmark while keeping full RTL replay TODO. |
| `results/processed/formal_checks.csv` | Yes | Verification status | Depth-2 event-tap, depth-8 event-classifier/slicer, depth-8 property-checker, depth-4 hash-signature, depth-6 MMIO/interrupt loggers, depth-6 registers, depth-8 replay-control, depth-14 replay-mismatch, depth-12 capsule-buffer, and depth-16 recorder SMTBMC BMC/cover targets pass. |
| `results/processed/rtl_capsule_exports.csv` | Yes | RTL capsule export status | Failing and fixed RTL smoke capsules decode to JSON, self-compare, fail missing-event, duplicate-event, metadata-corruption, payload-corruption, and order-corruption negative checks through the replay comparator, and pass memory-event PC-context checks. |
| `results/processed/rtl_firmware_alignment.csv` | Yes | RTL/firmware consistency status | Failing RTL-smoke capsules agree with firmware-sim property IDs and benchmark-specific replay-visible event evidence; fixed rows agree on property absence. |
| `results/raw/yosys_picorv32.txt` | Yes | Synthesis/resource table | Real Yosys generic synthesis report for the baseline PicoRV32 core. |
| `results/raw/yosys_replay_capsule_top.txt` | Yes | Synthesis/resource table | Real Yosys generic synthesis report for the record-side top. |
| `results/raw/yosys_picorv32_replaycapsule_wrapper.txt` | Yes | Synthesis/resource table | Real Yosys generic synthesis report for the integrated wrapper. |
| `results/processed/synthesis.csv` | Yes | Synthesis/resource table | Contains measured generic cell counts plus TODO/NA mapped resource and timing fields. |
| `results/processed/synthesis_overhead.csv` | Yes | Synthesis/resource table | Contains derived generic cell-count overhead context from measured baseline and wrapper rows, with mapped fields kept as NA. |
| `results/processed/evaluation_metrics.csv` | Yes | Evaluation metric table | Rolls up generated success rates, sizes, reduction ratios, cycles-to-failure, generic synthesis context, and explicit hardware TODOs. |
| `paper/figures/table01_synthesis_resources.md` | Yes | Synthesis/resource table | Generated Markdown table source derived from the synthesis CSVs; mapped fields remain NA. |
| `paper/figures/table02_replay_evidence.md` | Yes | Replay evidence table | Generated Markdown table source derived from replay and RTL/firmware alignment CSVs. |
| `paper/figures/table03_trace_baselines.md` | Yes | Baseline trace-size table | Generated Markdown table source derived from trace-size and RTL-smoke capsule-class CSVs. |
| `paper/figures/table04_event_sufficiency.md` | Yes | Ablation/sufficiency table | Generated Markdown table source derived from event-sufficiency and ablation CSVs. |
| `paper/figures/table05_formal_coverage.md` | Yes | Formal coverage table | Generated Markdown table source derived from the formal coverage CSV. |
| `results/processed/proof_obligations.csv` | Yes | Proof-obligation matrix | Generated CSV mapping replay-sufficiency theorem assumptions to current evidence and limits. |
| `docs/proof_obligation_matrix.md` | Yes | Proof-obligation matrix | Generated reviewer-facing theorem evidence matrix. |
| `paper/figures/table06_proof_obligations.md` | Yes | Proof-obligation table | Generated Markdown paper table source derived from proof-obligations CSV. |
| `paper/figures/table07_evaluation_metrics.md` | Yes | Evaluation metric table | Generated Markdown paper table source derived from evaluation metrics CSV. |
| `results/processed/claim_audit.csv` | Yes | Honesty gate | Generated audit of high-risk claim phrases; uncaveated rows fail the local gate. |
| `results/processed/toolchain_status.csv` | Yes | Reproducibility gate | Generated availability ledger for local tools and later-gate blockers. |
| `results/processed/summary.csv` | Yes | All figure/table provenance | One-command status ledger for generated artifacts and missing tools. |

## Paper Figure and Table Manifest

| ID | Asset | Paper role | Target output | Generated today? | Requires RTL/PicoRV32/Yosys artifacts? |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 | Architecture diagram | Show the record-side ReplayCapsule-RV path: core/fabric observations, event tap, classifier, slicer, capsule buffer, hash/signature, registers, and replay-control boundary. | `paper/figures/architecture_overview.svg` | Yes. Generated from script-level diagram specification. | No for current record-side diagram. Yes if the diagram claims a completed PicoRV32 SoC integration. |
| Fig. 2 | Replay flow | Show record, freeze, export, replay, compare, and property-signature verification using the replay comparator path. | `paper/figures/replay_flow.svg` | Yes. Generated from script-level diagram specification. | Yes for full firmware-running replay across the benchmark suite. |
| Fig. 3 | Baseline trace sizes | Compare available baseline trace/capsule sizes and mark unavailable baselines as TODO/NA without estimating them. | `paper/figures/baseline_trace_sizes.svg` | Yes. Generated from `results/processed/trace_sizes.csv`. | Yes for full-instruction trace and snapshot-on-failure baselines. |
| Fig. 4 | Ablation heatmap | Show which omitted event classes break replay for each benchmark and which omissions are benign for the observed fixture. | `paper/figures/ablation_heatmap.svg` | Yes. Generated from `results/processed/ablations.csv`. | Yes for buffer-size sweeps, last-K context-window sweeps, and RTL-backed ablations. |
| Fig. 5 | RTL capsule event classes | Show packet-class composition of exported RTL-smoke capsules without treating it as full benchmark-wide trace evidence. | `paper/figures/rtl_capsule_event_classes.svg` | Yes. Generated from `results/processed/rtl_capsule_event_classes.csv`. | Yes for full benchmark-wide RTL class counts. |
| Fig. 6 | Seeded interrupt campaign | Show seeded RTL-smoke interrupt-race reruns and frozen capsule packet counts after digest-match checks. | `paper/figures/randomized_interrupt_campaign.svg` | Yes. Generated from `results/processed/randomized_interrupt_campaign.csv`. | Yes for full record/replay randomized campaign. |
| Table 1 | Synthesis/resource table | Report monitor/resource cost and timing only from generated synthesis outputs. | `paper/figures/table01_synthesis_resources.md` | Generated partial table today from `results/processed/synthesis.csv` and `results/processed/synthesis_overhead.csv`. | Requires mapped FPGA flow for LUT/FF/BRAM/Fmax and mapped core-relative overhead. |
| Table 2 | Replay evidence table | Summarize model, firmware-sim, and RTL-smoke alignment status by benchmark while preserving the TODO full RTL suite row. | `paper/figures/table02_replay_evidence.md` | Generated partial table today from `results/processed/replay_experiments.csv` and `results/processed/rtl_firmware_alignment.csv`. | Requires full firmware-running RTL replay for final replay claims. |
| Table 3 | Trace-size baseline table | Summarize available firmware-sim trace-size baselines and exported RTL-smoke capsule bytes. | `paper/figures/table03_trace_baselines.md` | Generated partial table today from `results/processed/trace_sizes.csv` and `results/processed/rtl_capsule_event_classes.csv`. | Requires full benchmark-wide RTL trace-size rows. |
| Table 4 | Event-sufficiency table | Summarize model-level and RTL-smoke event-removal ablations that break replay by benchmark. | `paper/figures/table04_event_sufficiency.md` | Generated partial table today from `results/processed/event_sufficiency.csv`, `results/processed/ablations.csv`, and `results/processed/rtl_smoke_event_sufficiency.csv`. | Requires full benchmark-wide RTL-backed ablations. |
| Table 5 | Formal coverage table | Summarize bounded formal contract families, depths, obligations, and explicit limits. | `paper/figures/table05_formal_coverage.md` | Generated table today from `results/processed/formal_coverage.csv`. | End-to-end processor/replay theorem remains outside current bounded checks. |
| Table 6 | Proof-obligation table | Link replay-sufficiency theorem assumptions to current generated evidence and remaining limits. | `paper/figures/table06_proof_obligations.md` | Generated partial table today from `results/processed/proof_obligations.csv`. | End-to-end mechanized theorem remains outside current bounded checks. |
| Table 7 | Evaluation metric rollup | Summarize headline measured metrics and explicit hardware-dependent TODOs. | `paper/figures/table07_evaluation_metrics.md` | Generated partial table today from `results/processed/evaluation_metrics.csv`. | Requires benchmark-wide RTL replay, mapped FPGA resources/Fmax, runtime slowdown, and overflow counters. |

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
- `scripts/render_paper_tables.py`
- `results/raw/yosys_picorv32.txt`
- `results/raw/yosys_replay_capsule_top.txt`
- `results/raw/yosys_picorv32_replaycapsule_wrapper.txt`
- `results/processed/synthesis.csv`
- `results/processed/synthesis_overhead.csv`
- `paper/figures/table01_synthesis_resources.md`

Paper-readiness checks:
- Yosys generic cells may be reported only after a real report is parsed.
- Generic cell deltas may be reported only from `synthesis_overhead.csv` and
  must be labeled as generic Yosys context.
- LUT/FF/BRAM/Fmax require a mapped FPGA flow, not the generic Yosys report.
- Core-relative overhead may be discussed only as generic Yosys cell-count
  context until a mapped baseline and mapped ReplayCapsule build exist.

## Regeneration Order

Use the existing pipeline as the source of truth:

1. Run `scripts/run_all_tests.py` for the complete local status ledger.
2. Run `scripts/run_replay_experiments.py` for replay status.
3. Run `scripts/collect_trace_sizes.py` for baseline trace-size rows.
4. Run `scripts/run_ablations.py` for ablation rows.
5. Run `scripts/synth_yosys.py`; it uses system Yosys or workspace-local `yowasp-yosys` when available.
6. Run `scripts/parse_synthesis_reports.py` after synthesis.
7. Run `scripts/render_paper_tables.py` for generated Markdown table sources.
8. Run `scripts/make_figures.py` for generated SVG status figures.

## Missing Artifact Gates

| Gate | Needed artifacts | Unlocks |
| --- | --- | --- |
| PicoRV32 integration | Firmware-running record/replay traces for each benchmark | Full replay flow, full baseline comparison, full ablation heatmap, RTL-backed replay overhead context. |
| Full Verilator/cocotb plus RISC-V toolchain | Reproducible RTL simulation traces and firmware images | Benchmark-wide event logs, replay success, cycles to failure, overflow checks. |
| Yosys | Real synthesis report for baseline `picorv32`, `replay_capsule_top`, and integrated variants | Generic cell counts, generic cell-overhead context, and synthesis status. Current local flow satisfies this with `yowasp-yosys`. |
| FPGA mapping flow | Requires device-mapped reports for baseline and ReplayCapsule builds | LUT, FF, BRAM, Fmax, and timing-overhead fields. |
