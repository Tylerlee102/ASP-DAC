// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vreplaycapsule_verilator_top__pch.h"

//============================================================
// Constructors

Vreplaycapsule_verilator_top::Vreplaycapsule_verilator_top(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vreplaycapsule_verilator_top__Syms(contextp(), _vcname__, this)}
    , clk{vlSymsp->TOP.clk}
    , rst_n{vlSymsp->TOP.rst_n}
    , clear{vlSymsp->TOP.clear}
    , capture_mode{vlSymsp->TOP.capture_mode}
    , trap{vlSymsp->TOP.trap}
    , mem_valid{vlSymsp->TOP.mem_valid}
    , mem_instr{vlSymsp->TOP.mem_instr}
    , mem_ready{vlSymsp->TOP.mem_ready}
    , mem_wstrb{vlSymsp->TOP.mem_wstrb}
    , external_input_valid{vlSymsp->TOP.external_input_valid}
    , capsule_read_addr{vlSymsp->TOP.capsule_read_addr}
    , capsule_word5{vlSymsp->TOP.capsule_word5}
    , capsule_frozen{vlSymsp->TOP.capsule_frozen}
    , capsule_overflow{vlSymsp->TOP.capsule_overflow}
    , property_fail_valid{vlSymsp->TOP.property_fail_valid}
    , property_id{vlSymsp->TOP.property_id}
    , capsule_event_count{vlSymsp->TOP.capsule_event_count}
    , mem_addr{vlSymsp->TOP.mem_addr}
    , mem_wdata{vlSymsp->TOP.mem_wdata}
    , mem_rdata{vlSymsp->TOP.mem_rdata}
    , irq{vlSymsp->TOP.irq}
    , eoi{vlSymsp->TOP.eoi}
    , external_input_value{vlSymsp->TOP.external_input_value}
    , capsule_word0{vlSymsp->TOP.capsule_word0}
    , capsule_word1{vlSymsp->TOP.capsule_word1}
    , capsule_word2{vlSymsp->TOP.capsule_word2}
    , capsule_word3{vlSymsp->TOP.capsule_word3}
    , capsule_word4{vlSymsp->TOP.capsule_word4}
    , running_signature{vlSymsp->TOP.running_signature}
    , property_signature{vlSymsp->TOP.property_signature}
    , commit_count{vlSymsp->TOP.commit_count}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vreplaycapsule_verilator_top::Vreplaycapsule_verilator_top(const char* _vcname__)
    : Vreplaycapsule_verilator_top(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vreplaycapsule_verilator_top::~Vreplaycapsule_verilator_top() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vreplaycapsule_verilator_top___024root___eval_debug_assertions(Vreplaycapsule_verilator_top___024root* vlSelf);
#endif  // VL_DEBUG
void Vreplaycapsule_verilator_top___024root___eval_static(Vreplaycapsule_verilator_top___024root* vlSelf);
void Vreplaycapsule_verilator_top___024root___eval_initial(Vreplaycapsule_verilator_top___024root* vlSelf);
void Vreplaycapsule_verilator_top___024root___eval_settle(Vreplaycapsule_verilator_top___024root* vlSelf);
void Vreplaycapsule_verilator_top___024root___eval(Vreplaycapsule_verilator_top___024root* vlSelf);

void Vreplaycapsule_verilator_top::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vreplaycapsule_verilator_top::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vreplaycapsule_verilator_top___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vreplaycapsule_verilator_top___024root___eval_static(&(vlSymsp->TOP));
        Vreplaycapsule_verilator_top___024root___eval_initial(&(vlSymsp->TOP));
        Vreplaycapsule_verilator_top___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vreplaycapsule_verilator_top___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vreplaycapsule_verilator_top::eventsPending() { return false; }

uint64_t Vreplaycapsule_verilator_top::nextTimeSlot() {
    VL_FATAL_MT(__FILE__, __LINE__, "", "No delays in the design");
    return 0;
}

//============================================================
// Utilities

const char* Vreplaycapsule_verilator_top::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vreplaycapsule_verilator_top___024root___eval_final(Vreplaycapsule_verilator_top___024root* vlSelf);

VL_ATTR_COLD void Vreplaycapsule_verilator_top::final() {
    contextp()->executingFinal(true);
    Vreplaycapsule_verilator_top___024root___eval_final(&(vlSymsp->TOP));
    contextp()->executingFinal(false);
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vreplaycapsule_verilator_top::hierName() const { return vlSymsp->name(); }
const char* Vreplaycapsule_verilator_top::modelName() const { return "Vreplaycapsule_verilator_top"; }
unsigned Vreplaycapsule_verilator_top::threads() const { return 1; }
void Vreplaycapsule_verilator_top::prepareClone() const { contextp()->prepareClone(); }
void Vreplaycapsule_verilator_top::atClone() const {
    contextp()->threadPoolpOnClone();
}
