# Table 6. Replay-Sufficiency Proof Obligations

Generated from `../../results/processed/proof_obligations.csv`.

This table links theorem assumptions to current evidence. It is not a
mechanized end-to-end replay proof.

| Obligation | Assumption | Status | Evidence level | Current limit |
| --- | --- | --- | --- | --- |
| PO-01 | A0/A2 platform and firmware identity | PARTIAL | documentation+firmware-artifact | Identity fields are specified and generated firmware artifacts exist, but there is no external compiler or full RTL replay identity check. |
| PO-02 | A1/A3 deterministic architectural state and core step | PARTIAL | model+firmware-sim | The local interpreter and model are deterministic for the six workloads; this is not a mechanized RV32I ISA proof. |
| PO-03 | A4 boundary event completeness | PARTIAL | model+rtl-smoke | Completeness is exercised for six model benchmarks and twelve RTL-smoke capsules, not for arbitrary firmware or full benchmark-wide RTL traces. |
| PO-04 | A5 commit-index and same-index ordering | PASS_LOCAL | model+rtl-smoke | Comparator/order checks are generated cycle-index and commit-index fixtures plus RTL-smoke export checks; full firmware-running RTL replay remains pending. |
| PO-05 | A6 precise interrupt delivery | PARTIAL | rtl-smoke+firmware-sim | Seeded interrupt evidence covers RTL-smoke interrupt-race schedules; there is no full interrupt-controller proof or benchmark-wide randomized campaign. |
| PO-06 | A7 MMIO read/write contract | PASS_LOCAL | model+formal-bmc+rtl-smoke | Current checks cover local logger/control contracts and benchmark fixtures, not a complete bus-protocol proof. |
| PO-07 | A8 external memory mutation contract | ASSUMPTION_ONLY | documentation | The current six workloads do not include DMA or external RAM mutation RTL tests; the contract is specified but not exercised. |
| PO-08 | A9 deterministic safety property checker | PASS_LOCAL | formal-bmc+rtl-smoke+firmware-sim | Checks cover local property/signature RTL contracts and smoke alignment, not every future safety property. |
| PO-09 | A10 finite prefix sufficiency | PASS_LOCAL | model+formal-bmc+rtl-smoke | Prefix behavior is checked for model/firmware-sim workloads and bounded recorder contracts, not a full processor/replay theorem. |
| PO-10 | A11 recorder noninterference separate from sufficiency theorem | ASSUMPTION_ONLY | documentation | No perturbation or runtime-overhead proof exists yet; mapped and benchmark-wide hardware results are pending. |
