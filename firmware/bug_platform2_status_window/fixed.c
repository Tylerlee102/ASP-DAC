#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t latched_status = rc_profile2_read_command();
    if (latched_status == 0x55u) {
        uint32_t confirmed_status = rc_profile2_read_command();
        if (confirmed_status == 0x55u) {
            rc_profile2_write_config(RC_CONFIG_SAFE_MAGIC);
            rc_profile2_write_actuator(50u);
        } else {
            rc_profile2_write_actuator(RC_ACTUATOR_SAFE);
        }
    }
    return 0;
}
