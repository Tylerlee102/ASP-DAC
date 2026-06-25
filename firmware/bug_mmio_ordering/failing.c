#include "../common/mmio.h"

int main(void) {
    rc_write_actuator(25u);
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    return 0;
}

