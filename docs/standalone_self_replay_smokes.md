# Standalone Self-Replay Smokes

Status: `42/42` rows PASS.

These focused Icarus rows instantiate the reusable v2 RTL self-replay SoC shell outside the Verilator top. Each row records a PicoRV32 v2 firmware failure through the shell's internal instruction memory, MMIO, IRQ, watchdog, replay-mode controller, and captured capsule source, resets the core, launches captured-store replay, and checks that the replay source and consumer consume the same captured replay-critical word count. IRQ rows additionally require matching nonzero PicoRV32 interrupt-handler entry counts in record and replay phases.

- Benchmarks covered: `14` (commanded_actuator_limit_bug, environmental_controller_bug, interrupt_race_bug, late_config_sequence_bug, mmio_ordering_bug, platform2_config_order_bug, platform2_status_window_bug, power_rail_sequencer_bug, sensor_debounce_bug, sensor_threshold_bug, stack_corruption_bug, status_clear_on_read_bug, uart_command_bug, watchdog_timeout_bug)
- Stimulus image families: `base_model_mem, expanded_compiler_hex, expanded_profile2_compiler_hex, realistic_control_compiler_hex`

| Benchmark | Config | Family | Status | Shell | Property | Captured | Sent | Consumed | Done | IRQ record | IRQ replay | Signature |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `sensor_threshold_bug` | `core` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 3 | 2 | 2 | 2 | 1 | 0 | 0 | `5e050080` |
| `sensor_threshold_bug` | `hashed` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 3 | 2 | 2 | 2 | 1 | 0 | 0 | `5e050080` |
| `sensor_threshold_bug` | `full` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 3 | 2 | 2 | 2 | 1 | 0 | 0 | `5e050080` |
| `interrupt_race_bug` | `core` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 2 | 3 | 3 | 3 | 1 | 1 | 1 | `1a1e0093` |
| `interrupt_race_bug` | `hashed` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 2 | 3 | 3 | 3 | 1 | 1 | 1 | `1a1e0093` |
| `interrupt_race_bug` | `full` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 2 | 3 | 3 | 3 | 1 | 1 | 1 | `1a1e0093` |
| `mmio_ordering_bug` | `core` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e001e` |
| `mmio_ordering_bug` | `hashed` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e001e` |
| `mmio_ordering_bug` | `full` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e001e` |
| `stack_corruption_bug` | `core` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 4 | 1 | 1 | 1 | 1 | 0 | 0 | `8901aefb` |
| `stack_corruption_bug` | `hashed` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 4 | 1 | 1 | 1 | 1 | 0 | 0 | `8901aefb` |
| `stack_corruption_bug` | `full` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 4 | 1 | 1 | 1 | 1 | 0 | 0 | `8901aefb` |
| `uart_command_bug` | `core` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 1 | 3 | 3 | 3 | 1 | 0 | 0 | `ac7000fe` |
| `uart_command_bug` | `hashed` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 1 | 3 | 3 | 3 | 1 | 0 | 0 | `ac7000fe` |
| `uart_command_bug` | `full` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 1 | 3 | 3 | 3 | 1 | 0 | 0 | `ac7000fe` |
| `watchdog_timeout_bug` | `core` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 6 | 2 | 2 | 2 | 1 | 0 | 0 | `feed0081` |
| `watchdog_timeout_bug` | `hashed` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 6 | 2 | 2 | 2 | 1 | 0 | 0 | `feed0081` |
| `watchdog_timeout_bug` | `full` | `base_model_mem` | `PASS` | `rtl_self_replay_soc` | 6 | 2 | 2 | 2 | 1 | 0 | 0 | `feed0081` |
| `commanded_actuator_limit_bug` | `core` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 3 | 3 | 3 | 1 | 0 | 0 | `ac7000a4` |
| `commanded_actuator_limit_bug` | `hashed` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 3 | 3 | 3 | 1 | 0 | 0 | `ac7000a4` |
| `commanded_actuator_limit_bug` | `full` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 3 | 3 | 3 | 1 | 0 | 0 | `ac7000a4` |
| `late_config_sequence_bug` | `core` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e0013` |
| `late_config_sequence_bug` | `hashed` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e0013` |
| `late_config_sequence_bug` | `full` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e0013` |
| `sensor_debounce_bug` | `core` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 3 | 3 | 3 | 3 | 1 | 0 | 0 | `5e0500f4` |
| `sensor_debounce_bug` | `hashed` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 3 | 3 | 3 | 3 | 1 | 0 | 0 | `5e0500f4` |
| `sensor_debounce_bug` | `full` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 3 | 3 | 3 | 3 | 1 | 0 | 0 | `5e0500f4` |
| `status_clear_on_read_bug` | `core` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac7000a6` |
| `status_clear_on_read_bug` | `hashed` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac7000a6` |
| `status_clear_on_read_bug` | `full` | `expanded_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac7000a6` |
| `platform2_status_window_bug` | `core` | `expanded_profile2_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac7000a6` |
| `platform2_status_window_bug` | `hashed` | `expanded_profile2_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac7000a6` |
| `platform2_status_window_bug` | `full` | `expanded_profile2_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac7000a6` |
| `platform2_config_order_bug` | `core` | `expanded_profile2_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e0013` |
| `platform2_config_order_bug` | `hashed` | `expanded_profile2_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e0013` |
| `platform2_config_order_bug` | `full` | `expanded_profile2_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 2 | 2 | 2 | 1 | 0 | 0 | `0d0e0013` |
| `environmental_controller_bug` | `core` | `realistic_control_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac700064` |
| `environmental_controller_bug` | `hashed` | `realistic_control_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac700064` |
| `environmental_controller_bug` | `full` | `realistic_control_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 1 | 4 | 4 | 4 | 1 | 0 | 0 | `ac700064` |
| `power_rail_sequencer_bug` | `core` | `realistic_control_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 4 | 4 | 4 | 1 | 0 | 0 | `0d0e001e` |
| `power_rail_sequencer_bug` | `hashed` | `realistic_control_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 4 | 4 | 4 | 1 | 0 | 0 | `0d0e001e` |
| `power_rail_sequencer_bug` | `full` | `realistic_control_compiler_hex` | `PASS` | `rtl_self_replay_soc` | 5 | 4 | 4 | 4 | 1 | 0 | 0 | `0d0e001e` |

Allowed from this evidence:

- The reusable RTL self-replay SoC shell works outside the Verilator top for the base model-backed benchmark families and expanded compiler-built benchmark families across core, hashed, and full v2 recorder configs.
- The shell contains the focused instruction-memory, MMIO, IRQ, watchdog, replay-mode-controller, and captured-source path used by these rows.
- The captured-store replay path can preserve replay-critical words across a reset and feed the RTL consumer without host-preloaded capsule words.
- IRQ-triggered rows prove PicoRV32 interrupt-handler entry through nonzero, matching record/replay EOI counts.

Do not claim from this evidence:

- A board/silicon replay engine.
- Arbitrary peripheral coverage beyond the focused memory/MMIO/IRQ/watchdog shell used by these rows.
