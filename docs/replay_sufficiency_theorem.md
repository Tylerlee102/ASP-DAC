# Replay Sufficiency Theorem

This note states the target replay claim for ReplayCapsule-RV in engineering
terms. The matching formal assumptions are in `formal/assumptions.md`; the
symbolic statement and proof sketch are in
`formal/replay_sufficiency_theorem.md`.

## Claim

For a single-hart RV32I embedded firmware run, a replay capsule is sufficient to
reproduce a target safety-property violation when it contains:

- The exact firmware image identity and platform semantic profile.
- The exact initial architectural state, or reset inputs sufficient to derive it.
- Every nondeterministic boundary event that can influence the architectural
  trace before the target violation.
- Exact commit-index and same-index order for those events.
- The target safety-property violation signature.

Under those conditions, replaying the firmware with the recorded event stream
reconstructs the same architectural trace prefix and therefore reaches the same
violation signature.

## Theorem

Let `R` be an original execution of firmware image `F` from initial
architectural state `A0` on platform profile `P`. Let `C` be a replay capsule
whose image identity, platform profile, initial state, and boundary event prefix
match `R` through target point `t`.

Assume:

- The RV32I core and platform semantics are deterministic between boundary
  events.
- Interrupts are precise and are represented at commit-index boundaries.
- MMIO read values, external memory writes, reset inputs, and other external
  inputs that can affect the trace are captured exactly.
- MMIO writes are replay-visible observations and are validated against the
  original run.
- The safety property is a deterministic predicate over the captured
  architectural trace and boundary observations.

Then replaying `F` from `A0` under `P` with capsule `C` produces a replay run
`R'` that is replay-equivalent to `R` through `t`. In particular, if `R`
produces violation signature `S` at `t`, then `R'` also produces `S` at `t`.

## Proof Sketch

The proof is by induction over the ordered architectural transitions in the
prefix through the target violation.

Base case: the capsule fixes the firmware identity, platform profile, and
initial architectural state, so the original and replay states are equal before
the first transition.

Inductive step: assume the original and replay states are equal immediately
before the next transition.

- For an ordinary instruction using only registers, CSRs, immutable image bytes,
  and RAM, deterministic core semantics produce the same next state.
- For an MMIO read, the equal pre-state implies the same access address, width,
  and instruction context. The capsule supplies the same returned value and any
  required replay-visible side effect, so the next state is the same.
- For an MMIO write, the equal pre-state implies the same write address, width,
  and data. Replay validates the observation, and any later device effect must
  appear as its own recorded event.
- For an interrupt boundary, the same recorded line/delivery event and the same
  CSR state cause the same trap-entry decision and architectural trap effects.
- For an external memory write or other external input, the recorded event
  applies the same architectural state transformation at the same commit-index
  position.

Thus equality is preserved transition by transition. Since the safety checker is
deterministic over the captured trace, the same trace prefix yields the same
target violation signature.

## Limits

This theorem is conditional. It does not prove that the recorder captured every
real-world influence; that is an implementation obligation.

Important limits:

- No cycle-accurate replay is promised. Commit-index time preserves
  architectural ordering, not wall-clock latency.
- Multicore execution, DMA races, and shared-memory concurrency require extra
  event kinds and ordering assumptions.
- Device internals are not reconstructed unless their state becomes
  replay-visible through recorded events.
- Undefined, unspecified, or implementation-defined behavior must be excluded
  or fixed by the platform profile.
- Safety properties that depend on analog values, physical time, hidden device
  state, or host-side state outside the trace are not covered.
- If logging perturbs the original execution, the theorem applies to the
  recorded execution and its event sequence, not to a hypothetical uninstrumented
  run.
- Self-modifying code or executable RAM is allowed only when those bytes are
  part of architectural RAM state and all external mutations are captured.

The useful takeaway is narrow but strong: once the platform contract and event
capture are correct, replay does not need full device simulation. It needs the
same architectural starting point and the same ordered boundary facts.
