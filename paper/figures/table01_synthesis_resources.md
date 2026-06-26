# Table 1. Synthesis Resource Status

Generated from `../../results/processed/synthesis.csv` and `../../results/processed/synthesis_overhead.csv`.

Generic Yosys cell counts are measured from real local reports. Mapped FPGA LUT/FF/BRAM/Fmax fields remain `NA` until a mapped flow exists.

| Design | Tool | Status | Generic cells | LUTs | FFs | BRAMs | Fmax MHz | Notes |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| Baseline PicoRV32 | yowasp-yosys | MEASURED | 519 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| ReplayCapsule record-side top | yowasp-yosys | MEASURED | 1292 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |
| PicoRV32 + ReplayCapsule wrapper | yowasp-yosys | MEASURED | 2023 | NA | NA | NA | NA | Yosys generic cell count only; FPGA LUT/FF/BRAM/Fmax requires mapped flow |

## Generic Cell-Overhead Context

| Baseline | Instrumented build | Status | Baseline cells | Instrumented cells | Delta cells | Overhead vs baseline | Record-side cells | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Baseline PicoRV32 | PicoRV32 + ReplayCapsule wrapper | MEASURED | 519 | 2023 | 1504 | 289.79% | 1292 | Generic Yosys cell-count context only; mapped FPGA overhead requires LUT/FF/BRAM/Fmax reports |
