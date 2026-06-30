# Related Work Positioning

ReplayCapsule-RV should be positioned as a focused prototype for event-sufficient replay of single-hart RV32I interrupt/MMIO failures.

## Positioning Statement

ReplayCapsule-RV explores a middle point between full instruction tracing, coarse failure snapshots, and property-only logs. It records a compact set of replay-critical events plus optional diagnostics, then checks that replay agrees with the recorded failure signature and event stream.

## What The Project Does

- Runs compiler-backed firmware through RTL record/replay flows.
- Rejects corrupted capsule streams in negative replay.
- Measures workload scaling, buffer sensitivity, capsule baselines, runtime scaling, and ECP5 mapping for v1.
- Adds v2 RTL for compressed event packing, address dictionary tagging, payload hashing, adaptive diagnostic dropping, and BRAM-style event storage.
- Measures v2 all-benchmark replay, workload scaling, runtime overhead, buffer sensitivity, representative same-target ECP5 full-core overhead, and two added compiler-backed benchmark families.
- Adds a synthesizable v2 replay-consume controller prototype with corruption tests and host-streamed full-core checks.

## What The Project Does Not Claim

- It is not a full-system replay framework.
- It is not a multicore, cache, coherence, DMA, or OS replay system.
- It is not a replacement for trace/debug standards.
- It does not prove globally minimal event sets.
- It does not provide autonomous full-core hardware replay consumption; the full-core replay flow remains host-driven.
- It does not generalize the representative v2 ECP5 mapping point to all memory/buffer sizes.

## Reviewer-Safe Contribution Wording

"ReplayCapsule-RV explores event-sufficient failure capsules for replaying single-hart RV32I interrupt/MMIO failures, combining compiler-backed firmware-running RTL replay, corruption rejection, mapped recorder evidence, and scaling analysis."

"ReplayCapsule-RV v2 adds an adaptive compressed capsule format and a synthesizable replay-consume controller prototype with host-streamed full-core checks."

"ReplayCapsule-RV v2 reports measured zero-fail host-driven full RTL replay, workload scaling, runtime overhead, and representative same-target ECP5 full-core overhead for the scoped benchmark suite."

## Current Risk Framing

The strongest current claims now include v2 host-driven full RTL replay, RTL consumer checks, and measured scaling/mapped evidence for the scoped suite. The main v2 risk is scope discipline: do not present the replay-consume prototype as autonomous full-core replay, and do not generalize the claimable core/hashed ECP5 mapping point beyond the measured configuration.
