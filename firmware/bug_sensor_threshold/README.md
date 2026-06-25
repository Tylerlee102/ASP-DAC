# bug_sensor_threshold

Benchmark description for an RV32I firmware bug where a sensor alarm decision can use a torn or wrong threshold value around interrupt timing. This file describes the intended benchmark only; the main firmware owner should provide the actual Phase 1/2 source.

## Failing Intent

The failing firmware accepts a threshold update from the foreground command path while a timer-driven sensor ISR samples an ADC-like MMIO register and updates an alarm GPIO/MMIO register. The threshold value is assembled or published in multiple steps, so the ISR can observe a partially updated threshold or a threshold from the wrong configuration epoch.

The bug should be exposed by an event order where a threshold update is in progress, a sensor interrupt fires, the ISR reads the sensor sample, and the alarm comparison uses the intermediate threshold value.

## Fixed Intent

The fixed firmware publishes threshold updates atomically with respect to the sensor ISR. Acceptable fixes include committing the new threshold only after the command is fully parsed, disabling the relevant interrupt around the commit, using a versioned shadow value, or otherwise ensuring the ISR sees either the old complete threshold or the new complete threshold.

For the same recorded UART bytes, ADC samples, and interrupt timing, the fixed firmware should make the alarm decision from the committed threshold for that sample epoch.

## Expected Property Violation

For every sensor sample event, the alarm output must match:

```text
alarm_asserted == (sample_value >= committed_threshold_value)
```

The failing run should contain at least one sample where the alarm MMIO/GPIO write disagrees with the threshold value that was actually committed before or after the interrupted update. The violation may appear as a false alarm below the committed threshold or a missed alarm above it.

## Expected Capsule Contents

The replay capsule should contain enough exogenous events and architectural context to reproduce the threshold race:

- UART RX bytes or equivalent command input that begins and completes the threshold update.
- Timer interrupt delivery point for the sensor ISR, including interrupt enable state at delivery.
- ADC/sample MMIO read value used by the ISR.
- Alarm output MMIO/GPIO write produced by the comparison.
- Threshold commit metadata needed by the checker, such as the old threshold, new threshold, and commit point.
- Trap entry/exit context relevant to replay, including `mepc`, interrupt cause, and interrupt mask state if the implementation records it.

## Replay Validation Target

Replay of the failing capsule must reproduce the same ISR interleaving and the same incorrect alarm output for the recorded sample. Replay of the fixed firmware against the same event sequence should keep the threshold observation coherent and should not trigger the property violation.
