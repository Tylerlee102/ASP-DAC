# firmware_bug_agent

Subagent handoff for ReplayCapsule-RV firmware benchmark descriptions.

## Scope

Owned paths for this subagent:

- `firmware/bug_sensor_threshold/README.md`
- `firmware/bug_interrupt_race/README.md`
- `firmware/bug_mmio_ordering/README.md`
- `firmware/bug_stack_corruption/README.md`
- `firmware/bug_uart_command/README.md`
- `firmware/bug_watchdog_timeout/README.md`
- `docs/subagents/firmware_bug_agent.md`

This subagent creates benchmark descriptions only. Actual firmware source, build integration, Phase 1 failing implementations, and Phase 2 fixed implementations are owned by the main agent or other assigned agents.

## Completed Benchmark Contracts

Each benchmark README defines:

- Failing intent.
- Fixed intent.
- Expected property violation.
- Expected capsule contents.
- Replay validation target.

| Benchmark | Primary violation | Replay target |
| --- | --- | --- |
| `bug_sensor_threshold` | Alarm decision uses torn or wrong threshold around ISR timing. | Reproduce the incorrect alarm write, then verify the fix uses a coherent committed threshold. |
| `bug_interrupt_race` | Foreground clear loses an ISR-produced event. | Reproduce delivered/processed count mismatch, then verify every recorded event is processed once. |
| `bug_mmio_ordering` | Device observes a doorbell before command state is complete. | Reproduce stale/incomplete command consumption, then verify ordered publication. |
| `bug_stack_corruption` | Interrupt-time stack use corrupts guarded foreground state. | Reproduce guard/context corruption, then verify protected stack state survives. |
| `bug_uart_command` | Parser executes a command that was not received as a complete valid UART frame. | Reproduce the incorrect side effect, then verify invalid frames are rejected. |
| `bug_watchdog_timeout` | Blocking wait lets the watchdog reset before controlled recovery. | Reproduce deadline crossing/reset, then verify kick, abort, or timeout occurs first. |

## Coordination Notes

- The README files intentionally avoid concrete symbols, addresses, and source structure so the firmware owner can map them to the eventual harness.
- Property checkers should consume capsule metadata rather than infer intent from source-only comments.
- Capsule content lists are expected inputs to the ReplayCapsule schema discussion; they are not a final serialized format.
- If implementation constraints force a narrower scenario, keep the same observable violation and replay validation target whenever possible.
