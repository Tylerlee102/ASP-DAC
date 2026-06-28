# Commanded Actuator Limit Benchmark

This benchmark models firmware that accepts an external command and drives an
actuator. The failing variant writes an unsafe actuator value when the command
register contains the trigger value. The fixed variant programs the safe
configuration word and clamps the actuator command.
