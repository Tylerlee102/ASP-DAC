#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t sensor = rc_read_sensor();
    if (sensor > RC_SENSOR_THRESHOLD) {
        for (volatile uint32_t i = 0; i < 64; ++i) {
        }
    }
    return 0;
}
