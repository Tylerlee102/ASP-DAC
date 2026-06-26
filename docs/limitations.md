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

- The local executable path includes a deterministic Python event model, an RV32I firmware interpreter, directed HDL checks, twelve PicoRV32 wrapper firmware smokes, RTL-smoke capsule export self/negative-checks, and generic Yosys synthesis.
- The SoC RTL integration has twelve firmware smokes, not a completed benchmark-wide PicoRV32 replay/export system.
- `make`, C++ build support for full Verilator simulations, and a RISC-V cross compiler are not available locally.
- Mapped FPGA LUT/FF/BRAM/Fmax rows are TODO until a real mapped flow is run.
- Model-level and firmware-sim replay are measured for six benchmarks; RTL firmware-running evidence is currently limited to twelve wrapper smokes and twelve failing/fixed smoke-level capsule export self/negative-checks.
