# bug_interrupt_race

Benchmark description for an RV32I firmware bug where a foreground loop and an interrupt handler race over a pending-event flag. This file describes the intended benchmark only; the main firmware owner should provide the actual Phase 1/2 source.

## Failing Intent

The failing firmware uses a shared `pending` flag or small counter to hand off external interrupt work from an ISR to the foreground loop. The foreground loop reads the flag, begins processing, and then clears it with a store. If a new interrupt arrives between the read and the clear, the ISR sets the flag, but the foreground clear overwrites that new event.

The bug should be exposed by a recorded order where at least two interrupts are delivered close together and one event is lost because the clear is not atomic with respect to ISR updates.

## Fixed Intent

The fixed firmware must avoid losing ISR-produced events. Acceptable fixes include using a monotonic event counter, disabling the relevant interrupt around the consume-and-clear sequence, draining all pending hardware events before clearing software state, or using a ring buffer with synchronized head/tail updates.

For the same interrupt schedule, every delivered interrupt that represents a device event should be processed exactly once unless the device contract explicitly coalesces it.

## Expected Property Violation

The number of processed foreground events must equal the number of delivered device events:

```text
processed_event_count == delivered_event_count
```

The failing run should show a lower processed count than delivered count, with the lost event occurring after the foreground has observed the old pending flag but before it clears the shared state.

## Expected Capsule Contents

The replay capsule should contain the precise interleaving that makes the race deterministic:

- External interrupt deliveries, including interrupt ID/cause and delivery order.
- Interrupt enable and pending state around the foreground read/clear sequence.
- ISR entry/exit context, including `mepc`, `mcause`, and any nesting-relevant mask state.
- MMIO claim/status reads and completion/ack writes if the interrupt source is modeled as a device.
- Memory accesses to the shared pending flag or event counter that are required by the property checker.
- Final delivered and processed event counts.

## Replay Validation Target

Replay of the failing capsule must reproduce the lost-event interleaving and the mismatched delivered/processed counts. Replay of the fixed firmware against the same interrupt deliveries should process all recorded events exactly once or meet the explicitly documented coalescing rule.
