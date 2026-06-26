# Artifact Evaluation Notes

## One-command Path

The current local entry point is:

```sh
python scripts/run_all_tests.py
```

`scripts/reproduce_all.sh` wraps the same flow for Unix-like shells.
On Windows, use:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\reproduce_all.ps1
```

The PowerShell wrapper falls back to the bundled Codex Python runtime when the
ordinary `python` command is only the Windows Store alias.

## Expected Tooling

Required now:

- Python 3.9 or newer

Used when available for generic synthesis and bounded formal evidence:

- Yosys, including workspace-local `yowasp-yosys`
- OSS CAD Suite, including workspace-local Icarus Verilog, `vvp`, and Verilator lint
- SymbiYosys/SMTBMC, including workspace-local `yowasp-sby` and `yowasp-yosys-smtbmc`

Required for later RTL/synthesis gates:

- `make` and a C++ compiler for full Verilator builds
- a RISC-V bare-metal compiler toolchain
- optionally OpenROAD or vendor FPGA tools

Current non-RTL executable evidence:

- event-boundary model: `scripts/replaycapsule_model.py`
- RV32I instruction interpreter: `scripts/rv32i_firmware_sim.py`
- deterministic benchmark image builder: `scripts/build_firmware_images.py`
- replay-comparator negative fixtures: `scripts/run_replay_negative_tests.py`

Current RTL-smoke evidence:

- PicoRV32 wrapper and directed HDL checks: `results/processed/hdl_checks.csv`
- Seeded interrupt reproducibility campaign:
  `results/processed/randomized_interrupt_campaign.csv`
- RTL-smoke capsule export checks: `results/processed/rtl_capsule_exports.csv`
- RTL-smoke capsule event-class breakdown:
  `results/processed/rtl_capsule_event_classes.csv`
- RTL-smoke versus firmware-sim alignment: `results/processed/rtl_firmware_alignment.csv`

Current bounded formal evidence:

- Event-tap, event-classifier/slicer, property-checker, hash-signature,
  MMIO/interrupt logger, register block, replay-control, replay-mismatch,
  capsule-buffer, and recorder checks: `results/processed/formal_checks.csv`
- Reviewer-facing formal coverage packaging:
  `results/processed/formal_coverage.csv` and `docs/formal_coverage_matrix.md`

Current generic synthesis evidence:

- Baseline core, record-side top, and integrated wrapper generic cell counts:
  `results/processed/synthesis.csv`
- Derived generic cell-overhead context, with mapped FPGA fields preserved as
  `NA`: `results/processed/synthesis_overhead.csv`
- Generated paper table source for synthesis/resource reporting:
  `paper/figures/table01_synthesis_resources.md`

If these tools are absent, scripts must report unavailable steps as TODO/NA.
The current local flow can use `.tools/python/bin/yowasp-yosys.exe`,
`.tools/python/bin/yowasp-sby.exe`, and
`.tools/python/bin/yowasp-yosys-smtbmc.exe` when installed outside git tracking,
plus `.tools/oss-cad-suite/oss-cad-suite/` when extracted outside git tracking.

## Result Integrity

No paper result should be manually typed into a figure or summary table. Results must flow from generated raw artifacts to `results/processed/summary.csv` and then to figures.
