# Conference Readiness Dashboard

This file is the single source of truth for ReplayCapsule-RV submission readiness. A gate is marked `PASS`, `PARTIAL`, `TODO`, or `BLOCKED` only. Rows point to generated evidence or an exact blocker; missing measurements stay unavailable until a script or tool run produces them.

Last updated: 2026-06-26.

Top blocker: Mapped FPGA/ASIC resource/timing evidence and paper PDF build remain unavailable locally; full RTL record/replay is now all-PASS for the evaluated rows.

Format note: the ASP-DAC 2026 technical-paper preparation guide
(`https://www.aspdac.com/aspdac2026/author-information/`) states that
initial submissions must use IEEE style and that accepted camera-ready papers
may follow a different proceedings path. The paper source therefore uses
`IEEEtran` for the current initial-submission gate.

| Gate | Required for submission? | Current status | Evidence file/script | Pass condition | Owner | Blocker |
| --- | --- | --- | --- | --- | --- | --- |
| G1. One-command reproduction | Yes | PARTIAL | `make reproduce`; `scripts/reproduce_all.ps1`; `scripts/run_all_tests.py`; `results/processed/summary.csv` | One command regenerates all claimed local evidence and records unavailable gates without silent skips. | Reproducibility | The Verilator replay simulator builds locally and full RTL replay is all-PASS; full submission reproduction still lacks mapped PASS rows, compiler-backed firmware, and local paper PDF build. |
| G2. Full benchmark list | Yes | PASS | `firmware/bug_*`; `scripts/replaycapsule_model.py`; `results/processed/benchmark_coverage.csv` | Six benchmark families have failing/fixed firmware, model IDs, and generated coverage rows. | Benchmarks | None. |
| G3. Model-level replay | Yes | PASS | `scripts/run_replay_experiments.py`; `results/processed/replay_experiments.csv` | Every benchmark has generated model replay PASS rows. | Replay | None. |
| G4. Firmware-sim replay | Yes | PASS | `scripts/rv32i_firmware_sim.py`; `results/processed/firmware_sim_replay.csv`; `results/raw/firmware_sim_traces.json` | Every benchmark has generated RV32I interpreter replay PASS rows. | Firmware | None. |
| G5. Firmware-running RTL replay | Yes | PASS | `tb/verilator/`; `scripts/run_full_rtl_replay.py`; `results/processed/full_rtl_replay.csv`; `results/raw/verilator/build.log`; `results/debug/pass4/` | Record run produces a capsule, replay run consumes it, and all six benchmark families pass exact property/event/signature comparison at RTL. | RTL Replay | None for evaluated host-driven Verilator record/replay rows: 45/45 rows are PASS. RISC-V compiler is unavailable locally; firmware rows use verified HEX fallback images, not compiler-backed firmware. |
| G6. RTL capsule export | Yes | PASS | `scripts/export_rtl_capsules.py`; `results/processed/rtl_capsule_exports.csv`; `results/processed/full_rtl_replay.csv`; `results/raw/rtl_capsules/*.json`; `tb/verilator/` | Full RTL record flow exports capsules for all required variants. | RTL Replay | None for evaluated rows; full RTL record export is PASS for all 45 benchmark/variant/seed rows. |
| G7. RTL replay comparator | Yes | PASS | `tb/replay_testbench/replay_compare.py`; `tb/verilator/`; `results/processed/rtl_capsule_exports.csv`; `results/processed/full_rtl_replay.csv` | RTL replay consumes exported capsules and rejects missing, duplicate, reordered, and corrupted events. | Replay | None for evaluated rows; full RTL replay exact comparison is PASS for all 45 rows. |
| G8. Negative/corruption tests | Yes | PASS | `scripts/run_replay_negative_tests.py`; `scripts/run_full_rtl_negative.py`; `results/processed/replay_negative_tests.csv`; `results/processed/full_rtl_replay_negative.csv` | Required corruptions fail at the strongest claimed evidence level. | Verification | Full RTL corruption rows now run: 10 replay-critical corruptions reject and 2 cases are not applicable in the current commit-index harness. |
| G9. Event-sufficiency ablations | Yes | PARTIAL | `scripts/run_ablations.py`; `scripts/run_rtl_smoke_ablations.py`; `scripts/generate_conference_evidence_tables.py`; `results/processed/event_sufficiency_matrix.csv`; `paper/figures/table_event_sufficiency.md` | Every required event class is ablated for each benchmark at the strongest claimed evidence level. | Evaluation | Firmware-sim and full RTL event-removal ablations remain unavailable. |
| G10. Baseline trace-size comparison | Yes | PARTIAL | `scripts/collect_trace_sizes.py`; `scripts/generate_conference_evidence_tables.py`; `results/processed/baseline_comparison.csv` | Full instruction, commit, control-flow, store/output, MMIO, interrupt, snapshot, core-only capsule, and property-aware capsule baselines are measured and labeled by evidence level. | Evaluation | Core-only capsule and full RTL-backed baseline rows are unavailable; mapped/full RTL evidence cannot be inferred from model rows. |
| G11. Formal/BMC coverage | Yes | PASS | `scripts/run_formal_checks.py`; `scripts/summarize_formal_coverage.py`; `results/processed/formal_checks.csv`; `results/processed/formal_coverage.csv`; `docs/formal_coverage_matrix.md` | Bounded local RTL contracts run and report PASS/TODO honestly. | Formal | None for bounded local checks; not an end-to-end mechanized theorem. |
| G12. RTL lint/simulation | Yes | PASS | `scripts/run_hdl_checks.py`; `results/processed/hdl_checks.csv`; `results/processed/picorv32_smoke_summary.csv` | Directed module simulations, wrapper smokes, and lint-only checks pass or record missing tools. | RTL | None for the current local smoke scope. |
| G13. Mapped synthesis/resource/timing | Yes | BLOCKED | `scripts/run_mapped_synthesis.py`; `results/processed/mapped_synthesis.csv`; `results/processed/mapped_overhead.csv`; `results/raw/mapped_synthesis/` | A real FPGA or ASIC mapped flow produces resource/timing reports for baseline core, recorder, and wrapper. | Hardware | Yosys + nextpnr-ice40 was attempted. All three iCE40 place-and-route rows are `FAIL` because the selected target/top-level interface cannot place; no mapped PASS rows or overhead numbers exist. |
| G14. Runtime overhead / perturbation | Yes | BLOCKED | `results/processed/evaluation_metrics.csv`; `results/processed/full_rtl_replay.csv` | Runtime slowdown or perturbation is measured by a script on firmware-running RTL or hardware. | Evaluation | Full RTL replay is now all-PASS, but no script-backed runtime slowdown or perturbation rows are measured yet. |
| G15. Claim audit | Yes | PASS | `scripts/audit_claims.py`; `results/processed/claim_audit.csv` | Uncaveated high-risk claim phrases fail the audit. | Paper | None after current audit pass. |
| G16. Paper build | Yes | TODO | `paper/main.tex`; `paper/references.bib`; `scripts/build_paper.py`; `results/processed/paper_build_status.csv` | `paper/main.pdf` is generated by LaTeX and paper audits pass. | Paper | Local LaTeX may be unavailable; build status CSV records the exact state. |
| G17. ASP-DAC/IEEE format compliance | Yes | PARTIAL | `paper/main.tex`; `.github/workflows/reproduce.yml`; current ASP-DAC 2026 preparation guide checked on 2026-06-26 | Paper source uses IEEE conference style for initial-submission compatibility and compiles under the configured CI/container toolchain. | Paper | PDF build and page-count verification still depend on LaTeX build success. |
| G18. Artifact evaluation instructions | Yes | PASS | `artifact_evaluation.md`; `scripts/package_artifact.py`; `dist/replaycapsule-rv-artifact.zip` | Reviewer can run local/CI/container commands, inspect outputs, verify hashes, and package the artifact without private paths. | Artifact | None for instructions/package generation; full RTL/mapped gates remain explicit limitations. |

## Submission Decision

Current status: NOT READY.

Fatal before submission:

- Compiler-backed firmware is still unavailable; current full RTL rows use verified HEX fallback images.
- G13 mapped synthesis/resource/timing has real nextpnr FAIL rows and no PASS resource/timing report.
- G14 runtime overhead / perturbation has no measured rows.
- G16 paper PDF build is not yet a local PASS.

Allowed evidence claims:

- Model and firmware-sim replay across the six benchmark families.
- RTL-smoke capsule export, corruption rejection, and firmware-sim alignment.
- Bounded local formal checks and generic Yosys cell-count context.
- ReplayCapsule-RV produced firmware-running RTL record/replay agreement for all evaluated benchmark/variant/seed rows in the current single-hart RV32I host-driven Verilator harness.

Disallowed evidence claims:

- Compiler-backed firmware builds.
- FPGA/ASIC mapped LUT, FF, BRAM, timing, power, or runtime overhead.
- Synthesizable hardware replay-consume datapath.
- Global minimality, full-system replay, multicore/DMA support, or replacement for trace standards.
