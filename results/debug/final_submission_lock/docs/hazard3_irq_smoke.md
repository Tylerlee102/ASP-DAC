# Hazard3 IRQ Smoke

Status: `PASS`.

This focused smoke builds a tiny RV32I+Zicsr firmware image for the vendored Hazard3 core, asserts a machine external interrupt through a simple AHB memory/MMIO shell, requires the ISR to acknowledge the interrupt, and requires foreground code to write a done marker after returning through `mret`.

| Check | Status | Cycles | ISR writes | Ack writes | Done | IRQ final | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `hazard3_true_isr_smoke` | `PASS` | 76 | 1 | 1 | 1 | 0 | `results/raw/hazard3_irq_smoke/vvp_run.txt` |

Allowed from this evidence:

- The vendored Hazard3 candidate can execute a real machine external interrupt handler in a focused Icarus testbench.
- The handler uses standard CSR interrupt setup and `mret`, not PicoRV32 custom IRQ instructions.

Do not claim from this evidence:

- ReplayCapsule wrapping around Hazard3.
- Hazard3 ReplayCapsule record/replay or v2 MMIO+IRQ replay-consumer stimulus.
- Board/silicon integration.
