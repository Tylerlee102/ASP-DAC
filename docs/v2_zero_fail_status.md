# ReplayCapsule-RV v2 Zero-Fail Status

Last inspected: 2026-06-28.

## Bottom Line

The measured v2 evidence set is zero-fail for the scoped benchmark and
representative mapping claims. The authoritative audit file is
`results/processed/v2_zero_fail_bug_inventory.csv`; an empty data body means no
unexpected v2 FAIL, MISMATCH, TIMEOUT, or BLOCKED row remains in the required
measured v2 evidence set.

## Measured Evidence

| Requirement | Evidence | Current result |
| --- | --- | --- |
| v2 all-benchmark core/hashed/full replay | `results/processed/full_rtl_replay_v2.csv` | 135/135 PASS rows across core, hashed, and full recorder configs |
| v2 workload scaling | `results/processed/workload_scaling_v2_measured.csv` | 1125/1125 PASS rows |
| v2 buffer sensitivity | `results/processed/buffer_sensitivity_v2_measured.csv` | 6750/6750 v2 measured PASS rows across depths 64, 128, 256, 512, 1024, and 2048 |
| v2 runtime overhead | `results/processed/runtime_scaling_v2_measured.csv` | 25/25 MEASURED rows across baseline, disabled recorder, and v2 core/hashed/full configs |
| v2 mapped full-core overhead | `results/processed/mapped_scaling_v2_measured.csv` and `results/processed/mapped_scaling_overhead_v2_measured.csv` | Same-target ECP5-85k baseline plus v2 core/hashed/full PASS at memory 128, buffer depth 16; all 12 overhead rows are claim-allowed |
| v2 mapped recorder presence | `results/processed/mapped_recorder_presence_v2_measured.csv` | 3/3 PASS rows with recorder hierarchy present |
| v2 new benchmark PASS coverage | `results/processed/expanded_benchmark_replay_measured.csv` | 12/12 PASS rows for `commanded_actuator_limit_bug` and `late_config_sequence_bug` across core/hashed/full |
| v2 replay-consume system tests | `results/processed/replay_consumer_system_tests.csv` | 8/8 PASS rows |

## Reproduction Commands

Full measured v2 evidence:

```sh
make topconf-v2-measured
make replay-consumer-v2
```

Equivalent focused commands:

```sh
python scripts/run_v2_measured_evaluation.py --timeout-sec 45 --measure-all-buffer-depths
python scripts/run_expanded_benchmark_replay.py
python scripts/build_v2_zero_fail_bug_inventory.py
```

On Windows shells where `python3` resolves to the Microsoft Store alias, pass a
real interpreter explicitly, for example:

```sh
make topconf-v2-measured PYTHON=/path/to/python
make replay-consumer-v2 PYTHON=/path/to/python
```

## Scope Discipline

Safe claims:

- Compiler-backed, host-driven v2 full RTL record/replay passes for the scoped
  single-hart RV32I interrupt/MMIO benchmark suite.
- v2 workload scaling, runtime overhead, buffer sensitivity, and same-target
  ECP5 full-core overhead are measured in the listed CSVs.
- Two additional compiler-backed firmware benchmark families have measured v2
  PASS coverage.

Still forbidden:

- Do not claim autonomous full-core hardware replay consumption. The
  replay-consume controller is real RTL with tests, but the full-core replay
  flow remains host-driven.
- Do not claim ASIC area, power, or timing.
- Do not claim multicore, DMA, cache-coherent, OS, or broad platform replay.
- Do not describe v2 overhead as low; report the measured overhead.
