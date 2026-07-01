# bug_platform2_config_order

Alternate MMIO-profile configuration-ordering benchmark.

The failing firmware writes a nonzero actuator command in the alternate
`0x4000_0040` profile before publishing the safe configuration word. The fixed
firmware writes the configuration word first, then publishes the actuator value.
