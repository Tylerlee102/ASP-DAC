# Vendored FemtoRV32 Quark

- Upstream: `https://github.com/BrunoLevy/learn-fpga`
- Commit: `5c08c870315c09ccd9ec64ccde20ab3375b3f273`
- Source file: `FemtoRV/RTL/PROCESSOR/femtorv32_quark.v`
- Local copy: `third_party/femtorv32/femtorv32_quark.v`
- License: BSD-3-Clause, copied to `third_party/femtorv32/LICENSE`
- Local compatibility note: declaration order was adjusted so Icarus Verilog can elaborate the core; no logic change is intended.
- Purpose: second RV32I core breadth candidate for wrapper/synthesis and compiler-backed ReplayCapsule smoke evidence. This is not yet a full ReplayCapsule record/replay integration result.
