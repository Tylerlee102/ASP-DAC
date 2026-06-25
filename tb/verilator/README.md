# Verilator Verification Strategy

The Verilator harness should provide fast cycle-level regression for record,
freeze, replay, and deterministic rerun checks. It should be small enough to run
often and strict enough to catch event-sufficiency regressions.

## Harness Responsibilities

- build the ReplayCapsule RTL with a compact RV32I or boundary-level test core
- drive deterministic clocks, resets, interrupts, and MMIO responses
- load short embedded programs or instruction traces
- dump capsule events in a stable machine-readable format
- compute capsule and replay digests
- run record then replay in one invocation when possible
- emit a reproduction line with test name, seed, binary identity, and plusargs

## Core Scenarios

Record/replay smoke:

- no interrupt and no MMIO
- one MMIO read
- one interrupt
- one MMIO read followed by one interrupt
- one interrupt followed by one MMIO read

Freeze and overflow:

- freeze before any event
- freeze after each event count from 1 through buffer depth
- exact full buffer replay
- first over-capacity event sets overflow
- overflowed capsule refuses replay

Replay injection:

- replay consumes all captured events in order
- replay returns captured MMIO values despite changed live MMIO values
- replay injects captured interrupts at the expected boundaries
- replay reports mismatch on corrupted event kind, payload, or address

Deterministic rerun:

- same seed produces identical capsule digest
- same seed produces identical replay digest
- different live MMIO values during replay do not change architectural signature
  when values are captured in the capsule

## Trace Format

Prefer a line-oriented trace that is easy for property tests and CI to parse:

```text
event commit_index=<n> order=<n> kind=<kind> pc=<hex> addr=<hex> data=<hex> irq=<id> flags=<bits>
digest capsule=<hex> replay=<hex>
result status=<pass|fail> seed=<n> test=<name>
```

The trace should avoid simulator-specific formatting for fields that are compared
across runs.

## Negative Tests

The harness should include a way to replay intentionally corrupted capsules:

- swap adjacent events
- drop the final event
- duplicate an interrupt
- flip one bit in MMIO data
- change MMIO address
- change interrupt cause
- clear overflow while leaving an overfull capsule image

Each corruption mode should produce a specific failure reason instead of a
generic timeout.

## CI Expectations

The fast Verilator lane should run:

- smoke tests on every change
- directed freeze, overflow, MMIO, and interrupt tests on every verification
  change
- seeded deterministic replay tests with a small fixed seed list
- a nightly or manual extended seed sweep

When a Verilator failure occurs, keep the generated trace and seed artifact long
enough for local replay.
