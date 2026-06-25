#include "../common/mmio.h"

int main(void) {
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    rc_write_actuator(RC_ACTUATOR_SAFE);
    return 0;
}

