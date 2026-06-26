# Yosys SMTBMC Verification Scripts

This directory holds bounded model checking scripts and harness notes for
ReplayCapsule-RV. The goal is to prove the recorder and replay contracts around a
small nondeterministic RV32I boundary, not to prove every processor behavior.

Implemented now:

- `replay_capsule_top_bmc.sby` plus `replay_capsule_top_bmc_harness.sv`: depth-16
  BMC over a four-entry recorder configuration. The harness checks event-count
  bounds, failure-to-freeze, frozen-count stability, and sticky overflow. The
  one-command gate runs this through `scripts/run_formal_checks.py` when local
  SMTBMC tooling is available.

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
