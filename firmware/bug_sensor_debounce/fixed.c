#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t first_sample = rc_read_sensor();
    if (first_sample > RC_SENSOR_THRESHOLD) {
        uint32_t second_sample = rc_read_sensor();
        if (second_sample > RC_SENSOR_THRESHOLD) {
            rc_write_config(RC_CONFIG_SAFE_MAGIC);
        }
        rc_write_actuator(RC_ACTUATOR_SAFE);
    }
    return 0;
}
