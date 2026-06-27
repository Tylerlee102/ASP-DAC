#include "../common/mmio.h"

int main(void) {
    __asm__ volatile(".word 0x0600000b" ::: "memory");
    rc_workload_delay();
    *RC_MMIO_COMMAND = 1u;
    for (volatile uint32_t window = 0; window < 64u; ++window) {
        __asm__ volatile("" ::: "memory");
    }
    rc_write_config(0x1111u);
    rc_write_actuator(50u);
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    *RC_MMIO_COMMAND = 0u;
    return 0;
}
