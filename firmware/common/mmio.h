#ifndef REPLAYCAPSULE_MMIO_H
#define REPLAYCAPSULE_MMIO_H

#include <stdint.h>

#define RC_MMIO_SENSOR      ((volatile uint32_t *)0x40000000u)
#define RC_MMIO_ACTUATOR    ((volatile uint32_t *)0x40000004u)
#define RC_MMIO_CONFIG      ((volatile uint32_t *)0x40000008u)
#define RC_MMIO_COMMAND     ((volatile uint32_t *)0x4000000cu)
#define RC_CONFIG_SAFE_MAGIC 0x0000cafeu
#define RC_ACTUATOR_SAFE     0u
#define RC_SENSOR_THRESHOLD  700u

#ifndef RC_WORKLOAD_DELAY_ITERS
#define RC_WORKLOAD_DELAY_ITERS 0u
#endif

static inline void rc_workload_delay(void) {
    for (volatile uint32_t i = 0; i < RC_WORKLOAD_DELAY_ITERS; ++i) {
        __asm__ volatile("" ::: "memory");
    }
}

static inline uint32_t rc_read_sensor(void) {
    return *RC_MMIO_SENSOR;
}

static inline void rc_write_actuator(uint32_t value) {
    *RC_MMIO_ACTUATOR = value;
}

static inline void rc_write_config(uint32_t value) {
    *RC_MMIO_CONFIG = value;
}

static inline uint32_t rc_read_command(void) {
    return *RC_MMIO_COMMAND;
}

#endif
