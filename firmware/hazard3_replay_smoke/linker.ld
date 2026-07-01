ENTRY(_start)

MEMORY
{
  ROM (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00001000
  RAM (rwx) : ORIGIN = 0x00001800, LENGTH = 0x00000800
}

SECTIONS
{
  .irq_vector 0x00000010 :
  {
    KEEP(*(.text.irq))
  } > ROM

  .text 0x00000080 :
  {
    KEEP(*(.text.start))
    *(.text .text.*)
    *(.rodata .rodata.*)
  } > ROM

  .data :
  {
    *(.sdata .sdata.*)
    *(.data .data.*)
  } > RAM AT > ROM

  .bss (NOLOAD) :
  {
    __bss_start = .;
    *(.sbss .sbss.*)
    *(.bss .bss.*)
    *(COMMON)
    __bss_end = .;
  } > RAM

  __stack_top = ORIGIN(RAM) + LENGTH(RAM);
}
