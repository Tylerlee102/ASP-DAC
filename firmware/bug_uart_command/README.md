# bug_uart_command

Benchmark description for an RV32I firmware bug where UART command parsing accepts or executes the wrong command under interrupt/MMIO timing. This file describes the intended benchmark only; the main firmware owner should provide the actual Phase 1/2 source.

## Failing Intent

The failing firmware parses UART input from an RX FIFO or ISR-fed buffer without a robust frame boundary. A partial command, stale byte, overrun condition, or status/data read ordering issue causes the parser to execute a command that was not actually received as a complete valid frame.

The bug should be exposed by a recorded byte sequence where UART RX interrupts and MMIO status/data reads interleave so that the command state machine accepts a truncated, mixed, duplicated, or stale command.

## Fixed Intent

The fixed firmware must execute commands only after receiving a complete valid frame. Acceptable fixes include explicit length and checksum validation, synchronized ring-buffer head/tail handling, status-before-data UART reads according to the device contract, overrun handling that discards the partial frame, and rejecting stale buffer contents after reset or error recovery.

For the same UART bytes and interrupt timing, the fixed firmware should either execute exactly the intended valid command or reject the malformed frame without changing protected device state.

## Expected Property Violation

Protected command side effects must occur only for complete valid UART frames:

```text
protected_state_change => complete_valid_command_received
```

The failing run should show an actuator/MMIO/configuration write caused by an incomplete, malformed, duplicated, or mixed command frame.

## Expected Capsule Contents

The replay capsule should capture the UART-facing nondeterminism:

- UART RX byte values in the order observed by firmware.
- UART status register values, including ready, empty, overrun, framing, or error bits used by the parser.
- RX interrupt delivery points and interrupt mask state.
- MMIO writes or protected state changes caused by accepted commands.
- Parser/checker metadata identifying frame boundaries and command validity.
- Reset or buffer initialization state if stale bytes are part of the failing scenario.

## Replay Validation Target

Replay of the failing capsule must reproduce the same UART byte/status sequence and the same incorrect command side effect. Replay of the fixed firmware against the same capsule should reject the invalid frame or execute only the complete intended command.
