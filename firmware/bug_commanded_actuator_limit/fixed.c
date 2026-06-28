#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t command = rc_read_command();
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    if (command == 0x55u) {
        rc_write_actuator(50u);
    } else {
        rc_write_actuator(RC_ACTUATOR_SAFE);
    }
    return 0;
}
