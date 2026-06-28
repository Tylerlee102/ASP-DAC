.PHONY: test reproduce quickcheck check-toolchain firmware verify-deterministic-firmware check-evidence firmware-sim rtl-smoke verilator-smoke verilator-harness runtime-harnesses full-rtl-replay full-rtl-replay-one firmware-source-compare full-rtl-negative runtime-overhead mapped-synth workload-scaling-quick workload-scaling-full runtime-scaling-quick runtime-scaling-full capsule-baselines capsule-baselines-full buffer-sensitivity buffer-sensitivity-full recorder-config-quick recorder-config-full mapped-scaling-quick mapped-scaling-full event-ablation-scaling event-ablation-scaling-full topconf-matrix topconf-tables topconf-figures topconf-artifact private-marker-scan topconf-quick topconf-full topconf-v2-evidence topconf-v2-measured replay-consumer-v2 topconf-v2-artifact topconf-v2-quick topconf-v2-full paper paper-audit artifact replay-demo phase12-smoke

PYTHON ?= python3
VERILATOR ?= verilator
VERILATOR_ENV ?= env -u VERILATOR_ROOT -u VERILATOR_BIN -u OSS_CAD_SUITE
VERILATOR_MDIR ?= build/verilator/obj_dir
VERILATOR_OUTPUT ?= ../replaycapsule_sim
VERILATOR_EXTRA_FLAGS ?=
RUNTIME_RECORDER_MDIR ?= build/verilator/runtime_recorder_obj_dir
RUNTIME_BASELINE_MDIR ?= build/verilator/runtime_baseline_obj_dir
RUNTIME_RECORDER_OUTPUT ?= ../runtime_recorder_sim
RUNTIME_BASELINE_OUTPUT ?= ../runtime_baseline_sim
VERILATOR_CFLAGS ?= -std=c++17 -O2 -I$(abspath tb/verilator)
RUNTIME_RECORDER_CFLAGS ?= -std=c++17 -O2 -I$(abspath tb/verilator)
RUNTIME_BASELINE_CFLAGS ?= -std=c++17 -O2 -I$(abspath tb/verilator) -DRC_RUNTIME_BASELINE
BENCH ?= sensor_threshold_bug
VARIANT ?= failing
SEED ?= 1
MAX_CYCLES ?= 100000
DEBUG ?=
DEBUG_FLAGS = $(if $(DEBUG),--debug-events --dump-mmio --dump-property --dump-pc --dump-disasm-context,)
REQUIRE_COMPILER ?= 0
ALLOW_FALLBACK ?= 1
ARCH ?= v1
RECORDER_CONFIG ?= core
REQUIRE_COMPILER_FLAGS = $(if $(filter 1 true yes on,$(REQUIRE_COMPILER)),--require-compiler,)
FALLBACK_FLAGS = $(if $(filter 1 true yes on,$(ALLOW_FALLBACK)),--allow-fallback,)

RTL_COMMON = \
	rtl/event_pkg.sv \
	rtl/event_tap.sv \
	rtl/event_classifier.sv \
	rtl/capsule_buffer.sv \
	rtl/property_checker.sv \
	rtl/event_slicer.sv \
	rtl/hash_signature.sv \
	rtl/replay_capsule_top.sv \
	rtl/replaycapsule_v2/rcv2_payload_hasher.sv \
	rtl/replaycapsule_v2/rcv2_address_dictionary.sv \
	rtl/replaycapsule_v2/rcv2_adaptive_window.sv \
	rtl/replaycapsule_v2/rcv2_event_packer.sv \
	rtl/replaycapsule_v2/rcv2_event_fifo_bram.sv \
	rtl/replaycapsule_v2/rcv2_recorder.sv

VERILATOR_SOURCES = \
	tb/verilator/replaycapsule_verilator_top.sv \
	third_party/picorv32/picorv32.v \
	$(RTL_COMMON) \
	rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv \
	tb/verilator/main.cpp \
	tb/verilator/rtl_harness.cpp \
	tb/verilator/capsule_io.cpp

