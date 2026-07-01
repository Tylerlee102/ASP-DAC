# bug_environmental_controller

This expanded benchmark models a small closed-loop environmental controller that
combines a filtered sensor reading with a service-mode command before driving a
fan or actuator PWM register.

- `failing.c`: applies the computed PWM directly. With the measured ambient
  temperature and service-mode command, the actuator write exceeds the safe
  limit and triggers property 1.
- `fixed.c`: writes the safe configuration word and clamps the PWM to the
  allowed actuator limit before touching the actuator register.

The benchmark is still deterministic and scoped to the ReplayCapsule MMIO
model, but its structure is closer to ordinary embedded control firmware than a
single-register micro-kernel.
