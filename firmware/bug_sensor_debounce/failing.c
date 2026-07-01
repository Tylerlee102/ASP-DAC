#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t first_sample = rc_read_sensor();
    uint32_t second_sample = rc_read_sensor();
    if (first_sample > RC_SENSOR_THRESHOLD) {
        (void)second_sample;
        for (volatile uint32_t i = 0; i < 64; ++i) {
        }
    }
    return 0;
}
