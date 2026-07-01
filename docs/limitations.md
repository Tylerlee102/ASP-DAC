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

- The locked Linux CI path includes compiler-backed firmware builds, full RTL record/replay, negative corrupted-capsule checks, runtime summaries, same-target ECP5 place-and-route rows, paper build/audits, and artifact packaging.
- The v2 full-core replay path now uses an RTL capsule source, RTL replay-mode controller, and RTL replay-consume controller: the record path exercises a reset-persistent RTL capture store for replay-critical words, self-replay rows stream from that captured store without harness-preloaded capsule words, and the consumer drives core-facing MMIO read data and IRQ timing. The artifact also includes a reusable RTL self-replay shell with a focused Icarus standalone smoke. Remaining autonomy limits are board/silicon reset control and broad peripheral-shell integration beyond the focused testbench.
- Runtime overhead rows report Verilator cycle, commit, and simulator wall-clock measurements; they are not hardware runtime, energy, or power claims.
- Replay-critical workload scaling requires workload-aware capsule depth. The generated v1 evidence uses 256 entries for smoke and short workloads, 1024 for medium, 4096 for long, and 16384 for stress; fixed/no-failure rows can still assert the sticky overflow bit because they run until the cycle bound.
- The ECP5 mapped implementation is board-level recorder evidence. The artifact now also includes Nangate45 OpenROAD placed/global-routed area, timing, and power rows, but not detailed-route signoff, tapeout, silicon, or energy. The selected v2 minimal recorder profile removes diagnostic logic at compile time and has a separate same-target overhead row; the core/hashed diagnostic rows still show high LUT/FF overhead.
- Full RTL-backed ablation variants beyond the current model/RTL-smoke evidence remain future work.
