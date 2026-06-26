# stack_corruption_bug/failing Failure Contract

1. Expected action: perform a volatile store into the property checker's protected stack/RAM window.
2. Required event: `EV_STORE` to an address in `[0x00001000, 0x00001400)`, specifically the failing source's `0x00001010` write.
3. Expected property ID: 4.
4. Expected window: the first protected-memory store in `main`.
5. Fallback HEX behavior: executes from reset PC `0x00000080`, stores `0xdeadbeef` into `0x00001010`, and observes property 4.
6. Compiler-backed before-state: the compiler-built source preserved the volatile store, but the ELF was linked at `0x00000000` while the RTL reset PC was `0x00000080`. The short failing program did not execute from reset, so no protected store reached the checker.
7. First semantic mismatch: compiler image placement did not match the RTL reset contract. The monitored address itself is consistent with `rtl/property_checker.sv`.
