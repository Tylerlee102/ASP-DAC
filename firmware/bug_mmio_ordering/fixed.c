#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    rc_write_actuator(25u);
    return 0;
}
