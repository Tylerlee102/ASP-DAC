# Related Work

ReplayCapsule-RV is closest to hardware tracing, runtime verification, post-silicon debug capture, and deterministic replay. The project should not claim those categories as new.

The safe distinction is the event-sufficiency framing for embedded RV32I replay under interrupts and MMIO, with one event stream serving both property checking and replay-capsule generation. The detailed comparison is maintained in `docs/related_work_matrix.md` and `docs/novelty_matrix.md`.

ReplayCapsule-RV is not positioned as a replacement for RISC-V E-Trace or N-Trace. Those trace mechanisms compress control-flow information and can be far smaller than raw full-instruction traces; the generated `riscv_etrace_branch_trace_estimate` rows are therefore a stronger baseline than the raw trace rows. ReplayCapsule-RV instead records commit-indexed replay-driving boundary events, including MMIO values and interrupt timing, so the comparison claim is scoped to replay sufficiency for the modeled interrupt/MMIO bug class.

| Approach | Captured object | ReplayCapsule-RV delta |
| --- | --- | --- |
| Full instruction or commit traces | Retired instruction stream or per-commit state | Records only replay-driving boundary events and property-fail context. |
| RISC-V E-Trace/N-Trace-style branch tracing | Compressed control-flow discontinuities, synchronization, and trace context | Complementary to trace reconstruction; carries MMIO values and interrupt timing needed by the replay harness. |
| Deterministic VM replay | Nondeterministic device inputs and scheduling at OS or VM granularity | Uses commit-indexed single-hart RV32I boundary events inside a firmware-running RTL harness. |
| Runtime verification monitors | Assertion outcomes and local checker state | Uses property failure as the capture trigger, then validates the event stream by record/replay comparison. |
