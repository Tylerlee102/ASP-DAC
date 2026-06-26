ENTRY(_start)

MEMORY
{
  ROM (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00010000
  RAM (rwx) : ORIGIN = 0x00002000, LENGTH = 0x00002000
}

SECTIONS
{
  .text 0x00000000 :
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
