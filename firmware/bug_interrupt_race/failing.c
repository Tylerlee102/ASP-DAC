#include "../common/mmio.h"

int main(void) {
    *RC_MMIO_COMMAND = 1u;
    rc_write_config(0x1111u);
    rc_write_actuator(50u);
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    *RC_MMIO_COMMAND = 0u;
    return 0;
}

