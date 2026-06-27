# formal_model_agent Notes

Owned files:

- `docs/event_model.md`
- `docs/replay_sufficiency_theorem.md`
- `formal/assumptions.md`
- `formal/replay_sufficiency_theorem.md`
- `docs/subagents/formal_model_agent.md`

## Current Model Position

ReplayCapsule-RV is modeled as a single-hart RV32I architectural replay system.
The central boundary is the commit-indexed event stream: every nondeterministic
environment influence that can affect firmware or the safety checker must be
logged with exact payload and exact ordering.

The replay claim is conditional and prefix-oriented:

If the firmware image, platform profile, initial architectural state, and
boundary event prefix match the original run, deterministic replay reconstructs
the same architectural trace prefix and reaches the same safety-property
violation signature.

## Defined Terms

The docs now define:

- Architectural state.
- Firmware image.
- Deterministic core assumption.
- Nondeterministic boundary events.
- Commit-index time.
- Interrupt timing.
- MMIO reads and writes.
- External inputs.
- Safety-property violation signature.
- Replay capsule.
- Replay equivalence.

## Integration Contracts

Recorder and runtime work should preserve these contracts:

- Events are ordered by `(commit_index, order)`.
- A concrete event format may call `order` a global `seq`; the requirement is
  stable total ordering.
- `commit_index` counts retired firmware instructions, not cycles.
- Exact cycle fields or `cycle_window` fields are compatible as metadata, but
  the formal sufficiency claim is commit-index based.
- Interrupt events at index `k` occur after instruction `k` retires and before
  the next instruction retires.
- MMIO read values are replay inputs.
- MMIO writes are deterministic observations that replay validates.
- Device responses to writes must appear later as explicit events if firmware or
  the safety checker can observe them.
- DMA-like external RAM mutations are out of scope for the current prototype
  unless future work models them as explicit boundary events.
- Timer/counter/random observations are deterministic only if the platform says
  so; otherwise they are events.

## Open Questions For Other Agents

- Which exact CSR subset is supported in the initial RV32I profile?
- Are `cycle`, `time`, and `instret` exposed to firmware? If yes, are they
  deterministic commit-index functions or logged inputs?
- Is executable RAM supported in the initial implementation?
- Are DMA or other external memory writers in scope for the initial prototype?
- Does the recorder log interrupt line state, interrupt delivery, or both?
- What canonical binary format will represent `(commit_index, order, kind,
  payload)`?

## Do Not Overclaim

The theorem does not promise cycle-accurate replay, physical device simulation,
multicore replay, or proof of recorder noninterference. It proves only that a
complete architectural boundary event prefix is sufficient for deterministic
architectural replay of the selected violation prefix.
