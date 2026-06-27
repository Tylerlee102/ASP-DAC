# Event-Sufficiency Matrix

Generated from `../../results/processed/event_sufficiency_matrix.csv`.

Rows marked required are sufficient-evidence observations at the named evidence level, not a global minimality proof.

| Benchmark | Evidence level | Required core events | Diagnostic-only/optional observed | TODO/BLOCKED classes |
| --- | --- | --- | --- | --- |
| sensor_threshold_bug | model | MMIO read; interrupt enter | branch/jump; load/store; external input; checkpoint/hash | commit; MMIO write; interrupt exit; property fail; diagnostic PC context |
| sensor_threshold_bug | rtl-smoke | branch/jump; MMIO read; diagnostic PC context | load/store; MMIO write; interrupt enter; external input; checkpoint/hash | commit; interrupt exit; property fail |
| sensor_threshold_bug | firmware-sim | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| sensor_threshold_bug | full-rtl | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| interrupt_race_bug | model | interrupt enter | branch/jump; load/store; MMIO read; external input; checkpoint/hash | commit; MMIO write; interrupt exit; property fail; diagnostic PC context |
| interrupt_race_bug | rtl-smoke | MMIO write; interrupt enter; diagnostic PC context | branch/jump; load/store; MMIO read; external input; checkpoint/hash | commit; interrupt exit; property fail |
| interrupt_race_bug | firmware-sim | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| interrupt_race_bug | full-rtl | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| mmio_ordering_bug | model | none observed | branch/jump; load/store; MMIO read; interrupt enter; external input; checkpoint/hash | commit; MMIO write; interrupt exit; property fail; diagnostic PC context |
| mmio_ordering_bug | rtl-smoke | MMIO write; diagnostic PC context | branch/jump; load/store; MMIO read; interrupt enter; external input; checkpoint/hash | commit; interrupt exit; property fail |
| mmio_ordering_bug | firmware-sim | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| mmio_ordering_bug | full-rtl | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| stack_corruption_bug | model | load/store | branch/jump; MMIO read; interrupt enter; external input; checkpoint/hash | commit; MMIO write; interrupt exit; property fail; diagnostic PC context |
| stack_corruption_bug | rtl-smoke | load/store; diagnostic PC context | branch/jump; MMIO read; MMIO write; interrupt enter; external input; checkpoint/hash | commit; interrupt exit; property fail |
| stack_corruption_bug | firmware-sim | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| stack_corruption_bug | full-rtl | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| uart_command_bug | model | branch/jump; MMIO read; external input | load/store; interrupt enter; checkpoint/hash | commit; MMIO write; interrupt exit; property fail; diagnostic PC context |
| uart_command_bug | rtl-smoke | branch/jump; MMIO read; MMIO write; diagnostic PC context | load/store; interrupt enter; external input; checkpoint/hash | commit; interrupt exit; property fail |
| uart_command_bug | firmware-sim | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| uart_command_bug | full-rtl | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| watchdog_timeout_bug | model | MMIO read; interrupt enter | branch/jump; load/store; external input; checkpoint/hash | commit; MMIO write; interrupt exit; property fail; diagnostic PC context |
| watchdog_timeout_bug | rtl-smoke | branch/jump; MMIO read; diagnostic PC context | load/store; MMIO write; interrupt enter; external input; checkpoint/hash | commit; interrupt exit; property fail |
| watchdog_timeout_bug | firmware-sim | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
| watchdog_timeout_bug | full-rtl | none observed | none observed | commit; branch/jump; load/store; MMIO read; MMIO write; interrupt enter; interrupt exit; external input; property fail; checkpoint/hash; diagnostic PC context |
