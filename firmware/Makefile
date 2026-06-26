RISCV_PREFIX ?= riscv64-unknown-elf-
CC := $(RISCV_PREFIX)gcc
OBJCOPY := $(RISCV_PREFIX)objcopy
OBJDUMP := $(RISCV_PREFIX)objdump
SIZE := $(RISCV_PREFIX)size

CFLAGS ?= -march=rv32i -mabi=ilp32 -O2 -ffreestanding -fno-builtin -nostdlib -nostartfiles -Wall -Wextra
LDFLAGS ?= -T linker.ld -Wl,-Map,$(MAP)

SRC ?=
OUT ?= build/manual/firmware
ELF := $(OUT).elf
HEX := $(OUT).hex
MAP := $(OUT).map

.PHONY: all clean

all: $(ELF) $(HEX)

$(ELF): startup.S linker.ld $(SRC)
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -Icommon startup.S $(SRC) $(LDFLAGS) -o $@

$(HEX): $(ELF)
	$(OBJCOPY) -O verilog $< $@

clean:
	rm -rf build/manual
