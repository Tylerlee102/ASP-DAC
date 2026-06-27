# Artifact Evaluation Notes

Artifact evidence is locked to GitHub Actions run `28280927815`, commit `2c7245f626105fd8c3d4668096cf9cf1223f6481`, artifact `replaycapsule-rv-final-evidence` id `7921838018`.

The package is intentionally conservative: unsupported claims stay out of the paper and docs, and generated CSVs are the authority for numeric results.

## One-Command Paths

Full path:

```sh
make reproduce
```

Short smoke path:

```sh
make quickcheck
```

The strict CI path is `.github/workflows/final-reproduce.yml`.

## Commands Run By `make reproduce`

```sh
make firmware
make verilator-harness
make full-rtl-replay
make full-rtl-negative
make runtime-overhead
make mapped-synth
make paper
make paper-audit
make artifact
```

Additional final checks:

```sh
python3 scripts/run_all_tests.py
python3 scripts/summarize_artifact_manifest.py
python3 scripts/package_artifact.py
```

## Expected Runtime

On the Linux CI image, the final reproduction run completed in a few minutes. Full Verilator replay and mapped synthesis dominate runtime. Local Windows runs may rely on the bundled Python runtime and may not have the same Verilator/Yosys/nextpnr dynamic libraries.

## Expected Outputs

- `paper/main.pdf`
- `dist/replaycapsule-rv-artifact.zip`
- `results/processed/firmware_build.csv`
- `results/processed/full_rtl_replay.csv`
- `results/processed/full_rtl_replay_negative.csv`
- `results/processed/runtime_overhead.csv`
- `results/processed/runtime_overhead_summary.csv`
- `results/processed/mapped_synthesis.csv`
- `results/processed/mapped_overhead.csv`
- `results/processed/mapped_recorder_presence.csv`
- `results/processed/full_core_mapped_summary.csv`
- `results/processed/claim_audit.csv`
- `results/processed/paper_number_audit.csv`
- `results/processed/todo_audit.csv`
- `results/processed/artifact_manifest.csv`
- `docs/final_evidence_lock.md`
- `results/debug/final_submission_lock/`

## Regenerating Evidence

Firmware and replay:

```sh
make firmware
make verilator-harness
make full-rtl-replay
make full-rtl-negative
```

Runtime summaries:

```sh
make runtime-overhead
```

Mapped synthesis and recorder-presence verification:

```sh
make mapped-synth
python3 scripts/check_mapped_recorder_presence.py
```

Paper, tables, figures, and audits:

```sh
python3 scripts/generate_conference_evidence_tables.py
python3 scripts/summarize_evaluation_metrics.py
python3 scripts/render_paper_tables.py
python3 scripts/make_figures.py
make paper
make paper-audit
```

Artifact package:

```sh
python3 scripts/summarize_artifact_manifest.py
python3 scripts/package_artifact.py
```

## Verifying Results

- Firmware rows must be compiler-backed: `firmware_source=compiler_c`.
- Full RTL replay must have `rtl_record_status=PASS`, `replay_status=PASS`, and `final_signature_match=PASS`.
- Negative replay must report `0` unexpected accepts.
- Full-core mapped overhead is claimable only when both full-core board rows PASS on the same target and `mapped_recorder_presence.csv` is PASS.
- `paper/main.pdf` must exist and `paper_build_status.csv` must report PASS.
- Claim, number, and TODO audits must report zero failing rows.
- `artifact_manifest.csv` must have zero required missing files.

## Known Limitations

- Replay consume is host-driven in the Verilator harness; no hardware replay-consume datapath is claimed.
- The scope is single-hart RV32I interrupt/MMIO failures.
- DMA, multicore ordering, cache-coherence behavior, analog device state, and broad platform replay are not claimed.
- No ASIC area or power claim is made.
- The ECP5 implementation is evidence of place-and-route feasibility and overhead, not an area-optimized design.
