#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t sensor = rc_read_sensor();
    if (sensor > RC_SENSOR_THRESHOLD) {
        rc_write_config(RC_CONFIG_SAFE_MAGIC);
        rc_write_actuator(RC_ACTUATOR_SAFE);
    }
    return 0;
}
