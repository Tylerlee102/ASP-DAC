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

- The local Phase 1/2 executable path is a deterministic Python smoke model plus synthesizable RTL source files.
- The SoC RTL integration is a boundary scaffold, not a completed PicoRV32 firmware-running system.
- Verilator, Yosys, Make, and a RISC-V cross compiler were not available locally at kickoff.
- Synthesis and Fmax rows are TODO until a real flow is run.
- Only the sensor-threshold smoke replay is currently measured.

