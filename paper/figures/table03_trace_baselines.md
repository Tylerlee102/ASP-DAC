# Table 3. Trace-Size Baselines

Generated from `../../results/processed/trace_sizes.csv` and `../../results/processed/rtl_capsule_event_classes.csv`.

Firmware-sim rows compare baselines for the same local interpreter workload. RTL-smoke bytes are exported packet sizes only, not full benchmark-wide replay metrics.

| Benchmark | Full instruction bytes | Snapshot bytes | ReplayCapsule bytes | Capsule / full-instruction | ReplayCapsule replay | RTL-smoke capsule bytes |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Sensor threshold | 144 | 132 | 189 | 1.31x | True (firmware-sim) | 336 |
| Interrupt race | 40 | 132 | 84 | 2.10x | True (firmware-sim) | 63 |
| MMIO ordering | 24 | 132 | 42 | 1.75x | True (firmware-sim) | 42 |
| Stack corruption | 48 | 140 | 42 | 0.88x | True (firmware-sim) | 42 |
| UART command | 48 | 132 | 105 | 2.19x | True (firmware-sim) | 84 |
| Watchdog timeout | 112 | 132 | 147 | 1.31x | True (firmware-sim) | 252 |
