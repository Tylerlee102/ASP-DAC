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

For the ASP-DAC 2027 path, the selected v2 minimal recorder profile strips the property checker, context slicer, on-chip event buffer, signature, and detailed status counters through compile-time parameters. It keeps the commit-indexed replay-driving boundary events: MMIO reads and writes, external inputs, and interrupt enter/exit events. The core and hashed configurations remain diagnostic-rich comparison points rather than the area story.

The v2 recorder can be selected in the full-core record path. The v2 replay path now includes an RTL capsule source, replay-mode controller, and replay-consume controller: the controller arms captured-store replay, the source streams saved or captured replay-critical words, the consumer checks observed boundary events, and the wrapper drives core-facing MMIO read data and IRQ replay during measured Verilator runs. The current full-core design still relies on the Verilator harness for reset orchestration and the memory/peripheral shell; it is not a standalone board/silicon replay engine.
