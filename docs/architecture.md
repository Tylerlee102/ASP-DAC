# ReplayCapsule-RV Hardware Architecture

ReplayCapsule-RV records the external events needed to replay an embedded RV32I
run deterministically. The hardware does not try to store a full instruction
trace. Instead, it captures a compact, ordered capsule containing the
nondeterministic inputs at the RV32I boundary: interrupt behavior and MMIO
transactions.

This document is the architecture contract for synthesizable SystemVerilog
modules named:

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

## Replay Model

A replay is deterministic when the following inputs match the recorded run:

- reset vector, program image, data memory image, and configuration registers
- RV32I core implementation and integration parameters
- ordered external interrupt samples delivered to the core
- ordered MMIO read responses, write acknowledgements, and response timing when
  MMIO wait states can affect execution

The capsule is therefore "event-sufficient": it records only the external
events that can change the architectural path of the core, plus enough metadata
to schedule and check those events during replay.

The default time anchor is `commit_index`, the number of committed RV32I
instructions since capsule start. Some older notes use `retire_count` for the
same concept. `cycle_count` is optional and is used only when the integration
needs to reproduce replay-visible wait-state behavior. Portable capsule export
also assigns a monotonically increasing `event_seq` so simultaneous events have
a stable total order.

## Top-Level Flow

```text
               live IRQ/MMIO/core observation
                         |
                         v
                    event_tap
                         |
                         v
                 event_classifier
                  /             \
                 v               v
        interrupt_logger     mmio_logger
                  \             /
                   v           v
                    event_slicer
                         |
                         v
                  capsule_buffer
                         |
                         v
                  hash_signature
                         |
                         v
                     registers

During replay:

capsule_buffer -> replay_control -> IRQ/MMIO injection
                         |
                         v
                 property_checker
```

## Operating Modes

`replay_capsule_top` receives the selected capture mode and top-level control
signals. A SoC integration can source those controls from `registers`.

- `IDLE`: capture and replay state is reset or quiescent.
- `RECORD`: live interrupts and MMIO reach the core. Loggers record the events
  needed for a future replay. Buffer overflow is a fatal capsule error.
- `FROZEN`: recording has stopped and the capsule is immutable. Software may
  drain or inspect the buffer, but event contents, counts, pointers, and hash
  inputs cannot change except for documented status bits.
- `REPLAY`: live interrupt and MMIO response inputs are masked. Recorded
  events are consumed from `capsule_buffer` and driven by `replay_control`.
- `VERIFY`: replay mode plus stricter checking of observed core behavior,
  MMIO requests, write data, event order, and final signature.

Implementations may merge `REPLAY` and `VERIFY` internally, but the register
interface should expose verification status separately from basic playback.
`FROZEN` may be an explicit mode or a sticky state reached after a stop request
or fatal recorder condition.

## Module Responsibilities

### `replay_capsule_top`

`replay_capsule_top` is the integration shell for the record-side capsule path.
The current RTL parameterizes capsule depth and wires event observation,
classification, property checking, buffering, and signature generation. A fuller
top-level revision can also own IRQ width, MMIO address classification, register
control, and replay injection parameters.

It should keep detailed event classification policy inside `event_classifier`
and detailed property policy inside `property_checker`.

The current RTL top is record-side focused: it wires `event_tap`,
`property_checker`, `event_slicer`, `event_classifier`, `capsule_buffer`, and
`hash_signature`; assigns `event_id`; injects property-fail and checkpoint-hash
events; and exposes capsule readback/status. `replay_control`, `registers`,
`interrupt_logger`, and `mmio_logger` are present as companion modules for
integration or later top-level expansion.

### `event_tap`

`event_tap` normalizes observations from the RV32I core and platform fabric into
stable, clocked event candidates. It observes, at minimum:

- commit validity, committed PC, committed instruction, and `commit_index`
- branch and jump indicators
- memory validity, write direction, address, write data, and read data
- external input validity and value
- interrupt or trap enter/exit indicators

All asynchronous interrupt inputs must be synchronized before they become tap
events. The current `event_tap` emits one prioritized event candidate and raises
`multievent_pending` when multiple candidates are present in the same cycle.

### `event_classifier`

`event_classifier` decides whether an observed event should be kept under the
selected capture policy. The current classifier takes a 4-bit internal event
type, capture mode, property-window state, and overflow guard, then emits
`keep_event`, `event_is_nondeterministic`, and
`event_is_property_relevant`.

For the current replay-capsule policy, nondeterministic events are MMIO reads,
interrupt enter/exit, and external input. MMIO writes and selected control-flow
or memory events are property-relevant context.

### `interrupt_logger`

`interrupt_logger` records trap or interrupt enter/exit observations at a
`commit_index` and PC. It emits `EV_INTERRUPT_ENTER` or
`EV_INTERRUPT_EXIT`, tracks active nesting depth, and reports unpaired exits.

