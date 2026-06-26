# Final Reviewer Report

Generated review date: 2026-06-26.

This simulated panel uses the evidence in `docs/conference_readiness_dashboard.md` as the authority. It awards mapped credit only for the scoped tiny iCE40 PASS rows, and does not award credit for ungenerated full-core mapped overhead, power, compiler-backed firmware, paper PDF, or runtime-overhead results. The source-of-truth path for the missing compiler and LaTeX evidence is `.github/workflows/final-reproduce.yml`; claims remain blocked until remote CI artifacts prove them.

## Hardware Architecture Reviewer

Accept/reject leaning: borderline; full RTL replay is now strong, but hardware-cost evidence is still missing.

Top strengths:

- Clear record-side RTL module split: event tap, classifier, slicer, buffer, property checker, control/status, and wrapper integration.
- PicoRV32 wrapper smokes exercise failing, fixed, and selected no-failure cases.
- Verilator harness now builds and runs record/replay modes with 45/45 evaluated full RTL rows PASS, with the host-side replay limitation documented.
- Generic Yosys evidence is present and labeled as preliminary.
- Scoped tiny iCE40 mapped evidence exists for `replaycapsule_tiny_baseline` and `replaycapsule_recorder_tiny`.

Top weaknesses:

- Firmware-running RTL replay is host-driven and uses verified HEX fallback images locally; compiler-backed replay now depends on the final CI workflow.
- The attempted iCE40 mapped flow now has scoped tiny baseline and recorder PASS rows, but the full PicoRV32 and integrated wrapper rows still fail placement.
- Current-harness runtime wall-clock rows are measured, but baseline slowdown and cycle perturbation are not.
- Hardware figures are still stronger as architecture evidence than as implementation proof.

Required fixes before submission:

- Retarget or constrain the mapped flow and generate mapped resource/timing PASS rows, or remove hardware-overhead claims from the paper.

Fatal blockers:

- G13 and G14 in the dashboard; G16 for paper delivery.

## Formal Methods Reviewer

Accept/reject leaning: weak reject for proof strength, acceptable as an engineering proof sketch if claims stay scoped.

Top strengths:

- Assumptions are explicit and separated from evidence.
- Proof sketch is induction over commit index with deterministic-step and boundary-event cases.
- Proof-obligation matrix links assumptions to generated evidence and limits.

Top weaknesses:

- No mechanized end-to-end theorem.
- Recorder correctness is an assumption.
- External memory mutation and DMA are assumption-only.
- Commit-index semantics are not connected to a complete ISA proof.
- Formal coverage is bounded and local.

Required fixes before submission:

- Keep theorem wording conditional.
- Do not call the proof end-to-end or complete.

Fatal blockers:

- None if the paper frames formal evidence as bounded local support.

## EDA/Synthesis Reviewer

Accept/reject leaning: reject for EDA/hardware-results track without mapped flow.

Top strengths:

- Generic Yosys cell-count scripts exist.
- Baseline core, recorder top, and wrapper are separated.
- Yosys + nextpnr-ice40 is attempted by script, and failed rows point to raw logs.
- Scoped `replaycapsule_tiny_baseline` and `replaycapsule_recorder_tiny` iCE40 place-and-route rows pass with LUT/FF/Fmax numbers.

Top weaknesses:

- No full-core or baseline-versus-wrapper mapped LUT/FF/BRAM/Fmax PASS comparison.
- No ASIC area/timing/power report.
- The current iCE40 target cannot place the exposed full-core top-level designs because of IO/BEL pressure.
- No runtime overhead measurement against a comparable baseline.
- Paper cannot support hardware-cost conclusions.

Required fixes before submission:

- Add a placeable constrained FPGA top, retarget to a suitable FPGA/vendor flow, or add an OpenROAD setup, then regenerate `results/processed/mapped_synthesis.csv`.

Fatal blockers:

- G13 and G14 in the dashboard.

## Systems/Debug Reviewer

Accept/reject leaning: borderline if positioned as a scoped single-hart RTL replay artifact, reject if positioned as complete hardware implementation evidence.

Top strengths:

- The failure model is specific to interrupt/MMIO timing.
- Baselines include non-winning rows and failure-by-design rows.
- Negative tests check missing, duplicate, shifted, reordered, and corrupted events.
- Full RTL record/replay agrees for all 45 evaluated benchmark/variant/seed rows.

Top weaknesses:

- Longer workloads are synthetic model scaling, not firmware-running RTL.
- Core-only capsule baseline is unavailable.
- Firmware compiler path is not external-toolchain-backed locally; generated HEX fallback rows are verified but marked as fallback.
- No baseline perturbation results.

Required fixes before submission:

- Keep full RTL replay language scoped to the evaluated host-driven Verilator harness.
- Add longer firmware/RTL workloads if scaling is a major claim.

Fatal blockers:

- None for evaluated host-driven full RTL replay; G13/G14 remain fatal for hardware-cost claims.

## Artifact Evaluation Reviewer

Accept/reject leaning: accept artifact structure, reject submission readiness until missing gates are clear in the paper.

Top strengths:

- One-command local path exists.
- Toolchain status is generated.
- Artifact package script and hash manifests exist.

Top weaknesses:

- Local Verilator replay now builds with the available C++ path; the RISC-V compiler is still missing locally, but verified HEX fallback images exist and the final CI workflow requires compiler-backed replacement rows.
- Paper PDF build depends on LaTeX availability.
- Full RTL rows are all-PASS; mapped evidence is scoped to tiny wrappers while full-core mapped overhead remains blocked.
- Final CI is newly added and needs remote validation, uploaded logs, and generated artifacts.
- Artifact package should be regenerated after every evidence change.

Required fixes before submission:

- Run `.github/workflows/final-reproduce.yml` and attach logs/uploaded artifacts.
- Confirm `paper/main.pdf` builds.

Fatal blockers:

- G16 until the paper build is a PASS.

## Skeptical Novelty Reviewer

Accept/reject leaning: reject if novelty is broad; possible weak accept only with a narrow event-sufficiency framing and stronger evidence.

Top strengths:

- Narrow distinction: commit-indexed interrupt/MMIO boundary events for single-hart embedded RV32I replay.
- One event stream feeds property checking and replay capsule export.
- Ablation evidence shows which classes matter in generated scopes.

Top weaknesses:

- Deterministic replay and trace compression are well-known broad areas.
- RISC-V trace/debug standards are adjacent and must be handled carefully.
- Global minimality is not proved.
- Full-system replay is out of scope.
- Hardware evidence is not yet strong enough for bold conference claims.

Required fixes before submission:

- Keep related work specific.
- Avoid first-ever, replacement, outperforms, and minimality claims.

Fatal blockers:

- None if the paper uses the safe contribution wording and keeps evidence scoped.
