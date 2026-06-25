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

Required for later RTL/synthesis gates:

- Verilator
- Yosys
- a RISC-V bare-metal compiler toolchain
- optionally OpenROAD or vendor FPGA tools

Current non-RTL executable evidence:

- event-boundary model: `scripts/replaycapsule_model.py`
- RV32I instruction interpreter: `scripts/rv32i_firmware_sim.py`
- deterministic benchmark image builder: `scripts/build_firmware_images.py`

If these tools are absent, scripts must report unavailable steps as TODO/NA.

## Result Integrity

No paper result should be manually typed into a figure or summary table. Results must flow from generated raw artifacts to `results/processed/summary.csv` and then to figures.
