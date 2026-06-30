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
- Full-core replay consume remains host-driven in the Verilator harness. The v2 replay-consume controller is tested RTL and is wired into the full-core wrapper as a host-streamed checker: the harness supplies saved capsule words and the wrapper supplies observed boundary events. Capsule storage/streaming, core MMIO/IRQ replay muxing, and autonomous replay-mode control are not integrated.
- Runtime overhead rows report Verilator cycle, commit, and simulator wall-clock measurements; they are not hardware runtime, energy, or power claims.
- Replay-critical workload scaling requires workload-aware capsule depth. The generated v1 evidence uses 256 entries for smoke and short workloads, 1024 for medium, 4096 for long, and 16384 for stress; fixed/no-failure rows can still assert the sticky overflow bit because they run until the cycle bound.
- The ECP5 mapped implementation is board-level bring-up/debug instrumentation, not an area-optimized implementation and not an ASIC result. Disabling unselected v2 recorder logic reduces the smallest mapped point, but representative rows still show high LUT/FF overhead.
- Full RTL-backed ablation variants beyond the current model/RTL-smoke evidence remain future work.
