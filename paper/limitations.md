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

The current implementation is still scoped: replay consume is host-driven, the target is single-hart RV32I interrupt/MMIO behavior, and the ECP5 implementation prioritizes replay fidelity and auditability over area minimization. The measured evidence includes compiler-backed firmware, full firmware-running RTL replay, full RTL replay-critical corruption rejection, runtime summaries, bounded local formal checks, generic synthesis context, and same-target full-core ECP5 mapped resources/timing. The artifact does not claim ASIC area or power, multi-hart behavior, DMA behavior, cache-coherence behavior, broad platform replay, or a hardware replay-consume datapath.
