# Artifact Evaluation Notes

This artifact is intentionally conservative: unavailable hardware-dependent
measurements are recorded as `TODO`, `BLOCKED`, or `NA`; they are not estimated.

## One-command Path

The current local entry point is:

```sh
make reproduce
```

If `make` is unavailable, run the script directly:

```sh
python3 scripts/run_all_tests.py
```

`scripts/reproduce_all.sh` wraps the same flow for Unix-like shells. On
Windows, use:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\reproduce_all.ps1
```

The PowerShell wrapper falls back to the bundled Codex Python runtime when the
ordinary `python` command is only the Windows Store alias.

## CI, Docker, and Local Commands

Local smoke reproduction:

```sh
make reproduce
```

Blocked full RTL replay status ledger:

```sh
make full-rtl-replay
```

Paper source and build-status check:

```sh
make paper
make paper-audit
```

Artifact package:

```sh
make artifact
```

Docker path:

```sh
docker build -t replaycapsule-rv .
docker run --rm -v "$PWD:/work" -w /work replaycapsule-rv make check-toolchain
docker run --rm -v "$PWD:/work" -w /work replaycapsule-rv make full-rtl-replay-one BENCH=sensor_threshold_bug VARIANT=failing SEED=1
docker run --rm -v "$PWD:/work" -w /work replaycapsule-rv make full-rtl-replay
```

On PowerShell, use `"${PWD}"` if Docker expects the host path as a string.

GitHub Actions path:

- `.github/workflows/final-reproduce.yml` is the strict source-of-truth path
  for missing compiler and LaTeX evidence. It installs Python, make, Git,
  CMake, Verilator, Yosys, nextpnr-ice40, `gcc-riscv64-unknown-elf`,
  `binutils-riscv64-unknown-elf`, LaTeX packages, and zip support.
- The final workflow sets `REQUIRE_COMPILER=1` and `ALLOW_FALLBACK=0`, then
  runs `make check-toolchain`, `make firmware`, `make verilator-harness`,
  `make full-rtl-replay`, `make full-rtl-negative`, `make runtime-overhead`,
  `make mapped-synth`, `make paper`, `make paper-audit`, and `make artifact`.
- The workflow uploads `results/`, `paper/main.pdf`, and
  `dist/replaycapsule-rv-artifact.zip`.

WSL2 path:

```sh
sudo apt-get update
sudo apt-get install -y make g++ python3 verilator iverilog yosys gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf latexmk texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-publishers
make check-toolchain PYTHON=python3
make full-rtl-replay-one PYTHON=python3 BENCH=sensor_threshold_bug VARIANT=failing SEED=1
```

## Expected Runtime

The local smoke path should complete in minutes on a normal workstation when
workspace-local HDL/formal tools are present. Bounded formal checks, the
bounded iCE40 mapped-flow attempt, and full Verilator replay dominate the
runtime. Full RTL replay now writes executable PASS/FAIL rows rather than
tooling blocker rows when the simulator binary is built.

## Expected Outputs

Primary generated ledgers:

- `docs/conference_readiness_dashboard.md`
- `results/processed/summary.csv`
- `results/processed/toolchain_status.csv`
- `results/processed/full_rtl_replay.csv`
- `results/processed/firmware_source_comparison.csv`
- `results/processed/full_rtl_replay_negative.csv`
- `results/processed/runtime_overhead.csv`
- `results/processed/runtime_overhead_summary.csv`
- `results/processed/event_sufficiency_matrix.csv`
- `results/processed/baseline_comparison.csv`
- `results/processed/scaling_workloads.csv`
- `results/processed/buffer_sweep.csv`
- `results/processed/mapped_synthesis.csv`
- `results/processed/mapped_overhead.csv`
- `results/processed/artifact_manifest.csv`
- `dist/replaycapsule-rv-artifact.zip`

Generated figures and paper tables:

- `results/figures/`
- `paper/figures/`
- `paper/figures/table_event_sufficiency.md`

## Regenerating Tables and Figures

Run:

```sh
python3 scripts/generate_conference_evidence_tables.py
python3 scripts/render_paper_tables.py
python3 scripts/make_figures.py
```

The generated Markdown tables identify their source CSVs in the table headers.

## Inspecting Logs

Processed CSVs are in `results/processed/`. Raw HDL, formal, synthesis, and
capsule export artifacts are in `results/raw/`. The artifact manifest records
hashes and source producers for reviewer inspection.

## Smoke Versus Full Tests

Smoke path:

```sh
make rtl-smoke
make firmware-sim
```

Full local gate:

```sh
make reproduce
```

Scoped full RTL replay status (host-driven Verilator; not a mapped or
synthesizable replay-consume claim):

```sh
make full-rtl-replay-one BENCH=sensor_threshold_bug VARIANT=failing SEED=1
make full-rtl-replay
make full-rtl-negative
```

The full RTL replay target builds and runs the host-driven Verilator harness
under `tb/verilator` when `make`, a C++ compiler, and Verilator are available.
The current generated local ledger has 45/45 PASS rows. The full RTL corruption
suite rejects 10 replay-critical corruptions and marks 2 cases as not
applicable in the current commit-index harness. The RISC-V compiler is
unavailable locally; `results/processed/firmware_build.csv` records verified
HEX fallback rows and labels them as fallback, not compiler-backed firmware.
The final CI workflow disables fallback and must produce compiler-backed rows
before the paper may claim compiler-backed replay.

## Verifying Hashes

After `make reproduce`, inspect:

```sh
results/processed/artifact_manifest.csv
dist/artifact_package_manifest.csv
```

Each row records the file path, byte count, and SHA-256 hash.

## Expected Tooling

Required now:

- Python 3.11 or newer for the documented CI/container path

Used when available for generic synthesis and bounded formal evidence:

- Yosys, including workspace-local `yowasp-yosys`
- OSS CAD Suite, including workspace-local Icarus Verilog, `vvp`, and Verilator lint
- SymbiYosys/SMTBMC, including workspace-local `yowasp-sby` and `yowasp-yosys-smtbmc`

Required for RTL/synthesis gates:

- `make` and a C++ compiler for full Verilator builds and replay reruns
- a RISC-V bare-metal compiler toolchain for compiler-backed firmware builds,
  or verified HEX fallback images for harness-loading only
- a placeable FPGA/ASIC mapped flow such as constrained nextpnr, OpenROAD, or
  vendor FPGA tools

Current non-RTL executable evidence:

- event-boundary model: `scripts/replaycapsule_model.py`
- RV32I instruction interpreter: `scripts/rv32i_firmware_sim.py`
- deterministic benchmark image builder: `scripts/build_firmware_images.py`
- replay-comparator negative fixtures: `scripts/run_replay_negative_tests.py`

Current RTL-smoke evidence:

- PicoRV32 wrapper and directed HDL checks: `results/processed/hdl_checks.csv`
- PicoRV32 wrapper smoke observed capsule summaries:
  `results/processed/picorv32_smoke_summary.csv` and
  `results/processed/picorv32_smoke_coverage.csv`
- Seeded interrupt reproducibility campaign:
  `results/processed/randomized_interrupt_campaign.csv`
- Seeded interrupt campaign summary and coverage checklist:
  `results/processed/randomized_interrupt_summary.csv` and
  `results/processed/randomized_interrupt_coverage.csv`
- Seeded interrupt corruption-rejection checks:
  `results/processed/randomized_interrupt_corruption.csv`
- RTL-smoke capsule export checks: `results/processed/rtl_capsule_exports.csv`
- RTL-smoke capsule event-class breakdown:
  `results/processed/rtl_capsule_event_classes.csv`
- RTL-smoke event-class ablations:
  `results/processed/rtl_smoke_ablations.csv` and
  `results/processed/rtl_smoke_event_sufficiency.csv`
- RTL-smoke versus firmware-sim alignment: `results/processed/rtl_firmware_alignment.csv`

Current scoped full RTL evidence (host-driven; not mapped or synthesizable
replay-consume evidence):

- Built host-driven Verilator simulator: `build/verilator/replaycapsule_sim.exe`
- Verilator build log: `results/raw/verilator/build.log`
- Full RTL record/replay ledger: `results/processed/full_rtl_replay.csv`
- Firmware source comparison ledger:
  `results/processed/firmware_source_comparison.csv`
- Host-driven full RTL corrupted-capsule ledger, not synthesizable replay-consume evidence:
  `results/processed/full_rtl_replay_negative.csv`
- Pass-4 record/replay debug diffs: `results/debug/pass4/`

Current bounded formal evidence:

- Event-tap, event-classifier/slicer, property-checker, hash-signature,
  MMIO/interrupt logger, register block, replay-control, replay-mismatch,
  capsule-buffer, and recorder checks: `results/processed/formal_checks.csv`
- Reviewer-facing formal coverage packaging:
  `results/processed/formal_coverage.csv` and `docs/formal_coverage_matrix.md`
- Replay-sufficiency proof-obligation packaging:
  `results/processed/proof_obligations.csv` and
  `docs/proof_obligation_matrix.md`
- Bounded overflow contract packaging:
  `results/processed/overflow_contracts.csv`

Current generic synthesis evidence:

- Baseline core, record-side top, and integrated wrapper generic cell counts:
  `results/processed/synthesis.csv`
- Derived generic cell-overhead context, with mapped FPGA fields preserved as
  `NA`: `results/processed/synthesis_overhead.csv`
- Attempted iCE40 mapped-flow status, currently with scoped tiny baseline and
  recorder PASS rows plus full-core placement failures:
  `results/processed/mapped_synthesis.csv` and
  `results/processed/mapped_overhead.csv`
- Current-harness runtime wall-clock rows and baseline-overhead blockers:
  `results/processed/runtime_overhead.csv` and
  `results/processed/runtime_overhead_summary.csv`
- Generated metric rollup, with blocked hardware metrics preserved as `TODO`,
  `BLOCKED`, or `NA`:
  `results/processed/evaluation_metrics.csv`
- Generated per-benchmark local evidence coverage ledger:
  `results/processed/benchmark_coverage.csv`
- Generated claim audit for high-risk paper/reviewer wording:
  `results/processed/claim_audit.csv`
- Generated paper number and TODO/citation audits:
  `results/processed/paper_number_audit.csv` and
  `results/processed/todo_audit.csv`
- Generated toolchain status ledger:
  `results/processed/toolchain_status.csv`
- Generated artifact hash manifest for the main local evidence files:
  `results/processed/artifact_manifest.csv`
- Generated paper table source for synthesis/resource reporting:
  `paper/figures/table01_synthesis_resources.md`
- Generated paper table sources for replay evidence, trace-size baselines,
  event-sufficiency ablations, bounded formal coverage, proof obligations, and
  metric rollup:
  `paper/figures/table02_replay_evidence.md` through
  `paper/figures/table07_evaluation_metrics.md`
- Generated conference event-sufficiency matrix table:
  `paper/figures/table_event_sufficiency.md`

If these tools are absent, scripts must report unavailable steps as TODO/NA.
The current local flow can use `.tools/python/bin/yowasp-yosys.exe`,
`.tools/python/bin/yowasp-sby.exe`, and
`.tools/python/bin/yowasp-yosys-smtbmc.exe` when installed outside git tracking,
plus `.tools/oss-cad-suite/oss-cad-suite/` when extracted outside git tracking.

## Result Integrity

No paper result should be manually typed into a figure or summary table. Results must flow from generated raw artifacts to `results/processed/summary.csv`, `results/processed/artifact_manifest.csv`, and then to figures.

## Known Limitations

- Full firmware-running RTL replay is host-driven in the Verilator harness and
  uses verified HEX fallback images, not compiler-backed firmware or a
  synthesizable replay-consume datapath.
- Full-core mapped FPGA or ASIC area/timing overhead rows remain unavailable
  until comparable full-core baseline and ReplayCapsule mapped flows produce
  PASS reports. The current iCE40 evidence is limited to scoped tiny wrappers.
- Runtime overhead and perturbation measurements remain unavailable until a
  comparable baseline core wrapper or recorder-disabled top exists. Current
  rows measure only recorder-enabled host simulation wall-clock time.
- The current theorem is a written conditional argument plus generated evidence
  mapping, not a mechanized end-to-end processor/replay proof.
