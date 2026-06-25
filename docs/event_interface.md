# ReplayCapsule-RV Event Interface

This document defines the hardware-facing event contract shared by
`event_tap`, `event_classifier`, `interrupt_logger`, `mmio_logger`,
`event_slicer`, `capsule_buffer`, `replay_control`, `property_checker`,
`registers`, and `hash_signature`.

The current synthesizable RTL uses a compact internal event packet defined by
`replaycapsule_event_pkg`. The portable capsule format in
`docs/capsule_format.md` is the export/import representation built from these
packets.

## Common Conventions

- Clock is `clk`.
- Reset is active-low `rst_n`.
- `clear` returns recorder/replay state to a fresh capture baseline.
- Current event streams are valid-only. A later top-level integration may add
  ready/backpressure, but accepted events must still be stable for the cycle in
  which `event_valid` is asserted.
- `commit_index` is the RTL name for the replay model's logical commit index.
- Multiword portable capsule data is little-endian by increasing word index.

## Internal Event Packet

The current package constants are:

| Name | Value | Meaning |
| --- | --- | --- |
| `RC_EVENT_TYPE_W` | `4` | Internal event type width |
| `RC_EVENT_FLAG_W` | `4` | Internal flag width |
| `RC_WORD_W` | `32` | Payload word width |
| `RC_EVENT_WIDTH` | `168` | Packed event width |

The packed event layout is:

```text
event_packet = {
  event_type[3:0],
  flags[3:0],
  event_id[31:0],
  commit_index[31:0],
  pc[31:0],
  addr[31:0],
  data[31:0]
}
```

Field semantics:

| Field | Meaning |
| --- | --- |
| `event_type` | One of `rc_event_type_e` |
| `flags` | Event-specific flags; zero when unused |
| `event_id` | Source-local id, sequence slot, or cycle-time slot |
| `commit_index` | Logical replay time |
| `pc` | Associated committed PC or trap PC |
| `addr` | Memory or MMIO address, zero when unused |
| `data` | Instruction, MMIO value, input value, depth, or signature data |

`rc_pack_event` and the `rc_get_*` helpers are the canonical bit layout. Any
top-level packer in `replay_capsule_top` should use that layout rather than
reconstructing slices by hand.

## Internal Event Types

These are the current `rc_event_type_e` encodings.

| Value | Name | Meaning |
| --- | --- | --- |
| `4'h0` | `EV_COMMIT` | Committed instruction context |
| `4'h1` | `EV_BRANCH` | Taken branch context |
| `4'h2` | `EV_JUMP` | Taken jump context |
| `4'h3` | `EV_STORE` | Non-MMIO store context |
| `4'h4` | `EV_LOAD` | Non-MMIO load context |
| `4'h5` | `EV_MMIO_READ` | MMIO read value observed |
| `4'h6` | `EV_MMIO_WRITE` | MMIO write observed |
| `4'h7` | `EV_INTERRUPT_ENTER` | Trap or interrupt entry observed |
| `4'h8` | `EV_INTERRUPT_EXIT` | Trap or interrupt exit observed |
| `4'h9` | `EV_EXTERNAL_INPUT` | External input value observed |
| `4'ha` | `EV_PROPERTY_FAIL` | Property checker failure marker |
| `4'hb` | `EV_CHECKPOINT_HASH` | Hash checkpoint marker |

Current capture modes are:

| Value | Name | Meaning |
| --- | --- | --- |
| `4'h0` | `CAPTURE_ALL` | Keep all event types |
| `4'h1` | `CAPTURE_MMIO_INTERRUPT` | Keep MMIO, interrupt, input, and property events |
| `4'h2` | `CAPTURE_PROPERTY_AWARE` | Keep nondeterministic events and local property context |
| `4'h3` | `CAPTURE_REPLAYCAPSULE_RV` | Default replay-capsule capture policy |

## Portable Capsule Mapping

The portable capsule uses 8-bit event ids. The current RTL packet maps to the
portable ids as follows:

