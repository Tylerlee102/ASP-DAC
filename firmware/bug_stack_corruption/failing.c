#include "../common/mmio.h"

int main(void) {
    volatile uint32_t *protected_stack = (volatile uint32_t *)0x00001010u;
    *protected_stack = 0xdeadbeefu;
    rc_write_config(RC_CONFIG_SAFE_MAGIC);
    return 0;
}

