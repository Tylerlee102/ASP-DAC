# Randomized Interrupt Timing Strategy

Randomized interrupt tests should stress the timing boundary where external
nondeterminism becomes recorded event data. The goal is not random noise. The
goal is reproducible pressure on interrupt ordering, MMIO interactions, freeze,
overflow, and replay injection.

## Randomized Dimensions

Vary these dimensions under a seed:

- interrupt assert cycle
- interrupt deassert cycle
- interrupt source or cause
- interrupt masking windows if the core exposes them
- MMIO response latency
- MMIO return data
- order of MMIO and interrupt pressure
- freeze request cycle
- buffer capacity when parameterized
- replay live MMIO values
- replay live interrupt noise

Keep program images small and deterministic so mismatches point to replay logic,
not workload complexity.

## Scenario Families

Interrupt-only:

- single interrupt at each instruction boundary
- two interrupts separated by 0, 1, and many instructions
- interrupt pending across freeze request
- interrupt asserted during replay when live interrupts are not supposed to drive
  architectural state

Interrupt and MMIO:

- interrupt before MMIO request
- interrupt during MMIO wait
- interrupt on the MMIO response cycle
- interrupt immediately after MMIO read completes
- repeated MMIO reads while interrupts toggle

Buffer pressure:

- interrupts and MMIO reads fill the buffer exactly
- one additional required event overflows the buffer
- freeze near full-buffer boundary
- replay attempted on full and overflowed capsules

Replay corruption:

- wrong interrupt cause
- shifted interrupt delivery boundary
- swapped interrupt and MMIO events
- missing interrupt at replay boundary

## Seed Discipline

Every randomized test must emit:

- seed
- test family
- program or instruction trace identity
- RTL build identity if available
- buffer depth and relevant parameters
- record capsule digest
- replay digest
- first mismatch `(commit_index, order)` on failure

The same seed must be runnable in record-only, replay-only, and record-then-replay
modes. When a failure is found, convert the minimized seed into a directed test.

## Current Runnable RTL-Smoke Campaign

`scripts/run_randomized_interrupt_campaign.py` runs the current seeded Icarus
PicoRV32 wrapper campaign. It varies the interrupt pulse width after the command
MMIO write and also sweeps fixed interrupt assertion windows in
`interrupt_race_bug`. Each seed runs twice in fresh simulator invocations and
must reproduce the same expected property ID, frozen capsule count, signature,
and capsule-packet digest on both runs.

This is an RTL-smoke reproducibility campaign, not a full record-then-replay
randomized Verilator campaign. The stronger replay-noise and MMIO-latency cases
above remain pending until the full simulation/replay harness exists.

## Deterministic Replay Checks

For each selected seed:

1. Run record and save the frozen capsule.
2. Run replay with the same live MMIO and interrupt schedule.
3. Run replay with different live MMIO values and extra live interrupt noise.
4. Verify both replays consume the same capsule events.
5. Verify both replays produce the same architectural signature and replay digest.
6. Verify a corrupted copy of the capsule fails for the expected reason.

## Coverage Goals

Track coverage across:

- interrupt before, during, and after MMIO wait
- interrupt delivery at the first and last allowed commit-index boundary
- freeze before, during, and after pending interrupt capture
- exact full buffer
- overflow by interrupt
- overflow by MMIO read
- replay with live interrupt noise
- replay with changed live MMIO data
- deterministic rerun of the same seed in a fresh simulator process

## Failure Triage

Classify failures as:

- recorder ordering bug
- missing required event
- duplicate event
- stale frozen capsule mutation
- overflow validity bug
- replay injection bug
- scoreboard/checker bug
- nondeterministic testbench artifact

Only the last category should be fixed by changing the random testbench. The
other categories should become directed regression tests.
