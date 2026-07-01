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

The current implementation is still scoped: replay consume is host-driven in the full-core flow, the target is single-hart RV32I interrupt/MMIO behavior, and the ECP5 implementation prioritizes replay fidelity and auditability over area minimization. Replay-critical workload scaling requires workload-aware buffer depth: 256 entries for smoke and short workloads, 1024 for medium, 4096 for long, and 16384 for stress. At those selected depths, the generated capsule-size reduction against the raw full-instruction trace falls to 22.84% on stress workloads, so the paper does not claim the smallest buffer depth or the strongest trace-compression baseline.

The v2 replay-consume controller is tested RTL and is wired into the full-core Verilator wrapper to check observed boundary events against saved or captured capsule words. The v2 path now includes RTL capsule storage/source, MMIO and IRQ replay muxing around the core, and a replay-mode controller for captured-store handoff. It is still not an autonomous board/silicon replay datapath because reset orchestration and the memory/peripheral shell remain in the Verilator harness. The artifact reports Nangate45 OpenROAD placed/global-routed ASIC/open-PDK area, timing, and power rows, but does not claim detailed-route signoff, tapeout, silicon energy, multi-hart behavior, DMA behavior, cache-coherence behavior, broad platform replay, or autonomous full-core hardware replay consume.
