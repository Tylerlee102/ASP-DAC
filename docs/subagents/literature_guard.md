# literature_guard Notes

Subagent: literature_guard

Owned files:
- `docs/related_work_matrix.md`
- `docs/novelty_matrix.md`
- `docs/subagents/literature_guard.md`

Status date: 2026-06-25

## Work Performed

- Checked the assigned workspace. It contained no project files or Git repository at initial inspection; other subagent docs appeared during the run, and I read the local architecture, event model, capsule format, research plan, and replay sufficiency theorem before the final update.
- Created the assigned `docs` files only.
- Built a related-work matrix for the requested baselines: Security Capsules, Hassert, ENCORE, RISC-V E-Trace, RISC-V N-Trace, ReTrace, REMU, hardware runtime verification, embedded trace reconstruction/logging, post-silicon debug trace compression, FPGA checkpoint/replay, RISC-V debug modules, hardware-assisted memory safety, and runtime verification on FPGAs.
- Used only source-backed statements where practical. When only metadata or abstracts were available, details are marked as partially verified or needing source verification.

## Guardrail Summary

The safest novelty posture is:

ReplayCapsule-RV is a scoped single-hart RV32I embedded replay prototype for failures involving interrupts and MMIO. Its claim should be event sufficiency for replay of the observed failure path using commit-indexed boundary events, not general trace reconstruction, security enforcement, assertion verification, or full-system/peripheral modeling.

The highest-risk claims are:

- "First deterministic replay" or "first hardware replay."
- "First embedded black box" or "first interrupt logger."
- "Replacement for RISC-V E-Trace, N-Trace, Trace Control Interface, or Debug Module."
- "Complete replay for arbitrary peripherals."
- "Memory safety" or "security validation."
- Any overhead, compression, area, timing, power, or replay-success result without local measurements.

## Closest Prior Work

Strongest conceptual neighbors:

1. ReTrace: minimal nondeterminism capture plus deterministic replay, but at VM/IA32/software virtualization boundary.
2. FlashBox: deployed embedded nondeterministic event logging, especially interrupts.
3. RISC-V E-Trace and N-Trace: standard RISC-V control-flow trace with trap/interrupt reconstruction.
4. REMU and Vidi: FPGA/emulation record-replay and checkpoint/replay for hardware debug.
5. ENCORE and Hassert: FPGA-accelerated verification/debug infrastructure, but oriented around differential checking or assertions.

## Safe Differentiator

ReplayCapsule-RV can safely differentiate on the combination of:

- RV32I embedded scope.
- A replay-driving capsule rather than a full trace or assertion report.
- Explicit treatment of asynchronous interrupt delivery and MMIO observations as nondeterministic replay inputs.
- Local capsule/event specifics: `IRQ_LEVEL`, optional `IRQ_TAKEN`, `MMIO_READ`, `MMIO_WRITE`, firmware/platform hashes, initial state/reset inputs, and target violation signature.
- Firmware-visible replay boundary rather than VM, full FPGA state, or generic SoC internal signal reconstruction.

This is a combination claim, not a first-ever component claim.

## Source Status Checklist

Verified enough for high-level use:

- RISC-V E-Trace v2.0 ratified official docs.
- RISC-V N-Trace v1.0 ratified official docs.
- RISC-V Trace Control Interface v1.0 official docs.
- RISC-V Debug v1.0 official docs.
- ReTrace public PDF.
- ENCORE ACM/SIGDA high-level abstract.
- Vidi public PDF/ACM metadata.
- FlashBox ACM metadata and abstract-level description.
- HardBound and CHERI high-level memory-safety positioning.

Needs full-paper verification before detailed claims:

- Security Capsules internals and evaluation.
- Hassert mechanism, limitations, and results.
- REMU mechanism/results.
- DESSERT, StateMover, StateReveal details if used as FPGA checkpoint/replay baselines.
- Post-silicon debug trace compression metrics and algorithms.
- Runtime verification monitor synthesis details beyond category-level contrast.

## Maintenance Protocol

When the main project adds implementation/evaluation details:

1. Replace scope assumptions with actual module names, event schemas, and replay contract.
2. Add a "Measured against" column only after matched experiments exist.
3. Move any "partially verified" row to "verified" only after the primary paper or official spec has been read.
4. Keep unsafe claims in the docs. They are useful paper-writing tripwires.
5. If a claim becomes stronger, add the exact evidence needed: test name, artifact path, benchmark, hardware target, and commit/result identifier.

## Suggested Next Literature Tasks

1. Read and summarize Security Capsules full paper.
2. Read and summarize Hassert full paper.
3. Read REMU and Vidi together, focusing on replay boundary and checkpoint assumptions.
4. Read FlashBox and Conware together, focusing on interrupt/MMIO replay failure modes.
5. Check whether current RISC-V trace/data-trace documents define anything close to MMIO value replay.
