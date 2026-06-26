# ReplayCapsule-RV Novelty Matrix

Status date: 2026-06-25

This file states conservative, source-aware novelty language for ReplayCapsule-RV. It is aligned with the local architecture, event model, capsule format, research plan, and replay sufficiency theorem docs. It should be updated after RTL, firmware benchmarks, replay harness results, and synthesis/evaluation results are available. Until then, treat this as a claim-safety document rather than a final paper contribution section.

## Safe Top-Line Novelty Statement

ReplayCapsule-RV is best positioned as a narrow embedded RISC-V replay artifact: a hardware/architecture prototype that captures and replays firmware-visible nondeterministic events needed to reproduce RV32I failures involving asynchronous interrupts and MMIO. The defensible novelty is the combination of an event-sufficiency replay contract, single-hart RV32I embedded scope, commit-indexed boundary events, and an interrupt/MMIO replay boundary. It should be framed as complementary to RISC-V trace/debug standards, assertion-based hardware verification, FPGA checkpoint/replay systems, and memory-safety hardware.

Do not claim first deterministic replay, first hardware replay, first embedded logging, first RISC-V trace, or full-device determinism.

## Claim Matrix

| Potential contribution | Already covered by prior work | Risk level | Safe claim wording | Evidence needed for stronger claim |
| --- | --- | --- | --- | --- |
| Event-sufficient failure capsule instead of full instruction/signal trace | ReTrace logs minimal VM nondeterminism and expands traces later; E-Trace/N-Trace reconstruct control flow; post-silicon debug compresses/selects internal trace signals. | Medium | "ReplayCapsule-RV targets a replay-driving event capsule rather than a full instruction trace or internal signal trace." | Formal event-sufficiency definition; proof sketch or replay equivalence argument; measured capsule size versus clear baselines. |
| Commit-indexed boundary replay | Deterministic replay systems already order nondeterministic events; trace standards and debug systems can carry timing/context information. | Medium | "ReplayCapsule-RV anchors boundary events to RV32I commit-index/retire-count time, with optional cycle deltas only when wait-state behavior is replay-visible." | Tests showing replay equivalence under same commit-index events; evidence that optional cycle fields are sufficient for configured wait-state cases. |
| RV32I embedded replay under interrupts | FlashBox logs embedded nondeterministic events including interrupts; E-Trace/N-Trace trace traps caused by interrupts/exceptions; debug modules expose triggers/run control. | Medium | "The prototype specializes replay capture for RV32I embedded failures where interrupt delivery is a replay input." | Exact interrupt event schema; deterministic injection mechanism; tests covering nested, disabled, pending, and timer/external interrupt cases. |
| MMIO replay boundary | Peripheral modeling/emulation and firmware fuzzing work already treats MMIO and interrupts as central nondeterministic sources; Conware warns naive MMIO replay can fail when behavior changes. | High | "ReplayCapsule-RV treats MMIO observations as part of the replay contract for the observed failure execution." | MMIO read/write classification; side-effect model; examples with ready bits, interrupt-status registers, write-one-to-clear, and timing-sensitive peripherals. |
| Hardware-assisted capture | Security Capsules, Hassert, hardware runtime verification, FPGA monitors, debug modules, and post-silicon trace buffers already add hardware observers/checkers. | Medium | "ReplayCapsule-RV uses hardware assist for replay capture rather than for assertion checking, security monitoring, or generic observability." | RTL/spec for capture unit; synthesis area/timing/power; perturbation analysis. |
| Replay of failing execution rather than online violation detection | Runtime verification and assertion monitors detect property violations online. | Low | "ReplayCapsule-RV is a post-failure reproduction mechanism, not a runtime-verification monitor." | Demonstrations where a failure is captured once and replayed offline with the same visible failure. |
| Complement to RISC-V E-Trace/N-Trace | E-Trace/N-Trace are ratified trace standards with branch history, trap tracing, optional timestamps/context/data payloads, and trace sinks/control. | High | "ReplayCapsule-RV complements standard trace by adding replay semantics for nondeterministic interrupt/MMIO events." | Mapping to or coexistence with E-Trace/N-Trace packets; storage and bandwidth comparison; decoder/replayer integration. |
| Complement to RISC-V Debug Module | Debug spec already provides halt/resume, triggers, system bus access, and debug transport. | Low | "ReplayCapsule-RV may use debug infrastructure for control or extraction, but the capsule format and replay contract are separate." | Debug integration plan; compliance notes; proof that replay works without relying on unspecified debug behavior. |
| FPGA/emulation replay differentiation | REMU and Vidi already provide deterministic replay/checkpointing for FPGA emulation or reconfigurable hardware; DESSERT/StateMover/StateReveal cover snapshots/debug windows. | High | "ReplayCapsule-RV is not a generic FPGA checkpoint/replay framework; it targets an RV32I firmware-visible event stream." | Boundary diagram; comparison table against REMU/Vidi; experiment showing replay from event capsules rather than full FPGA state snapshots. |
| Failure artifact for reproducibility | Many systems create logs, traces, checkpoints, or black-box records. | Medium | "ReplayCapsule-RV packages replay inputs and metadata for reproducing a scoped embedded failure." | File/spec definition; versioning; deterministic replayer; reproducibility tests across repeated replays. |
| Debugging memory-corruption or security failures | CHERI/HardBound and related hardware memory safety prevent/contain memory errors; Security Capsules/SPECS-style systems detect security-relevant violations. | High | "ReplayCapsule-RV may help reproduce failures caused by memory or security bugs, but it does not enforce memory safety or security properties." | Case studies only; do not generalize beyond observed failures. |

