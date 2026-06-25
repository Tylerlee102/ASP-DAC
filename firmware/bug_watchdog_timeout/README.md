# bug_watchdog_timeout

Benchmark description for an RV32I firmware bug where watchdog servicing is delayed or ordered incorrectly around blocking MMIO and interrupt timing. This file describes the intended benchmark only; the main firmware owner should provide the actual Phase 1/2 source.

## Failing Intent

The failing firmware services the watchdog only after a blocking MMIO poll, long critical section, or interrupt-disabled device transaction. If the device remains busy for the recorded number of polls, the watchdog deadline passes before the firmware writes the watchdog kick register, causing an unexpected watchdog reset.

The bug should be exposed by a run where the device busy/status values, interrupt mask state, and watchdog deadline combine to make the timeout deterministic.

## Fixed Intent

The fixed firmware must make watchdog progress bounded and explicit. Acceptable fixes include adding a device poll timeout, servicing the watchdog before entering a known bounded wait, breaking long waits into deadline-checked chunks, re-enabling interrupts where safe, or aborting the device operation before the watchdog window expires.

For the same device busy sequence, the fixed firmware should either service the watchdog before the deadline or take a controlled error path that avoids an unexpected reset.

## Expected Property Violation

The firmware must not allow an unexpected watchdog reset while it is in a recoverable device wait:

```text
recoverable_wait_active && watchdog_deadline_reached => controlled_timeout_or_kick_before_reset
```

The failing run should show a watchdog reset event before the firmware reaches its intended kick or controlled timeout path.

## Expected Capsule Contents

The replay capsule should contain the timing and MMIO observations needed to make the timeout deterministic:

- Watchdog configuration, deadline/window metadata, and watchdog kick MMIO writes.
- Device busy/status MMIO read values that keep the firmware in the blocking wait.
- Interrupt enable/disable state and timer interrupt deliveries relevant to deadline advancement.
- Watchdog timeout/reset event, including the program counter or phase where reset occurred if recorded.
- Any cycle, tick, or logical-time markers used by ReplayCapsule to determine deadline crossing.
- Final reset reason/status MMIO value used by the property checker.

## Replay Validation Target

Replay of the failing capsule must reproduce the watchdog deadline crossing and reset at the same firmware phase. Replay of the fixed firmware against the same device busy sequence should service, abort, or timeout before an unexpected watchdog reset occurs.
