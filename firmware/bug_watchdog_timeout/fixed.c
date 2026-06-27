#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    for (uint32_t i = 0; i < 4; ++i) {
        *RC_MMIO_COMMAND = 0xfeedu;
        (void)rc_read_sensor();
    }
    return 0;
}