| Internal Type | Capsule Type |
| --- | --- |
| `EV_COMMIT` | `CONTEXT_COMMIT` |
| `EV_BRANCH` | `CONTEXT_BRANCH` |
| `EV_JUMP` | `CONTEXT_JUMP` |
| `EV_STORE` | `CONTEXT_STORE` |
| `EV_LOAD` | `CONTEXT_LOAD` |
| `EV_MMIO_READ` | `MMIO_READ` |
| `EV_MMIO_WRITE` | `MMIO_WRITE` |
| `EV_INTERRUPT_ENTER` | `INTERRUPT_ENTER` |
| `EV_INTERRUPT_EXIT` | `INTERRUPT_EXIT` |
| `EV_EXTERNAL_INPUT` | `EXTERNAL_INPUT` |
| `EV_PROPERTY_FAIL` | `PROPERTY_FAIL` |
| `EV_CHECKPOINT_HASH` | `HASH_CHECKPOINT` |

Fields not present in the current compact packet, such as byte enables, response
codes, latency, IRQ vector width, and source ids, must be written as zero or
filled by `replay_capsule_top` if the integration provides them.

## `event_tap`

`event_tap` observes core and fabric activity and emits one prioritized event
candidate.

Inputs:

```text
commit_valid
commit_pc[31:0]
commit_instr[31:0]
commit_index[31:0]
branch_taken
jump_taken

mem_valid
mem_write
mem_addr[31:0]
mem_wdata[31:0]
mem_rdata[31:0]

external_input_valid
external_input_value[31:0]
interrupt_enter
interrupt_exit
```

Outputs:

```text
event_valid
event_type[3:0]
event_commit_index[31:0]
event_pc[31:0]
event_addr[31:0]
event_data[31:0]
multievent_pending
```

The current priority order is interrupt enter, interrupt exit, external input,
MMIO read, MMIO write, non-MMIO store, non-MMIO load, branch, jump, commit.
`multievent_pending` tells the top-level integration that more than one
candidate was present in the same cycle.

## `event_classifier`

`event_classifier` receives `event_valid`, `event_type`, `capture_mode`,
`property_window_active`, and `overflow_guard`. It emits:

```text
keep_event
event_is_nondeterministic
event_is_property_relevant
```

In the current RTL, nondeterministic events are `EV_MMIO_READ`,
`EV_INTERRUPT_ENTER`, `EV_INTERRUPT_EXIT`, and `EV_EXTERNAL_INPUT`. Property
relevant events additionally include `EV_MMIO_WRITE`, `EV_STORE`, `EV_BRANCH`,
`EV_JUMP`, `EV_PROPERTY_FAIL`, and `EV_CHECKPOINT_HASH`.

## `interrupt_logger`

`interrupt_logger` records trap-entry and trap-exit observations.

Inputs:

```text
trap_enter
trap_exit
commit_index[31:0]
pc[31:0]
```

Outputs:

```text
event_valid
event_type[3:0]
event_commit_index[31:0]
event_pc[31:0]
event_data[31:0]
unpaired_exit
active_depth[7:0]
```

`event_type` is `EV_INTERRUPT_ENTER` or `EV_INTERRUPT_EXIT`. `event_data`
contains the current interrupt/trap nesting depth in the low byte. If future
hardware exposes raw interrupt levels, `replay_capsule_top` can either encode
them as `EV_EXTERNAL_INPUT` or extend the logger and capsule mapping with an
IRQ-level event.

## `mmio_logger`

`mmio_logger` records bus accesses whose address matches its configured MMIO
window.

Inputs:

```text
bus_valid
bus_write
bus_addr[31:0]
bus_wdata[31:0]
bus_rdata[31:0]
commit_index[31:0]
pc[31:0]
```

Outputs:

```text
event_valid
event_type[3:0]
event_commit_index[31:0]
event_pc[31:0]
event_addr[31:0]
event_data[31:0]
```

Reads produce `EV_MMIO_READ` with `event_data = bus_rdata`; writes produce
`EV_MMIO_WRITE` with `event_data = bus_wdata`.

## `event_slicer`

The current `event_slicer` is a property-context slicer, not a binary
packetizer. It keeps a configurable last-`K` window around property failures.

Inputs:

```text
event_valid
event_type[3:0]
property_fail_valid
capture_mode[3:0]
```

Outputs:

```text
property_window_active
keep_context_event
```

When a property failure is observed, `property_window_active` remains asserted
for `LAST_K` accepted events. `keep_context_event` is true for required
nondeterministic events, property failures, all events in `CAPTURE_ALL`, and
events inside the active context window.

