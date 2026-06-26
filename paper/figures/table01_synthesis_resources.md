# Table 1. Synthesis Resource Status

Generated from `../../results/processed/synthesis.csv`, `../../results/processed/synthesis_overhead.csv`, and `../../results/processed/mapped_synthesis.csv`.

Generic Yosys cell counts are measured from real local reports. Mapped rows are shown only where a real place-and-route flow produced them.

| Design | Tool | Status | Generic cells | LUTs | FFs | BRAMs | Fmax MHz | Notes |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| Baseline PicoRV32 | yowasp-yosys | MEASURED | 519 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| ReplayCapsule record-side top | yowasp-yosys | MEASURED | 1324 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| PicoRV32 + ReplayCapsule wrapper | yowasp-yosys | MEASURED | 2055 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |

## Generic Cell-Overhead Context

| Baseline | Instrumented build | Status | Baseline cells | Instrumented cells | Delta cells | Overhead vs baseline | Record-side cells | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Baseline PicoRV32 | PicoRV32 + ReplayCapsule wrapper | MEASURED | 519 | 2055 | 1536 | 295.95% | 1324 | Generic Yosys cell-count context only; mapped FPGA overhead requires LUT/FF/BRAM/Fmax reports |

## Scoped Mapped FPGA Rows

| Target | Flow | Design | Status | LUTs | FFs | BRAMs | Fmax MHz | Notes |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| ice40-hx8k | yosys+synth_ice40+nextpnr-ice40 | replaycapsule_tiny_baseline | PASS | 46 | 32 | NA | 157.51 | real mapped iCE40 place-and-route completed |
| ice40-hx8k | yosys+synth_ice40+nextpnr-ice40 | replaycapsule_recorder_tiny | PASS | 372 | 205 | NA | 77.40 | real mapped iCE40 place-and-route completed |
| ice40-hx8k | yosys+synth_ice40+nextpnr-ice40 | picorv32 | FAIL | NA | NA | NA | NA | nextpnr-ice40 place-and-route failed: ERROR: Unable to find a placement location for cell 'pcpi_insn[7]$sb_io' |
| ice40-hx8k | yosys+synth_ice40+nextpnr-ice40 | replay_capsule_top | FAIL | NA | NA | NA | NA | nextpnr-ice40 place-and-route failed: ERROR: Unable to place cell 'u_capsule_buffer.mem[47]_SB_DFFE_Q_92_DFFLC', no BELs remaining to implement cell type 'ICESTORM_LC' |
| ice40-hx8k | yosys+synth_ice40+nextpnr-ice40 | picorv32_replaycapsule_wrapper | FAIL | NA | NA | NA | NA | nextpnr-ice40 place-and-route failed: ERROR: Unable to place cell 'u_replay_capsule_top.u_capsule_buffer.mem[37]_SB_DFFE_Q_144_DFFLC', no BELs remaining to implement cell type 'ICESTORM_LC' |
