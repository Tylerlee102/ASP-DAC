# RV32I Firmware Simulation Evidence

`scripts/rv32i_firmware_sim.py` is a lightweight RV32I execution harness for the benchmark suite.

It is not an RTL simulator and it is not a substitute for PicoRV32/Verilator. Its purpose is to move the project beyond source-only firmware intent by executing real RV32I instruction encodings for the six benchmark programs and exporting ReplayCapsule-style event evidence.

## What It Executes

The harness builds small RV32I programs for:

- `sensor_threshold_bug`
- `interrupt_race_bug`
- `mmio_ordering_bug`
- `stack_corruption_bug`
- `uart_command_bug`
- `watchdog_timeout_bug`

The implemented instruction subset is the subset used by these programs:

- `lui`
- `addi`
- `lw`
- `sw`
- `beq`
- `bne`
- `blt`
- `jal`
- `add`
- `ebreak`

## What It Records

The interpreter records:

- `EV_COMMIT`
- `EV_BRANCH`
- `EV_JUMP`
- `EV_STORE`
- `EV_LOAD`
- `EV_MMIO_READ`
- `EV_MMIO_WRITE`
- `EV_INTERRUPT_ENTER`
- `EV_INTERRUPT_EXIT`
- `EV_EXTERNAL_INPUT`
- `EV_PROPERTY_FAIL`

It writes:

- `results/raw/firmware_sim_traces.json`
- `results/processed/firmware_sim_replay.csv`

`results/raw/firmware_sim_traces.json` includes the firmware instruction words used for each benchmark.

## Evidence Level

Rows marked `firmware-sim` prove that benchmark firmware programs can be encoded as RV32I words, executed by the local interpreter, and replay-compared under commit-index evidence.

Rows marked `firmware-sim` do not prove that PicoRV32 firmware-running RTL simulation passes. The current HDL checks include five PicoRV32 wrapper smokes for selected failing images; full benchmark-wide firmware-running RTL replay remains pending.
