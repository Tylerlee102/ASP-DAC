// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vreplaycapsule_verilator_top.h for the primary calling header

#include "Vreplaycapsule_verilator_top__pch.h"

void Vreplaycapsule_verilator_top___024root___ctor_var_reset(Vreplaycapsule_verilator_top___024root* vlSelf);

Vreplaycapsule_verilator_top___024root::Vreplaycapsule_verilator_top___024root(Vreplaycapsule_verilator_top__Syms* symsp, const char* namep)
 {
    vlSymsp = symsp;
    vlNamep = strdup(namep);
    // Reset structure values
    Vreplaycapsule_verilator_top___024root___ctor_var_reset(this);
}

void Vreplaycapsule_verilator_top___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vreplaycapsule_verilator_top___024root::~Vreplaycapsule_verilator_top___024root() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
