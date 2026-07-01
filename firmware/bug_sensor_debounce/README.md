# bug_sensor_debounce

This expanded benchmark models firmware that debounces a noisy sensor by reading
the sensor twice before taking an actuator action.

The failing firmware observes a high first sample, ignores the low second
sample, and spends too long in the alarm path before producing a safe actuator
response. The fixed firmware treats a high-then-low pair as noise and writes a
safe actuator value promptly.
