# baseline_agent Plan

Owned files:

- `docs/baselines.md`
- `scripts/collect_trace_sizes.py`

Mission:

Define strong baselines and implement trace-size collection over real artifacts when present.

Baselines:

- full instruction trace
- full commit trace
- branch-only trace
- store-only trace
- MMIO-only trace
- interrupt + MMIO trace
- snapshot-on-failure baseline
- property-aware ReplayCapsule-RV

Output must include replay success, trace bytes, events per kilo-instruction, failure reproduction accuracy, and whether overhead is RTL-backed or simulator-only. Missing artifacts are reported as TODO/NA, not guessed.