If a future integration exposes raw IRQ line levels, those levels should be
encoded as an external input or added as an explicit IRQ-level event before they
can influence replay.

### `mmio_logger`

`mmio_logger` records transactions whose addresses match configured MMIO
windows. The current logger records valid/write, address, read or write data,
`commit_index`, and PC. Future bus integrations can extend the payload with byte
enables, response codes, and latency when those fields affect replay or
checking.

The logger treats normal instruction memory and deterministic data memory as
out of scope. If external memory is nondeterministic, the integration must mark
it as MMIO or provide another recorder.

### `event_slicer`

`event_slicer` selects property-relevant context around a failure. The current
module maintains a configurable last-`K` context window after
`property_fail_valid` and emits `property_window_active` and
`keep_context_event`.

Portable 32-bit capsule packetization is an export/import layer described in
`docs/capsule_format.md`; it can be implemented in `replay_capsule_top`, host
software, or a future extension of `event_slicer`.

### `capsule_buffer`

`capsule_buffer` stores packed internal event packets. The current packet width
is `RC_EVENT_WIDTH = 168`, matching `{event_type, flags, event_id,
commit_index, pc, addr, data}` from `replaycapsule_event_pkg`.

Recording must not silently drop events. If the buffer cannot accept a required
event, hardware must either stall the core through an integration-provided hold
signal or raise a fatal overflow status.

### `replay_control`

`replay_control` consumes packed internal event packets and schedules them
against either `commit_index` or a cycle-time slot carried in `event_id`. The
current replay path injects MMIO/external-input values and interrupt enter/exit
pulses when the selected time base matches.

Strict request matching for MMIO writes is an integration obligation for
`replay_capsule_top` or a future `replay_control` extension.

### `property_checker`

`property_checker` consumes the internal event fields and emits a property id
and signature when a monitored safety property fails. The current checker covers
prototype embedded properties: actuator limit, interrupt during critical
section, sensor response deadline, stack protection, and MMIO ordering.

General replay invariants such as event ordering, no write after freeze, and
hash agreement remain top-level or verification-plan obligations.

### `registers`

`registers` provides the software control and status plane. The current block
exposes capture mode, replay enable, capsule clear, capsule frozen, capsule
overflow, event count, and failure signature. A wider integration can add IRQ
masks, MMIO windows, buffer pointers, hash words, and first-error sequence
registers.

The register block must not directly inspect core buses. It controls policy and
reports status owned by the recorder and replay modules.

### `hash_signature`

`hash_signature` computes a streaming 32-bit determinism signature over accepted
internal event packets. The signature is an integrity and replay consistency
check, not a security primitive.

Portable capsule export may widen this to the four-word hash fields in the v1
format, but the input order must still match accepted event order.

## Event Ordering

Internal events are ordered by the sequence in which accepted packets are
written to `capsule_buffer`. Portable capsule export assigns `event_seq`; the
current internal packet carries `event_id` and `commit_index`.

Scheduling uses these fields:

- `commit_index`: logical replay time
- `event_id`: source-local id, sequence slot, or cycle-time slot
- `pc`, `addr`, and `data`: event-specific evidence
- `event_type`: event kind

When multiple event candidates share the same cycle, `event_tap` uses this
priority order and raises `multievent_pending`:

1. interrupt enter
2. interrupt exit
3. external input
4. MMIO read
5. MMIO write
6. non-MMIO store
7. non-MMIO load
8. branch
9. jump
10. commit

`replay_capsule_top` must either drain all same-cycle candidates in a stable
order or document that lower-priority candidates are intentionally outside the
selected capture policy.

## Integration Assumptions

- Single RV32I hart in v1. Multihart ordering is out of scope.
- One clock domain is preferred. Cross-clock IRQ or bus inputs must be
  synchronized before they reach `event_tap`.
- The core is deterministic given identical reset state, instruction memory,
  deterministic data memory, and replayed external events.
- Firmware image identity, platform profile, and initial architectural state are
  fixed by reset contract, companion manifest, or capsule hashes before replay
  is trusted.
- Instruction memory and non-MMIO data memory contents are identical between
  record and replay.
- Reset-time inputs, uninitialized RAM, firmware-visible counters, and other
  external inputs are either deterministic by platform contract or mapped to
  interrupt/MMIO events before they can affect the core.
- MMIO address windows are configured before capture and included in the
  capsule configuration hash.
- The integration can either stall the core on recorder backpressure or provide
  enough buffering that required events cannot overflow under the configured
  workload.
- During replay, live peripherals are not allowed to drive replayed MMIO read
  data or interrupt lines into the core.
- DMA, coherent caches, self-modifying external instruction memory, and other
  nondeterministic bus masters require a separate event source or must be
  disabled for v1 replay.
- Reset during an active capsule terminates the capsule unless explicitly
  represented by a future reset event type.
