# Table 2. Replay Evidence Status

Generated from `../../results/processed/replay_experiments.csv` and `../../results/processed/rtl_firmware_alignment.csv`.

Model and firmware-sim rows are commit-index replay checks. RTL-smoke rows are property/key-event alignment checks, not full benchmark-wide RTL replay.

| Benchmark | Model replay | Firmware-sim replay | RTL-smoke property alignment | RTL-smoke key-event alignment | Property ID |
| --- | --- | --- | --- | --- | --- |
| Sensor threshold | PASS (model) | PASS (firmware-sim) | PASS (rtl-smoke) | PASS (rtl-smoke) | P3_SENSOR_DEADLINE |
| Interrupt race | PASS (model) | PASS (firmware-sim) | PASS (rtl-smoke) | PASS (rtl-smoke) | P2_INTERRUPT_CRITICAL |
| MMIO ordering | PASS (model) | PASS (firmware-sim) | PASS (rtl-smoke) | PASS (rtl-smoke) | P5_MMIO_ORDERING |
| Stack corruption | PASS (model) | PASS (firmware-sim) | PASS (rtl-smoke) | PASS (rtl-smoke) | P4_STACK_PROTECT |
| UART command | PASS (model) | PASS (firmware-sim) | PASS (rtl-smoke) | PASS (rtl-smoke) | P1_ACTUATOR_LIMIT |
| Watchdog timeout | PASS (model) | PASS (firmware-sim) | PASS (rtl-smoke) | PASS (rtl-smoke) | P6_WATCHDOG_TIMEOUT |
| Full firmware-running RTL suite | TODO (rtl) | TODO (rtl) | NA | NA | requires PicoRV32/Verilator/RISC-V toolchain artifacts |
