#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    *RC_MMIO_COMMAND = 1u;
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    rc_write_actuator(RC_ACTUATOR_SAFE);
    *RC_MMIO_COMMAND = 0u;
    return 0;
}
