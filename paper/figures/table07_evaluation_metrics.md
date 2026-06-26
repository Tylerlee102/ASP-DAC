# Table 7. Evaluation Metric Rollup

Generated from `../../results/processed/evaluation_metrics.csv`.

Metrics marked `TODO` require benchmark-wide firmware-running RTL, mapped FPGA,
or hardware timing data and are not estimated.

| Metric | Status | Value | Unit | Evidence level | Notes |
| --- | --- | ---: | --- | --- | --- |
| model_replay_success_rate | MEASURED (model) | 6/6 (100.0%) | percent | model | Model-level commit-index replay rows. |
| firmware_sim_replay_success_rate | MEASURED (firmware-sim) | 6/6 (100.0%) | percent | firmware-sim | RV32I firmware-sim commit-index replay rows. |
| firmware_running_rtl_replay_success_rate | TODO (rtl) | TODO | percent | rtl | Benchmark-wide firmware-running RTL replay remains blocked by missing make/C++/RISC-V compiler support. |
| replay_negative_fixture_pass_rate | MEASURED (model) | 96/96 (100.0%) | percent | model | Benchmark-derived positive and negative comparator fixtures across commit-index and cycle-index modes. |
| hdl_frontend_pass_rate | MEASURED (rtl-smoke) | 28/28 (100.0%) | percent | rtl-smoke | Directed Icarus simulations, PicoRV32 wrapper smokes, and Verilator lint-only frontend checks. |
| directed_icarus_module_pass_rate | MEASURED (rtl-smoke) | 9/9 (100.0%) | percent | rtl-smoke | Standalone directed Icarus module simulations excluding PicoRV32 wrapper smoke rows. |
| picorv32_wrapper_smoke_pass_rate | MEASURED (rtl-smoke) | 15/15 (100.0%) | percent | rtl-smoke | Firmware-running PicoRV32 wrapper smokes, including failing/fixed images and selected no-failure edge cases. |
| verilator_lint_pass_rate | MEASURED (rtl-smoke) | 4/4 (100.0%) | percent | rtl-smoke | Verilator lint-only frontend checks for top-level integration and property assertion sources. |
| picorv32_smoke_log_sanity_pass_rate | MEASURED (rtl-smoke) | 6/6 (100.0%) | percent | rtl-smoke | Generated log-level checks over PicoRV32 wrapper smoke capsule counts, property IDs, freeze state, and overflow state. |
| six_benchmark_local_coverage_rate | MEASURED (model+firmware-sim+rtl-smoke) | 6/6 (100.0%) | percent | model+firmware-sim+rtl-smoke | Per-benchmark local evidence coverage across model replay, firmware-sim replay, wrapper smokes, RTL-smoke exports, alignment, and sufficiency rows; full RTL replay remains TODO. |
| rtl_smoke_capsule_export_pass_rate | MEASURED (rtl-smoke) | 12/12 (100.0%) | percent | rtl-smoke | Exported RTL-smoke capsules parse and pass self/negative checks; not benchmark-wide RTL replay. |
| rtl_smoke_false_property_failures | MEASURED (rtl-smoke) | 0/6 | count | rtl-smoke | Fixed RTL-smoke and firmware-sim variants both avoid property failures. |
| rtl_smoke_missed_property_failures | MEASURED (rtl-smoke) | 0/6 | count | rtl-smoke | Failing RTL-smoke and firmware-sim variants align on property IDs. |
| seeded_rtl_smoke_interrupt_reproducibility_rate | MEASURED (rtl-smoke) | 13/13 (100.0%) | percent | rtl-smoke | Seeded interrupt-race RTL-smoke cases rerun in fresh simulator invocations and compare frozen capsule digests. |
| seeded_randomized_interrupt_coverage_item_pass_rate | MEASURED (rtl-smoke) | 8/12 (66.7%) | percent | rtl-smoke | Generated checklist over current seeded interrupt coverage, seed-specific corruption rejection, and stronger randomized RTL cases still marked TODO. |
| bounded_buffer_overflow_contract_pass_rate | MEASURED (rtl-smoke+formal-bmc) | 4/4 (100.0%) | percent | rtl-smoke+formal-bmc | Local overflow contract evidence from directed capsule-buffer simulation, bounded formal checks, and PicoRV32 wrapper smoke no-overflow sanity; benchmark-wide runtime overflow rate remains TODO. |
| median_firmware_sim_replaycapsule_bytes | MEASURED (firmware-sim) | 94.5 | bytes | firmware-sim | ReplayCapsule bytes over firmware-sim failing runs. |
| median_firmware_sim_full_instruction_trace_bytes | MEASURED (firmware-sim) | 48 | bytes | firmware-sim | Full instruction-trace bytes over firmware-sim failing runs. |
| median_firmware_sim_snapshot_bytes | MEASURED (firmware-sim) | 132 | bytes | firmware-sim | Architectural snapshot bytes over firmware-sim failing runs. |
| median_firmware_sim_reduction_vs_full_instruction | MEASURED (firmware-sim) | 0.667 | x | firmware-sim | Full-instruction bytes divided by ReplayCapsule bytes; less than 1.0 means the capsule is larger for these tiny workloads. |
| median_firmware_sim_reduction_vs_snapshot | MEASURED (firmware-sim) | 1.414 | x | firmware-sim | Snapshot bytes divided by ReplayCapsule bytes. |
| median_model_reduction_vs_full_commit | MEASURED (model) | 0.762 | x | model | Model full-commit bytes divided by model ReplayCapsule bytes using fixed record-size estimates. |
| median_model_cycles_to_failure | MEASURED (model) | 7.5 | cycles | model | Median cycle index of EV_PROPERTY_FAIL in generated failing traces. |
| median_model_commits_to_failure | MEASURED (model) | 3.5 | commits | model | Median commit index of EV_PROPERTY_FAIL in generated failing traces. |
| median_firmware_sim_cycles_to_failure | MEASURED (firmware-sim) | 7.5 | cycles | firmware-sim | Median cycle index of EV_PROPERTY_FAIL in generated failing traces. |
| median_firmware_sim_commits_to_failure | MEASURED (firmware-sim) | 5 | commits | firmware-sim | Median commit index of EV_PROPERTY_FAIL in generated failing traces. |
| generic_yosys_cell_delta | MEASURED (generic-yosys) | 1504 | cells | generic-yosys | Generic unmapped cell-count delta; not LUT/FF/BRAM/Fmax. |
| generic_yosys_cell_overhead_percent | MEASURED (generic-yosys) | 289.79 | percent | generic-yosys | Generic unmapped cell-count overhead; mapped FPGA overhead remains TODO. |
| mapped_lut_overhead_percent | TODO (mapped-fpga) | TODO | percent | mapped-fpga | Requires mapped FPGA LUT reports. |
| mapped_ff_overhead_percent | TODO (mapped-fpga) | TODO | percent | mapped-fpga | Requires mapped FPGA FF reports. |
| bram_overhead | TODO (mapped-fpga) | TODO | brams | mapped-fpga | Requires mapped FPGA BRAM reports. |
| fmax_loss_percent | TODO (mapped-fpga) | TODO | percent | mapped-fpga | Requires timing reports from OpenROAD or vendor FPGA flow. |
| runtime_slowdown_percent | TODO (rtl) | TODO | percent | rtl | Requires benchmark-wide firmware-running RTL or hardware execution timing. |
| buffer_overflow_rate | TODO (rtl) | TODO | percent | rtl | Requires benchmark-wide runtime overflow counters; bounded buffer checks exist separately. |
