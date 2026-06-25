# bug_mmio_ordering

Benchmark description for an RV32I firmware bug where device-visible MMIO operations occur in an unsafe order. This file describes the intended benchmark only; the main firmware owner should provide the actual Phase 1/2 source.

## Failing Intent

The failing firmware prepares a device command in memory or shadow registers, then writes an MMIO doorbell/control register before all command fields are valid from the device perspective. The device may observe a stale address, length, command opcode, payload byte, or status bit because the firmware omits the required ordering discipline around descriptor setup and doorbell notification.

The bug should be exposed by a replay where the device consumes the command immediately after the doorbell write and before the intended descriptor state is complete.

## Fixed Intent

The fixed firmware must make command publication explicit and ordered. Acceptable fixes include using volatile MMIO accessors, issuing the required `fence` before the doorbell write, writing descriptor fields in the documented order, and reading/acknowledging device status only after the relevant completion condition is visible.

For the same device timing, the doorbell must not become visible until the descriptor or command registers contain the complete intended command.

## Expected Property Violation

At every device doorbell/control write, the device-visible command state must match the command the firmware intended to submit:

```text
doorbell_observed => descriptor_complete_and_current
```

The failing run should show a doorbell/control MMIO write followed by a device response, interrupt, or status value that corresponds to stale or incomplete command state.

## Expected Capsule Contents

The replay capsule should capture the order-sensitive boundary between firmware and device:

- All MMIO writes to command, descriptor, status, and doorbell/control registers that participate in the transaction.
- Memory stores to any descriptor or command buffer the device is allowed to read.
- Device observations that are exogenous from the core's perspective, such as status register values, completion interrupts, error codes, or modeled DMA reads.
- Any ordering-relevant architectural events, including `fence` execution if the implementation records it.
- The intended command identity or checker metadata needed to compare expected descriptor state with device-observed state.

## Replay Validation Target

Replay of the failing capsule must reproduce the same device-visible ordering and the same stale or incomplete command consumption. Replay of the fixed firmware against the same device responses should show the doorbell after the command state is complete and should satisfy the ordering property.
