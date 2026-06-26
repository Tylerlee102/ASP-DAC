# Evaluation

The evaluation will report replay success, capsule size, trace reduction, event rate, hardware overhead, Fmax loss, runtime overhead, buffer overflow rate, and false or missed property failures.

Current measured local results cover six model-level benchmark capsules, six RV32I firmware-sim benchmark capsules, twelve failing/fixed RTL-smoke capsule export self/negative/PC-context checks and packet-byte size rows, twelve RTL-smoke versus firmware-sim alignment rows, the replay comparator, nine directed Icarus SystemVerilog module simulations, twelve PicoRV32 wrapper firmware smokes, Verilator lint for `replay_capsule_top`, `picorv32_replaycapsule_wrapper`, `replaycapsule_soc`, and `replay_capsule_properties`, bounded SMTBMC replay-control, recorder, and capsule-buffer proof/cover checks, and generic Yosys synthesis cell counts for both tops. The suites exercise failing and fixed sensor-threshold, interrupt-race, MMIO-ordering, stack-corruption, UART-command, and watchdog-timeout images. The full six-benchmark firmware-running RTL replay/export/compare suite remains TODO because local `make`/C++ build support and a RISC-V compiler are still absent. FPGA-mapped LUT/FF/BRAM/Fmax numbers also remain TODO until an OpenROAD or vendor flow is run.

Current generated artifacts:

- `results/processed/replay_experiments.csv`
- `results/processed/firmware_sim_replay.csv`
- `results/processed/rtl_capsule_exports.csv`
- `results/processed/rtl_firmware_alignment.csv`
- `results/processed/trace_sizes.csv`
- `results/processed/ablations.csv`
- `results/processed/event_sufficiency.csv`
- `results/processed/hdl_checks.csv`
- `results/processed/formal_checks.csv`
- `results/processed/synthesis.csv`
- `results/figures/*.svg`

The paper must label current replay, baseline, ablation, and event-sufficiency numbers as model-level, firmware-sim, or RTL-smoke evidence until replaced or corroborated by benchmark-wide RTL/PicoRV32 runs. Current RTL simulation evidence is twelve PicoRV32 wrapper smokes and exported smoke capsule byte counts, current formal evidence is bounded replay-control, recorder, and capsule-buffer BMC/cover targets, and current synthesis evidence is limited to Yosys generic cell counts.

The result pipeline is:

1. `scripts/run_all_tests.py`
2. `scripts/run_replay_experiments.py`
3. `scripts/collect_trace_sizes.py`
4. `scripts/run_ablations.py`
5. `scripts/synth_yosys.py`
6. `scripts/parse_synthesis_reports.py`
7. `scripts/make_figures.py`

The one-command local gate is `scripts/run_all_tests.py`, wrapped by `scripts/reproduce_all.ps1` on Windows and `scripts/reproduce_all.sh` on Unix-like shells.
