# Artifact Evaluation Notes

## One-command Path

The current local entry point is:

```sh
python scripts/run_all_tests.py
```

`scripts/reproduce_all.sh` wraps the same flow for Unix-like shells.

## Expected Tooling

Required now:

- Python 3.9 or newer

Required for later RTL/synthesis gates:

- Verilator
- Yosys
- a RISC-V bare-metal compiler toolchain
- optionally OpenROAD or vendor FPGA tools

If these tools are absent, scripts must report unavailable steps as TODO/NA.

## Result Integrity

No paper result should be manually typed into a figure or summary table. Results must flow from generated raw artifacts to `results/processed/summary.csv` and then to figures.

