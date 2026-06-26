# Pass 7 Before-State Evidence

Source CI run: 28268835038

Current facts:
- Firmware build: 15/15 compiler-backed PASS.
- Full RTL replay: 33/45 compiler-backed PASS.
- Failing rows: interrupt_race_bug/failing seeds 1-3; mmio_ordering_bug/failing seeds 1-3; stack_corruption_bug/failing seeds 1-3; uart_command_bug/failing seeds 1-3.
- Error: NO_EXPECTED_FAILURE.
- Negative replay: 10 replay-critical corruptions rejected, 2 NA, 0 unexpected accepts.
- Paper PDF: built.

This directory freezes the failed-but-useful CI evidence before the compiler-firmware semantics fix.