VERILATOR_ABS_SOURCES = $(foreach src,$(VERILATOR_SOURCES),$(abspath $(src)))

RUNTIME_RECORDER_SOURCES = \
	tb/verilator/replaycapsule_verilator_top.sv \
	third_party/picorv32/picorv32.v \
	$(RTL_COMMON) \
	rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv \
	tb/verilator/runtime_main.cpp

RUNTIME_BASELINE_SOURCES = \
	tb/verilator/picorv32_baseline_top.sv \
	third_party/picorv32/picorv32.v \
	tb/verilator/runtime_main.cpp

RUNTIME_RECORDER_ABS_SOURCES = $(foreach src,$(RUNTIME_RECORDER_SOURCES),$(abspath $(src)))
RUNTIME_BASELINE_ABS_SOURCES = $(foreach src,$(RUNTIME_BASELINE_SOURCES),$(abspath $(src)))

test:
	$(PYTHON) scripts/run_all_tests.py

reproduce: check-toolchain firmware verilator-harness full-rtl-replay full-rtl-negative runtime-overhead firmware-source-compare mapped-synth paper paper-audit artifact

quickcheck: check-toolchain firmware verilator-smoke paper-audit

check-toolchain:
	$(PYTHON) scripts/check_toolchain.py --gate reproduce

firmware:
	$(PYTHON) scripts/build_firmware.py $(REQUIRE_COMPILER_FLAGS)

verify-deterministic-firmware:
	$(PYTHON) scripts/verify_deterministic_firmware.py

check-evidence:
	$(PYTHON) scripts/check_no_fallback_pass.py

firmware-sim:
	$(PYTHON) scripts/rv32i_firmware_sim.py --self-test --out-csv results/processed/firmware_sim_replay.csv --out-json results/raw/firmware_sim_traces.json

rtl-smoke: firmware
	$(PYTHON) scripts/run_hdl_checks.py
	$(PYTHON) scripts/export_rtl_capsules.py
	$(PYTHON) scripts/summarize_picorv32_smokes.py

verilator-smoke:
	$(PYTHON) scripts/check_verilator_compile.py --verilator $(VERILATOR)

verilator-harness:
	$(PYTHON) -c "from pathlib import Path; Path('build/verilator').mkdir(parents=True, exist_ok=True); Path('results/raw/verilator').mkdir(parents=True, exist_ok=True)"
	$(VERILATOR_ENV) $(VERILATOR) --cc --exe --build --sv \
		-Wno-TIMESCALEMOD \
		$(VERILATOR_EXTRA_FLAGS) \
		--top-module replaycapsule_verilator_top \
		-Irtl -Irtl/replaycapsule_v2 -Irtl/rv32i_integration -Ithird_party/picorv32 -Itb/verilator \
		--Mdir $(VERILATOR_MDIR) \
		-CFLAGS "$(VERILATOR_CFLAGS)" \
		-o $(VERILATOR_OUTPUT) \
		$(VERILATOR_ABS_SOURCES) > results/raw/verilator/build.log 2>&1
	@test -x build/verilator/replaycapsule_sim || test -x build/verilator/replaycapsule_sim.exe || test -x "$(VERILATOR_OUTPUT)" || test -x "$(VERILATOR_OUTPUT).exe" || (echo "ERROR: Verilator simulator binary missing. See results/raw/verilator/build.log." && exit 1)

