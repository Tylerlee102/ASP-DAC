# Formal Assumptions

This file records the assumptions required by the ReplayCapsule-RV replay
sufficiency theorem. The assumptions are part of the theorem statement, not
claims already proved by this repository.

## A0. Platform Profile

There is a fixed platform profile `P` containing:

- RV32I ISA semantics and any enabled extensions.
- CSR set, reset behavior, privilege behavior, and trap behavior.
- Memory map partitioning addresses into immutable image, RAM, and MMIO.
- Alignment and fault behavior for each access class.
- Interrupt sources, priorities, masking rules, and trap-vector rules.
- Semantics for counters and timers, or a declaration that their reads are
  boundary events.

The replay engine and recorder use the same `P` version.

## A1. Architectural State Completeness

The architectural state `A` contains every firmware-visible value that can
affect future execution or the checked safety property:

`A = (pc, x, csr, priv, ram, trap_state)`

where `x0 = 0`, `ram` contains all mutable replay-visible bytes, and
`trap_state` covers any trap bookkeeping not otherwise represented.

If an implementation feature can influence future execution but is not in `A`,
it must be represented as a boundary event or excluded by `P`.

## A2. Firmware Image Identity

The immutable firmware image `F` used during replay is byte-identical to the
image used during recording for all immutable regions. The platform profile
defines which regions are immutable. Mutable executable memory, when allowed, is
part of `ram` rather than `F`.

Replay must reject a capsule if the image or platform identity does not match.

## A3. Deterministic Core

There exists a deterministic transition relation:

`step(P, F, A, input) -> A'`

for each architectural transition, where `input` is either empty or one
boundary payload consumed by the transition.

For equal `(P, F, A, input)`, `step` returns the same `A'` and the same
architectural observation. Nondeterministic facts are not hidden inside `step`;
they must arrive as boundary payloads.

## A4. Boundary Event Completeness

For the execution prefix under replay, the capsule contains every
nondeterministic input that can affect architectural state or the safety
checker. This includes, when applicable:

- Reset inputs and unspecified reset values.
- MMIO read values and MMIO access faults.
- Interrupt line changes, interrupt edges, and nondeterministic delivery facts.
- External memory writes such as DMA.
- Host/debug/sensor inputs not otherwise represented.
- Firmware-visible timer, counter, or random values that are not deterministic
  functions of the current architectural state and commit-index time.

No omitted environmental fact may influence the replayed prefix.

## A5. Commit-Index Ordering

Each event is ordered by `(commit_index, order)`.

`commit_index = k` means exactly `k` firmware instructions have retired.
Asynchronous events at `k` occur after instruction `k` has retired and before
the next instruction retires. Events sharing `k` are applied in ascending
`order`.

The event order in the capsule matches the order that affected the original
run. A concrete format may implement `order` as a global monotonic `seq`; the
formal requirement is that the order is total, stable, and replayed exactly.

## A6. Precise Interrupts

Interrupt effects are precise at instruction boundaries. An interrupt event at
`commit_index = k` cannot partially modify the architectural effects of
instruction `k` or of the next retired instruction. Trap entry is an ordered
architectural transition at the same commit-index boundary.

If platform interrupt delivery has behavior not derived from line state, CSR
state, and `P`, the capsule records enough `interrupt_delivery` payload to make
delivery deterministic.

## A7. MMIO Contract

An MMIO read returns the value recorded in the corresponding `mmio_read` event
and applies only replay-visible side effects represented by that event or by
later boundary events.

An MMIO write is determined by the current architectural state. Replay validates
that the observed address, width, byte lanes, data, and fault behavior match the
capsule. Device reactions to writes are included only when they later become
architecturally visible, at which point they must be captured as boundary
events.

## A8. External Memory Mutation Contract

The core is the only writer to `ram` except for recorded
`external_memory_write` events. Such events specify address, bytes, fault or
ordering behavior if relevant, and exact commit-index/order.

## A9. Safety Property Determinism

The safety property checker is deterministic over:

- The architectural trace prefix.
- Replay-visible boundary observations, such as MMIO writes and trap events.
- Fixed property configuration included in or identified by the capsule.

If the property depends on host time, hidden device state, random choices, or
external files, those dependencies must be fixed by the capsule or excluded from
the theorem.

## A10. Prefix Sufficiency

The theorem covers only the finite prefix through the target violation. Events
after the target violation are irrelevant to reproducing that violation.

## A11. Recorder Noninterference Is Separate

The theorem is about replaying the recorded execution. It assumes the event log
accurately describes the execution that occurred under recording. It does not,
by itself, prove that instrumentation preserved the behavior of an
uninstrumented deployment.
