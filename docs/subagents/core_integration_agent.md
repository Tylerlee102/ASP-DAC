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

Until PicoRV32 and Verilator are present, Phase 1 uses a deterministic Python event model and a synthesizable RTL boundary scaffold.

