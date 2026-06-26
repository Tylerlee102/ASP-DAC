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

The current implementation is also an early scaffold: twelve PicoRV32 wrapper firmware smokes, twelve failing/fixed RTL-smoke capsule export self/negative/PC-context checks, twelve RTL/firmware-sim alignment rows, and generic synthesis numbers are measured, but benchmark-wide firmware-running replay tests and mapped FPGA timing/resource numbers remain pending.
