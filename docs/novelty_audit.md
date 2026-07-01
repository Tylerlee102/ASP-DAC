# ReplayCapsule-RV Novelty Audit

## Safe Claim

ReplayCapsule-RV explores event-sufficient failure capsules for replaying single-hart RV32I interrupt/MMIO failures, combining compiler-backed firmware-running RTL replay, corruption rejection, mapped recorder evidence, and scaling analysis.

ReplayCapsule-RV v2 adds an adaptive compressed capsule format, an RTL capture/source path, a replay-mode controller, and a synthesizable replay-consume controller prototype. The v2 recorder is integrated into the full-core record/replay harness and has measured zero-fail replay, scaling, runtime, a selected minimal-recorder ECP5 full-core overhead point, and measured core/hashed diagnostic mapping comparisons. The v2 replay source, replay-mode controller, and consumer are real RTL with corruption tests, full-core checks, reset-persistent capture-store tests, record-signature evidence, and same-instance self-replay rows from the captured RTL store. The path is not yet a standalone board/silicon replay engine because reset orchestration and the memory/peripheral shell remain in the Verilator harness.

## Forbidden Claims

- Do not claim "first" or "never done before".
- Do not claim global minimality.
- Do not claim replacement for RISC-V trace/debug standards.
- Do not claim full-system, multicore, cache, coherence, DMA, or OS replay.
- Do not call overhead low or negligible unless same-target measured data supports it.
- Claim only the generated Nangate45 OpenROAD placed/global-routed area, timing, and power rows; do not claim detailed-route signoff, tapeout, silicon, or energy.
- Do not claim a standalone board/silicon replay engine until reset control and the memory/peripheral shell are integrated outside Verilator orchestration.

## Audit Categories

### RISC-V Trace/Debug Standards

Prior work and standards define broad trace, debug, and observability mechanisms. ReplayCapsule-RV does not replace those standards. The project focuses on a narrower failure-capsule path for single-hart RV32I interrupt/MMIO replay.

### Post-Silicon Trace Compression

Prior work compresses execution traces and debug streams. ReplayCapsule-RV v2 uses compact event words, address tokens, and payload hashes, with measured full-core replay evidence for the scoped benchmark suite. Compression should be framed as scoped and measured for these workloads, not proven as generally optimal.

### Deterministic Replay

Prior deterministic replay systems can cover broader software and hardware scopes. ReplayCapsule-RV demonstrates deterministic replay for a constrained single-hart RV32I class using event-sufficient interrupt/MMIO capsules. It does not claim full-system replay.

### Hardware Runtime Monitors

ReplayCapsule-RV uses hardware property/event monitoring, but the contribution is the coupling of those events to replay capsules and corruption rejection. It does not claim a new general runtime-monitor theory.

### Embedded Logging

Embedded logs often capture diagnostic context. ReplayCapsule-RV separates replay-critical from diagnostic context in v2, but diagnostic capture is optional and must remain clearly distinguished from replay-critical validation.

### FPGA/Emulation Replay

The repository has ECP5 evidence for v1 and representative same-target ECP5-85k full-core overhead evidence for the selected v2 minimal recorder, with measured core/hashed diagnostic comparisons. The v2 mapping point is memory 128 and buffer depth 8. The selected minimal recorder profile records replay-critical boundary events and is reported separately from the diagnostic-rich core/hashed comparison rows.

### Checkpoint/Snapshot Systems

ReplayCapsule-RV compares against snapshot-at-failure estimates. It should not claim snapshots are obsolete; the safe statement is that event capsules can be much smaller for the measured single-hart MMIO/interrupt cases.

### Runtime Verification

The property checker supplies failure IDs and signatures. The project does not claim complete formal coverage of every RV32I behavior.

### Hardware Security Capsules

ReplayCapsule-RV rejects corrupted capsule streams in negative replay and v2 replay-consumer tests. It should not claim a complete security mechanism, tamper-proof storage, or adversarial integrity model beyond the tested corruption cases.

## Evidence Status

- v1 full RTL replay: measured.
- v1 negative replay: measured.
- v1 workload-scaling failures: diagnosed as buffer overflow.
- v2 recorder: RTL and Yosys hierarchy check.
- v2 replay source/consumer: RTL tests, full-core replay checks with RTL-streamed capsule words and MMIO/IRQ replay stimulus, and ECP5-85k prototype mapping.
- v2 workload replay: measured zero-fail in `results/processed/workload_scaling_v2_measured.csv`.
- v2 mapped full-core overhead: selected minimal-recorder same-target ECP5-85k overhead claim plus measured core/hashed diagnostic comparisons in `results/processed/mapped_scaling_v2_measured.csv` and `results/processed/mapped_scaling_overhead_v2_measured.csv`.
