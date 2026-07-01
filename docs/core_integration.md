# Core Integration Plan

ReplayCapsule-RV should use PicoRV32 first because it is compact, RV32I-friendly, and easy to wrap in small FPGA-style SoCs.

## Phase 1 Boundary

The current implementation uses a deterministic SoC scaffold in `rtl/rv32i_integration/replaycapsule_soc.sv`. It is deliberately a boundary exerciser, not a paper result. It provides the signals the replay capsule hardware needs while the real RISC-V simulator/toolchain path is brought up.

PicoRV32 has also been vendored under `third_party/picorv32`, and `rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv` instantiates the upstream core with IRQ and trace support enabled. The wrapper connects native memory transactions, trace-valid events, IRQ/EOI observations, and external inputs into `replay_capsule_top`.

The v2 self-replay source/controller integration now also exists as reusable RTL in `rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv`. The focused Icarus smoke `tb_picorv32_standalone_self_replay_smoke` records a PicoRV32 v2 failure, resets the core, launches captured-store replay through that shell, checks that the replay consumer consumes the captured words, and requires matching nonzero PicoRV32 interrupt-handler entry counts on IRQ-triggered rows. This is still a focused testbench shell, not a board/silicon replay flow.

The current wrapper handles PicoRV32 trace classes explicitly: `TRACE_ADDR`
records are treated as memory-address sideband rather than commit records, and
the commit counter advances only on non-address trace records. Memory events in
the smoke capsules use the most recent instruction-fetch address as their PC
context, which is adequate for local smoke evidence but still below a full RVFI
or retirement-validated integration.

## PicoRV32 Integration Target

Connect:

- instruction memory at reset PC `0x0000_0080`
- data memory below the MMIO aperture
- MMIO aperture at `0x4000_0000`
- timer interrupt source into the core interrupt request line
- sensor input register
- actuator/PWM output register
- command/UART register
- commit visibility via either a retirement pulse wrapper, RVFI-style wrapper, or an instruction-valid approximation validated against the core configuration

## Modes

- deterministic seeded input mode for reproducible baseline experiments
- randomized interrupt mode for stress testing
- replay mode in which MMIO read values and interrupt timing come from a capsule

## Open Work

- Add a bare-metal RISC-V compiler path.
- Scale the fifteen current PicoRV32 wrapper smokes into full replay/export/compare
  runs for all benchmark firmware images.
- Connect fuller instruction/data memory and MMIO peripheral models around the PicoRV32 wrapper.
- Confirm the commit pulse corresponds to architectural instruction retirement.
