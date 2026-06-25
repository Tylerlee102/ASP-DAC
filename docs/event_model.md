# ReplayCapsule-RV Event Model

This document defines the replay boundary for ReplayCapsule-RV: a single-hart
RV32I embedded target whose firmware execution can be replayed deterministically
when all nondeterministic architectural inputs are logged as boundary events.

The model is intentionally architectural. It is not a cycle-accurate hardware
model and it does not try to reconstruct hidden device internals. Its claim is
that, under the assumptions below, the same firmware image, same initial
architectural state, and same commit-indexed boundary event stream are
sufficient to reproduce the same architectural execution prefix and the same
safety-property violation signature.

## Scope

In scope:

- One RV32I hart, normally machine-mode embedded firmware.
- A fixed platform memory map that partitions addresses into immutable firmware
  image, RAM, and MMIO regions.
- Precise exceptions and interrupts at architectural instruction boundaries.
- MMIO values and externally driven state changes recorded as events.
- Safety properties that are deterministic predicates over the captured
  architectural trace.

Out of scope unless explicitly modeled as events:

- Multicore races, cache-coherence behavior, and shared-memory interleavings.
- Cycle-accurate timing, analog behavior, metastability, and electrical effects.
- Device-internal state that is never observed through architectural effects.
- Undefined or implementation-specific behavior not fixed by the platform
  contract.

## Architectural State

An architectural state `A` is the replay-visible machine state needed by the
RV32I architectural semantics and by the safety checker:

- `pc`: the next program counter, or the trap handler program counter after a
  trap-entry transition.
- `x[0..31]`: the integer register file, with `x0 == 0`.
- `csr`: all CSRs that can affect or be observed by firmware in the selected
  platform profile, including interrupt-enable, pending, trap-vector, exception,
  counter, and status CSRs when present.
- `priv`: current privilege mode if the platform exposes more than one mode.
- `ram`: replay-visible mutable memory bytes outside immutable firmware image
  and outside MMIO.
- `trap_state`: any architectural trap bookkeeping not already represented in
  `pc` and `csr`.

The state excludes pipeline contents, caches, branch predictors, clock phase,
and other microarchitectural details unless those details become visible through
the fields above. If executable RAM is allowed, the RAM bytes are part of
`ram`; the immutable firmware image only covers immutable code/data regions.

## Firmware Image

A firmware image `F` is the immutable input program and platform description:

- Byte contents of immutable executable and read-only data regions.
- Entry point and reset vector.
- Platform memory map, including RAM and MMIO address ranges.
- ISA and platform profile used for decoding and CSR behavior.
- Optional symbol/build metadata used by diagnostics, not by replay semantics.
- A content hash or manifest hash used to reject replay against the wrong image.

Replay equivalence requires the same `F` and compatible semantic version for the
platform model. A capsule may include a full image or a hash plus an external
image reference, but the replay engine must verify identity before trusting the
event log.

## Deterministic Core Assumption

The deterministic core assumption says that, between nondeterministic boundary
events, the next architectural transition is a pure function of `F`, the current
architectural state, and any boundary payload consumed by that transition.

Concretely:

- Instruction decode and RV32I execution are deterministic for the selected ISA
  profile.
- RAM reads return the current bytes in `ram`; RAM writes update `ram`
  deterministically.
- Loads from immutable image regions return bytes from `F`.
- Exceptions are precise and deterministic from the same pre-state.
- Interrupt arbitration is deterministic from the same interrupt-pending state,
  CSR state, privilege state, and event order.
- Any firmware-visible counter, timer, random source, debug input, uninitialized
  memory value, or implementation-defined CSR behavior is either deterministic
  by platform contract or represented by an event.

If the firmware can observe cycle timing through `cycle`, `time`, device timers,
or MMIO, those observations are part of the nondeterministic boundary unless the
platform defines them as deterministic functions of commit-index time.

## Commit-Index Time

Commit-index time is the logical replay clock.

`commit_index = k` means exactly `k` firmware instructions have retired. The
first retired instruction has instruction index `1`; the state after it has
`commit_index = 1`.

Boundary events are tagged by:

- `commit_index`: the number of retired instructions at the instant the event is
  applied or observed.
- `order`: a stable serial number for events with the same `commit_index`; an
  implementation may use one global monotonic `seq` field for this ordering.
- `kind`: the event kind.
- `payload`: event-specific data.

Asynchronous events, including interrupt-line changes and DMA-like memory
mutations, occur between retired instructions and therefore use the
`commit_index` of the last retired instruction. A trap-entry transition caused by
an asynchronous interrupt does not retire a firmware instruction; it is ordered
at the same `commit_index` before the next instruction retires.

Commit-index time is not wall-clock time and is not a cycle count. It preserves
the ordering that matters for architectural replay, not physical latency.
Cycle-index fields or `cycle_window` constraints can be carried as diagnostic or
stricter replay metadata, but the sufficiency theorem below relies only on
commit-index ordering.

## Nondeterministic Boundary Events

