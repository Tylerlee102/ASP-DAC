# Final Evidence Lock

This document locks the evidence used for the main-track submission polish pass. Numeric evidence below is read from `results/processed/*.csv`.

## CI And Artifact

- CI run: latest successful final-reproduce run on master
- Commit: `current master commit`
- Artifact: `replaycapsule-rv-final-evidence`
- Artifact id: `see GitHub Actions artifact metadata`
- Artifact digest: `see GitHub Actions artifact metadata`
- Final CI gate: PASS (none)
- Final CI verification: PASS

## Firmware And Replay

- Compiler-backed firmware builds: 15/15 PASS from `results/processed/firmware_build.csv`.
- Benchmark families: 6.
- Full RTL replay: 45/45 PASS from `results/processed/full_rtl_replay.csv`.
- Full RTL negative replay: 10 rejected, 0 unexpected accepts, 2 not-applicable rows from `results/processed/full_rtl_replay_negative.csv`.

## Runtime Overhead Summary

- baseline_no_recorder / sim_wall_time_sec: median 0.018194, n=45, status MEASURED; simulator wall-clock time; not hardware runtime
- recorder_present_disabled / sim_wall_time_sec: median 0.024409, n=45, status MEASURED; simulator wall-clock time; not hardware runtime
- recorder_enabled / sim_wall_time_sec: median 0.024731, n=45, status MEASURED; simulator wall-clock time; not hardware runtime
- recorder_present_disabled_vs_baseline_no_recorder / cycle_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_present_disabled_vs_baseline_no_recorder / commit_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_present_disabled_vs_baseline_no_recorder / sim_wall_time_overhead_pct: median 32.550000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_enabled_vs_baseline_no_recorder / cycle_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_enabled_vs_baseline_no_recorder / commit_overhead_pct: median 0.000000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus
- recorder_enabled_vs_baseline_no_recorder / sim_wall_time_overhead_pct: median 33.950000, n=45, status MEASURED; relative to baseline_no_recorder with same firmware/stimulus

## Mapped Overhead Summary

- Summary: PASS on ecp5-85k using yosys+synth_ecp5+nextpnr-ecp5; overhead claim allowed: yes.
- full_core_baseline_board: 2814 LUT, 883 FF, 6 BRAM, Fmax 63.47 MHz.
- full_core_replaycapsule_board: 6859 LUT, 3901 FF, 6 BRAM, Fmax 50.70 MHz.
- Overhead: LUT 143.75%, FF 341.79%, BRAM 0.00%, Fmax delta -20.12%.
- Recorder presence: PASS.

## Paper Build

- Paper target: `paper/main.pdf`
- Status: PASS
- Tool: locked-ci-artifact
- Output: `paper\main.pdf`

## Locked Copy Directory

The files named in the submission prompt are copied into `results/debug/final_submission_lock/` for reviewer-facing freeze/audit purposes.