runtime-harnesses:
	$(PYTHON) -c "from pathlib import Path; Path('build/verilator').mkdir(parents=True, exist_ok=True); Path('results/raw/runtime_overhead').mkdir(parents=True, exist_ok=True)"
	$(VERILATOR_ENV) $(VERILATOR) --cc --exe --build --sv \
		-Wno-TIMESCALEMOD \
		--top-module replaycapsule_verilator_top \
		-Irtl -Irtl/replaycapsule_v2 -Irtl/rv32i_integration -Ithird_party/picorv32 -Itb/verilator \
		--Mdir $(RUNTIME_RECORDER_MDIR) \
		-CFLAGS "$(RUNTIME_RECORDER_CFLAGS)" \
		-o $(RUNTIME_RECORDER_OUTPUT) \
		$(RUNTIME_RECORDER_ABS_SOURCES) > results/raw/runtime_overhead/recorder_build.log 2>&1
	$(VERILATOR_ENV) $(VERILATOR) --cc --exe --build --sv \
		-Wno-TIMESCALEMOD \
		--top-module picorv32_baseline_top \
		-Ithird_party/picorv32 -Itb/verilator \
		--Mdir $(RUNTIME_BASELINE_MDIR) \
		-CFLAGS "$(RUNTIME_BASELINE_CFLAGS)" \
		-o $(RUNTIME_BASELINE_OUTPUT) \
		$(RUNTIME_BASELINE_ABS_SOURCES) > results/raw/runtime_overhead/baseline_build.log 2>&1
	@test -x build/verilator/runtime_recorder_sim || test -x build/verilator/runtime_recorder_sim.exe || test -x "$(RUNTIME_RECORDER_OUTPUT)" || test -x "$(RUNTIME_RECORDER_OUTPUT).exe" || (echo "ERROR: runtime recorder simulator missing. See results/raw/runtime_overhead/recorder_build.log." && exit 1)
	@test -x build/verilator/runtime_baseline_sim || test -x build/verilator/runtime_baseline_sim.exe || test -x "$(RUNTIME_BASELINE_OUTPUT)" || test -x "$(RUNTIME_BASELINE_OUTPUT).exe" || (echo "ERROR: runtime baseline simulator missing. See results/raw/runtime_overhead/baseline_build.log." && exit 1)

full-rtl-replay: firmware
	$(PYTHON) scripts/run_full_rtl_replay.py --arch $(ARCH) --recorder-config $(RECORDER_CONFIG) $(FALLBACK_FLAGS) $(DEBUG_FLAGS)

full-rtl-replay-one: firmware
	$(PYTHON) scripts/run_full_rtl_replay.py --arch $(ARCH) --recorder-config $(RECORDER_CONFIG) --benchmark $(BENCH) --variant $(VARIANT) --seed $(SEED) --max-cycles $(MAX_CYCLES) $(FALLBACK_FLAGS) $(DEBUG_FLAGS)

firmware-source-compare:
	$(PYTHON) scripts/compare_firmware_sources.py

full-rtl-negative: firmware
	$(PYTHON) scripts/run_full_rtl_negative.py

runtime-overhead: full-rtl-replay
	$(PYTHON) scripts/run_runtime_overhead.py

mapped-synth:
	$(PYTHON) scripts/run_mapped_synthesis.py

topconf-matrix:
	$(PYTHON) scripts/generate_topconf_matrix.py

workload-scaling-quick: firmware
	$(PYTHON) scripts/generate_scaled_workloads.py --mode quick
	$(PYTHON) scripts/run_workload_scaling.py --mode quick

workload-scaling-full: firmware
	$(PYTHON) scripts/generate_scaled_workloads.py --mode full
	$(PYTHON) scripts/run_workload_scaling.py --mode full

runtime-scaling-quick: firmware
	$(PYTHON) scripts/run_runtime_scaling.py --mode quick

runtime-scaling-full: firmware
	$(PYTHON) scripts/run_runtime_scaling.py --mode full

capsule-baselines:
	$(PYTHON) scripts/run_capsule_baselines.py

capsule-baselines-full: capsule-baselines

buffer-sensitivity:
	$(PYTHON) scripts/run_buffer_sensitivity.py

buffer-sensitivity-full: buffer-sensitivity

recorder-config-quick: firmware
	$(PYTHON) scripts/recorder_config_matrix.py --mode quick

recorder-config-full: firmware
	$(PYTHON) scripts/recorder_config_matrix.py --mode full

mapped-scaling-quick:
	$(PYTHON) scripts/run_mapped_scaling.py --mode quick
	$(PYTHON) scripts/diagnose_mapped_failures.py

mapped-scaling-full:
	$(PYTHON) scripts/run_mapped_scaling.py --mode representative
	$(PYTHON) scripts/diagnose_mapped_failures.py

