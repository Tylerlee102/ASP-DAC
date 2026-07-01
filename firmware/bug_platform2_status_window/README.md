# bug_platform2_status_window

Alternate MMIO-profile status-window benchmark.

The failing firmware acts on the first command/status sample from the alternate
`0x4000_0040` profile after the second sample has cleared. The fixed firmware
confirms the second sample before publishing a bounded actuator value.
