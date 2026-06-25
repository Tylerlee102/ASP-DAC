# cocotb Verification Strategy

cocotb tests should provide readable, directed record/replay scenarios with
Python scoreboards. These tests are the best place to validate protocol intent,
negative fixtures, and failure messages before longer randomized campaigns.

## Testbench Components

Recommended components:

- clock/reset helper
- RV32I boundary driver or instruction trace shim
- interrupt driver with cycle-accurate scheduling
- MMIO responder that can return different record and replay values
- capsule monitor that observes committed events
- replay injector monitor that observes consumed events
- architectural signature monitor when the core exposes commit state
- scoreboard that compares record trace, replay trace, and final signature

## Directed Test Checklist

Event ordering:

- record two adjacent MMIO reads and verify `(commit_index, order)`
- record interrupt then MMIO read in adjacent architectural windows
- replay the same capsule and verify cursor order equals record order
- corrupt event ordering fields and verify scoreboard failure

Buffer freeze:

- freeze an empty capsule
- freeze after one event
- freeze on a full capsule without overflow
- attempt or model a write after freeze and verify the checker catches it
- verify capsule digest is unchanged across replay

Overflow:

- fill the buffer exactly and verify replay-valid can still be true
- add one more required event and verify overflow is set
- verify an overflowed capsule cannot start replay successfully
- verify event count and write pointer remain in legal bounds

Interrupt pairing:

- record one interrupt and replay exactly one injection
- record two interrupts with distinct causes or sources
- schedule live interrupt noise during replay and verify policy behavior
- delete, duplicate, or corrupt an interrupt event and expect failure

MMIO capture:

- record a single MMIO read and replay with a different live device value
- verify replay returns the captured value
- verify address, size, byte lane, and data match the captured event
- corrupt the MMIO address or payload and expect failure

Replay injection:

- replay a complete capsule and verify clean end-of-capsule
- replay with wrong next event kind and expect failure
- replay with early end-of-capsule and expect failure
- verify replay cursor cannot advance after completion

## Scoreboard Rules

The scoreboard should compare at each replay-visible event boundary:

- event `commit_index`
- event `order`
- event kind
- PC or delivery boundary
- MMIO address and data
- interrupt ID or cause
- replay consumed flag
- error state

On failure, report the test name, seed if present, event index, expected event,
observed event, record digest, replay digest, and final architectural signature.

## Regression Groups

Suggested groups:

- `smoke`: reset, no events, one MMIO read, one interrupt
- `directed`: all checklist tests above
- `negative`: corrupted capsules and checker self-tests
- `replay`: record once, replay multiple times with changed live inputs
- `stress-short`: small randomized timing around directed programs

Every cocotb test that uses randomness must print and store the seed.
