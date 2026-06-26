# core_integration_agent Plan

Owned files:

- `docs/core_integration.md`
- `rtl/rv32i_integration/README.md`
- `firmware/common/README.md`
- `tb/system/README.md`

Mission:

Plan PicoRV32-first integration with a minimal embedded SoC:

- RV32I core
- instruction memory
- data memory
- timer interrupt source
- MMIO sensor input
- MMIO actuator/PWM output
- UART or command register
- commit-event visibility
- deterministic seeded input mode
- randomized interrupt mode

Phase 1 now uses a deterministic Python event model, an RV32I firmware interpreter, a synthesizable RTL boundary scaffold, and PicoRV32 wrapper smokes. Full Verilator/C++ simulation and external RISC-V compiler paths remain future integration work.
