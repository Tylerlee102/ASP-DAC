# ReplayCapsule-RV

ReplayCapsule-RV is a research prototype for event-sufficient hardware failure capsules for replaying embedded single-hart RV32I interrupt/MMIO bugs.

The current locked evidence comes from GitHub Actions run `28278972828`, commit `6b5bf98676e62bc39ddcecaf0d543f8a2a9dc1ad`, artifact `replaycapsule-rv-final-evidence` id `7921197214`.

## Main Evidence

- Compiler-backed firmware: `15/15` PASS in `results/processed/firmware_build.csv`.
- Full RTL replay: `45/45` PASS in `results/processed/full_rtl_replay.csv`.
- Full RTL negative replay: `10` replay-critical corruptions rejected, `0` unexpected accepts, `2` not-applicable rows in `results/processed/full_rtl_replay_negative.csv`.
- Runtime summaries: baseline, recorder-present-disabled, and recorder-enabled rows in `results/processed/runtime_overhead_summary.csv`.
- Full-core mapped overhead: PASS on `ecp5-85k` using `yosys+synth_ecp5+nextpnr-ecp5`.
- Recorder presence: PASS in `results/processed/mapped_recorder_presence.csv`.
- Paper build and audits: PASS in `results/processed/paper_build_status.csv`, `claim_audit.csv`, `paper_number_audit.csv`, and `todo_audit.csv`.
- Artifact package: `dist/replaycapsule-rv-artifact.zip`.

## Quick Start

Full reproduction path:

```sh
make reproduce
```

Short smoke path:

```sh
make quickcheck
```

The strict CI path is `.github/workflows/final-reproduce.yml`. It installs the compiler, Verilator, Yosys, nextpnr, LaTeX, and packaging tools, then runs the final evidence flow.

## Reproduction Targets

`make reproduce` calls:

- `make firmware`
- `make verilator-harness`
- `make full-rtl-replay`
- `make full-rtl-negative`
- `make runtime-overhead`
- `make mapped-synth`
- `make paper`
- `make paper-audit`
- `make artifact`

Useful focused commands:

```sh
make mapped-synth
make paper
make paper-audit
make artifact
python3 scripts/run_all_tests.py
python3 scripts/summarize_artifact_manifest.py
python3 scripts/package_artifact.py
```

On Windows, the PowerShell wrapper can use the bundled Codex Python runtime when the ordinary `python` command is only the Windows Store alias:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\reproduce_all.ps1
```

## Expected Outputs

- `paper/main.pdf`
- `dist/replaycapsule-rv-artifact.zip`
- `results/processed/full_rtl_replay.csv`
- `results/processed/full_rtl_replay_negative.csv`
- `results/processed/runtime_overhead.csv`
- `results/processed/runtime_overhead_summary.csv`
- `results/processed/mapped_synthesis.csv`
- `results/processed/mapped_overhead.csv`
- `results/processed/mapped_recorder_presence.csv`
- `results/processed/full_core_mapped_summary.csv`
- `results/processed/artifact_manifest.csv`
- `docs/final_evidence_lock.md`
- `results/debug/final_submission_lock/`

## Mapped FPGA Evidence

The full-core board-level mapped rows use the same target, flow, memory size, clock/reset assumptions, and realistic board-level I/O.

| Design | Target | LUT | FF | BRAM | Fmax MHz |
| --- | --- | ---: | ---: | ---: | ---: |
| `full_core_baseline_board` | `ecp5-85k` | 2814 | 883 | 6 | 63.47 |
| `full_core_replaycapsule_board` | `ecp5-85k` | 6859 | 3901 | 6 | 50.70 |

The measured full-core mapped overhead is LUT `143.75%`, FF `341.79%`, BRAM `0.00%`, and Fmax delta `-20.12%`. The prototype prioritizes replay fidelity and auditability over area minimization.

## Scope

Allowed claims:

- Event-sufficient capsules for scoped single-hart RV32I interrupt/MMIO failures.
- Compiler-backed host-driven full RTL replay for the generated benchmark suite.
- Full RTL corrupted-capsule rejection for replay-critical corruption classes.
- Runtime summaries and same-target full-core ECP5 mapped overhead.

Forbidden claims:

- ASIC area or power.
- Hardware replay-consume datapath.
- Multicore, DMA, cache-coherent, or broad platform support.
- Replacement for RISC-V trace/debug standards.
- Globally smallest trace or universal deterministic replay.

## Main Directories

- `rtl/`: ReplayCapsule RTL modules and mapped board wrappers.
- `firmware/`: compiler-built firmware benchmarks.
- `tb/`: Verilator and replay-comparator harnesses.
- `scripts/`: reproduction, audit, table, figure, synthesis, and packaging scripts.
- `paper/`: IEEE-style paper source and generated table/figure assets.
- `docs/`: reviewer-facing model, evidence, limitation, and submission docs.
- `results/processed/`: generated CSV evidence.
