# Conclusion

ReplayCapsule-RV investigates a precise embedded-debug question: which hardware-visible events are sufficient to deterministically replay RV32I safety failures caused by interrupts and MMIO? The repository now contains the formal scaffold, synthesizable record-side RTL modules, a replay comparator, smoke experiments, and a no-fake-results evaluation pipeline. The next step is to replace the Phase 1 scaffold with a firmware-running PicoRV32 system and collect real replay, ablation, and synthesis results.

