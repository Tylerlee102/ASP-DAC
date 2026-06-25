# bug_stack_corruption

Benchmark description for an RV32I firmware bug where interrupt timing corrupts stack-resident state. This file describes the intended benchmark only; the main firmware owner should provide the actual Phase 1/2 source.

## Failing Intent

The failing firmware uses a stack layout that is unsafe under an interrupt delivered at a high stack-water mark. A trap frame, ISR-local buffer, nested call frame, or command parser frame overwrites a neighboring stack canary, saved return address, saved register, or foreground local value.

The bug should be exposed by a run where the foreground path reaches a deep or large stack frame, an interrupt arrives, and the ISR stack use writes outside the safe region.

## Fixed Intent

The fixed firmware must preserve stack-resident foreground state across interrupt entry and return. Acceptable fixes include reserving enough stack for worst-case ISR nesting, using a separate interrupt stack, bounding local buffers, validating command lengths before stack copies, or adding a guard/canary check with a safe failure path.

For the same interrupt timing and input bytes, the fixed firmware should return to the foreground path with saved registers, return address, canary, and protected locals unchanged.

## Expected Property Violation

Protected stack state must remain stable across the interrupt window:

```text
stack_guard_after_isr == stack_guard_before_isr
saved_context_after_isr == saved_context_before_isr
```

The failing run should show a corrupted canary, saved register, return address, or protected local value after ISR return. The corruption must be attributable to the recorded interrupt timing and stack writes, not to an unconstrained replay artifact.

## Expected Capsule Contents

The replay capsule should include enough context to reproduce the stack overwrite:

- Foreground input or state that drives the stack to the high-water condition.
- Interrupt delivery point while the vulnerable frame is live.
- Trap entry/exit context, including `sp`, `mepc`, `mcause`, and saved register metadata if recorded.
- Memory writes in the stack and guard region needed by the checker.
- Any UART/MMIO input bytes that affect stack frame size, parser length, or nested call depth.
- Final guard/context values observed after ISR return.

## Replay Validation Target

Replay of the failing capsule must reproduce the same interrupt-at-high-water condition and the same protected stack corruption. Replay of the fixed firmware against the same event sequence should preserve the guarded state and return through the expected control path.
