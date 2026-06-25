# Hardware Architecture

The RTL is organized around small modules:

- `event_tap` observes core, memory, MMIO, external input, and interrupt signals.
- `event_classifier` chooses events according to capture policy.
- `property_checker` emits safety-property failures and signatures.
- `event_slicer` selects property-relevant context.
- `capsule_buffer` stores accepted event packets and freezes on failure.
- `hash_signature` computes a determinism signature over accepted packets.
- `replay_control` is the replay-side injection scaffold.

The current internal event packet is 168 bits: event type, flags, event id, commit index, PC, address, and data.

