# ReplayCapsule-RV Chat Context

> Generated file. Refresh after code, paper, evidence, or artifact changes with `make chat-context` or by running `scripts/update_chat_context.py` with a real Python 3 executable.

- Generated at: `2026-06-30T22:48:33-07:00`
- Repository root: `C:\Users\tyboy\OneDrive\Documents\New project`
- Python used for this snapshot: `C:\Users\tyboy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

## Current Git State

- Branch: `codex/aspdac-80-submission-package`
- Commit: `2d9fa9b3`
- Working tree status: `0 changed paths`
- Changed paths: none

## Read This First

- This repo is a ReplayCapsule-RV research artifact for scoped single-hart RV32I interrupt/MMIO failure replay.
- The project already contains RTL, firmware benchmarks, Verilator replay harnesses, v2 compressed recorder logic, a v2 replay-consume checker, FPGA mapping evidence, generated paper assets, artifact packages, a second-core wrapper/replay-smoke breadth gate, a focused Hazard3 true-ISR firmware smoke, and a seeded Hazard3 v2 MMIO+IRQ replay benchmark matrix.
- The current strongest claim is event-sufficient replay for scoped embedded interrupt/MMIO failures with compiler-backed full RTL replay evidence.
- The v2 full RTL replay path now preloads capsule words into an RTL replay source, then uses the RTL replay consumer to drive replay MMIO/IRQ inputs into the core-facing paths; evidence rows should show `replay_stimulus_source=rtl_capsule_source_mmio_irq`.
- For conference-review questions, check `docs/conference_readiness_dashboard.md`, `docs/final_reviewer_report.md`, `docs/main_track_submission_review.md`, and `docs/novelty_audit.md`.

## Repository Inventory

- Counted files: `52067`
- Counted size: `5.93 GB`
- `.git` and `.tools` are skipped as repository metadata/local toolchain cache.

| Path | Files | Size | Notes |
| --- | ---: | ---: | --- |
| `.devcontainer` | 1 | 331 B | development container config |
| `.dockerignore` | 1 | 106 B | top-level file |
| `.git` | 0 | 0 B | skipped local metadata/toolchain |
| `.gitattributes` | 1 | 14 B | top-level file |
| `.github` | 4 | 19.87 KB | CI workflows |
| `.gitignore` | 1 | 79 B | top-level file |
| `.tools` | 0 | 0 B | skipped local metadata/toolchain |
| `AGENTS.md` | 1 | 651 B | top-level file |
| `artifact_evaluation.md` | 1 | 5.27 KB | top-level file |
| `build` | 400 | 26.44 MB | generated build outputs |
| `constraints` | 2 | 2.59 KB | FPGA constraints |
| `dist` | 6 | 142.06 MB | artifact zip packages |
| `Dockerfile` | 1 | 830 B | top-level file |
| `docs` | 59 | 320.46 KB | design, review, and readiness docs |
| `firmware` | 717 | 1.43 MB | firmware benchmarks and build outputs |
| `formal` | 35 | 88.53 KB | formal assumptions/proof scripts |
| `Makefile` | 1 | 14.71 KB | top-level file |
| `paper` | 84 | 377.07 KB | paper source, figures, tables, PDF |
| `README.md` | 1 | 13.25 KB | top-level file |
| `requirements.txt` | 1 | 177 B | top-level file |
| `results` | 50513 | 5.76 GB | raw and processed evidence |
| `rtl` | 46 | 244.84 KB | hardware design source |
| `scripts` | 98 | 1.23 MB | reproduction, analysis, audit, packaging scripts |
| `tb` | 39 | 311.05 KB | testbenches and Verilator harnesses |
| `third_party` | 54 | 616.29 KB | vendored dependencies |

## Implemented Components

### RTL

- Core ReplayCapsule modules: `capsule_buffer.sv`, `event_classifier.sv`, `event_pkg.sv`, `event_slicer.sv`, `event_tap.sv`, `hash_signature.sv`, `interrupt_logger.sv`, `mmio_logger.sv`, `property_checker.sv`, `registers.sv`, `replay_capsule_top.sv`, `replay_control.sv`
- v2 modules: `rcv2_adaptive_window.sv`, `rcv2_address_dictionary.sv`, `rcv2_capsule_rom.sv`, `rcv2_capsule_source.sv`, `rcv2_event_fifo_bram.sv`, `rcv2_event_packer.sv`, `rcv2_event_stream_fifo.sv`, `rcv2_irq_replay_driver.sv`, `rcv2_mmio_replay_driver.sv`, `rcv2_payload_hasher.sv`, `rcv2_recorder.sv`, `rcv2_replay_consumer.sv`, ... `1` more
- RV32I/PicoRV32 integration modules: `femtorv32_replaycapsule_v2_wrapper.sv`, `femtorv32_replaycapsule_wrapper.sv`, `hazard3_replaycapsule_v2_wrapper.sv`, `picorv32_replaycapsule_wrapper.sv`, `replaycapsule_soc.sv`, `replaycapsule_v2_self_replay_soc.sv`, `replaycapsule_v2_self_replay_top.sv`
- Mapped board/wrapper modules: `full_core_baseline_board_top.sv`, `full_core_replaycapsule_board_top.sv`, `full_core_replaycapsule_v2_board_top.sv`, `mapped_memory.sv`, `rcv2_replay_consumer_pin_limited_wrapper.sv`, `replaycapsule_recorder_tiny_wrapper.sv`, `replaycapsule_tiny_baseline_wrapper.sv`, `replaycapsule_v2_recorder_wrapper.sv`
- Vendored core sources: `femtorv32`, `hazard3`, `picorv32`

### Firmware And Harnesses

- Compiler-backed firmware benchmarks in current firmware evidence: `interrupt_race_bug`, `mmio_ordering_bug`, `sensor_threshold_bug`, `stack_corruption_bug`, `uart_command_bug`, `watchdog_timeout_bug`
- Expanded v2 benchmark families in measured replay evidence: `commanded_actuator_limit_bug`, `environmental_controller_bug`, `late_config_sequence_bug`, `platform2_config_order_bug`, `platform2_status_window_bug`, `power_rail_sequencer_bug`, `sensor_debounce_bug`, `status_clear_on_read_bug`
- Verilator harness files live under `tb/verilator/` and include record/replay execution, capsule JSON I/O, runtime comparisons, and hardware-driven v2 replay stimulus checks.
- Directed replay-consumer tests live under `tb/replay_consumer/`; system tests and HDL checks live under `tb/system/`.

### Paper And Packaging

- Paper source is under `paper/` with generated figures, tables, and ACM/ASP-DAC-style `paper/main.pdf`.
- Artifact packages are under `dist/`.
- Submission/readiness docs are under `docs/`.

## Evidence Status

| Area | Current generated evidence |
| --- | --- |
| Compiler firmware | `15/15` compiler-backed rows PASS in `results/processed/firmware_build.csv` |
| Full RTL replay v1 | `45/45` rows PASS in `results/processed/full_rtl_replay.csv` |
| Full RTL replay v2 | `135/135` rows PASS with RTL-driven MMIO/IRQ replay-consumer checks in `results/processed/full_rtl_replay_v2.csv` |
| v2 self-replay handoff | `243/243` rows PASS from captured RTL store in `results/processed/self_replay_handoff_v2.csv` |
| Standalone self-replay smokes | `42/42` rows PASS through the reusable RTL self-replay SoC shell across base and expanded MMIO/interrupt/watchdog/profile2 families and 3 v2 recorder configs, including `3` IRQ rows with matching nonzero PicoRV32 record/replay interrupt-handler entry counts, in `results/processed/standalone_self_replay_smokes.csv` |
| Negative replay | `10` replay-critical corruptions rejected; `0` unexpected accepts in `results/processed/full_rtl_replay_negative.csv` |
| v2 measured workload scaling | `750/750` rows PASS from `results/processed/workload_scaling_v2_measured_summary.csv` |
| Expanded benchmark replay | `144/144` rows PASS in `results/processed/expanded_benchmark_replay_measured.csv` |
| v2 zero-fail inventory | `0` open bug rows in `results/processed/v2_zero_fail_bug_inventory.csv` |
| HDL checks | `41/41` PASS in `results/processed/hdl_checks.csv` |
| Formal checks | `20/20` PASS in `results/processed/formal_checks.csv` |
| Second-core breadth | `15` PASS checks and `1` scope-boundary row in `results/processed/second_core_breadth.csv`; `56/56` focused FemtoRV32 replay rows across `4` v1 capture profiles in `results/processed/second_core_replay_smokes.csv`; `126/126` scoped seeded v2 MMIO replay-consumer rows across `14` benchmark families, `3` recorder configs, and `3` seeds in `results/processed/second_core_v2_smokes.csv` |
| Interrupt-capable second-core candidate | `11` PASS checks and `1` scope-boundary row in `results/processed/second_core_irq_candidate.csv`; Hazard3 is vendored/pinned with IRQ/CSR/MRET markers and Verilator frontend lint |
| Hazard3 true ISR smoke | `1/1` focused firmware row PASS in `results/processed/hazard3_irq_smoke.csv`; RV32I+Zicsr firmware takes a machine external interrupt, writes an ISR marker, acknowledges the IRQ, returns with `mret`, and writes done |
| Hazard3 v2 MMIO+IRQ replay benchmark matrix | `48/48` seeded rows PASS in `results/processed/hazard3_v2_replay_smoke.csv`; benchmarks=8 configs=core,hashed seeds=3 properties=1,2,4,5; ReplayCapsule wraps Hazard3, records MMIO plus true ISR marker/ack evidence, replays with host sensor/IRQ perturbed, and consumes the selected v2 recorder capsule stream |
| v2 selected mapped overhead | `lut 8.26%; ff 3.77%; bram 0.00%; fmax_mhz -0.04%` in `results/processed/mapped_scaling_overhead_v2_measured.csv` |
| ASIC/open-PDK | `PASS`; `5/5` OpenROAD placed/global-routed Nangate45 rows PASS with area/timing/power; `5/5` Yosys+ABC synthesis-only rows PASS; OpenROAD probe `BLOCKED`; local Docker `PASS`; OpenROAD Docker image `PASS`; WSL probe `PASS`; physical area overheads: `minimal 1.72%; core 19.47%; hashed 19.85%; full 23.27%`; physical power overheads: `minimal 10.02%; core 29.05%; hashed 45.24%; full 46.91%`; synthesis-only area overheads: `minimal 1.76%; core 19.84%; hashed 20.27%; full 21.76%` |

## Paper And Artifacts

- Paper build: `PASS` from `results/processed/paper_build_status.csv`.
- ASP-DAC page audit: `total_pages=6; ASP-DAC permits six body pages plus one reference page`; `body_pages_before_references=5; limit is 6 including figures and tables`; `reference_start_page=6; expected label aspdac:references-start`.
- Numeric claim audit: `PASS`.
- Private marker scan: `PASS`.
- Dist artifacts: `artifact_package_manifest.csv`, `replaycapsule-rv-artifact.zip`, `replaycapsule-rv-topconf-artifact.zip`, `replaycapsule-rv-topconf-v2-artifact.zip`, `topconf_artifact_package_manifest.csv`, `topconf_v2_artifact_manifest.csv`

## Current Claim Boundaries

Allowed claims:

- Event-sufficient capsules for scoped single-hart RV32I interrupt/MMIO failures.
- Compiler-backed full RTL record/replay rows for the generated benchmark suite.
- v2 hardware-driven full-core replay-consume checks for measured v2 replay rows.
- v2 RTL capture-store primitive that retains replay-critical capsule words across reset, with HDL and record-signature evidence.
- v2 replay-mode controller primitive that arms the captured store and starts controller-driven same-instance replay without harness-preloaded capsule words.
- v2 same-instance self-replay handoff rows that replay from the captured RTL store without Verilator preloading saved capsule words.
- Reusable v2 RTL self-replay SoC shell plus a focused Icarus standalone self-replay matrix that records, resets, launches captured-store replay, checks captured/source-sent/consumer-consumed handoff for base and expanded MMIO/interrupt/watchdog/profile2 failures, and requires nonzero matching PicoRV32 interrupt-handler entry counts on IRQ-triggered rows.
- Expanded compiler-backed benchmark families, including two alternate-MMIO-profile families, when `expanded_benchmark_replay_measured.csv` is current.
- Corrupted-capsule rejection for replay-critical corruption classes.
- Second open-source RV32I core wrapper/replay-smoke breadth only: FemtoRV32 Quark is vendored, wrapped with ReplayCapsule, linted, generically synthesized, has one compiler-backed capture smoke, has a reusable v1 RTL packet checker for 168-bit capsules, has a scoped v1 MMIO replay driver for replay reads, has focused capsule-derived replay smoke rows over base and expanded benchmark families across v1 capture profiles, including wrapper-level IRQ-boundary and profile2-MMIO evidence, and has scoped seeded v2 MMIO replay-consumer benchmark/config rows that perturb replay-side host MMIO inputs while reproducing the property signature.
- Hazard3 is vendored as a pinned interrupt-capable second-core candidate with Apache-2.0 license metadata, external/software/timer IRQ ports, machine CSR/MRET support markers, Verilator frontend lint, a focused RV32I+Zicsr firmware smoke that takes a machine external interrupt and returns with `mret`, and a seeded v2 ReplayCapsule MMIO+IRQ replay-consumer benchmark matrix across multiple Hazard3 firmware workload families and core/hashed recorder configs.
- Nangate45 OpenROAD placed/global-routed ASIC/open-PDK area, timing, and power rows, explicitly not detailed-route signoff, tapeout, silicon, or energy.
- Same-target ECP5 mapped overhead for the selected v2 minimal recorder profile, with diagnostic core/hashed rows kept separate.
- Reproducible paper/artifact evidence when the generated CSVs and package files are present.

Do not claim yet:

- Standalone board/silicon replay flow independent of testbench reset orchestration and the focused reusable memory/MMIO/IRQ/watchdog shell.
- Detailed-route ASIC signoff, tapeout, silicon, or energy.
- True CPU interrupt/ISR replay on FemtoRV32; full v2 MMIO+IRQ replay-consumer stimulus on FemtoRV32; multicore, DMA, cache/coherence, broad platform, or arbitrary peripheral support.
- Hazard3 full-diagnostic `full` recorder-config replay with all-commit IRQ lookahead.
- Do not claim replacement for RISC-V trace/debug standards.
- Do not claim global minimal trace, universal deterministic replay, or first-ever hardware replay.
- Area-optimized overhead claims for diagnostic-rich configurations.

## Autonomous Replay Status

| Item | Status | Evidence |
| --- | --- | --- |
| v2 RTL replay consumer exists | `yes` | `rtl/replaycapsule_v2/rcv2_replay_consumer.sv` |
| v2 RTL capsule source exists | `yes` | `rtl/replaycapsule_v2/rcv2_capsule_source.sv` |
| v2 RTL replay-mode controller exists | `yes` | `rtl/replaycapsule_v2/rcv2_replay_mode_controller.sv` |
| Reusable v2 self-replay RTL shell exists | `yes` | `rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv` |
| Reusable v2 self-replay SoC shell exists | `yes` | `rtl/rv32i_integration/replaycapsule_v2_self_replay_soc.sv` |
| Replay-mode controller sequences source/consumer handoff | `yes` | controller drives store clear, capture enable, source select, start, and expected count |
| Replay-mode controller HDL test | `PASS` | `tb_rcv2_replay_mode_controller` in `results/processed/hdl_checks.csv` |
| Standalone self-replay shell lint | `PASS` | `verilator_lint_replaycapsule_v2_self_replay_top` in `results/processed/hdl_checks.csv` |
| Standalone self-replay SoC shell lint | `PASS` | `verilator_lint_replaycapsule_v2_self_replay_soc` in `results/processed/hdl_checks.csv` |
| Focused non-Verilator self-replay smoke | `PASS` | `tb_picorv32_standalone_self_replay_smoke` in `results/processed/hdl_checks.csv` |
| Focused standalone self-replay matrix | `42/42` | `results/processed/standalone_self_replay_smokes.csv`; shell-clean=42/42 irq-entry-clean=3 benchmarks=14 configs=core,full,hashed |
| RTL source captures replay-critical words | `yes` | source contains capture-store controls and counters |
| Capture store retains across reset | `PASS` | `tb_rcv2_capsule_source` in `results/processed/hdl_checks.csv` |
| v2 record signatures exercise capture store | `279/279` | `results/raw/rtl_signatures_v2/*_record.json` notes |
| Consumer wired into PicoRV32 wrapper | `yes` | `rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv` |
| Replay consumer drives core-facing MMIO read data | `yes` | wrapper contains `.mem_rdata(core_mem_rdata)` and `replay_consume_mmio_value` |
| Replay consumer drives core-facing IRQ input | `yes` | wrapper contains `.irq(core_irq)` and `replay_consume_irq_valid` |
| Hazard3 v2 wrapper wires replay consumer | `yes` | `rtl/rv32i_integration/hazard3_replaycapsule_v2_wrapper.sv` |
| Hazard3 replay consumer drives core-facing MMIO/IRQ | `yes` | wrapper drives `core_hrdata` and registered Hazard3 IRQ level from replay-consumer outputs |
| Harness still injects replay MMIO values | `no` | `tb/verilator/rtl_harness.cpp` contains `replay_mmio_value` |
| Harness still injects replay IRQ timing | `no` | `tb/verilator/rtl_harness.cpp` contains `irq_from_capsule` |
| v2 full RTL rows use RTL MMIO/IRQ replay stimulus | `135/135` | `results/processed/full_rtl_replay_v2.csv`; configs=core,full,hashed |
| v2 self-replay uses replay-mode controller and captured RTL store without preload | `243/243` | `results/processed/self_replay_handoff_v2.csv`; configs=core,full,hashed benchmarks=12 |
| Hazard3 v2 MMIO+IRQ replay benchmark matrix | `48/48` | `results/processed/hazard3_v2_replay_smoke.csv`; benchmarks=8 configs=core,hashed seeds=3 with host IRQ low during replay |

Current interpretation: **v2 full-core replay is hardware-driven for MMIO/IRQ replay stimulus in the Verilator evidence path**.

Additional progress: **the RTL source now has a capture-store path that retains replay-critical capsule words across reset, an RTL replay-mode controller now arms the store and starts captured-store self-replay without Verilator preloading saved capsule words, a reusable RTL self-replay SoC shell now has a focused Icarus standalone matrix covering base and expanded MMIO, interrupt, watchdog, and profile2 failures with captured/source-sent/consumer-consumed count agreement plus matching nonzero PicoRV32 interrupt-handler entry counts on IRQ rows, and Hazard3 now has a seeded v2 MMIO+IRQ replay-consumer matrix with host-side replay IRQ held low.**

Remaining boundary: the broad replay matrix still uses Verilator orchestration, and the standalone evidence is a focused reusable memory/MMIO/IRQ/watchdog shell rather than a board/silicon replay flow.

## Highest-Leverage Next Priorities

1. 80%-level submission package: closed for the scoped ASP-DAC attempt. ASIC/OpenROAD physical rows, Hazard3 matrix rows, autonomous/captured-store replay wording, artifact packages, and audits are synchronized. Keep future edits claim-disciplined and rerun the audits.
2. Optional above-80 standalone replay: broad board/peripheral integration beyond the focused reusable memory/MMIO/IRQ/watchdog/profile2 shell remains future work only if the paper wants a standalone board/silicon replay claim.
3. Optional above-80 second-core breadth: full-diagnostic all-commit Hazard3 replay remains future work only if the paper wants to claim that specific stronger config.
4. Optional above-80 ASIC strengthening: detailed-route signoff, tapeout, silicon, and energy remain future work only if the paper wants claims beyond the current global-route physical evidence.

## File Map For Future Chats

- Start here: `docs/CHAT_CONTEXT.md`.
- Project summary: `README.md`.
- Current submission readiness: `docs/conference_readiness_dashboard.md`, `docs/final_reviewer_report.md`, `docs/main_track_submission_review.md`.
- Novelty/scope guardrails: `docs/novelty_audit.md`, `docs/novelty_matrix.md`, `docs/limitations.md`, `docs/related_work_positioning.md`.
- Hardware architecture: `docs/architecture.md`, `docs/core_integration.md`, `rtl/`, `rtl/replaycapsule_v2/`, `rtl/rv32i_integration/`.
- Second-core breadth: `docs/second_core_breadth.md`, `docs/second_core_replay_smokes.md`, `docs/second_core_v2_smokes.md`, `docs/second_core_irq_candidate.md`, `docs/hazard3_irq_smoke.md`, `docs/hazard3_v2_replay_smoke.md`, `results/processed/second_core_breadth.csv`, `results/processed/second_core_replay_smokes.csv`, `results/processed/second_core_v2_smokes.csv`, `results/processed/second_core_irq_candidate.csv`, `results/processed/hazard3_irq_smoke.csv`, `results/processed/hazard3_v2_replay_smoke.csv`, `firmware/hazard3_irq_smoke/`, `firmware/hazard3_replay_smoke/`, `tb/system/tb_hazard3_irq_smoke.v`, `tb/system/tb_hazard3_v2_replay_smoke.sv`, `scripts/run_hazard3_irq_smoke.py`, `scripts/run_hazard3_v2_replay_smoke.py`, `rtl/rv32i_integration/hazard3_replaycapsule_v2_wrapper.sv`, `rtl/rv32i_integration/femtorv32_replaycapsule_v2_wrapper.sv`, `tb/system/tb_femtorv32_v2_replay_smoke.sv`, `third_party/femtorv32/`, and `third_party/hazard3/`.
- Standalone self-replay matrix: `docs/standalone_self_replay_smokes.md`, `results/processed/standalone_self_replay_smokes.csv`, `rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv`, and `rtl/rv32i_integration/replaycapsule_v2_self_replay_soc.sv`.
- ASIC/open-PDK: `docs/asic_openpdk_evidence.md`, `docs/asic_physical_tool_probe.md`, `results/processed/asic_openpdk.csv`, `results/processed/asic_openpdk_overhead.csv`, `results/processed/asic_openpdk_yosys_area.csv`, `results/processed/asic_openpdk_yosys_area_overhead.csv`, `results/processed/asic_openpdk_summary.csv`, `results/processed/asic_physical_tool_probe.csv`, `results/raw/asic_openpdk/`, `scripts/run_asic_openroad_docker.ps1`, `scripts/materialize_nangate45_from_orfs.py`, and `.github/workflows/asic-openroad.yml`.
- Replay evidence: `results/processed/full_rtl_replay.csv`, `results/processed/full_rtl_replay_v2.csv`, `results/processed/full_rtl_replay_negative.csv`.
- v2 measured evidence: `docs/v2_zero_fail_status.md`, `results/processed/*_v2_measured*.csv`.
- Paper source: `paper/main.tex`, `paper/sections/`, `paper/main.pdf`.
- Build and audit entry points: `Makefile`, especially `make topconf-v2-measured`, `make paper-audit`, and `make chat-context`.

## Update Rules

- Run `make chat-context` after adding/removing RTL, firmware, scripts, paper sections, generated evidence, or artifacts.
- If `python` or `python3` resolves to the Windows Store alias, run `make PYTHON="C:/Users/tyboy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe" chat-context`.
- Future chats should read this file first and refresh it if it looks stale relative to `git status` or recent work.
- This file is generated, so do not manually edit it for lasting changes. Edit `scripts/update_chat_context.py`, rerun the updater, and commit both files if using git.
