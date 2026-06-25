# SystemVerilog Assertion Checklist

This directory should contain RTL-adjacent assertions for the ReplayCapsule-RV
recorder and replay injector. Assertions should be bound near the interfaces they
check, with a small set of shared helper sequences for event handshakes.

## Assertion Conventions

- Prefix properties with the block and requirement, for example
  `rc_rec_commit_order_monotonic`.
- Separate assumptions from assertions. Assumptions belong in harness files unless
  they express a real environmental contract.
- Prefer local protocol checks over end-to-end scoreboarding in SVA.
- Add one cover property for every major scenario that is otherwise hard to see
  in simulation.
- Every assertion with a waiver must cite the architectural assumption that makes
  the waiver safe.

## Event Ordering

Required assertions:

- Event write accepts are serialized into one committed order.
- Committed event `(commit_index, order)` never regresses.
- `order` increments or otherwise changes deterministically for multiple events
  at the same `commit_index`.
- No two committed required events share the same `(commit_index, order)`.
- A later event cannot become visible before an earlier accepted event.
- Replay cursor advances only after a successful event match or documented skip.
- Event kind, position, and payload are sampled from the same committed entry.
- Reset clears pending ordering state before the first post-reset event.

Useful covers:

- back-to-back event commits
- interrupt event adjacent to MMIO event
- replay consumes the final event in a capsule

## Buffer Freeze

Required assertions:

- Freeze is sticky until reset or an explicitly documented capsule clear.
- No event data RAM write occurs after freeze.
- No event metadata write occurs after freeze.
- No write pointer, count, digest, or overflow status change occurs after freeze
  except documented status transitions.
- A freeze request while an event commit is in progress resolves to one
  deterministic final capsule state.
- Replay reads only from the frozen capsule, not from speculative in-flight data.
- Freeze cannot report complete while a required accepted event is missing from
  the committed buffer.

Useful covers:

- freeze with empty buffer
- freeze with exactly one event
- freeze on the same cycle as the last legal event
- freeze after overflow

## Overflow

Required assertions:

- Overflow flag is sticky until reset or documented capsule clear.
- Writing the first event beyond capacity raises overflow.
- No out-of-range buffer write can occur.
- A capsule with overflow cannot be marked replay-valid.
- Event count saturates or remains within representable bounds after overflow.
- Overflow caused by an interrupt, MMIO read, or metadata event is reported with
  enough status to diagnose the event kind.
- Replay refuses to start, or enters invalid state, when the capsule overflow flag
  is set.

Useful covers:

- buffer exactly full with no overflow
- first event after full buffer sets overflow
- replay start attempted on overflowed capsule

## Interrupt Pairing

Required assertions:

- Every recorded interrupt has exactly one committed interrupt event.
- Interrupt event payload captures the delivered cause or source ID.
- Interrupt event is associated with the `(commit_index, order)` delivery
  boundary used by replay.
- Replay injects an interrupt only when the next captured event is an interrupt
  event whose boundary matches the current replay point.
- Replay injection consumes exactly one interrupt event.
- No interrupt is injected twice from one captured event.
- Live external interrupts are masked, ignored, or explicitly arbitrated during
  replay according to the architecture contract.
- Interrupt pending and taken states cannot create a zero-length duplicate pair.

Useful covers:

- interrupt taken with no nearby MMIO
- interrupt adjacent to MMIO read completion
- two interrupts separated by one instruction boundary
- replay reaches an interrupt boundary and injects it

## MMIO Capture

Required assertions:

- Every nondeterministic MMIO read accepted by the core creates one MMIO read
  event.
- MMIO read address, size, byte lane, and returned data are sampled atomically.
- Captured MMIO read data is stable before the core can retire or consume the
  load result.
- MMIO read events preserve program order relative to interrupts and other MMIO
  reads.
- MMIO writes are either explicitly recorded or proven deterministic by contract.
- MMIO events are not captured for normal memory accesses.
- Replay supplies captured read data instead of live device data.
- Replay flags a mismatch if the next event is not an MMIO read for the current
  access.

Useful covers:

- single MMIO read capture
- back-to-back MMIO read capture
- MMIO read with changed live value during replay
- interrupt pending during MMIO read response

## Replay Injection

Required assertions:

- Replay mode cannot consume events before replay start is acknowledged.
- Replay cursor starts at the first committed event.
- Replay cursor never advances past the frozen event count.
- Replay expected event kind and `(commit_index, order)` match the observed
  replay boundary.
- Replay payload is injected without mutation.
- Replay mismatch enters an error state before architectural state can diverge
  further, when the interface permits early detection.
- End-of-capsule is observed only after all required events are consumed.
- Replay completion requires no pending unmatched event.

Useful covers:

- replay consumes all events
- replay detects wrong event kind
- replay detects wrong MMIO address
- replay detects unexpected end-of-capsule

## Property Checker Correctness

The assertion library should include intentionally small checker self-tests or
formal harness modes that demonstrate failures for invalid traces.

Required negative fixtures:

- swapped adjacent event order
- duplicate interrupt event
- missing MMIO event
- corrupted MMIO payload
- replay cursor skip
- write after freeze
- overflowed capsule marked valid

Each negative fixture should have a companion positive fixture so failures point
to checker behavior rather than broken harness setup.
