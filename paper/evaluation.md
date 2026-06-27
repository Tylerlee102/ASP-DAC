# Evaluation

The evaluation reports replay success, capsule size, trace reduction, event rate, hardware overhead, Fmax loss, runtime overhead, buffer overflow rate, and false or missed property failures.

Current measured results cover six model-level benchmark capsules, six RV32I firmware-sim benchmark capsules, a generated six-benchmark local coverage ledger, benchmark-derived replay-comparator negative fixtures across commit-index and cycle-index modes, full compiler-backed firmware-running RTL replay rows, full RTL replay-critical corruption checks, a bounded overflow contract ledger, the replay comparator, directed Icarus SystemVerilog module simulations, fifteen PicoRV32 wrapper firmware smokes with generated log-level capsule sanity summaries, Verilator lint for `replay_capsule_top`, `picorv32_replaycapsule_wrapper`, `replaycapsule_soc`, and `replay_capsule_properties`, bounded SMTBMC event-tap, event-classifier/slicer, property-checker, hash-signature, MMIO/interrupt logger, register, replay-control, replay-mismatch, recorder, and capsule-buffer proof/cover checks, runtime-overhead summaries, generic Yosys synthesis context, and same-target full-core ECP5 mapped LUT/FF/BRAM/Fmax numbers. The suites exercise failing, fixed, and selected no-failure edge sensor-threshold, interrupt-race, MMIO-ordering, stack-corruption, UART-command, and watchdog-timeout images.

Current generated artifacts:

- `results/processed/replay_experiments.csv`
- `results/processed/replay_negative_tests.csv`
- `results/processed/firmware_sim_replay.csv`
- `results/processed/rtl_capsule_exports.csv`
- `results/processed/rtl_capsule_event_classes.csv`
- `results/processed/rtl_firmware_alignment.csv`
- `results/processed/randomized_interrupt_campaign.csv`
- `results/processed/randomized_interrupt_summary.csv`
- `results/processed/randomized_interrupt_coverage.csv`
- `results/processed/randomized_interrupt_corruption.csv`
- `results/processed/trace_sizes.csv`
- `results/processed/ablations.csv`
- `results/processed/event_sufficiency.csv`
- `results/processed/rtl_smoke_ablations.csv`
- `results/processed/rtl_smoke_event_sufficiency.csv`
- `results/processed/hdl_checks.csv`
- `results/processed/picorv32_smoke_summary.csv`
- `results/processed/picorv32_smoke_coverage.csv`
- `results/processed/benchmark_coverage.csv`
- `results/processed/formal_checks.csv`
- `results/processed/formal_coverage.csv`
- `results/processed/overflow_contracts.csv`
- `results/processed/proof_obligations.csv`
- `results/processed/synthesis.csv`
- `results/processed/synthesis_overhead.csv`
- `results/processed/mapped_synthesis.csv`
- `results/processed/mapped_overhead.csv`
- `results/processed/mapped_recorder_presence.csv`
- `results/processed/full_core_mapped_summary.csv`
- `results/processed/runtime_overhead.csv`
- `results/processed/runtime_overhead_summary.csv`
- `results/processed/evaluation_metrics.csv`
- `results/processed/claim_audit.csv`
- `results/processed/toolchain_status.csv`
- `results/processed/artifact_manifest.csv`
- `results/figures/*.svg`
- `paper/figures/table01_synthesis_resources.md`
- `paper/figures/table02_replay_evidence.md`
- `paper/figures/table03_trace_baselines.md`
- `paper/figures/table04_event_sufficiency.md`
- `paper/figures/table05_formal_coverage.md`
- `paper/figures/table06_proof_obligations.md`
- `paper/figures/table07_evaluation_metrics.md`

The paper labels replay, baseline, ablation, interrupt-campaign, and event-sufficiency numbers as model-level, firmware-sim, RTL-smoke, or full RTL evidence according to their source CSVs. Current full RTL evidence is compiler-backed host-driven record/replay and replay-critical corruption rejection; current formal evidence is bounded event-tap, event-classifier/slicer, property-checker, hash-signature, MMIO/interrupt logger, register, replay-control, replay-mismatch, recorder, and capsule-buffer BMC/cover targets plus a generated theorem proof-obligation matrix. Current mapped evidence is same-target ECP5 place-and-route for board-level full-core baseline and ReplayCapsule wrappers.

The result pipeline is:

1. `scripts/run_all_tests.py`
2. `scripts/run_replay_experiments.py`
3. `scripts/collect_trace_sizes.py`
4. `scripts/run_ablations.py`
5. `scripts/synth_yosys.py`
6. `scripts/parse_synthesis_reports.py`
7. `scripts/run_mapped_synthesis.py`
8. `scripts/make_figures.py`

The one-command local gate is `scripts/run_all_tests.py`, wrapped by `scripts/reproduce_all.ps1` on Windows and `scripts/reproduce_all.sh` on Unix-like shells.
