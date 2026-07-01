    .section .text.irq, "ax"
    .option norvc
    .globl hazard3_irq_handler
hazard3_irq_handler:
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
    li t2, 0x40000004
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
    la t0, hazard3_irq_handler
    csrw mtvec, t0
    li t0, 0x800
    csrs mie, t0
    li t0, 0x8
    csrs mstatus, t0

    li t0, 0x40000000
    li t1, 1
    sw t1, 0(t0)

3:
    la t2, irq_count
    lw t3, 0(t2)
    beqz t3, 3b

    li t0, 0x40000008
    sw t3, 0(t0)

4:
    j 4b

    .section .bss, "aw"
    .balign 4
irq_count:
    .word 0
