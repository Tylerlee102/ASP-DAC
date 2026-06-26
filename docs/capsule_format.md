# ReplayCapsule-RV Capsule Format

The capsule is a little-endian stream of 32-bit words. It is designed to be
simple for synthesizable SystemVerilog to produce and consume: fixed event
headers, word-aligned payloads, no variable-byte packing, and no requirement for
software-only compression.

## Word Stream Layout

```text
capsule_header
event_record[0]
event_record[1]
...
event_record[event_count - 1]
capsule_footer
```

All numeric fields are unsigned unless an event explicitly says otherwise.
Reserved fields must be written as zero and ignored by readers.

## Relation To Internal RTL Packets

The current synthesizable RTL stores compact 168-bit internal event packets:

```text
{event_type[3:0], flags[3:0], event_id, commit_index, pc, addr, data}
```

The portable capsule stream expands those packets into versioned 32-bit records.
Fields not present in the current packet, such as byte enables, response codes,
latency, source ids, and multiword IRQ vectors, are written as zero unless
`replay_capsule_top` or host-side export logic supplies them.

## Header

The v1 header is 24 words.

| Word | Field | Description |
| --- | --- | --- |
| 0 | `magic` | ASCII `RCP1`, encoded as `0x31504352` |
| 1 | `format_version` | `0x00010000` for v1.0 |
| 2 | `header_words` | Number of 32-bit words in the header, `24` for v1 |
| 3 | `flags` | Capsule-wide options |
| 4 | `hart_id` | RV32I hart identifier, usually `0` |
| 5 | `irq_width` | Number of effective interrupt bits recorded |
| 6 | `mmio_window_count` | Number of configured MMIO windows |
| 7 | `event_count` | Number of event records in the capsule |
| 8 | `payload_words` | Total words occupied by event records |
| 9 | `initial_pc` | Reset or capture-start PC, if available |
| 10 | `initial_commit_index` | Commit index at capsule start |
| 11 | `initial_cycle_count` | Cycle count at capsule start, or zero |
| 12 | `image_hash_0` | Firmware image or manifest hash word 0 |
| 13 | `image_hash_1` | Firmware image or manifest hash word 1 |
| 14 | `image_hash_2` | Firmware image or manifest hash word 2 |
| 15 | `image_hash_3` | Firmware image or manifest hash word 3 |
| 16 | `platform_hash_0` | Platform semantic profile hash word 0 |
| 17 | `platform_hash_1` | Platform semantic profile hash word 1 |
| 18 | `platform_hash_2` | Platform semantic profile hash word 2 |
| 19 | `platform_hash_3` | Platform semantic profile hash word 3 |
| 20 | `config_hash_0` | Recorder configuration hash word 0 |
| 21 | `config_hash_1` | Recorder configuration hash word 1 |
| 22 | `config_hash_2` | Recorder configuration hash word 2 |
| 23 | `config_hash_3` | Recorder configuration hash word 3 |

### Header Flags

| Bit | Name | Meaning |
| --- | --- | --- |
| 0 | `HAS_CYCLE_DELTAS` | Event records include meaningful `cycle_delta` values |
| 1 | `VERIFY_MMIO_WRITES` | Replay must compare MMIO writes |
| 2 | `HAS_INTERRUPT_EVENTS` | Capsule contains interrupt enter/exit observations |
| 3 | `HAS_SLICE_MARKERS` | Capsule contains `SLICE_MARKER` records |
| 4 | `STRICT_REPLAY` | Mismatches are fatal and stop replay |
| 31:5 | `RESERVED` | Must be zero |

`image_hash` and `platform_hash` bind the capsule to the firmware identity and
semantic profile used by the replay model. `config_hash` covers integration
settings that affect event sufficiency, including IRQ width, IRQ masks, MMIO
windows, reset vector, replay mode flags, and hash algorithm selection.

The header does not have to contain a full architectural checkpoint. If reset
inputs, initial RAM, CSR reset values, or firmware-visible counters are not
fixed by platform contract, they must be supplied by a companion manifest or by
future event sources before replay is considered sufficient.

## Event Record Header

Every event starts with a fixed 5-word header.

| Word | Field | Description |
| --- | --- | --- |
| 0 | `record_info` | Type, flags, and payload length |
| 1 | `event_seq` | Monotonic event sequence number |
| 2 | `commit_delta` | Commit-index delta from previous event |
| 3 | `cycle_delta` | Cycle delta from previous event, or zero |
| 4 | `source_info` | Source id and subtype data |

`record_info` layout:

| Bits | Field | Description |
| --- | --- | --- |
| 31:24 | `event_type` | One of the event types below |
| 23:16 | `event_flags` | Event-specific flags |
| 15:0 | `payload_words` | Number of payload words after the fixed header |

