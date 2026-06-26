# mmio_ordering_bug/failing Failure Contract

1. Expected action: write a nonzero actuator value before the safe config magic is visible.
2. Required event: `EV_MMIO_WRITE ACTUATOR_ADDR=25` before `EV_MMIO_WRITE CONFIG_ADDR=0x0000cafe`.
3. Expected property ID: 5.
4. Expected window: immediate first actuator write in `main`.
5. Fallback HEX behavior: executes from reset PC `0x00000080`, writes actuator before config, and observes property 5.
6. Compiler-backed before-state: compiler firmware built successfully, but the ELF was linked at `0x00000000` and the RTL reset PC was `0x00000080`. This short program ended before the reset address, so the unsafe MMIO order was never executed.
7. First semantic mismatch: compiler image placement did not match the RTL reset contract.
