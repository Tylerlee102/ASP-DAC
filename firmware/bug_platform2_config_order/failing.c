#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    rc_profile2_write_actuator(25u);
    rc_profile2_write_config(RC_CONFIG_SAFE_MAGIC);
    return 0;
}