`source_info` layout:

| Bits | Field | Description |
| --- | --- | --- |
| 31:16 | `source_id` | IRQ index, MMIO bus id, or checker source |
| 15:8 | `phase` | Source-local phase or bus phase |
| 7:0 | `tag` | Source-local transaction tag, or zero |

`event_seq` starts at zero for the first event in a capsule.

## Event Types

| ID | Name | Required For Replay | Purpose |
| --- | --- | --- | --- |
| `0x01` | `SYNC` | No | Capture boundary, resume point, or explicit state marker |
| `0x02` | `CONTEXT_COMMIT` | No | Committed instruction context |
| `0x03` | `CONTEXT_BRANCH` | No | Taken branch context |
| `0x04` | `CONTEXT_JUMP` | No | Taken jump context |
| `0x05` | `CONTEXT_LOAD` | No | Non-MMIO load context |
| `0x06` | `CONTEXT_STORE` | No | Non-MMIO store context |
| `0x10` | `IRQ_LEVEL` | Integration-dependent | Effective interrupt vector changed |
| `0x11` | `INTERRUPT_ENTER` | Yes | Core reported interrupt or trap entry |
| `0x12` | `INTERRUPT_EXIT` | Yes | Core reported interrupt or trap exit |
| `0x20` | `MMIO_READ` | Yes | MMIO read request and recorded response |
| `0x21` | `MMIO_WRITE` | Usually | MMIO write observation and acknowledgement |
| `0x22` | `EXTERNAL_INPUT` | Yes, when used | External input value observed |
| `0x30` | `SLICE_MARKER` | No | Bounded chunk marker inserted by `event_slicer` |
| `0x31` | `FREEZE` | No | Capture freeze boundary and stop reason |
| `0x40` | `PROPERTY_FAIL` | No | Safety property failure marker |
| `0x70` | `HASH_CHECKPOINT` | No | Intermediate hash snapshot |
| `0x7e` | `ERROR` | No | Recorder-visible fatal condition |
| `0x7f` | `END` | No | Explicit end marker before footer, optional |

IDs not listed here are reserved.

## Payloads

### `SYNC`

Payload length: 4 words.

| Word | Field |
| --- | --- |
| 0 | `pc` |
| 1 | `irq_value` |
| 2 | `mmio_read_ordinal` |
| 3 | `mmio_write_ordinal` |

`SYNC` is useful at capture start and slice boundaries. It is not a substitute
for a full architectural checkpoint.

### `CONTEXT_*`

Payload length: 4 words.

| Word | Field |
| --- | --- |
| 0 | `pc` |
| 1 | `addr` |
| 2 | `data` |
| 3 | `internal_event_type` |

Context events preserve property-window evidence from the current RTL packet.
They are not required for minimal event-sufficient replay unless a property or
debug workflow consumes them.

### `IRQ_LEVEL`

Payload length: `ceil(irq_width / 32)` words.

Each payload word contains the effective interrupt level after masking and
synchronization. Bit 0 of payload word 0 is interrupt line 0. For `irq_width`
larger than 32, subsequent words continue the vector.

Replay applies the new vector when the event's time anchor is reached and holds
that vector until the next `IRQ_LEVEL` event. The current RTL does not directly
emit this event; it records interrupt enter/exit and external inputs instead.

### `INTERRUPT_ENTER`

Payload length: 3 words.

| Word | Field |
| --- | --- |
| 0 | `pc` |
| 1 | `cause_or_zero` |
| 2 | `active_depth` |

The current `interrupt_logger` supplies PC and active depth. Cause is zero until
the top-level integration exposes trap cause.

### `INTERRUPT_EXIT`

Payload length: 3 words.

| Word | Field |
| --- | --- |
| 0 | `pc` |
| 1 | `cause_or_zero` |
| 2 | `active_depth` |

Replay uses this event to reproduce interrupt/trap exit observations when the
platform requires them for property checking or input scheduling.

### `MMIO_READ`

Payload length: 6 words.

| Word | Field |
| --- | --- |
| 0 | `addr` |
| 1 | `byte_en` |
| 2 | `rdata` |
| 3 | `resp` |
| 4 | `latency_cycles` |
| 5 | `mmio_window_id` |

The replay engine expects the core to issue a read with matching `addr` and
`byte_en` when this event is due. It then returns `rdata` and `resp` after the
recorded latency when `HAS_CYCLE_DELTAS` is set, or as soon as the request is
accepted when the replay mode uses commit-index ordering.

The current RTL packet supplies `addr` and `rdata`; absent byte enable,
response, latency, and window fields are exported as zero.

### `MMIO_WRITE`

Payload length: 6 words.

