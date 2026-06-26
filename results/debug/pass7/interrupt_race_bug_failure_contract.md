# interrupt_race_bug/failing Failure Contract

1. Expected action: unmask PicoRV32 IRQs, enter a command-marked critical section by writing `1` to `0x4000000c`, and keep that section open long enough for an interrupt to be delivered before config clears it.
2. Required event: `EV_MMIO_WRITE COMMAND_ADDR=1` followed by `EV_INTERRUPT_ENTER` while `critical_section_active` is true.
3. Expected property ID: 2.
4. Expected window: shortly after the command write and before the first config write clears the critical section.
5. Fallback HEX behavior: executes from reset PC `0x00000080`, unmasks IRQs with PicoRV32 `maskirq`, delays in the IRQ window, and observes property 2.
6. Compiler-backed before-state: ELF entry was linked at `0x00000000` while RTL reset fetched at `0x00000080`; the failing logic was not reached in the failing row, producing `NO_EXPECTED_FAILURE`.
7. First semantic mismatch: reset/link placement mismatch prevented the compiler image from starting at the RTL reset contract. The C failing source also needed an explicit PicoRV32 IRQ unmask and volatile delay window to match the benchmark contract.
