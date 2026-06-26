# Baseline Plan

ReplayCapsule-RV must be compared against strong baselines, not strawmen.

## Baselines

| Baseline | Captures | Replay Expectation | Hardware Status |
| --- | --- | --- | --- |
| full instruction trace | every fetched/retired instruction | should replay or reconstruct all control flow if inputs are also captured | simulator-first |
| full commit trace | committed PC/instruction/register side effects | should reproduce architectural path with high storage cost | simulator-first |
| branch-only trace | taken branches/jumps | insufficient for MMIO/interrupt nondeterminism | simulator-first |
| store-only trace | all stores | useful for output evidence, insufficient for input replay | simulator-first |
| MMIO-only trace | MMIO reads/writes | enough for some polling failures, not interrupt races | RTL-capable |
| interrupt + MMIO trace | interrupt timing plus MMIO values | likely sufficient for many supported bugs | RTL-capable |
| snapshot-on-failure | failure-time state snapshot | helps diagnosis but cannot replay pre-failure nondeterminism by itself | simulator-first |
| property-aware ReplayCapsule-RV | nondeterministic events plus property context | target design | RTL-backed |

## Required Measurements

- replay success
- trace/capsule bytes
- events per kilo-instruction
- failure reproduction accuracy
- implemented hardware overhead or simulator-only overhead status

`scripts/collect_trace_sizes.py` computes available trace-size metrics from generated artifacts. It reports missing baselines as TODO rather than estimating them. When RTL smoke capsule exports are available, the script also reports `rtl_smoke_replaycapsule_rv` rows from the exported 168-bit packet counts; those rows are capsule-size evidence only, not benchmark-wide replay-success evidence. `scripts/summarize_rtl_capsule_classes.py` decodes the same RTL-smoke packets into event-class counts for baseline transparency. `scripts/summarize_synthesis_overhead.py` reports only generic Yosys cell-overhead context; mapped FPGA overhead remains pending.
