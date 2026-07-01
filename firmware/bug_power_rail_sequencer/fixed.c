#include "../common/mmio.h"

static uint32_t rail_enable_mask(uint32_t sensor, uint32_t command) {
    uint32_t mask = 0u;
    if (sensor > RC_SENSOR_THRESHOLD) {
        mask |= 0x1u;
    }
    if (command == 0x55u) {
        mask |= 0x2u;
    }
    return mask;
}

int main(void) {
    rc_workload_delay();
    uint32_t sensor = rc_read_sensor();
    uint32_t command = rc_read_command();
    uint32_t rails = rail_enable_mask(sensor, command);

    if (rails != 0u) {
        rc_write_config(RC_CONFIG_SAFE_MAGIC);
        rc_write_actuator(rails);
    }
    return 0;
}