event-ablation-scaling:
	$(PYTHON) scripts/run_event_ablation_scaling.py

event-ablation-scaling-full: event-ablation-scaling

topconf-tables:
	$(PYTHON) scripts/generate_topconf_tables.py

topconf-figures:
	$(PYTHON) scripts/generate_topconf_figures.py

topconf-artifact:
	$(PYTHON) scripts/generate_topconf_reviewer_audit.py
	$(PYTHON) scripts/package_topconf_artifact.py

private-marker-scan:
	$(PYTHON) scripts/scan_private_markers.py

topconf-quick: topconf-matrix firmware full-rtl-replay full-rtl-negative runtime-overhead workload-scaling-quick capsule-baselines buffer-sensitivity runtime-scaling-quick mapped-scaling-quick event-ablation-scaling recorder-config-quick topconf-tables topconf-figures paper paper-audit artifact topconf-artifact private-marker-scan

topconf-full: topconf-matrix firmware full-rtl-replay full-rtl-negative runtime-overhead workload-scaling-full capsule-baselines-full buffer-sensitivity-full runtime-scaling-full mapped-scaling-full event-ablation-scaling-full recorder-config-full topconf-tables topconf-figures paper paper-audit artifact topconf-artifact private-marker-scan

replay-consumer-v2:
	$(PYTHON) scripts/run_replay_consumer_tests.py
	$(PYTHON) scripts/run_replay_consumer_mapping.py
	-$(PYTHON) scripts/run_second_target_mapping.py

topconf-v2-evidence:
	$(PYTHON) scripts/diagnose_workload_failures.py
	$(PYTHON) scripts/run_workload_scaling_v2.py
	$(PYTHON) scripts/run_buffer_sensitivity_v2.py
	$(PYTHON) scripts/run_capsule_baselines_v2.py
	$(PYTHON) scripts/run_mapped_scaling_v2.py
	$(PYTHON) scripts/benchmark_manifest.py
	$(PYTHON) scripts/generate_topconf_v2_tables.py

topconf-v2-measured:
	$(PYTHON) scripts/run_v2_measured_evaluation.py --timeout-sec 45 --measure-all-buffer-depths
	$(PYTHON) scripts/run_expanded_benchmark_replay.py
	$(PYTHON) scripts/benchmark_manifest.py
	$(PYTHON) scripts/build_v2_zero_fail_bug_inventory.py

topconf-v2-artifact:
	$(PYTHON) scripts/package_topconf_v2_artifact.py

topconf-v2-quick: firmware full-rtl-replay full-rtl-negative runtime-overhead workload-scaling-quick runtime-scaling-quick topconf-v2-evidence replay-consumer-v2 paper paper-audit artifact topconf-v2-artifact private-marker-scan

topconf-v2-full: firmware full-rtl-replay full-rtl-negative workload-scaling-full buffer-sensitivity-full capsule-baselines-full runtime-scaling-full mapped-scaling-full event-ablation-scaling-full recorder-config-full topconf-v2-evidence topconf-v2-measured replay-consumer-v2 paper paper-audit artifact topconf-v2-artifact private-marker-scan

paper:
	$(PYTHON) scripts/generate_conference_evidence_tables.py
	$(PYTHON) scripts/render_paper_tables.py
	$(PYTHON) scripts/make_figures.py
	$(PYTHON) scripts/build_paper.py

paper-audit:
	$(PYTHON) scripts/audit_claims.py
	$(PYTHON) scripts/audit_paper_numbers.py
	$(PYTHON) scripts/audit_todos.py

artifact:
	$(PYTHON) scripts/generate_submission_docs.py
	$(PYTHON) scripts/summarize_artifact_manifest.py
	$(PYTHON) scripts/package_artifact.py

replay-demo:
	$(PYTHON) tb/replay_testbench/replay_driver.py --demo --mode commit-index

phase12-smoke:
	$(PYTHON) scripts/replaycapsule_model.py --self-test --dump-json results/raw/phase12_sensor_threshold_trace.json
