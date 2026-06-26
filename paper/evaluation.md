# Evaluation

The evaluation will report replay success, capsule size, trace reduction, event rate, hardware overhead, Fmax loss, runtime overhead, buffer overflow rate, and false or missed property failures.

Current measured local results cover six model-level benchmark capsules, six RV32I firmware-sim benchmark capsules, benchmark-derived replay-comparator negative fixtures across commit-index and cycle-index modes, twelve failing/fixed RTL-smoke capsule export self/missing-event/duplicate-event/metadata-corruption/payload-corruption/order-corruption/PC-context checks and packet-byte size rows, RTL-smoke capsule event-class counts, twelve RTL-smoke versus firmware-sim alignment rows, a seeded RTL-smoke interrupt-race reproducibility campaign with generated family summary and coverage/TODO ledgers, the replay comparator, nine directed Icarus SystemVerilog module simulations, fifteen PicoRV32 wrapper firmware smokes, Verilator lint for `replay_capsule_top`, `picorv32_replaycapsule_wrapper`, `replaycapsule_soc`, and `replay_capsule_properties`, bounded SMTBMC event-tap, event-classifier/slicer, property-checker, hash-signature, MMIO/interrupt logger, register, replay-control, replay-mismatch, recorder, and capsule-buffer proof/cover checks, and generic Yosys synthesis cell counts for baseline `picorv32`, `replay_capsule_top`, and `picorv32_replaycapsule_wrapper`. The suites exercise failing, fixed, and selected no-failure edge sensor-threshold, interrupt-race, MMIO-ordering, stack-corruption, UART-command, and watchdog-timeout images. The full six-benchmark firmware-running RTL replay/export/compare suite remains TODO because local `make`/C++ build support and a RISC-V compiler are still absent. FPGA-mapped LUT/FF/BRAM/Fmax numbers also remain TODO until an OpenROAD or vendor flow is run.

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
- `results/processed/trace_sizes.csv`
- `results/processed/ablations.csv`
- `results/processed/event_sufficiency.csv`
- `results/processed/rtl_smoke_ablations.csv`
- `results/processed/rtl_smoke_event_sufficiency.csv`
- `results/processed/hdl_checks.csv`
- `results/processed/formal_checks.csv`
- `results/processed/formal_coverage.csv`
- `results/processed/proof_obligations.csv`
- `results/processed/synthesis.csv`
- `results/processed/synthesis_overhead.csv`
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

The paper must label current replay, baseline, ablation, interrupt-campaign, and event-sufficiency numbers as model-level, firmware-sim, or RTL-smoke evidence until replaced or corroborated by benchmark-wide RTL/PicoRV32 runs. Current RTL simulation evidence is fifteen PicoRV32 wrapper smokes, exported smoke capsule byte counts, exported-capsule event-class ablations, and seeded interrupt rerun digest checks; current formal evidence is bounded event-tap, event-classifier/slicer, property-checker, hash-signature, MMIO/interrupt logger, register, replay-control, replay-mismatch, recorder, and capsule-buffer BMC/cover targets plus a generated theorem proof-obligation matrix, and current synthesis evidence is limited to Yosys generic cell counts and derived generic cell-overhead context.

The result pipeline is:

1. `scripts/run_all_tests.py`
2. `scripts/run_replay_experiments.py`
3. `scripts/collect_trace_sizes.py`
4. `scripts/run_ablations.py`
5. `scripts/synth_yosys.py`
6. `scripts/parse_synthesis_reports.py`
7. `scripts/make_figures.py`

The one-command local gate is `scripts/run_all_tests.py`, wrapped by `scripts/reproduce_all.ps1` on Windows and `scripts/reproduce_all.sh` on Unix-like shells.
