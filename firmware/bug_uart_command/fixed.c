#include "../common/mmio.h"

int main(void) {
    uint32_t command = rc_read_command();
    if (command == 0x55u) {
        rc_write_config(RC_CONFIG_SAFE_MAGIC);
        rc_write_actuator(RC_ACTUATOR_SAFE);
    }
    return 0;
}

