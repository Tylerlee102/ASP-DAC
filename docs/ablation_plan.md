# Ablation Plan

The ablation study asks which event classes are necessary for replay under the defined model.

## Required Ablations

| Ablation | Expected Risk |
| --- | --- |
| remove branch events | property-context or debug evidence may degrade; replay of MMIO-driven failures may still pass |
| remove store events | stack/control-flow corruption evidence may disappear |
| remove MMIO read values | polling and sensor-input failures stop replaying |
| remove interrupt timing | interrupt-race and watchdog failures stop replaying |
| remove external input values | command/UART and GPIO-driven failures stop replaying |
| remove checkpoint hashes | replay may still reproduce but integrity checks weaken |
| remove property-aware slicing | capsule grows or loses failure-local evidence depending policy |
| vary capsule buffer size | overflow rate and replay validity change |
| vary last-K context window | reviewer-visible evidence changes, replay may remain sufficient |

The current model-level ablation script exercises all six benchmark models and writes:

- `results/processed/ablations.csv`
- `results/processed/event_sufficiency.csv`

It includes event-class removals, buffer-size sweeps, and last-K context-window sweeps at the model level. Full RTL-backed ablations still require firmware-running PicoRV32/RTL traces.
