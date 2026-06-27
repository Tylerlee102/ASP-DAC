# Top-Conference Evaluation Matrix

This matrix defines the quick and full evaluation space before results are marked PASS. Result-producing scripts update separate evidence CSVs; this file is a plan, not a pass list.

| Experiment group | Defined rows | Evidence output |
|---|---:|---|
| Buffer-depth sensitivity | 8 | results/processed/buffer_sensitivity.csv |
| Capsule-size baseline comparison | 420 | results/processed/capsule_baseline_comparison.csv |
| Event-sufficiency ablation at scale | 8 | results/processed/event_ablation_scaling.csv |
| Failure diagnosis for failed mapped rows | 76 | results/processed/mapped_failure_diagnosis.csv |
| Full-core mapped FPGA scaling | 152 | results/processed/mapped_scaling.csv |
| Negative/corruption replay | 12 | results/processed/full_rtl_replay_negative.csv |
| Paper figure/table generation | 2 | paper/figures/fig_*.pdf, paper/tables/*.tex |
| Recorder presence after mapping | 76 | results/processed/mapped_recorder_presence.csv |
| Recorder-configuration sensitivity | 10 | results/processed/recorder_config_replay.csv |
| Replay correctness | 420 | results/processed/workload_scaling.csv |
| Runtime overhead | 420 | results/processed/runtime_scaling.csv |
| Workload scaling | 8 | results/processed/workload_scaling.csv |

Quick mode covers all six benchmark families with a small seed/scale subset for local debugging.
Full mode expands seeds, workload scales, memory sizes, buffer depths, and recorder configurations when CI time permits.
Rows remain `DEFINED` here until their corresponding processed CSV contains measured, estimated, blocked, timeout, or failed evidence.
