# evaluation_agent Plan

Owned files:

- `docs/experimental_methodology.md`
- `scripts/run_replay_experiments.py`
- `scripts/synth_yosys.py`
- `scripts/parse_synthesis_reports.py`
- `scripts/make_figures.py`
- `results/processed/summary.csv`

Mission:

Create a result pipeline that only emits measured results. Local missing tools such as Yosys, OpenROAD, or Verilator must become explicit TODO/NA fields.

Metrics:

- replay success rate
- capsule size
- trace reduction ratio
- LUT/FF/BRAM overhead
- Fmax before/after
- runtime slowdown
- cycles to failure
- events per kilo-instruction
- buffer overflow rate
- false and missed property failures

