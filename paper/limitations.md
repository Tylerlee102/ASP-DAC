# Limitations

The current model is limited to a single RV32I hart, deterministic core execution, identical firmware and initial state, and modeled nondeterminism at the interrupt/MMIO boundary.

Out of scope:

- multicore
- cache coherence
- DMA unless modeled as events
- analog nondeterminism
- undefined C behavior guarantees
- arbitrary external bus reordering
- unsupported properties
- unbounded firmware claims

The current implementation is also an early scaffold: six PicoRV32 wrapper firmware smokes and generic synthesis numbers are measured, but benchmark-wide firmware-running tests, replay outputs, and mapped FPGA timing/resource numbers remain pending.
