#include "../common/mmio.h"

static uint32_t clamp_pwm(uint32_t value) {
    return value > 100u ? 100u : value;
}

int main(void) {
    rc_workload_delay();
    uint32_t raw_temperature = rc_read_sensor();
    uint32_t service_mode = rc_read_command();
    uint32_t filtered_temperature = (raw_temperature * 3u + 650u) >> 2;
    uint32_t requested_pwm = 0u;

    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    if (filtered_temperature > RC_SENSOR_THRESHOLD) {
        requested_pwm = 70u + ((filtered_temperature - RC_SENSOR_THRESHOLD) >> 1);
    }
    if (service_mode == 0x55u) {
        requested_pwm += 120u;
    }

    rc_write_actuator(clamp_pwm(requested_pwm));
    return 0;
}
