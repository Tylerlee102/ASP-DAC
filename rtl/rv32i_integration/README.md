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

PicoRV32 is now vendored under `third_party/picorv32`. The wrapper is source-present but has not been compiled or simulated locally because Verilator/Yosys are unavailable.

## MMIO Map

| Address | Name | Direction | Purpose |
|---|---|---:|---|
| `0x4000_0000` | sensor | read | external sensor sample |
| `0x4000_0004` | actuator | write | safe actuator/PWM command |
| `0x4000_0008` | config | write | safety configuration latch |
| `0x4000_000c` | command | read/write | UART/command-register stand-in |
