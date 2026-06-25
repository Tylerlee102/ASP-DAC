# rtl_architect Handoff

Role: document the hardware architecture, capsule format, event interface,
event types, and integration assumptions for ReplayCapsule-RV.

Owned files:

- `docs/architecture.md`
- `docs/capsule_format.md`
- `docs/event_interface.md`
- `docs/subagents/rtl_architect.md`

Do not edit RTL. The main agent owns synthesizable implementation files.

## Current Architecture Contract

The docs define a v1 event-sufficient replay system for an embedded RV32I hart.
The required module names are:

- `replay_capsule_top`
- `event_tap`
- `event_classifier`
- `capsule_buffer`
- `property_checker`
- `interrupt_logger`
- `mmio_logger`
- `event_slicer`
- `replay_control`
- `registers`
- `hash_signature`

The design records external nondeterminism at the interrupt and MMIO boundary,
not a full instruction trace. Replay is scheduled primarily by `commit_index`,
with optional cycle or event-id timing for integrations where latency affects
visible behavior.

## Key Decisions

- Current RTL stores compact 168-bit packets:
  `{event_type, flags, event_id, commit_index, pc, addr, data}`.
- Portable capsule words are little-endian 32-bit records exported from those
  packets.
- `event_seq` is assigned by portable capsule export; current RTL packets carry
  `event_id` and `commit_index`.
- `EV_MMIO_READ`, `EV_INTERRUPT_ENTER`, `EV_INTERRUPT_EXIT`, and
  `EV_EXTERNAL_INPUT` are the current nondeterministic event types.
- `EV_MMIO_WRITE`, context events, `EV_PROPERTY_FAIL`, and
  `EV_CHECKPOINT_HASH` are property/checker/debug evidence.
- `event_slicer` currently implements a last-`K` property-context window rather
  than binary packetization.
- Frozen capsules are immutable; overflow or event loss fails closed.
- `hash_signature` is an integrity and determinism signature, not a security
  primitive.
- Recorder overflow is fatal unless the integration can stall the core before
  losing an event.
- Replay mode must mask live IRQ and MMIO response inputs from the core.

## Open Integration Choices For The Main Agent

- Choose the exact memory-mapped control bus used by `registers`.
- Choose the exact core observation signals available for trap or interrupt
  taken metadata.
- Decide whether cycle-accurate replay is required for the first RTL target.
- Decide whether `replay_control`, `registers`, `interrupt_logger`, and
  `mmio_logger` should be wired into `replay_capsule_top` or remain companion
  modules around it.
- Decide whether raw IRQ level changes are needed in addition to interrupt
  enter/exit events.
- Set default capsule buffer depth and MMIO window parameters.
- Decide whether portable capsule export is hardware packetization, host-side
  conversion from `capsule_buffer`, or both.
