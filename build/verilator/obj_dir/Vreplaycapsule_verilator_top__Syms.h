// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VREPLAYCAPSULE_VERILATOR_TOP__SYMS_H_
#define VERILATED_VREPLAYCAPSULE_VERILATOR_TOP__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vreplaycapsule_verilator_top.h"

// INCLUDE MODULE CLASSES
#include "Vreplaycapsule_verilator_top___024root.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES) Vreplaycapsule_verilator_top__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vreplaycapsule_verilator_top* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vreplaycapsule_verilator_top___024root TOP;

    // CONSTRUCTORS
    Vreplaycapsule_verilator_top__Syms(VerilatedContext* contextp, const char* namep, Vreplaycapsule_verilator_top* modelp);
    ~Vreplaycapsule_verilator_top__Syms();

    // METHODS
    const char* name() const { return TOP.vlNamep; }
};

#endif  // guard
