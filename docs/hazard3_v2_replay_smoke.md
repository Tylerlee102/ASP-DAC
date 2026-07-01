# Hazard3 v2 Replay Benchmark Matrix

Status: `PASS` (48/48 rows PASS).

These Icarus rows wrap the vendored Hazard3 core with the v2 ReplayCapsule recorder and RTL replay consumer. Each row runs compiler-built RV32I+Zicsr firmware, records a firmware MMIO read plus true machine external interrupt handler marker/ack events, resets the core, perturbs replay-side host sensor input while keeping host replay IRQ deasserted, and requires the RTL replay consumer to drive core-facing MMIO data and IRQ stimulus while reproducing the recorded property signature.

- Benchmarks covered: `8` (actuator_limit_bug, interrupt_critical_bug, mmio_ordering_bug, post_config_actuator_limit_bug, profile2_actuator_limit_bug, profile2_interrupt_critical_bug, profile2_mmio_ordering_bug, stack_protect_bug).
- Recorder configs covered: `2` (core, hashed).
- Seeds covered: `3` (1, 2, 3).
- Property IDs covered: `4` (1, 2, 4, 5).

| Benchmark | Seed | Config | Status | Property | Words | Consumed | IRQ record/replay | MMIO drives | IRQ drives | Sensor -> replay host | Evidence |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- | --- |
| `actuator_limit_bug` | 1 | `core` | `PASS` | 1 | 6 | 6 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_actuator_limit_bug_core_seed1.txt` |
| `actuator_limit_bug` | 2 | `core` | `PASS` | 1 | 6 | 6 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_actuator_limit_bug_core_seed2.txt` |
| `actuator_limit_bug` | 3 | `core` | `PASS` | 1 | 6 | 6 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_actuator_limit_bug_core_seed3.txt` |
| `actuator_limit_bug` | 1 | `hashed` | `PASS` | 1 | 6 | 6 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_actuator_limit_bug_hashed_seed1.txt` |
| `actuator_limit_bug` | 2 | `hashed` | `PASS` | 1 | 6 | 6 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_actuator_limit_bug_hashed_seed2.txt` |
| `actuator_limit_bug` | 3 | `hashed` | `PASS` | 1 | 6 | 6 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_actuator_limit_bug_hashed_seed3.txt` |
| `interrupt_critical_bug` | 1 | `core` | `PASS` | 2 | 4 | 4 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_interrupt_critical_bug_core_seed1.txt` |
| `interrupt_critical_bug` | 2 | `core` | `PASS` | 2 | 4 | 4 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_interrupt_critical_bug_core_seed2.txt` |
| `interrupt_critical_bug` | 3 | `core` | `PASS` | 2 | 4 | 4 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_interrupt_critical_bug_core_seed3.txt` |
| `interrupt_critical_bug` | 1 | `hashed` | `PASS` | 2 | 4 | 4 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_interrupt_critical_bug_hashed_seed1.txt` |
| `interrupt_critical_bug` | 2 | `hashed` | `PASS` | 2 | 4 | 4 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_interrupt_critical_bug_hashed_seed2.txt` |
| `interrupt_critical_bug` | 3 | `hashed` | `PASS` | 2 | 4 | 4 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_interrupt_critical_bug_hashed_seed3.txt` |
| `stack_protect_bug` | 1 | `core` | `PASS` | 4 | 5 | 5 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_stack_protect_bug_core_seed1.txt` |
| `stack_protect_bug` | 2 | `core` | `PASS` | 4 | 5 | 5 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_stack_protect_bug_core_seed2.txt` |
| `stack_protect_bug` | 3 | `core` | `PASS` | 4 | 5 | 5 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_stack_protect_bug_core_seed3.txt` |
| `stack_protect_bug` | 1 | `hashed` | `PASS` | 4 | 5 | 5 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_stack_protect_bug_hashed_seed1.txt` |
| `stack_protect_bug` | 2 | `hashed` | `PASS` | 4 | 5 | 5 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_stack_protect_bug_hashed_seed2.txt` |
| `stack_protect_bug` | 3 | `hashed` | `PASS` | 4 | 5 | 5 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_stack_protect_bug_hashed_seed3.txt` |
| `mmio_ordering_bug` | 1 | `core` | `PASS` | 5 | 6 | 6 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_mmio_ordering_bug_core_seed1.txt` |
| `mmio_ordering_bug` | 2 | `core` | `PASS` | 5 | 6 | 6 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_mmio_ordering_bug_core_seed2.txt` |
| `mmio_ordering_bug` | 3 | `core` | `PASS` | 5 | 6 | 6 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_mmio_ordering_bug_core_seed3.txt` |
| `mmio_ordering_bug` | 1 | `hashed` | `PASS` | 5 | 6 | 6 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_mmio_ordering_bug_hashed_seed1.txt` |
| `mmio_ordering_bug` | 2 | `hashed` | `PASS` | 5 | 6 | 6 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_mmio_ordering_bug_hashed_seed2.txt` |
| `mmio_ordering_bug` | 3 | `hashed` | `PASS` | 5 | 6 | 6 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_mmio_ordering_bug_hashed_seed3.txt` |
| `profile2_actuator_limit_bug` | 1 | `core` | `PASS` | 1 | 7 | 7 | 1/1 | 2 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_actuator_limit_bug_core_seed1.txt` |
| `profile2_actuator_limit_bug` | 2 | `core` | `PASS` | 1 | 7 | 7 | 1/1 | 2 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_actuator_limit_bug_core_seed2.txt` |
| `profile2_actuator_limit_bug` | 3 | `core` | `PASS` | 1 | 7 | 7 | 1/1 | 2 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_actuator_limit_bug_core_seed3.txt` |
| `profile2_actuator_limit_bug` | 1 | `hashed` | `PASS` | 1 | 7 | 7 | 1/1 | 2 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_actuator_limit_bug_hashed_seed1.txt` |
| `profile2_actuator_limit_bug` | 2 | `hashed` | `PASS` | 1 | 7 | 7 | 1/1 | 2 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_actuator_limit_bug_hashed_seed2.txt` |
| `profile2_actuator_limit_bug` | 3 | `hashed` | `PASS` | 1 | 7 | 7 | 1/1 | 2 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_actuator_limit_bug_hashed_seed3.txt` |
| `profile2_interrupt_critical_bug` | 1 | `core` | `PASS` | 2 | 5 | 5 | 1/1 | 2 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_interrupt_critical_bug_core_seed1.txt` |
| `profile2_interrupt_critical_bug` | 2 | `core` | `PASS` | 2 | 5 | 5 | 1/1 | 2 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_interrupt_critical_bug_core_seed2.txt` |
| `profile2_interrupt_critical_bug` | 3 | `core` | `PASS` | 2 | 5 | 5 | 1/1 | 2 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_interrupt_critical_bug_core_seed3.txt` |
| `profile2_interrupt_critical_bug` | 1 | `hashed` | `PASS` | 2 | 5 | 5 | 1/1 | 2 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_interrupt_critical_bug_hashed_seed1.txt` |
| `profile2_interrupt_critical_bug` | 2 | `hashed` | `PASS` | 2 | 5 | 5 | 1/1 | 2 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_interrupt_critical_bug_hashed_seed2.txt` |
| `profile2_interrupt_critical_bug` | 3 | `hashed` | `PASS` | 2 | 5 | 5 | 1/1 | 2 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_interrupt_critical_bug_hashed_seed3.txt` |
| `profile2_mmio_ordering_bug` | 1 | `core` | `PASS` | 5 | 7 | 7 | 1/1 | 2 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_mmio_ordering_bug_core_seed1.txt` |
| `profile2_mmio_ordering_bug` | 2 | `core` | `PASS` | 5 | 7 | 7 | 1/1 | 2 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_mmio_ordering_bug_core_seed2.txt` |
| `profile2_mmio_ordering_bug` | 3 | `core` | `PASS` | 5 | 7 | 7 | 1/1 | 2 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_mmio_ordering_bug_core_seed3.txt` |
| `profile2_mmio_ordering_bug` | 1 | `hashed` | `PASS` | 5 | 7 | 7 | 1/1 | 2 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_mmio_ordering_bug_hashed_seed1.txt` |
| `profile2_mmio_ordering_bug` | 2 | `hashed` | `PASS` | 5 | 7 | 7 | 1/1 | 2 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_mmio_ordering_bug_hashed_seed2.txt` |
| `profile2_mmio_ordering_bug` | 3 | `hashed` | `PASS` | 5 | 7 | 7 | 1/1 | 2 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_profile2_mmio_ordering_bug_hashed_seed3.txt` |
| `post_config_actuator_limit_bug` | 1 | `core` | `PASS` | 1 | 7 | 7 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_post_config_actuator_limit_bug_core_seed1.txt` |
| `post_config_actuator_limit_bug` | 2 | `core` | `PASS` | 1 | 7 | 7 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_post_config_actuator_limit_bug_core_seed2.txt` |
| `post_config_actuator_limit_bug` | 3 | `core` | `PASS` | 1 | 7 | 7 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_post_config_actuator_limit_bug_core_seed3.txt` |
| `post_config_actuator_limit_bug` | 1 | `hashed` | `PASS` | 1 | 7 | 7 | 1/1 | 1 | 24 | 650 -> 0 | `results/raw/hazard3_v2_replay_smoke/vvp_run_post_config_actuator_limit_bug_hashed_seed1.txt` |
| `post_config_actuator_limit_bug` | 2 | `hashed` | `PASS` | 1 | 7 | 7 | 1/1 | 1 | 24 | 667 -> 123 | `results/raw/hazard3_v2_replay_smoke/vvp_run_post_config_actuator_limit_bug_hashed_seed2.txt` |
| `post_config_actuator_limit_bug` | 3 | `hashed` | `PASS` | 1 | 7 | 7 | 1/1 | 1 | 24 | 683 -> 698 | `results/raw/hazard3_v2_replay_smoke/vvp_run_post_config_actuator_limit_bug_hashed_seed3.txt` |

Allowed from this evidence:

- Hazard3 has a seeded ReplayCapsule v2 MMIO+IRQ replay-consumer matrix across multiple firmware bug classes and selected v2 recorder configurations.
- The replay phase uses the RTL replay consumer to drive core-facing MMIO read data and IRQ stimulus while host-side replay IRQ remains deasserted.
- The observed interrupt-enter event is tied to firmware execution of the Hazard3 ISR marker write.

Do not claim from this evidence:

- ASIC implementation-cost claims; use `results/processed/asic_openpdk.csv` for those.
- Board/silicon replay.
- Multicore, DMA, cache/coherence, or arbitrary peripheral replay.
- Full operating-system or application-suite coverage beyond these scoped firmware benchmark rows.