A nondeterministic boundary event is any environment-sourced fact that can alter
the future architectural trace but is not determined by `F` and the current
architectural state.

Required event families are:

- `reset_input`: reset-time values not fixed by `F`, such as boot straps,
  initial interrupt levels, implementation-selected CSR reset values, and
  initial RAM contents when RAM is not platform-initialized.
- `interrupt_line`: externally driven interrupt assertion, deassertion, or edge
  observation at a commit-index boundary.
- `interrupt_delivery`: the interrupt cause and trap-entry choice when delivery
  itself is not fully derivable from recorded line state and deterministic core
  rules.
- `mmio_read`: the value returned by a load from an MMIO address, including
  width, address, byte lanes, and any replay-visible read side effect.
- `mmio_write_observed`: the address, width, byte lanes, and data of an MMIO
  store. The write is deterministic from firmware state, so replay normally
  validates it rather than using it as an input.
- `external_memory_write`: DMA or another external agent mutating replay-visible
  RAM.
- `external_input`: any other input channel that can affect architectural state,
  such as debug commands, sensor samples, host packets, or non-MMIO device
  callbacks.

An event log is sufficient only if every such influence before the target
violation is present, exact, and ordered.

## Interrupt Timing

Interrupt timing is represented at instruction boundaries:

- An interrupt-line event at `commit_index = k` is applied after instruction `k`
  has retired and before the next firmware instruction retires.
- If delivery is deterministic from pending lines and CSRs, the replay engine
  recomputes whether the interrupt is taken.
- If delivery depends on platform behavior not otherwise modeled, the capsule
  records `interrupt_delivery` with the cause, privilege target, and trap-entry
  architectural effects or enough data to recompute them.
- Multiple interrupt events at the same `commit_index` are applied by `order`.

This is sufficient for precise RV-style interrupts. It does not model
mid-instruction asynchronous effects; such behavior is outside this profile.

## MMIO Reads and Writes

MMIO is the primary nondeterministic boundary for embedded firmware.

For an MMIO read, the capsule records:

- Instruction index or commit point of the load.
- Address, width, byte lanes, and alignment behavior.
- Returned value.
- Exception result if the access faults.
- Any replay-visible side effect that must affect later architectural behavior
  and is not already represented by later events.

For an MMIO write, the replay engine recomputes the write from the replayed
firmware state and validates it against the capsule:

- Address, width, byte lanes, and data.
- Exception result if the access faults.
- Optional device-facing metadata used by a harness.

The theorem does not require replaying the true internal state of the device. It
requires reproducing all device effects that later become visible to firmware or
to the safety checker.

## External Inputs

External inputs are modeled by the earliest architectural point at which they
can influence replay:

- If firmware observes the input by loading MMIO, it is an `mmio_read` value.
- If the input changes interrupt state, it is an `interrupt_line` event.
- If it mutates RAM without firmware executing a store, it is an
  `external_memory_write` event.
- If it changes reset-time state, it is a `reset_input` event.

The event payload should include enough provenance for debugging, but replay
semantics depend only on the architectural effect and ordering.

## Safety-Property Violation Signature

A safety property `Prop` is a deterministic predicate over an architectural trace
prefix and optional boundary observations. A violation occurs when `Prop` reports
failure for the first or target prefix selected by the checker.

A violation signature identifies that replay reached the same failure:

- `property_id`: stable identifier for the checked property.
- `commit_index` and same-index `order` or transition ordinal.
- `pc` and trap/exception cause when relevant.
- Witness fields used by the property, such as register names, memory
  addresses, MMIO addresses, assertion IDs, or expected/actual values.
- Optional digest of the replayed trace prefix or capsule prefix.

The signature is a locator and equality check, not a standalone proof. If a
property depends on data outside the captured trace, that data must be added to
the capsule or fixed by assumption.

## Replay Capsule

A replay capsule `C` is the portable replay input:

- Firmware identity: image hash, manifest hash, or embedded image bytes.
- Platform identity: ISA profile, CSR profile, memory map, reset contract, and
  semantic model version.
- Initial architectural state or reset inputs sufficient to derive it.
- Commit-indexed boundary event log through at least the target violation.
- MMIO write observations used to validate replay and device-harness behavior.
- Target safety-property violation signature.
- Integrity metadata, such as capsule hash, event-log hash, and recorder
  version.

The capsule may contain data after the target violation, but the sufficiency
claim for reproducing a violation only needs the prefix through that violation.

## Replay Equivalence

An original run `R` and a replay run `R'` are replay-equivalent through target
point `t` when:

- They use the same firmware image and platform semantics.
- Their initial architectural states are equal.
- For every architectural transition through `t`, their replay-visible states
  are equal.
- They consume the same nondeterministic event payloads at the same
  commit-index/order positions.
- They produce the same MMIO write observations, traps, exceptions, and safety
  checker observations through `t`.
- They emit the same target violation signature.

Replay equivalence ignores hidden microarchitectural state and unobserved device
state. It is equivalence of the architectural execution relevant to firmware and
the chosen safety property.
