# Second-Core IRQ Candidate

Status: `PASS`.

Hazard3 is vendored as a pinned interrupt-capable RV32 candidate. This source and frontend-readiness gate proves the candidate has real interrupt/CSR machinery and can be parsed by the local Verilator frontend, but it does not by itself prove firmware execution or ReplayCapsule record/replay on Hazard3. The separate focused ISR firmware smoke is tracked in `docs/hazard3_irq_smoke.md`, and the seeded v2 ReplayCapsule MMIO+IRQ replay-consumer benchmark matrix is tracked in `docs/hazard3_v2_replay_smoke.md`.

| Check | Status | Evidence | Notes |
| --- | --- | --- | --- |
| `hazard3_source_present` | `PASS` | `third_party/hazard3/hdl` | Vendored Hazard3 HDL is present with 38 Verilog/include files. |
| `hazard3_filelist_present` | `PASS` | `third_party/hazard3/hdl/hazard3.f` | Filelist names 21 core source files including the IRQ controller. |
| `hazard3_license_tracked` | `PASS` | `third_party/hazard3/LICENSE` | Apache-2.0 license is vendored with the candidate core. |
| `hazard3_source_pinned` | `PASS` | `third_party/hazard3/VENDORED.md` | Vendored metadata pins upstream commit 8af992930f71a69b0e06c38734c1094f41a05ca0. |
| `hazard3_declares_rv32i` | `PASS` | `third_party/hazard3/Readme.md` | README declares RV32I/RV32E scope and CSR support. |
| `hazard3_external_irq_ports` | `PASS` | `third_party/hazard3/hdl/hazard3_cpu_1port.v` | Top-level candidate exposes external, software, and timer interrupt inputs. |
| `hazard3_irq_configurable` | `PASS` | `third_party/hazard3/hdl/hazard3_config.vh` | Candidate has configurable external IRQ count and trap-vector reset/writability parameters. |
| `hazard3_csr_interrupt_support` | `PASS` | `third_party/hazard3/hdl/hazard3_csr.v` | CSR block implements standard machine trap/interrupt CSRs needed for true ISR replay work. |
| `hazard3_mret_decode_present` | `PASS` | `third_party/hazard3/hdl/hazard3_decode.v` | Candidate decodes or documents MRET, enabling real interrupt-return firmware instead of wrapper-only IRQ pulses. |
| `hazard3_irq_controller_present` | `PASS` | `third_party/hazard3/hdl/hazard3_irq_ctrl.v` | Candidate includes an IRQ controller module with external interrupt pending logic. |
| `hazard3_frontend_lint` | `PASS` | `results/raw/second_core_irq_candidate/verilator_lint_hazard3_cpu_1port.txt` | Verilator frontend lint accepts the vendored Hazard3 single-port CPU top and filelist. |
| `hazard3_replay_scope_boundary` | `INFO` | `docs/second_core_irq_candidate.md` | This source/frontend probe is not itself a ReplayCapsule wrapper or replay result; the separate Hazard3 ISR smoke is tracked in docs/hazard3_irq_smoke.md and the seeded v2 ReplayCapsule MMIO+IRQ benchmark matrix is tracked in docs/hazard3_v2_replay_smoke.md. |

Allowed from this evidence:

- Hazard3 is a vendored, pinned, Apache-2.0 interrupt-capable second-core candidate.
- The candidate exposes external, software, and timer IRQ inputs and contains machine trap/interrupt CSR support.
- The candidate HDL filelist passes local Verilator frontend lint.

Do not claim from this evidence:

- Hazard3 firmware execution from this source/frontend probe alone; use `docs/hazard3_irq_smoke.md` for the separate focused ISR smoke.
- Hazard3 ReplayCapsule replay from this source/frontend probe alone; use `docs/hazard3_v2_replay_smoke.md` for the separate seeded v2 replay matrix.
- Cross-core behavioral equivalence or portability.

Next step: broaden beyond the current scoped Hazard3 v2 matrix only if the paper needs OS/application-suite coverage or full-diagnostic all-commit replay.
