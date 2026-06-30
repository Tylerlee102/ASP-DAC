# ReplayCapsule-RV v2 Zero-Fail Status

Last inspected: 2026-06-29.

## Bottom Line

The measured v2 evidence set is zero-fail for the scoped benchmark and
representative mapping claims. The authoritative audit file is
`results/processed/v2_zero_fail_bug_inventory.csv`; an empty data body means no
unexpected v2 FAIL, MISMATCH, TIMEOUT, or BLOCKED row remains in the required
measured v2 evidence set.

## Measured Evidence

| Requirement | Evidence | Current result |
| --- | --- | --- |
| v2 all-benchmark core/hashed/full replay | `results/processed/full_rtl_replay_v2.csv` | 135/135 PASS rows across core, hashed, and full recorder configs with RTL consumer checks |
| v2 workload scaling | `results/processed/workload_scaling_v2_measured.csv` | 1125/1125 PASS rows |
| v2 buffer sensitivity | `results/processed/buffer_sensitivity_v2_measured.csv` | 1125/1125 v2 measured PASS rows at the measured depth; other depths remain explicit blocked placeholders unless regenerated |
| v2 runtime overhead | `results/processed/runtime_scaling_v2_measured.csv` | 25/25 MEASURED rows across baseline, disabled recorder, and v2 core/hashed/full configs |
| v2 mapped full-core overhead | `results/processed/mapped_scaling_v2_measured.csv` and `results/processed/mapped_scaling_overhead_v2_measured.csv` | Same-target ECP5-85k baseline plus v2 minimal/core/hashed PASS at memory 128, buffer depth 8; selected minimal recorder profile is `+8.26%` LUT and `+3.77%` FF |
| v2 mapped recorder presence | `results/processed/mapped_recorder_presence_v2_measured.csv` | 3/3 measured minimal/core/hashed rows PASS with recorder hierarchy present |
| v2 minimal recorder fidelity | `results/processed/hdl_checks.csv` | `tb_rcv2_minimal_recorder` PASS: selected minimal recorder emits replay-critical boundary events accepted by the v2 replay consumer |
| v2 new benchmark PASS coverage | `results/processed/expanded_benchmark_replay_measured.csv` | 36/36 PASS rows for `commanded_actuator_limit_bug` and `late_config_sequence_bug` across core/hashed/full and three seeds |
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

On Windows shells, prefer the checked-in interpreter-discovery wrapper for the
local gate, or pass a real interpreter explicitly:

```sh
.\scripts\reproduce_all.ps1
make topconf-v2-measured PYTHON=/path/to/python
make replay-consumer-v2 PYTHON=/path/to/python
```

## Scope Discipline

Safe claims:

- Compiler-backed, host-driven v2 full RTL record/replay passes for the scoped
  single-hart RV32I interrupt/MMIO benchmark suite.
- v2 workload scaling, runtime overhead, measured-depth buffer sensitivity, and
  same-target ECP5 full-core overhead for the selected minimal recorder profile
  are measured in the listed CSVs; core/hashed mapped rows are diagnostic
  comparisons.
- Two additional compiler-backed firmware benchmark families have measured v2
  PASS coverage across three seeds.

Still forbidden:

- Do not claim autonomous full-core hardware replay consumption. The
  replay-consume controller is real RTL with tests and host-streamed full-core
  checks, but capsule storage/streaming and MMIO/IRQ replay muxing remain
  future work.
- Do not claim ASIC area, power, or timing.
- Do not claim multicore, DMA, cache-coherent, OS, or broad platform replay.
- Do not describe broad v2 overhead as low; report the measured overhead for
  each recorder config.
