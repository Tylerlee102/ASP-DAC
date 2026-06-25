# ablation_agent Plan

Owned files:

- `docs/ablation_plan.md`
- `scripts/run_ablations.py`

Mission:

Show which event classes are necessary for which bug families. The ablation study must explain failure causes, not only report pass/fail.

Ablations:

- remove branch events
- remove store events
- remove MMIO read values
- remove interrupt timing
- remove external input values
- remove checkpoint hashes
- remove property-aware slicing
- vary capsule buffer size
- vary last-K context window

