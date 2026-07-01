# Table 1. Synthesis Resource Status

Generated from `../../results/processed/synthesis.csv`, `../../results/processed/synthesis_overhead.csv`, and `../../results/processed/mapped_synthesis.csv`.

Generic Yosys cell counts are measured from real local reports. Mapped rows are shown only where a real place-and-route flow produced them.

| Design | Tool | Status | Generic cells | LUTs | FFs | BRAMs | Fmax MHz | Notes |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| Baseline PicoRV32 | yowasp-yosys | MEASURED | 519 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| ReplayCapsule record-side top | yowasp-yosys | MEASURED | 1324 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| PicoRV32 + ReplayCapsule wrapper | yowasp-yosys | MEASURED | 2055 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| FemtoRV32 | oss-cad-suite:yosys | MEASURED | 155 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| femtorv32_replaycapsule_wrapper | oss-cad-suite:yosys | MEASURED | 1645 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |

## Generic Cell-Overhead Context

| Baseline | Instrumented build | Status | Baseline cells | Instrumented cells | Delta cells | Overhead vs baseline | Record-side cells | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Baseline PicoRV32 | PicoRV32 + ReplayCapsule wrapper | MEASURED | 519 | 2055 | 1536 | 295.95% | 1324 | Generic Yosys cell-count context only; mapped FPGA overhead requires LUT/FF/BRAM/Fmax reports |

## Scoped Mapped FPGA Rows

| Target | Flow | Design | Status | LUTs | FFs | BRAMs | Fmax MHz | Notes |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| ecp5-85k | yosys+synth_ecp5+nextpnr-ecp5 | full_core_baseline_board | PASS | 2814 | 883 | 6 | 63.47 | real mapped ecp5-85k board-level place-and-route completed; memory_words=2048; allowed top-level IO only |
| ecp5-85k | yosys+synth_ecp5+nextpnr-ecp5 | full_core_replaycapsule_board | PASS | 6859 | 3901 | 6 | 50.70 | real mapped ecp5-85k board-level place-and-route completed; memory_words=2048; allowed top-level IO only |
| ice40-hx8k | yosys+synth_ice40+nextpnr-ice40 | replaycapsule_tiny_baseline | PASS | 46 | 32 | NA | 157.48 | real mapped ice40-hx8k place-and-route completed |
| ice40-hx8k | yosys+synth_ice40+nextpnr-ice40 | replaycapsule_recorder_tiny | PASS | 365 | 205 | NA | 63.93 | real mapped ice40-hx8k place-and-route completed |
