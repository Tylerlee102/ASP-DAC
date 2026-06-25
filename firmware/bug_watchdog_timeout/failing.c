#include "../common/mmio.h"

int main(void) {
    uint32_t sensor = rc_read_sensor();
    if (sensor > RC_SENSOR_THRESHOLD) {
        for (volatile uint32_t i = 0; i < 256; ++i) {
        }
    }
    *RC_MMIO_COMMAND = 0xfeedu;
    return 0;
}

