# Second-Core v2 Replay-Consumer Smokes

Status: `126/126` rows PASS.

These scoped Icarus rows run the FemtoRV32 v2 wrapper on compiler-built base and expanded benchmark firmware, record a v2 MMIO/property stream, reset the wrapped core, perturb replay-side host MMIO inputs, and require the v2 replay consumer to consume the captured stream while reproducing the recorded property signature.

- Benchmarks covered: `14` (commanded_actuator_limit_bug, environmental_controller_bug, interrupt_race_bug, late_config_sequence_bug, mmio_ordering_bug, platform2_config_order_bug, platform2_status_window_bug, power_rail_sequencer_bug, sensor_debounce_bug, sensor_threshold_bug, stack_corruption_bug, status_clear_on_read_bug, uart_command_bug, watchdog_timeout_bug).
- Recorder configs covered: `3` (core, full, hashed).
- Seeds covered: `3` (1, 2, 3).
- Wrapper-level IRQ-boundary rows: `9` PASS.
- Watchdog rows: `9` PASS.
- Replay command perturbation rows: `54` PASS.
- The full diagnostic v2 config uses the same strict-order replay consumer, with the FemtoRV32 core held until the first replay word is preloaded so startup diagnostic events are consumed in order.

| Benchmark | Seed | Config | Status | Property | Words | Consumed | Signature match | Changed sensor | Changed command | Record signature | Replay signature |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| `sensor_threshold_bug` | 1 | `core` | `PASS` | 3 | 2 | 2 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 2 | `core` | `PASS` | 3 | 2 | 2 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 3 | `core` | `PASS` | 3 | 2 | 2 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 1 | `hashed` | `PASS` | 3 | 2 | 2 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 2 | `hashed` | `PASS` | 3 | 2 | 2 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 3 | `hashed` | `PASS` | 3 | 2 | 2 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 1 | `full` | `PASS` | 3 | 42 | 42 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 2 | `full` | `PASS` | 3 | 42 | 42 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `sensor_threshold_bug` | 3 | `full` | `PASS` | 3 | 42 | 42 | `PASS` | `PASS` | `NA` | `5e0500c2` | `5e0500c2` |
| `interrupt_race_bug` | 1 | `core` | `PASS` | 2 | 3 | 3 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 2 | `core` | `PASS` | 2 | 3 | 3 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 3 | `core` | `PASS` | 2 | 3 | 3 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 1 | `hashed` | `PASS` | 2 | 3 | 3 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 2 | `hashed` | `PASS` | 2 | 3 | 3 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 3 | `hashed` | `PASS` | 2 | 3 | 3 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 1 | `full` | `PASS` | 2 | 21 | 21 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 2 | `full` | `PASS` | 2 | 21 | 21 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `interrupt_race_bug` | 3 | `full` | `PASS` | 2 | 21 | 21 | `PASS` | `PASS` | `NA` | `1a1e00c2` | `1a1e00c2` |
| `mmio_ordering_bug` | 1 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 2 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 3 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 1 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 2 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 3 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 1 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 2 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `mmio_ordering_bug` | 3 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `stack_corruption_bug` | 1 | `core` | `PASS` | 4 | 1 | 1 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 2 | `core` | `PASS` | 4 | 1 | 1 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 3 | `core` | `PASS` | 4 | 1 | 1 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 1 | `hashed` | `PASS` | 4 | 1 | 1 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 2 | `hashed` | `PASS` | 4 | 1 | 1 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 3 | `hashed` | `PASS` | 4 | 1 | 1 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 1 | `full` | `PASS` | 4 | 21 | 21 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 2 | `full` | `PASS` | 4 | 21 | 21 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `stack_corruption_bug` | 3 | `full` | `PASS` | 4 | 21 | 21 | `PASS` | `PASS` | `NA` | `8901aefb` | `8901aefb` |
| `uart_command_bug` | 1 | `core` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 2 | `core` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 3 | `core` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 1 | `hashed` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 2 | `hashed` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 3 | `hashed` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 1 | `full` | `PASS` | 1 | 23 | 23 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 2 | `full` | `PASS` | 1 | 23 | 23 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `uart_command_bug` | 3 | `full` | `PASS` | 1 | 23 | 23 | `PASS` | `PASS` | `PASS` | `ac7000e9` | `ac7000e9` |
| `watchdog_timeout_bug` | 1 | `core` | `PASS` | 6 | 2 | 2 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 2 | `core` | `PASS` | 6 | 2 | 2 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 3 | `core` | `PASS` | 6 | 2 | 2 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 1 | `hashed` | `PASS` | 6 | 2 | 2 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 2 | `hashed` | `PASS` | 6 | 2 | 2 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 3 | `hashed` | `PASS` | 6 | 2 | 2 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 1 | `full` | `PASS` | 6 | 36 | 36 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 2 | `full` | `PASS` | 6 | 36 | 36 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `watchdog_timeout_bug` | 3 | `full` | `PASS` | 6 | 36 | 36 | `PASS` | `PASS` | `NA` | `feed00ff` | `feed00ff` |
| `commanded_actuator_limit_bug` | 1 | `core` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 2 | `core` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 3 | `core` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 1 | `hashed` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 2 | `hashed` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 3 | `hashed` | `PASS` | 1 | 3 | 3 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 1 | `full` | `PASS` | 1 | 23 | 23 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 2 | `full` | `PASS` | 1 | 23 | 23 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `commanded_actuator_limit_bug` | 3 | `full` | `PASS` | 1 | 23 | 23 | `PASS` | `PASS` | `PASS` | `ac7000a7` | `ac7000a7` |
| `late_config_sequence_bug` | 1 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 2 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 3 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 1 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 2 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 3 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 1 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 2 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `late_config_sequence_bug` | 3 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `sensor_debounce_bug` | 1 | `core` | `PASS` | 3 | 3 | 3 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 2 | `core` | `PASS` | 3 | 3 | 3 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 3 | `core` | `PASS` | 3 | 3 | 3 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 1 | `hashed` | `PASS` | 3 | 3 | 3 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 2 | `hashed` | `PASS` | 3 | 3 | 3 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 3 | `hashed` | `PASS` | 3 | 3 | 3 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 1 | `full` | `PASS` | 3 | 44 | 44 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 2 | `full` | `PASS` | 3 | 44 | 44 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `sensor_debounce_bug` | 3 | `full` | `PASS` | 3 | 44 | 44 | `PASS` | `PASS` | `NA` | `5e0500fd` | `5e0500fd` |
| `status_clear_on_read_bug` | 1 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 2 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 3 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 1 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 2 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 3 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 1 | `full` | `PASS` | 1 | 26 | 26 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 2 | `full` | `PASS` | 1 | 26 | 26 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `status_clear_on_read_bug` | 3 | `full` | `PASS` | 1 | 26 | 26 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 1 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 2 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 3 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 1 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 2 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 3 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 1 | `full` | `PASS` | 1 | 26 | 26 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 2 | `full` | `PASS` | 1 | 26 | 26 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_status_window_bug` | 3 | `full` | `PASS` | 1 | 26 | 26 | `PASS` | `PASS` | `PASS` | `ac7000a1` | `ac7000a1` |
| `platform2_config_order_bug` | 1 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 2 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 3 | `core` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 1 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 2 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 3 | `hashed` | `PASS` | 5 | 2 | 2 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 1 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 2 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `platform2_config_order_bug` | 3 | `full` | `PASS` | 5 | 20 | 20 | `PASS` | `PASS` | `NA` | `0d0e000c` | `0d0e000c` |
| `environmental_controller_bug` | 1 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 2 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 3 | `core` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 1 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 2 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 3 | `hashed` | `PASS` | 1 | 4 | 4 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 1 | `full` | `PASS` | 1 | 36 | 36 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 2 | `full` | `PASS` | 1 | 36 | 36 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `environmental_controller_bug` | 3 | `full` | `PASS` | 1 | 36 | 36 | `PASS` | `PASS` | `PASS` | `ac700067` | `ac700067` |
| `power_rail_sequencer_bug` | 1 | `core` | `PASS` | 5 | 4 | 4 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 2 | `core` | `PASS` | 5 | 4 | 4 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 3 | `core` | `PASS` | 5 | 4 | 4 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 1 | `hashed` | `PASS` | 5 | 4 | 4 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 2 | `hashed` | `PASS` | 5 | 4 | 4 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 3 | `hashed` | `PASS` | 5 | 4 | 4 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 1 | `full` | `PASS` | 5 | 31 | 31 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 2 | `full` | `PASS` | 5 | 31 | 31 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |
| `power_rail_sequencer_bug` | 3 | `full` | `PASS` | 5 | 31 | 31 | `PASS` | `PASS` | `PASS` | `0d0e001f` | `0d0e001f` |

Allowed from this evidence:

- Scoped seeded FemtoRV32 v2 MMIO replay-consumer smokes reproduce the recorded property signature for 14 benchmark families across 3 seeds and core, hashed, and full recorder configurations while replay-side host MMIO inputs are perturbed.
- The v2 consumer consumes the captured replay stream and supplies replay MMIO values at the core-facing wrapper boundary for these focused base/expanded cases.
- The matrix includes wrapper-level IRQ-boundary and watchdog cases, but these remain wrapper/recorder stimuli rather than true FemtoRV32 CPU interrupt handling.

Do not claim from this evidence:

- v2 replay that drives both FemtoRV32 core-facing MMIO and IRQ inputs.
- True CPU interrupt/ISR replay on FemtoRV32.
