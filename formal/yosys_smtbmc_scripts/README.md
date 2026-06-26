# Yosys SMTBMC Verification Scripts

This directory holds bounded model checking scripts and harness notes for
ReplayCapsule-RV. The goal is to prove the recorder and replay contracts around a
small nondeterministic RV32I boundary, not to prove every processor behavior.

Implemented now:

- `event_tap_bmc.sby` plus `event_tap_bmc_harness.sv`: depth-2 BMC over the
  event-tap priority encoder and field routing. The harness checks the
  interrupt, external-input, MMIO, load/store, branch/jump, and commit priority
  order, verifies key payload fields, and checks `multievent_pending`.
- `event_tap_cover.sby`: depth-2 cover run over the same event-tap harness. It
  checks that interrupt, MMIO read, store, branch, and multievent cases are
  reachable.
- `event_classifier_slicer_bmc.sby` plus
  `event_classifier_slicer_bmc_harness.sv`: depth-8 BMC over capture-policy
  classification and LAST_K context-window behavior. The harness checks
  nondeterministic/property-relevant flags, keep-event rules for each capture
  mode, and context-window reset/open/expire transitions.
- `event_classifier_slicer_cover.sby`: depth-8 cover run over the same
  classifier/slicer harness. It checks that capture-all, MMIO evidence,
  overflow-guard retention, context-window opening, and context-window expiry
  are reachable.
- `property_checker_bmc.sby` plus `property_checker_bmc_harness.sv`: depth-8
  BMC over reduced-deadline property-checker behavior. The harness checks
  failure IDs and signatures for actuator-limit, interrupt-critical,
  sensor-deadline, stack-protect, MMIO-ordering, and watchdog-timeout failures,
  plus reset/clear and exposed state transitions.
- `property_checker_cover.sby`: depth-8 cover run over the same checker
  harness. It checks that all six supported failure families are reachable.
- `hash_signature_bmc.sby` plus `hash_signature_bmc_harness.sv`: depth-4 BMC
  over the rolling signature accumulator. The harness checks reset/clear seed,
  no-event stability, and the exact rotate/XOR update for accepted event
  packets.
- `hash_signature_cover.sby`: depth-4 cover run over the same hash-signature
  harness. It checks that reset, clear, no-event stability, and event-update
  states are reachable.
- `mmio_interrupt_loggers_bmc.sby` plus
  `mmio_interrupt_loggers_bmc_harness.sv`: depth-6 BMC over MMIO event field
  routing and interrupt depth tracking. The harness checks read/write packet
  fields, interrupt enter/exit packet fields, active-depth increments and
  decrements, and sticky unpaired-exit detection.
- `mmio_interrupt_loggers_cover.sby`: depth-6 cover run over the same
  logger harness. It checks that MMIO read/write events, paired interrupt
  enter/exit, and unpaired interrupt exit cases are reachable.
- `registers_bmc.sby` plus `registers_bmc_harness.sv`: depth-6 BMC over the
  MMIO-visible control/status register block. The harness checks address decode,
  readback muxing, reset defaults, global clear behavior, control writes, and
  one-cycle `capsule_clear` pulse behavior.
- `registers_cover.sby`: depth-6 cover run over the same register harness. It
  checks status/count readback, control writes, and global clear pulse
  reachability.
- `replay_control_bmc.sby` plus `replay_control_bmc_harness.sv`: depth-8 BMC
  over replay consume/inject behavior. The harness checks disabled and
  time-mismatched events remain idle, MMIO/external-input packets inject data,
  interrupt enter/exit packets inject exactly one pulse, non-injectable event
  kinds are not consumed, and replay underflow is sticky until clear.
- `replay_control_cover.sby`: depth-8 cover run over the same replay-control
  harness. It checks that MMIO injection, interrupt injection, and underflow are
  reachable.
- `capsule_buffer_bmc.sby` plus `capsule_buffer_bmc_harness.sv`: depth-12 BMC
  over a four-entry buffer. The harness checks count bounds, failure-to-freeze,
  frozen-count stability, sticky overflow, legal write-count increments, and
  first-overflow behavior.
- `capsule_buffer_cover.sby`: depth-12 cover run over the same buffer harness.
  It checks that one-write, frozen, and overflow states are reachable.
- `replay_capsule_top_bmc.sby` plus `replay_capsule_top_bmc_harness.sv`: depth-16
  BMC over a four-entry recorder configuration. The harness checks event-count
  bounds, failure-to-freeze, frozen-count stability, and sticky overflow. The
  one-command gate runs this through `scripts/run_formal_checks.py` when local
  SMTBMC tooling is available.
- `replay_capsule_top_cover.sby`: depth-16 cover run over the same harness. It
  checks that captured-event, frozen-capsule, and overflow states are reachable,
  which guards against over-constraining the bounded proof harness.

## Recommended Targets

Create one script per proof family:

- `ordering.sby`: event accept, commit, `(commit_index, order)`, and replay
  cursor ordering
- `freeze.sby`: immutability after freeze and deterministic final state
- `overflow.sby`: full-buffer boundary, overflow sticky flag, replay invalidation
- `interrupt_pairing.sby`: record-to-replay interrupt event pairing
- `mmio_capture.sby`: MMIO read capture and replay data injection
- `replay_mismatch.sby`: wrong event kind, address, payload, and early EOF
- `checker_selftest.sby`: positive and negative fixtures for property checkers

If a single top-level script is used instead, each proof family should still be
selectable by task name.

## Harness Assumptions

Keep assumptions minimal and visible:

- clock and reset are well formed
- input handshakes obey ready/valid stability while stalled
- MMIO responses eventually arrive only in liveness-oriented cover runs
- record and replay modes are mutually exclusive unless a design mode documents
  otherwise
- interrupt lines may change nondeterministically between sampling boundaries
- buffer depth is a small parameter for proof, usually 2 to 4 entries

Avoid assuming away the failures the properties are meant to catch. In
particular, do not assume no overflow, no concurrent interrupt and MMIO activity,
or no freeze during pending work unless that behavior is impossible by design.

## Proof Depths

Start with shallow bounded checks and increase depth after harness stability:

- depth 4: reset, empty freeze, no-event replay start
- depth 8: one event record and replay
- depth 12: two adjacent events and one interrupt/MMIO pairing
- depth 16 or greater: full buffer, overflow, freeze near boundary

For parameterized proofs, use the smallest buffer depth that can express the
bug class. Overflow proofs should use at least depth 2 so full and over-full are
distinct states.

## Expected Properties

Each target should assert:

- no assertion failures
- no X-dependent control state in synthesis-visible logic when the tool can check
  it
- no out-of-range memory write
- no illegal replay-valid state after overflow
- no mutable frozen capsule state
- no replay consumption at the wrong `(commit_index, order)`

Each target should cover:

- at least one successful record
- at least one successful replay consumption
- at least one boundary case relevant to the target

## Checker Self-Tests

Property checkers need their own proof or bounded simulation target. The checker
self-test should instantiate a tiny synthetic event source and drive:

- a valid trace that passes
- swapped adjacent events that fail
- missing final event that fails
- duplicate event that fails
- MMIO payload corruption that fails
- interrupt cause mismatch that fails
- write after freeze that fails

The self-test is important because an end-to-end proof can pass when a checker is
not connected to the right signal or is overconstrained.

## Triage Notes

When a proof fails, preserve:

- script name and task
- solver and depth
- parameter values
- counterexample waveform
- failing property name
- minimal seed or nondeterministic input trace if exported

Counterexamples should be reduced to a directed cocotb or Verilator test whenever
the failure represents a real design risk.
