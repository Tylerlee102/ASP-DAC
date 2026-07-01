# Second-Core Replay Smokes

Status: `56/56` rows PASS.

These focused Icarus rows run compiler-built firmware on the FemtoRV32 ReplayCapsule wrapper, capture a property-fail capsule, reset the wrapped core, load captured packets into a scoped v1 RTL MMIO replay driver for replay reads, and require the replay property, signature, and v1 RTL replay-checker-consumed capsule packets to match.

- Benchmarks covered: `14` (commanded_actuator_limit_bug, environmental_controller_bug, interrupt_race_bug, late_config_sequence_bug, mmio_ordering_bug, platform2_config_order_bug, platform2_status_window_bug, power_rail_sequencer_bug, sensor_debounce_bug, sensor_threshold_bug, stack_corruption_bug, status_clear_on_read_bug, uart_command_bug, watchdog_timeout_bug)
- v1 capture profiles covered: `4` (capture_all, mmio_interrupt, property_aware, replaycapsule_default)

| Benchmark | Capture profile | Status | Property | Capsule count | Checker consumed | MMIO driver hits | Signature | Replay sensor | Replay command |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `sensor_threshold_bug` | `capture_all` | `PASS` | 3 | 42 | 42 | 1 | `5e0500c2` | 850 | 0 |
| `sensor_threshold_bug` | `mmio_interrupt` | `PASS` | 3 | 2 | 2 | 1 | `5e0500c2` | 850 | 0 |
| `sensor_threshold_bug` | `property_aware` | `PASS` | 3 | 2 | 2 | 1 | `5e0500c2` | 850 | 0 |
| `sensor_threshold_bug` | `replaycapsule_default` | `PASS` | 3 | 6 | 6 | 1 | `5e0500c2` | 850 | 0 |
| `interrupt_race_bug` | `capture_all` | `PASS` | 2 | 21 | 21 | 0 | `1a1e00c2` | 850 | 0 |
| `interrupt_race_bug` | `mmio_interrupt` | `PASS` | 2 | 3 | 3 | 0 | `1a1e00c2` | 850 | 0 |
| `interrupt_race_bug` | `property_aware` | `PASS` | 2 | 2 | 2 | 0 | `1a1e00c2` | 850 | 0 |
| `interrupt_race_bug` | `replaycapsule_default` | `PASS` | 2 | 4 | 4 | 0 | `1a1e00c2` | 850 | 0 |
| `mmio_ordering_bug` | `capture_all` | `PASS` | 5 | 20 | 20 | 0 | `0d0e000c` | 850 | 0 |
| `mmio_ordering_bug` | `mmio_interrupt` | `PASS` | 5 | 2 | 2 | 0 | `0d0e000c` | 850 | 0 |
| `mmio_ordering_bug` | `property_aware` | `PASS` | 5 | 1 | 1 | 0 | `0d0e000c` | 850 | 0 |
| `mmio_ordering_bug` | `replaycapsule_default` | `PASS` | 5 | 3 | 3 | 0 | `0d0e000c` | 850 | 0 |
| `stack_corruption_bug` | `capture_all` | `PASS` | 4 | 21 | 21 | 0 | `8901aefb` | 850 | 0 |
| `stack_corruption_bug` | `mmio_interrupt` | `PASS` | 4 | 1 | 1 | 0 | `8901aefb` | 850 | 0 |
| `stack_corruption_bug` | `property_aware` | `PASS` | 4 | 1 | 1 | 0 | `8901aefb` | 850 | 0 |
| `stack_corruption_bug` | `replaycapsule_default` | `PASS` | 4 | 3 | 3 | 0 | `8901aefb` | 850 | 0 |
| `uart_command_bug` | `capture_all` | `PASS` | 1 | 23 | 23 | 1 | `ac7000e9` | 850 | 85 |
| `uart_command_bug` | `mmio_interrupt` | `PASS` | 1 | 3 | 3 | 1 | `ac7000e9` | 850 | 85 |
| `uart_command_bug` | `property_aware` | `PASS` | 1 | 2 | 2 | 1 | `ac7000e9` | 850 | 85 |
| `uart_command_bug` | `replaycapsule_default` | `PASS` | 1 | 4 | 4 | 1 | `ac7000e9` | 850 | 85 |
| `watchdog_timeout_bug` | `capture_all` | `PASS` | 6 | 36 | 36 | 1 | `feed00ff` | 850 | 0 |
| `watchdog_timeout_bug` | `mmio_interrupt` | `PASS` | 6 | 2 | 2 | 1 | `feed00ff` | 850 | 0 |
| `watchdog_timeout_bug` | `property_aware` | `PASS` | 6 | 2 | 2 | 1 | `feed00ff` | 850 | 0 |
| `watchdog_timeout_bug` | `replaycapsule_default` | `PASS` | 6 | 5 | 5 | 1 | `feed00ff` | 850 | 0 |
| `commanded_actuator_limit_bug` | `capture_all` | `PASS` | 1 | 23 | 23 | 1 | `ac7000a7` | 850 | 85 |
| `commanded_actuator_limit_bug` | `mmio_interrupt` | `PASS` | 1 | 3 | 3 | 1 | `ac7000a7` | 850 | 85 |
| `commanded_actuator_limit_bug` | `property_aware` | `PASS` | 1 | 2 | 2 | 1 | `ac7000a7` | 850 | 85 |
| `commanded_actuator_limit_bug` | `replaycapsule_default` | `PASS` | 1 | 4 | 4 | 1 | `ac7000a7` | 850 | 85 |
| `late_config_sequence_bug` | `capture_all` | `PASS` | 5 | 20 | 20 | 0 | `0d0e000c` | 850 | 0 |
| `late_config_sequence_bug` | `mmio_interrupt` | `PASS` | 5 | 2 | 2 | 0 | `0d0e000c` | 850 | 0 |
| `late_config_sequence_bug` | `property_aware` | `PASS` | 5 | 1 | 1 | 0 | `0d0e000c` | 850 | 0 |
| `late_config_sequence_bug` | `replaycapsule_default` | `PASS` | 5 | 3 | 3 | 0 | `0d0e000c` | 850 | 0 |
| `sensor_debounce_bug` | `capture_all` | `PASS` | 3 | 44 | 44 | 2 | `5e0500fd` | 850 | 0 |
| `sensor_debounce_bug` | `mmio_interrupt` | `PASS` | 3 | 3 | 3 | 2 | `5e0500fd` | 850 | 0 |
| `sensor_debounce_bug` | `property_aware` | `PASS` | 3 | 3 | 3 | 2 | `5e0500fd` | 850 | 0 |
| `sensor_debounce_bug` | `replaycapsule_default` | `PASS` | 3 | 7 | 7 | 2 | `5e0500fd` | 850 | 0 |
| `status_clear_on_read_bug` | `capture_all` | `PASS` | 1 | 26 | 26 | 2 | `ac7000a1` | 850 | 85 |
| `status_clear_on_read_bug` | `mmio_interrupt` | `PASS` | 1 | 4 | 4 | 2 | `ac7000a1` | 850 | 85 |
| `status_clear_on_read_bug` | `property_aware` | `PASS` | 1 | 3 | 3 | 2 | `ac7000a1` | 850 | 85 |
| `status_clear_on_read_bug` | `replaycapsule_default` | `PASS` | 1 | 5 | 5 | 2 | `ac7000a1` | 850 | 85 |
| `platform2_status_window_bug` | `capture_all` | `PASS` | 1 | 26 | 26 | 2 | `ac7000a1` | 850 | 85 |
| `platform2_status_window_bug` | `mmio_interrupt` | `PASS` | 1 | 4 | 4 | 2 | `ac7000a1` | 850 | 85 |
| `platform2_status_window_bug` | `property_aware` | `PASS` | 1 | 3 | 3 | 2 | `ac7000a1` | 850 | 85 |
| `platform2_status_window_bug` | `replaycapsule_default` | `PASS` | 1 | 5 | 5 | 2 | `ac7000a1` | 850 | 85 |
| `platform2_config_order_bug` | `capture_all` | `PASS` | 5 | 20 | 20 | 0 | `0d0e000c` | 850 | 0 |
| `platform2_config_order_bug` | `mmio_interrupt` | `PASS` | 5 | 2 | 2 | 0 | `0d0e000c` | 850 | 0 |
| `platform2_config_order_bug` | `property_aware` | `PASS` | 5 | 1 | 1 | 0 | `0d0e000c` | 850 | 0 |
| `platform2_config_order_bug` | `replaycapsule_default` | `PASS` | 5 | 3 | 3 | 0 | `0d0e000c` | 850 | 0 |
| `environmental_controller_bug` | `capture_all` | `PASS` | 1 | 36 | 36 | 2 | `ac700067` | 650 | 85 |
| `environmental_controller_bug` | `mmio_interrupt` | `PASS` | 1 | 4 | 4 | 2 | `ac700067` | 650 | 85 |
| `environmental_controller_bug` | `property_aware` | `PASS` | 1 | 3 | 3 | 2 | `ac700067` | 650 | 85 |
| `environmental_controller_bug` | `replaycapsule_default` | `PASS` | 1 | 5 | 5 | 2 | `ac700067` | 650 | 85 |
| `power_rail_sequencer_bug` | `capture_all` | `PASS` | 5 | 31 | 31 | 2 | `0d0e001f` | 850 | 85 |
| `power_rail_sequencer_bug` | `mmio_interrupt` | `PASS` | 5 | 4 | 4 | 2 | `0d0e001f` | 850 | 85 |
| `power_rail_sequencer_bug` | `property_aware` | `PASS` | 5 | 3 | 3 | 2 | `0d0e001f` | 850 | 85 |
| `power_rail_sequencer_bug` | `replaycapsule_default` | `PASS` | 5 | 5 | 5 | 2 | `0d0e001f` | 850 | 85 |

Allowed from this evidence:

- FemtoRV32 ReplayCapsule capture/replay smokes pass for 14 base and expanded benchmark families across 4 v1 capture profiles, including wrapper-level interrupt-boundary, profile2-MMIO, realistic-control, stack, command-limit, and watchdog cases.
- A scoped v1 RTL MMIO replay driver stores captured 168-bit packets and supplies replay MMIO-read values during the FemtoRV32 replay phase.
- The replay packet comparison is consumed by a reusable v1 RTL checker for the 168-bit capsule format used by the FemtoRV32 wrapper.
- The second-core wrapper can reproduce captured property/signature/capsule evidence after reset for this focused set.

Do not claim from this evidence:

- A seeded v2 second-core ReplayCapsule evaluation.
- Full v2 replay-consumer stimulus that drives FemtoRV32 core-facing MMIO/IRQ inputs.
- True CPU interrupt/ISR replay on FemtoRV32; the vendored Quark core has no external interrupt/CSR machinery.
- Cross-core equivalence, broad platform portability, mapped FPGA, or ASIC evidence for FemtoRV32.
