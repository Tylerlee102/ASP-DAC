# Property Test Strategy

Property tests should exercise ReplayCapsule event streams and checker logic
outside the RTL. They are useful for finding gaps in the encoder, decoder,
scoreboard, digesting, and replay cursor before those gaps become slow hardware
debug sessions.

## Reference Model

Maintain a small host-side model with:

- event data type matching the logical event vocabulary
- recorder model with bounded capacity, freeze, and overflow
- replay cursor model with strict kind and payload matching
- MMIO model that distinguishes captured values from live values
- interrupt model that pairs record delivery points with replay injection points
- digest model for frozen capsule identity

The model should be intentionally stricter than the implementation where
possible. If the implementation allows behavior the model rejects, document the
architectural reason in the test.

## Generated Inputs

Generators should produce:

- empty traces
- one-event traces
- full-buffer traces
- overflow traces
- repeated MMIO reads to the same address with different values
- interrupts near MMIO reads
- adjacent interrupts with distinct causes
- freeze requests at every legal position
- corrupted capsules for negative checks
- replay live inputs that differ from record live inputs

Bias generation toward small counterexamples so failures are easy to turn into
directed RTL tests.

## Required Properties

Event ordering:

- encoding and decoding preserve `(commit_index, order)`
- sorting or map iteration cannot silently reorder same-index events
- replay consumes events in the same order the recorder committed them

Buffer freeze:

- freeze makes the capsule digest stable
- writes after freeze are rejected or ignored without mutating frozen state
- replay uses the frozen event count, not a live write pointer

Overflow:

- first event beyond capacity marks overflow
- overflowed capsules are never replay-valid
- event count stays within capacity

Interrupt pairing:

- each recorded interrupt maps to exactly one replay injection
- duplicate, missing, or wrong-cause interrupts fail
- interrupt ordering relative to MMIO events is preserved

MMIO capture:

- replay returns captured MMIO data, not generated live data
- wrong MMIO address, width, lane, or payload fails
- back-to-back reads remain distinct events

Replay injection:

- wrong event kind fails before cursor advancement
- early end-of-capsule fails when a required event remains
- extra event at replay completion fails unless explicitly marked optional

Seeded determinism:

- same seed and input program generate the same event stream
- same capsule replays to the same digest across repeated runs
- failure shrinking preserves the reproduction seed or emits a minimized fixture

## Checker Correctness

Every checker should be tested with both valid and invalid traces. Required
negative examples:

- adjacent event swap
- dropped MMIO read
- duplicated interrupt
- corrupted MMIO value
- corrupted interrupt cause
- stale digest after mutation
- overflow flag cleared on an over-capacity stream

The property suite should fail if any negative example passes.

## Artifact Contract

On failure, save:

- property name
- random seed
- minimized event list
- capsule digest
- replay digest if replay ran
- corruption applied for negative tests

These artifacts should be parseable by the cocotb or Verilator directed harness.
