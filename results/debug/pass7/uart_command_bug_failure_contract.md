# uart_command_bug/failing Failure Contract

1. Expected action: read the unsafe command byte and write an unsafe actuator value.
2. Required event: `EV_MMIO_READ COMMAND_ADDR=0x55` followed by `EV_MMIO_WRITE ACTUATOR_ADDR=250`.
3. Expected property ID: 1.
4. Expected window: immediately after the command MMIO read in `main`.
5. Fallback HEX behavior: executes from reset PC `0x00000080`, observes command `0x55`, branches to the unsafe path, writes actuator `250`, and observes property 1.
6. Compiler-backed before-state: the compiler-built source read the correct MMIO address, but the ELF was linked at `0x00000000` while the RTL reset PC was `0x00000080`. The short failing program did not execute from reset, so no command read or unsafe actuator write reached the checker.
7. First semantic mismatch: compiler image placement did not match the RTL reset contract.
