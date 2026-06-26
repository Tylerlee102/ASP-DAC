# Table 4. Event-Sufficiency Ablation Summary

Generated from `../../results/processed/event_sufficiency.csv` and `../../results/processed/ablations.csv`.

Rows are model-level ablation evidence until firmware-running RTL traces exist.

| Benchmark | Evidence level | Required event classes | Event-removal ablations that break replay |
| --- | --- | --- | --- |
| Sensor threshold | model | mmio read values; interrupt timing | mmio read; interrupt timing |
| Interrupt race | model | interrupt timing | interrupt timing |
| MMIO ordering | model | property fail pc and mmio context only | none observed in event-removal rows |
| Stack corruption | model | store events | store |
| UART command | model | branch events; mmio read values; external input values | branch; mmio read; external input |
| Watchdog timeout | model | mmio read values; interrupt timing | mmio read; interrupt timing |
