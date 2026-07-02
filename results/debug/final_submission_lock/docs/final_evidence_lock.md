# Final Evidence Lock

This document locks the evidence used for the main-track submission polish pass. Numeric evidence below is read from `results/processed/*.csv`.

## CI And Artifact

- CI run: latest successful final-reproduce run on master
- Commit: `current master commit`
- Artifact: `replaycapsule-rv-final-evidence`
- Artifact id: `see GitHub Actions artifact metadata`
- Artifact digest: `see GitHub Actions artifact metadata`
- Final CI gate: PASS (none)
- Final CI verification: FAIL (2 hard failure rows)

## Firmware And Replay

- Compiler-backed firmware builds: 15/15 PASS from `results/processed/firmware_build.csv`.
- Benchmark families: 6.
- Full RTL replay: 45/45 PASS from `results/processed/full_rtl_replay.csv`.
- Full RTL negative replay: 10 rejected, 0 unexpected accepts, 2 not-applicable rows from `results/processed/full_rtl_replay_negative.csv`.

## Runtime Overhead Summary

- baseline_no_recorder / sim_wall_time_sec: median 0.014222, n=45, status MEASURED; simulator wall-clock time; not hardware runtime
- recorder_present_disabled / sim_wall_time_sec: median 0.098393, n=45, status MEASURED; simulator wall-clock time; not hardware runtime
- recorder_enabled / sim_wall_time_sec: median 0.099966, n=45, status MEASURED; simulator wall-clock time; not hardware runtime
- recorder_present_disabled_vs_baseline_no_recorder / cycle_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_present_disabled_vs_baseline_no_recorder / commit_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_present_disabled_vs_baseline_no_recorder / sim_wall_time_overhead_pct: median 570.680000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_enabled_vs_baseline_no_recorder / cycle_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_enabled_vs_baseline_no_recorder / commit_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_enabled_vs_baseline_no_recorder / sim_wall_time_overhead_pct: median 565.540000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus

## Mapped Overhead Summary

- Summary: PASS on ecp5-85k using yosys+synth_ecp5+nextpnr-ecp5; overhead claim allowed: yes.
- full_core_baseline_board: 3332 LUT, 883 FF, 6 BRAM, Fmax 63.47 MHz.
- full_core_replaycapsule_board: NA LUT, NA FF, NA BRAM, Fmax NA MHz.
- Overhead: LUT NA%, FF NA%, BRAM NA%, Fmax delta NA%.
- v2 minimal recorder profile: LUT 8.26%, FF 3.77%, BRAM 0.00%, Fmax delta -0.04%.
- v2 diagnostic comparison, not selected area claim: core LUT 68.00%, hashed LUT 67.69%.
- Recorder presence: PASS.

## ASIC/open-PDK Evidence

- Summary: PASS; 5/5 OpenROAD placed/global-routed rows PASS with area, WNS/TNS, and power.
- Selected v2 minimal physical overhead: area 1.72%, power 10.02%.
- Selected v2 minimal synthesis-only area overhead: 1.76%.
- Scope boundary: OpenROAD rows are global-routed implementation evidence, not detailed-route signoff, tapeout, silicon, or energy data.

## Paper Build

- Paper target: `paper/main.pdf`
- Status: PASS
- Tool: tectonic
- Output: `paper\main.pdf`

## Locked Copy Directory

The files named in the submission prompt are copied into `results/debug/final_submission_lock/` for reviewer-facing freeze/audit purposes.
