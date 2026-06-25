# ReplayCapsule-RV Verification Plan

## Purpose

ReplayCapsule-RV captures only the events required to deterministically replay an
embedded RV32I execution across interrupts and MMIO. Verification must show that
the captured capsule is event-sufficient: if the same program image, initial
architectural state, and capsule are supplied to replay, every externally visible
architectural decision occurs in the same commit-indexed order as the original
run.

This plan covers the verification strategy and assertion checklist for:

- event ordering
- buffer freeze
- overflow handling
- interrupt pairing
- MMIO capture
- replay injection
- property checker correctness
- randomized interrupt timing
- seeded deterministic replay

## Core Invariants

The following invariants should be treated as release-blocking.

1. Record order is total and stable.
   Every captured event has one `(commit_index, order)` position in the capsule,
   and consumers see the same order the recorder committed.

2. Freeze makes the capsule immutable.
   Once freeze is observed, no later write can change captured event data,
   metadata, write pointers, count fields, overflow flags, or checksums except for
   explicitly documented status bits.

3. Overflow is fail-closed.
   If the recorder cannot capture a required event, replay must be marked
   unavailable or invalid. No truncated capsule may be advertised as complete.

4. Interrupts are paired at replay-visible boundaries.
   Each interrupt taken during record maps to exactly one replay injection point,
   including cause, privilege-relevant metadata if present, and the architectural
   commit-index boundary at which it is delivered.

5. MMIO reads are data events.
   Every nondeterministic MMIO read value used by the core during record is
   captured before it can influence architectural state, then injected during
   replay without consulting the live device value.

6. Replay never invents or drops required events.
   Replay consumes captured events exactly once, in order, and flags any mismatch
   between expected event type, target, timing window, or payload.

7. Checkers are checked.
   Property checkers and scoreboards must include negative tests that prove they
   fail on reordered, missing, duplicated, stale, or corrupted events.

8. Seeds are part of the artifact.
   Every randomized test records the seed, build identity, test name, event
   capsule digest, and replay digest needed to reproduce a failure.

## Verification Layers

### Formal Assertions

SystemVerilog assertions should guard local hardware invariants that must hold
cycle-by-cycle. Priority targets:

- recorder write pointer monotonicity
- no write after freeze
- overflow sticky behavior
- interrupt record and injection pairing
- MMIO read capture before retirement or architectural use
- replay event consumption ordering
- illegal state transition detection

See [formal/sv_assertions/README.md](../formal/sv_assertions/README.md).

### Bounded Model Checking

Yosys SMTBMC jobs should prove the small bounded forms of the invariants under a
minimal RV32I harness, with nondeterministic interrupts and MMIO responses. The
formal harness should not try to prove a full processor. It should prove the
ReplayCapsule interface contract around the processor boundary.

See [formal/yosys_smtbmc_scripts/README.md](../formal/yosys_smtbmc_scripts/README.md).

### Directed Simulation

Directed cocotb and Verilator tests should build small scenarios that exercise a
single risk at a time:

- one MMIO read, one interrupt, no overflow
- back-to-back MMIO reads
- interrupt adjacent to MMIO read
- nested or pending interrupts, if supported
- freeze while accepted events are pending
- buffer full and buffer overflow boundaries
- record then replay with live device values intentionally changed

See [tb/cocotb/README.md](../tb/cocotb/README.md) and
[tb/verilator/README.md](../tb/verilator/README.md).

### Property and Model-Based Tests

Host-side property tests should stress the event stream format, encoder/decoder,
scoreboard, replay cursor, capsule digesting, and negative checker fixtures. These
tests should run without RTL when possible so they can explore many event
sequences quickly.

See [tb/property_tests/README.md](../tb/property_tests/README.md).

### Randomized Interrupt Campaigns

Random interrupt timing tests should vary interrupt arrival, deassertion,
masking, MMIO latency, freeze timing, and buffer pressure while preserving seed
reproducibility.

See [tb/randomized_interrupt_tests/README.md](../tb/randomized_interrupt_tests/README.md).

## Event Model

Use a single reference event vocabulary across formal, simulation, and property
tests. The exact bit layout can evolve, but every checker should agree on these
logical fields:

- `commit_index`: retired-instruction count at the architectural boundary
- `order`: stable serial number for events at the same `commit_index`
- `kind`: reset input, interrupt line, interrupt delivery, MMIO read, MMIO write
  observation, external memory write, external input, replay marker, overflow,
  freeze, or implementation-specific metadata
- `pc`: diagnostic instruction PC or trap PC associated with the event when known
- `boundary`: replay-visible architectural boundary associated with the event
- `addr`: MMIO address when applicable
- `data`: captured MMIO data or event payload
- `irq_id`: interrupt source or encoded cause when applicable
- `mode`: record, replay, idle, frozen, or invalid
- `digest_input`: fields that participate in capsule identity

If the implementation intentionally excludes a field, the verification owner
must document why the field is not needed for deterministic replay.

## Scoreboard Strategy

The main scoreboard compares a record trace and a replay trace at replay-visible
boundaries, not just at end-of-test. It should check:

- same number of consumed required events
- same ordered event kind stream
- same interrupt delivery order and cause
- same MMIO read address and injected value
- same `(commit_index, order)` positions for boundary events
- same architectural commit stream when exposed by the core
- same final register and memory signature for the test program
- same capsule digest before and after freeze
- no live MMIO value used during replay for captured reads

The scoreboard must fail loudly on first mismatch and include the seed, event
position, PC, event kind, expected payload, observed payload, and capsule digest.

## Coverage Targets

Functional coverage should track:

- freeze observed with 0, 1, many, full, and overflowed event buffers
- overflow at each legal event kind
- interrupt before, during, and after MMIO wait states
- interrupt just before and just after the replay injection boundary in
  commit-index time
- replay with matching capsule
- replay with event kind mismatch
- replay with payload mismatch
- replay with missing final event
- replay with duplicate event
- replay with changed live MMIO value
- deterministic rerun of the same seed across at least two simulator invocations

## Exit Criteria

A verification milestone is complete when:

- release-blocking formal properties pass at the agreed bounded depth
- every checklist item in the relevant README is implemented or explicitly waived
- directed record/replay tests pass in both cocotb and Verilator when available
- property tests include positive and negative checker fixtures
- randomized interrupt tests emit reproducible seed artifacts
- at least one failing-seed replay has been demonstrated end-to-end
- documentation records any architectural assumptions that the capsule depends on
