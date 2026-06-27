# Limitations

ReplayCapsule-RV v1 is intentionally narrow.

## In Scope

- single-core RV32I embedded systems
- deterministic core execution
- fixed firmware image and reset state
- deterministic instruction memory and non-MMIO data memory
- nondeterministic boundary events through MMIO reads, external inputs, and interrupt timing
- supported safety properties with explicit failure signatures
- bounded firmware benchmarks

## Out Of Scope

- multicore replay
- cache coherence
- DMA unless represented as modeled events
- analog nondeterminism
- undefined C behavior guarantees
- arbitrary external bus reordering
- unmodeled wait-state side effects
- self-modifying external instruction memory
- security-grade cryptographic capsule integrity

## Current Implementation Limits

- The locked Linux CI path includes compiler-backed firmware builds, host-driven full RTL record/replay, negative corrupted-capsule checks, runtime summaries, same-target ECP5 place-and-route rows, paper build/audits, and artifact packaging.
- The replay-consume path is host-driven in the Verilator harness; no synthesizable replay-consume datapath is claimed.
- Runtime overhead rows report Verilator cycle, commit, and simulator wall-clock measurements; they are not hardware runtime, energy, or power claims.
- The ECP5 mapped implementation is a board-level feasibility and overhead measurement, not an area-optimized implementation and not an ASIC result.
- Full RTL-backed trace-size reductions and full RTL ablation variants beyond the current model/RTL-smoke evidence remain future work.