## `capsule_buffer`

`capsule_buffer` stores packed internal event packets.

Inputs:

```text
clear
event_valid
event_packet[RC_EVENT_WIDTH-1:0]
fail_freeze
read_addr[ADDR_W-1:0]
```

Outputs:

```text
read_data[RC_EVENT_WIDTH-1:0]
frozen
overflow
write_count[ADDR_W:0]
```

`fail_freeze` transitions the buffer to an immutable frozen state. While
`frozen` is set, later `event_valid` pulses do not modify stored packets.
Overflow is sticky until reset or clear.

## `replay_control`

`replay_control` consumes packed internal event packets and injects replay
inputs when the selected time base matches.

Inputs:

```text
replay_enable
commit_index_mode
current_cycle[31:0]
current_commit_index[31:0]
replay_event_valid
replay_event_packet[RC_EVENT_WIDTH-1:0]
```

Outputs:

```text
replay_event_consume
inject_mmio_valid
inject_mmio_value[31:0]
inject_interrupt_enter
inject_interrupt_exit
replay_underflow
```

With `commit_index_mode` set, replay time is `commit_index`; otherwise the
current RTL uses `event_id` as the cycle-time slot. `EV_MMIO_READ` and
`EV_EXTERNAL_INPUT` inject `data` as `inject_mmio_value`.
`EV_INTERRUPT_ENTER` and `EV_INTERRUPT_EXIT` inject one-cycle control pulses.

## `property_checker`

`property_checker` consumes event fields and emits:

```text
property_fail_valid
property_id[7:0]
property_signature[31:0]
sensor_deadline_active
critical_section_active
```

The current checker implements prototype safety properties for actuator limits,
interrupts in critical sections, sensor-response deadlines, stack protection,
and MMIO ordering.

## `registers`

The current register block is selected by `bus_valid` and `bus_addr[31:4]`.

| Offset | Name | Access | Current Behavior |
| --- | --- | --- | --- |
| `0x00` | `REG_CONTROL` | RW | read `{27'h0, replay_enable, capture_mode}`; write `capture_mode[3:0]`, `replay_enable[4]`, `capsule_clear[8]` |
| `0x04` | `REG_STATUS` | RO | read `{30'h0, capsule_overflow, capsule_frozen}` |
| `0x08` | `REG_COUNT` | RO | read `event_count` |
| `0x0c` | `REG_SIG` | RO | read `failure_signature` |

The architecture leaves room for a wider future map with MMIO windows, hash
words, read/write pointers, and first-error sequence registers.

## `hash_signature`

`hash_signature` consumes accepted `event_packet` values and emits a 32-bit
rolling signature. The current implementation folds the packet words with XOR
and rotates/mixes the accumulated signature. It is a determinism signature, not
a cryptographic hash.

## Top-Level Integration Requirements

The current `replay_capsule_top` bridges the compact record-side modules:

- select event candidates from `event_tap` and property/checkpoint injection
- apply `event_classifier` and `event_slicer` keep decisions
- pack kept events with `rc_pack_event`
- write accepted packets into `capsule_buffer`
- feed accepted packets to `hash_signature`
- expose capsule readback, frozen/overflow status, running signature, property
  failure status, and captured event type

`registers`, `replay_control`, `interrupt_logger`, and `mmio_logger` are
available companion modules. A fuller SoC integration can wire them around
`replay_capsule_top` or fold them into a future top-level revision.

For portable capsule export, the top-level or host-side reader maps stored
internal packets into the v1 capsule records described in
`docs/capsule_format.md`.

## Required Invariants

- `commit_index` is stable for the event cycle that asserts `event_valid`.
- If multiple candidate events occur together, `multievent_pending` must be
  handled by the top-level integration or the later event is intentionally
  outside the selected capture policy.
- No stored packet may change after `capsule_buffer.frozen` is set.
- Overflow is fail-closed: an overflowed capsule is not replay-valid.
- Replay consumes a packet only when its selected time base matches.
- During replay, live peripheral values must not override injected MMIO or
  interrupt events.
- A portable capsule exporter must assign a monotonic `event_seq` even though
  the current internal packet stores only `event_id` and `commit_index`.
