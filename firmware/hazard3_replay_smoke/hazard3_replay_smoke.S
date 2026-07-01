    .section .text.irq, "ax"
    .option norvc

#ifndef WORKLOAD_ID
#define WORKLOAD_ID 2
#endif

    .globl hazard3_replay_irq_handler
hazard3_replay_irq_handler:
    addi sp, sp, -16
    sw ra, 12(sp)
    sw t0, 8(sp)
    sw t1, 4(sp)
    sw t2, 0(sp)

    la t0, irq_count
    lw t1, 0(t0)
    addi t1, t1, 1
    sw t1, 0(t0)

    li t2, 0x40000010
    sw t1, 0(t2)
    li t2, 0x40000014
    sw t1, 0(t2)

    lw t2, 0(sp)
    lw t1, 4(sp)
    lw t0, 8(sp)
    lw ra, 12(sp)
    addi sp, sp, 16
    mret

    .section .text.start, "ax"
    .option norvc
    .globl _start
_start:
    la sp, __stack_top

    la t0, __bss_start
    la t1, __bss_end
1:
    bgeu t0, t1, 2f
    sw zero, 0(t0)
    addi t0, t0, 4
    j 1b

2:
    la t0, hazard3_replay_irq_handler
    csrw mtvec, t0
    li t0, 0x800
    csrs mie, t0
    li t0, 0x8
    csrs mstatus, t0

    li t0, 0x40000000
    lw s0, 0(t0)

#if WORKLOAD_ID == 1
    /* Actuator-limit bug: record/replay IRQ, then command an unsafe actuator value. */
    li t0, 0x4000000c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x40000004
    li t1, 150
    sw t1, 0(t0)
#elif WORKLOAD_ID == 2
    /* Interrupt-critical bug: command bit 0 opens the critical section before IRQ entry. */
    li t0, 0x4000000c
    li t1, 1
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x40000008
    sw s0, 0(t0)
#elif WORKLOAD_ID == 3
    /* Sensor-deadline bug: high sensor input is not followed by a safe actuator response. */
    li t0, 0x4000000c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t4, 64
sensor_deadline_delay:
    addi t4, t4, -1
    bnez t4, sensor_deadline_delay
#elif WORKLOAD_ID == 4
    /* Stack-protect bug: write inside the protected stack range after IRQ replay setup. */
    li t0, 0x4000000c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x00001000
    li t1, 0x12345678
    sw t1, 0(t0)
#elif WORKLOAD_ID == 5
    /* MMIO-ordering bug: actuator command before safe config magic. */
    li t0, 0x4000000c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x40000004
    li t1, 85
    sw t1, 0(t0)
#elif WORKLOAD_ID == 6
    /* Watchdog-timeout bug: high sensor input starts the watchdog, then no heartbeat. */
    li t0, 0x4000000c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t4, 64
watchdog_delay:
    addi t4, t4, -1
    bnez t4, watchdog_delay
#elif WORKLOAD_ID == 7
    /* Profile-2 actuator-limit bug: same property through the alternate MMIO profile. */
    li t0, 0x40000040
    lw s0, 0(t0)
    li t0, 0x4000004c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x40000044
    li t1, 150
    sw t1, 0(t0)
#elif WORKLOAD_ID == 8
    /* Profile-2 interrupt-critical bug. */
    li t0, 0x40000040
    lw s0, 0(t0)
    li t0, 0x4000004c
    li t1, 1
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x40000048
    sw s0, 0(t0)
#elif WORKLOAD_ID == 9
    /* Profile-2 MMIO-ordering bug. */
    li t0, 0x40000040
    lw s0, 0(t0)
    li t0, 0x4000004c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x40000044
    li t1, 85
    sw t1, 0(t0)
#elif WORKLOAD_ID == 10
    /* Safe-config then actuator-limit bug: ordering is correct, value is unsafe. */
    li t0, 0x4000000c
    li t1, 2
    sw t1, 0(t0)
    jal ra, wait_for_irq
    li t0, 0x40000008
    li t1, 0xcafe
    sw t1, 0(t0)
    li t0, 0x40000004
    li t1, 150
    sw t1, 0(t0)
#else
#error "Unsupported WORKLOAD_ID"
#endif

done_loop:
    j done_loop

wait_for_irq:
    la t2, irq_count
1:
    lw t3, 0(t2)
    beqz t3, 1b
    ret

    .section .bss, "aw"
    .balign 4
irq_count:
    .word 0
