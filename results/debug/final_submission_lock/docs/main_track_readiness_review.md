# Main-Track Readiness Review

Evidence basis: CI run latest successful final-reproduce run on master, artifact `replaycapsule-rv-final-evidence` id `see GitHub Actions artifact metadata`.

## Hardware architecture reviewer

- score: weak accept
- strengths: clean recorder decomposition; selected v2 replay-critical mapped profile is now present.
- weaknesses: diagnostic-rich record-side overhead is substantial.
- fatal blockers: none.
- required edits before submission: keep minimal recorder and diagnostic rows separate.
- final recommendation: weak accept.

## EDA/synthesis reviewer

- score: weak accept
- strengths: same-target ECP5 baseline and ReplayCapsule rows pass P&R; Nangate45 OpenROAD placed/global-routed area, timing, and power rows are present.
- weaknesses: no detailed-route signoff, tapeout, or silicon energy result.
- fatal blockers: none.
- required edits before submission: state target, flow, memory, board IO constraints, and global-route-only ASIC scope.
- final recommendation: weak accept.

## Systems/debug reviewer

- score: accept
- strengths: compiler-backed full RTL replay, captured-store self-replay handoff, and corruption rejection are strong.
- weaknesses: reset orchestration and memory/peripheral shell remain harness-scoped.
- fatal blockers: none.
- required edits before submission: make the board/silicon replay boundary prominent.
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
