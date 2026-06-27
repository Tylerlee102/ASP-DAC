#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    volatile uint32_t scratch = 0xdeadbeefu;
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    return (int)(scratch & 1u);
}
