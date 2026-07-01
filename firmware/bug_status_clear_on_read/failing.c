#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t latched_status = rc_read_command();
    uint32_t cleared_status = rc_read_command();
    (void)cleared_status;
    if (latched_status == 0x55u) {
        rc_write_actuator(180u);
    } else {
        rc_write_actuator(RC_ACTUATOR_SAFE);
    }
    return 0;
}
