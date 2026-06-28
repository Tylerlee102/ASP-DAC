# Late Config Sequence Benchmark

This benchmark models firmware that sequences actuator writes around a safety
configuration register. The failing variant drives the actuator before the safe
configuration word is visible. The fixed variant establishes the safe
configuration before the actuator write.