## Novelty Boundary by Baseline

| Baseline | What not to claim | Defensible distinction |
| --- | --- | --- |
| Security Capsules | Do not claim a new capsule concept or security assertion validation. | ReplayCapsule-RV uses capsule language for replay evidence, not security assertion checking. |
| Hassert | Do not claim new assertion-to-hardware verification. | ReplayCapsule-RV captures replay events instead of synthesizing or accelerating assertions. |
| ENCORE | Do not claim new FPGA-accelerated processor verification or live differential checking. | ReplayCapsule-RV records a failing execution for deterministic replay, not continuous DUT/reference comparison. |
| E-Trace | Do not claim RISC-V instruction tracing is missing interrupt support. | E-Trace reconstructs control flow; ReplayCapsule-RV defines replay inputs for nondeterministic external observations. |
| N-Trace | Do not compete as a trace standard. | N-Trace encodes program-flow trace; ReplayCapsule-RV packages replay-driving events. |
| ReTrace | Do not claim minimal-nondeterminism replay is new. | ReplayCapsule-RV moves the idea from VM/IA32 software replay to an embedded RV32I hardware event boundary. |
| REMU | Do not claim FPGA deterministic replay is new. | ReplayCapsule-RV avoids claiming full bit/cycle visibility and focuses on firmware-visible interrupt/MMIO replay. |
| Vidi | Do not claim reconfigurable-hardware record/replay is new. | ReplayCapsule-RV is ISA/firmware-centric rather than FPGA channel-centric. |
| FlashBox | Do not claim first embedded nondeterministic event logger. | ReplayCapsule-RV can claim a richer RV32I replay contract if it demonstrably includes interrupt timing and MMIO observations. |
| Post-silicon trace compression | Do not claim trace compression superiority. | ReplayCapsule-RV selects events by replay sufficiency, not generic state observability. |
| Hardware memory safety | Do not claim prevention or containment. | ReplayCapsule-RV helps reproduce, not prevent, failures. |

## Recommended Paper Wording

Use language like:

> ReplayCapsule-RV explores whether a single-hart RV32I target can replay embedded failures from an event-sufficient capsule that records commit-indexed firmware-visible nondeterminism introduced by interrupts and MMIO. Unlike processor trace standards that reconstruct control flow, assertion monitors that detect property violations, or FPGA emulation frameworks that checkpoint hardware state, the capsule is intended to drive deterministic re-execution of the failing firmware path.

Avoid language like:

> ReplayCapsule-RV is the first hardware deterministic replay system for RISC-V.

> ReplayCapsule-RV replaces E-Trace/N-Trace.

> ReplayCapsule-RV guarantees deterministic replay for arbitrary peripherals.

> ReplayCapsule-RV provides memory safety or security validation.

## Source Verification Gaps

Resolve these before submitting a paper or making public claims:

1. Read the full Security Capsules paper before making detailed claims about capsule structure, monitored signals, or overhead/evaluation.
2. Read the full Hassert paper before making detailed claims about replay-like debug, supported assertions, FPGA resources, or limitations.
3. Read the full REMU paper before making detailed claims about its checkpoint/replay boundary, replay mechanism, or measured results.
4. Read the full FlashBox paper before making detailed claims about whether it performs deterministic replay or only postmortem event logging.
5. Survey RISC-V data trace and N-Trace future data/bus trace support before saying MMIO is outside standards.
6. Add local evaluation evidence before making any compression, overhead, replay-success, or coverage claims.
7. Confirm whether optional cycle-delta replay is needed for each benchmark; otherwise keep claims at commit-index architectural replay.
