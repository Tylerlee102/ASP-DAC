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

The v1 mapped full-core configuration disables unselected v2 recorder logic, but the remaining recorder, capsule buffer, signature, property-checker, and status plumbing are still substantial FPGA instrumentation. This overhead is acceptable for the intended bring-up/debug use case, where the instrumented bitstream is used to capture replayable failures and is not shipped as always-on production silicon.

The v2 recorder can be selected in the host-driven full-core record path. The v2 replay-consume controller itself is tested and maps standalone, but it is not yet wired into full-core instruction replay: the current full-core design does not include a capsule memory source feeding the consumer, a core MMIO/IRQ replay mux, observed-event feedback from PicoRV32 into the consumer, or an autonomous replay-mode controller.
