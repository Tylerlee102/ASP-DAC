# System Testbench Plan

This directory will hold the firmware-running SoC tests.

Current local status:

- deterministic Phase 1/2 event-model smoke test: `scripts/replaycapsule_model.py`
- RTL SoC boundary scaffold: `rtl/rv32i_integration/replaycapsule_soc.sv`
- PicoRV32/Verilator firmware-running testbench: TODO

Required next tests:

- hello-world firmware emits commits without property failure
- MMIO smoke firmware captures sensor read and actuator/config writes
- timer interrupt source can be scheduled by cycle and by commit index
- replay mode injects MMIO read values and interrupt timing from a capsule
- same property id and failure signature reproduce under commit-index replay

Current directed SystemVerilog test sources:

- `tb_property_checker.sv`
- `tb_capsule_buffer.sv`
- `tb_replay_control.sv`
- `tb_event_classifier_slicer.sv`
- `tb_hash_signature.sv`
- `tb_event_tap.sv`

They are run by `scripts/run_hdl_checks.py` when Icarus Verilog and `vvp` are
available. The current local gate reports them as PASS in
`results/processed/hdl_checks.csv`.
