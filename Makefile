.PHONY: test reproduce replay-demo phase12-smoke

PYTHON ?= python3

test:
	$(PYTHON) scripts/run_all_tests.py

reproduce: test

replay-demo:
	$(PYTHON) tb/replay_testbench/replay_driver.py --demo --mode commit-index

phase12-smoke:
	$(PYTHON) scripts/replaycapsule_model.py --self-test --dump-json results/raw/phase12_sensor_threshold_trace.json

