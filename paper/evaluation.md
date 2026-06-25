# Evaluation

The evaluation will report replay success, capsule size, trace reduction, event rate, hardware overhead, Fmax loss, runtime overhead, buffer overflow rate, and false or missed property failures.

Current measured local results cover six model-level benchmark capsules, six RV32I firmware-sim benchmark capsules, and the replay comparator. The suites exercise sensor-threshold, interrupt-race, MMIO-ordering, stack-corruption, UART-command, and watchdog-timeout failures. Verilator, Yosys, and a RISC-V compiler were not available in the local environment at kickoff, so firmware-running RTL simulation and synthesis are marked TODO until real tools are run.

Current generated artifacts:

- `results/processed/replay_experiments.csv`
- `results/processed/firmware_sim_replay.csv`
- `results/processed/trace_sizes.csv`
- `results/processed/ablations.csv`
- `results/processed/event_sufficiency.csv`
- `results/processed/synthesis.csv`
- `results/figures/*.svg`

The paper must label current replay, baseline, ablation, and event-sufficiency numbers as model-level or firmware-sim evidence until replaced or corroborated by RTL/PicoRV32 runs.

The result pipeline is:

1. `scripts/run_all_tests.py`
2. `scripts/run_replay_experiments.py`
3. `scripts/collect_trace_sizes.py`
4. `scripts/run_ablations.py`
5. `scripts/synth_yosys.py`
6. `scripts/parse_synthesis_reports.py`
7. `scripts/make_figures.py`

The one-command local gate is `scripts/run_all_tests.py`, wrapped by `scripts/reproduce_all.ps1` on Windows and `scripts/reproduce_all.sh` on Unix-like shells.