| Word | Field |
| --- | --- |
| 0 | `addr` |
| 1 | `byte_en` |
| 2 | `wdata` |
| 3 | `resp` |
| 4 | `latency_cycles` |
| 5 | `mmio_window_id` |

During replay, the core must produce the same write address, byte enables, and
data. The recorded response and latency are used to acknowledge the write if the
integration routes MMIO writes through `replay_control`.

The current RTL packet supplies `addr` and `wdata`; absent byte enable,
response, latency, and window fields are exported as zero.

### `EXTERNAL_INPUT`

Payload length: 2 words.

| Word | Field |
| --- | --- |
| 0 | `input_id` |
| 1 | `value` |

The current `event_tap` supplies only the input value. Exporters should write
`input_id = 0` unless the integration provides source identity.

### `SLICE_MARKER`

Payload length: 4 words.

| Word | Field |
| --- | --- |
| 0 | `slice_index` |
| 1 | `first_event_seq` |
| 2 | `slice_word_offset` |
| 3 | `previous_slice_hash` |

The marker lets software and hardware verify long captures in bounded pieces.
It must appear only between complete event records.

### `FREEZE`

Payload length: 4 words.

| Word | Field |
| --- | --- |
| 0 | `reason` |
| 1 | `status_snapshot` |
| 2 | `write_ptr` |
| 3 | `event_count` |

`FREEZE` records the transition to an immutable capsule. It is optional because
the footer also records final status, but it is useful for hardware checkers and
streaming readers. If present, no later event may change the replay prefix
except `HASH_CHECKPOINT`, `END`, and footer words.

### `PROPERTY_FAIL`

Payload length: 4 words.

| Word | Field |
| --- | --- |
| 0 | `property_id` |
| 1 | `property_signature` |
| 2 | `pc` |
| 3 | `commit_index` |

This event identifies the target or observed safety-property violation. The
current `property_checker` emits an 8-bit property id and 32-bit signature.

### `HASH_CHECKPOINT`

Payload length: 4 words.

| Word | Field |
| --- | --- |
| 0 | `hash_0` |
| 1 | `hash_1` |
| 2 | `hash_2` |
| 3 | `hash_3` |

The checkpoint records the streaming hash state after all previous capsule
words have been accepted.

### `ERROR`

Payload length: 4 words.

| Word | Field |
| --- | --- |
| 0 | `error_code` |
| 1 | `first_bad_event_seq` |
| 2 | `status_snapshot` |
| 3 | `reserved` |

Fatal recorder errors should stop capture and set the footer status to failed.

### `END`

Payload length: 0 words.

`END` is optional because the footer already contains `event_count` and
`payload_words`. If present, it must be the last event before the footer.

## Footer

The v1 footer is 12 words.

| Word | Field | Description |
| --- | --- | --- |
| 0 | `footer_magic` | ASCII `RCPF`, encoded as `0x46504352` |
| 1 | `footer_words` | Number of footer words, `12` for v1 |
| 2 | `event_count` | Repeated for reverse parsing |
| 3 | `payload_words` | Repeated for reverse parsing |
| 4 | `final_commit_index` | Commit index at capture end |
| 5 | `final_cycle_count` | Cycle count at capture end, or zero |
| 6 | `status` | Final recorder status |
| 7 | `last_event_seq` | Last accepted event sequence number |
| 8 | `hash_0` | Final stream hash word 0 |
| 9 | `hash_1` | Final stream hash word 1 |
| 10 | `hash_2` | Final stream hash word 2 |
| 11 | `hash_3` | Final stream hash word 3 |

The final stream hash covers the header with footer hash fields absent, all
event record words in capsule order, and footer words 0 through 7. The hash
algorithm is selected by integration configuration and included in
`config_hash`.

## Status Values

| Bit | Name | Meaning |
| --- | --- | --- |
| 0 | `CAPTURE_OK` | Capture completed without fatal recorder error |
| 1 | `STOP_REQUESTED` | Software requested stop |
| 2 | `BUFFER_OVERFLOW` | Required event could not be stored |
| 3 | `EVENT_DROPPED` | A valid event was not accepted |
| 4 | `SOURCE_ERROR` | Logger saw an illegal source sequence |
| 5 | `HASH_ERROR` | Hash block reported an internal error |
| 31:6 | `RESERVED` | Must be zero |

## Compatibility Rules

- Readers must reject capsules whose `magic`, `format_version`, or
  `header_words` they do not support.
- Unknown event types are fatal in `STRICT_REPLAY`.
- Unknown event flags are ignored only when their event type explicitly allows
  it. Otherwise they are fatal in `STRICT_REPLAY`.
- Payload lengths must match the event type unless a future version defines an
  extension flag.
- The footer event count and payload word count must match the header.
