# Main-Track Submission Review

Evidence basis: CI run 28280927815, artifact `replaycapsule-rv-final-evidence` id `7921838018`.

## Hardware architecture reviewer

- score: weak accept
- strengths: clean recorder decomposition; full-core ECP5 mapping is now present.
- weaknesses: record-side overhead is substantial.
- fatal blockers: none.
- required edits before submission: keep overhead discussion honest.
- final recommendation: weak accept.

## EDA/synthesis reviewer

- score: weak accept
- strengths: same-target ECP5 baseline and ReplayCapsule rows pass P&R.
- weaknesses: no ASIC area or power.
- fatal blockers: none.
- required edits before submission: state target, flow, memory, and board IO constraints.
- final recommendation: weak accept.

## Systems/debug reviewer

- score: accept
- strengths: compiler-backed full RTL replay and corruption rejection are strong.
- weaknesses: host-driven replay consume path.
- fatal blockers: none.
- required edits before submission: make host-driven scope prominent.
- final recommendation: accept.

## Formal/replay model reviewer

- score: borderline
- strengths: commit-index model and proof obligations are clear.
- weaknesses: no mechanized end-to-end processor proof.
- fatal blockers: none.
- required edits before submission: frame theorem as conditional model support.
- final recommendation: borderline.

## Artifact evaluation reviewer

- score: accept
- strengths: CI artifact, paper build, audits, and package are available.
- weaknesses: local Windows toolchain may not reproduce every Linux CI step.
- fatal blockers: none.
- required edits before submission: document CI and Docker paths.
- final recommendation: accept.

## Skeptical novelty reviewer

- score: borderline
- strengths: narrow trace/debug distinction is defensible.
- weaknesses: deterministic replay and tracing are crowded areas.
- fatal blockers: none.
- required edits before submission: lean on event-sufficient scoped failure class.
- final recommendation: borderline.

## Overall

No reviewer identifies a remaining fatal blocker in the locked evidence. The submission should be treated as main-track ready if the paper remains scoped and the artifact is shipped with the locked CI evidence.
