#include "../common/mmio.h"

int main(void) {
    rc_workload_delay();
    uint32_t command = rc_read_command();
    if (command == 0x55u) {
        rc_write_actuator(250u);
    }
    return 0;
}
