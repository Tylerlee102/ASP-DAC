# RV32I Integration Scaffold

Phase 1 provides two integration layers:

- `replaycapsule_soc.sv`: a deterministic SoC boundary scaffold that drives the same visible signals expected from a small RV32I core.
- `picorv32_replaycapsule_wrapper.sv`: a PicoRV32-facing wrapper that instantiates the vendored upstream core and connects its native memory, trace, IRQ, and EOI signals to `replay_capsule_top`.

The scaffold drives:

- commit valid, PC, instruction, and commit index
- memory access valid/write/address/data
- MMIO sensor input
- MMIO actuator and configuration writes
- timer interrupt enter signal

The deterministic scaffold is not claimed as a PicoRV32 integration result. It exists so the event tap, property checker, and capsule buffer can be developed before Verilator and a RISC-V compiler are available locally.

PicoRV32 is now vendored under `third_party/picorv32`. The wrapper is exercised
by Icarus smoke tests for all six failing/fixed benchmark images and by
Verilator lint. The wrapper treats PicoRV32 `TRACE_ADDR` records as
memory-address sideband rather than architectural commits, and uses the most
recent instruction-fetch address as the memory-event PC context for smoke-level
capsules. Full benchmark-wide RTL replay/export/compare simulation remains
pending.

FemtoRV32 Quark is vendored under `third_party/femtorv32` as a second RV32I
core candidate. The current evidence checks source/license metadata, a
ReplayCapsule wrapper, Verilator frontend lint, and generic Yosys synthesis
through `results/processed/second_core_breadth.csv`. The wrapper also has one
compiler-built sensor-threshold capture smoke in `results/processed/hdl_checks.csv`.
There is not yet a full firmware-running FemtoRV32 ReplayCapsule record/replay
row or interrupt replay claim.

## MMIO Map

| Address | Name | Direction | Purpose |
|---|---|---:|---|
| `0x4000_0000` | sensor | read | external sensor sample |
| `0x4000_0004` | actuator | write | safe actuator/PWM command |
| `0x4000_0008` | config | write | safety configuration latch |
| `0x4000_000c` | command | read/write | UART/command-register stand-in |
