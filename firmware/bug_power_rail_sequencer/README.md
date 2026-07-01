# bug_power_rail_sequencer

This expanded benchmark models a simple power-rail startup sequence. Firmware
derives a rail-enable mask from sensor and command inputs, then enables rails
through the actuator register.

- `failing.c`: enables the rails before writing the safe configuration word,
  triggering property 5.
- `fixed.c`: writes the safe configuration word before enabling the same rails.

The intent is to exercise a realistic configuration-before-enable ordering bug
without adding a new property checker or a new peripheral model.
