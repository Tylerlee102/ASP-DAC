.PHONY: test reproduce check-toolchain firmware firmware-sim rtl-smoke verilator-smoke verilator-harness full-rtl-replay full-rtl-replay-one firmware-source-compare full-rtl-negative runtime-overhead mapped-synth paper paper-audit artifact replay-demo phase12-smoke

PYTHON ?= python3
VERILATOR ?= verilator
VERILATOR_ENV ?= env -u VERILATOR_ROOT -u VERILATOR_BIN -u OSS_CAD_SUITE
VERILATOR_MDIR ?= build/verilator/obj_dir
VERILATOR_OUTPUT ?= ../replaycapsule_sim
VERILATOR_CFLAGS ?= -std=c++17 -O2 -I$(abspath tb/verilator)
BENCH ?= sensor_threshold_bug
VARIANT ?= failing
SEED ?= 1
MAX_CYCLES ?= 100000
DEBUG ?=
DEBUG_FLAGS = $(if $(DEBUG),--debug-events --dump-mmio --dump-property --dump-pc --dump-disasm-context,)
REQUIRE_COMPILER ?= 0
ALLOW_FALLBACK ?= 1
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
	rtl/replay_capsule_top.sv

VERILATOR_SOURCES = \
	tb/verilator/replaycapsule_verilator_top.sv \
	third_party/picorv32/picorv32.v \
	$(RTL_COMMON) \
	rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv \
	tb/verilator/main.cpp \
	tb/verilator/rtl_harness.cpp \
	tb/verilator/capsule_io.cpp

VERILATOR_ABS_SOURCES = $(foreach src,$(VERILATOR_SOURCES),$(abspath $(src)))

test:
	$(PYTHON) scripts/run_all_tests.py

reproduce: check-toolchain firmware rtl-smoke full-rtl-replay full-rtl-negative runtime-overhead firmware-source-compare mapped-synth paper paper-audit artifact

check-toolchain:
	$(PYTHON) scripts/check_toolchain.py --gate reproduce

firmware:
	$(PYTHON) scripts/build_firmware.py $(REQUIRE_COMPILER_FLAGS)

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
		--top-module replaycapsule_verilator_top \
		-Irtl -Irtl/rv32i_integration -Ithird_party/picorv32 -Itb/verilator \
		--Mdir $(VERILATOR_MDIR) \
		-CFLAGS "$(VERILATOR_CFLAGS)" \
		-o $(VERILATOR_OUTPUT) \
		$(VERILATOR_ABS_SOURCES) > results/raw/verilator/build.log 2>&1
	@test -x build/verilator/replaycapsule_sim || test -x build/verilator/replaycapsule_sim.exe || (echo "ERROR: Verilator simulator binary missing. See results/raw/verilator/build.log." && exit 1)

full-rtl-replay: firmware
	$(PYTHON) scripts/run_full_rtl_replay.py $(FALLBACK_FLAGS) $(DEBUG_FLAGS)

full-rtl-replay-one: firmware
	$(PYTHON) scripts/run_full_rtl_replay.py --benchmark $(BENCH) --variant $(VARIANT) --seed $(SEED) --max-cycles $(MAX_CYCLES) $(FALLBACK_FLAGS) $(DEBUG_FLAGS)

firmware-source-compare:
	$(PYTHON) scripts/compare_firmware_sources.py

full-rtl-negative: firmware
	$(PYTHON) scripts/run_full_rtl_negative.py

runtime-overhead: full-rtl-replay
	$(PYTHON) scripts/run_runtime_overhead.py

mapped-synth:
	$(PYTHON) scripts/run_mapped_synthesis.py

paper:
	$(PYTHON) scripts/generate_conference_evidence_tables.py
	$(PYTHON) scripts/render_paper_tables.py
	$(PYTHON) scripts/build_paper.py

paper-audit:
	$(PYTHON) scripts/audit_claims.py
	$(PYTHON) scripts/audit_paper_numbers.py
	$(PYTHON) scripts/audit_todos.py

artifact:
	$(PYTHON) scripts/summarize_artifact_manifest.py
	$(PYTHON) scripts/package_artifact.py

replay-demo:
	$(PYTHON) tb/replay_testbench/replay_driver.py --demo --mode commit-index

phase12-smoke:
	$(PYTHON) scripts/replaycapsule_model.py --self-test --dump-json results/raw/phase12_sensor_threshold_trace.json
