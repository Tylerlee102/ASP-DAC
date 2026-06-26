# Table 4. Event-Sufficiency Ablation Summary

Generated from `../../results/processed/event_sufficiency.csv`, `../../results/processed/ablations.csv`, and `../../results/processed/rtl_smoke_event_sufficiency.csv`.

Model rows are commit-index replay ablations. RTL-smoke rows remove event
classes from exported capsules and rerun the replay comparator; they are not
full benchmark-wide RTL replay.

| Benchmark | Model required classes | RTL-smoke required classes | Model event-removal ablations that break replay |
| --- | --- | --- | --- |
| Sensor threshold | mmio read values; interrupt timing | pc context; branch events; mmio read values | mmio read; interrupt timing |
| Interrupt race | interrupt timing | pc context; mmio write observations; interrupt timing | interrupt timing |
| MMIO ordering | property fail pc and mmio context only | pc context; mmio write observations | none observed in event-removal rows |
| Stack corruption | store events | pc context; store events | store |
| UART command | branch events; mmio read values; external input values | pc context; branch events; mmio read values; mmio write observations | branch; mmio read; external input |
| Watchdog timeout | mmio read values; interrupt timing | pc context; branch events; mmio read values | mmio read; interrupt timing |
