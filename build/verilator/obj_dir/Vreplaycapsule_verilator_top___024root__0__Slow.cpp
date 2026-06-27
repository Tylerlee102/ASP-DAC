// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vreplaycapsule_verilator_top.h for the primary calling header

#include "Vreplaycapsule_verilator_top__pch.h"

VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___eval_static(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_static\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
    vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0 = vlSelfRef.rst_n;
    vlSelfRef.__Vtrigprevexpr___TOP__clear__0 = vlSelfRef.clear;
    vlSelfRef.__Vtrigprevexpr___TOP__capture_mode__0
        = vlSelfRef.capture_mode;
    vlSelfRef.__Vtrigprevexpr___TOP__mem_ready__0 = vlSelfRef.mem_ready;
    vlSelfRef.__Vtrigprevexpr___TOP__mem_rdata__0 = vlSelfRef.mem_rdata;
    vlSelfRef.__Vtrigprevexpr___TOP__irq__0 = vlSelfRef.irq;
    vlSelfRef.__Vtrigprevexpr___TOP__external_input_valid__0
        = vlSelfRef.external_input_valid;
    vlSelfRef.__Vtrigprevexpr___TOP__external_input_value__0
        = vlSelfRef.external_input_value;
    vlSelfRef.__Vtrigprevexpr___TOP__capsule_read_addr__0
        = vlSelfRef.capsule_read_addr;
    vlSelfRef.__Vtrigprevexpr___TOP__clk__1 = vlSelfRef.clk;
    vlSelfRef.__Vtrigprevexpr___TOP__rst_n__1 = vlSelfRef.rst_n;
}

VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___eval_initial(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_initial\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_initial__TOP
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[0U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[1U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[2U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[3U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[4U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[5U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[6U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[7U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[8U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[9U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[10U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[11U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[12U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[13U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[14U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[15U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[16U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[17U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[18U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[19U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[20U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[21U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[22U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[23U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[24U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[25U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[26U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[27U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[28U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[29U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[30U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[31U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[32U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[33U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[34U] = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[35U] = 0U;
    }
}

VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___eval_final(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_final\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vreplaycapsule_verilator_top___024root___eval_phase__stl(Vreplaycapsule_verilator_top___024root* vlSelf);

VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___eval_settle(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_settle\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VstlIterCount;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vreplaycapsule_verilator_top___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
#endif
            VL_FATAL_MT("tb/verilator\\replaycapsule_verilator_top.sv", 3, "", "DIDNOTCONVERGE: Settle region did not converge after '--converge-limit' of 10000 tries");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        vlSelfRef.__VstlPhaseResult = Vreplaycapsule_verilator_top___024root___eval_phase__stl(vlSelf);
        vlSelfRef.__VstlFirstIteration = 0U;
    } while (vlSelfRef.__VstlPhaseResult);
}

VL_ATTR_COLD bool Vreplaycapsule_verilator_top___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___dump_triggers__stl(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(Vreplaycapsule_verilator_top___024root___trigger_anySet__stl(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD bool Vreplaycapsule_verilator_top___024root___trigger_anySet__stl(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___trigger_anySet__stl\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___stl_sequent__TOP__0(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___stl_sequent__TOP__0\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq = 0;
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu = 0;
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_2;
    __VdfgRegularize_h6e95ff9d_0_2 = 0;
    // Body
    vlSelfRef.mem_valid = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid;
    vlSelfRef.mem_instr = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr;
    vlSelfRef.eoi = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi;
    vlSelfRef.commit_count = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
    vlSelfRef.mem_addr = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
    vlSelfRef.mem_wdata = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata;
    vlSelfRef.mem_wstrb = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb;
    if ((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wdata
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wstrb = 0x0fU;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
            = vlSelfRef.mem_rdata;
    } else if ((1U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wdata
            = ((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                << 0x00000010U) | (0x0000ffffU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2));
        if ((2U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wstrb = 0x0cU;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
                = (vlSelfRef.mem_rdata >> 0x10U);
        } else {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wstrb = 3U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
                = (0x0000ffffU & vlSelfRef.mem_rdata);
        }
    } else if ((2U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wdata
            = ((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                << 0x00000018U) | ((0x00ff0000U & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                                                   << 0x00000010U))
                                   | ((0x0000ff00U
                                       & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                                          << 8U)) |
                                      (0x000000ffU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wstrb
            = (0x0000000fU & ((IData)(1U) << (3U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
            = ((2U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)
                ? ((1U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)
                    ? (vlSelfRef.mem_rdata >> 0x18U)
                    : (0x000000ffU & (vlSelfRef.mem_rdata
                                      >> 0x10U))) :
               ((1U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)
                 ? (0x000000ffU & (vlSelfRef.mem_rdata
                                   >> 8U)) : (0x000000ffU
                                              & vlSelfRef.mem_rdata)));
    }
    vlSelfRef.capsule_word0 = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem
        [vlSelfRef.capsule_read_addr][0U];
    vlSelfRef.capsule_word1 = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem
        [vlSelfRef.capsule_read_addr][1U];
    vlSelfRef.capsule_word2 = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem
        [vlSelfRef.capsule_read_addr][2U];
    vlSelfRef.capsule_word3 = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem
        [vlSelfRef.capsule_read_addr][3U];
    vlSelfRef.capsule_word4 = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem
        [vlSelfRef.capsule_read_addr][4U];
    vlSelfRef.capsule_word5 = (0x000000ffU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem
                               [vlSelfRef.capsule_read_addr][5U]);
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs
           [vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1]
           & (- (IData)(((0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1))
                         & (0x23U >= (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1))))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs
           [vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2]
           & (- (IData)((0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2)))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write = 0U;
    __VdfgRegularize_h6e95ff9d_0_2 = ((~ (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state)))
                                      & (IData)(vlSelfRef.rst_n));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata = 0U;
    if ((0x40U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
        if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata
                = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc
                   + ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr)
                       ? 2U : 4U));
        } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store)
                    & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch)))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata
                = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu)
                    ? vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_q
                    : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out);
        } else if ((1U & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata
                = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc
                   | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr));
        } else if ((2U & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata
                = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending
                   & (~ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask));
        }
    }
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1 = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
                                                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata));
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
           == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts
        = VL_LTS_III(32, vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1, vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
           < vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc
        = ((0U != (1U & (IData)((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                                 >> 0x00000020U))))
            ? (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data)
            : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__fetch_context_pc);
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_rdcycle_rdcycleh_rdinstr_rdinstrh
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycle)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycleh)
              | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstr)
                 | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstrh))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid
        = (IData)(((~ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                       >> 0x00000021U)) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid)));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid)
           & (0U != (1U & (IData)((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                                   >> 0x00000020U)))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter
        = ((0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi)
           & (0U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit
        = ((0U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi)
           & (0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer
        = ((IData)(vlSelfRef.mem_ready) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)
           & (IData)(__VdfgRegularize_h6e95ff9d_0_2));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_read
        = (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch)
            | (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1))
           & (IData)(__VdfgRegularize_h6e95ff9d_0_2));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0 = 0U;
    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_beq) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0
            = replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq;
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bne) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0
            = (1U & (~ (IData)(replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq)));
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bge) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0
            = (1U & (~ (IData)(replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts)));
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bgeu) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0
            = (1U & (~ (IData)(replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu)));
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slti_blt_slt) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0
            = replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts;
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sltiu_bltu_sltu) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0
            = replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu;
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out = 0U;
    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal_jalr_addi_add_sub) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sub)
                ? (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                   - vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2)
                : (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                   + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2));
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_compare) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0;
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xori)
                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xor))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out
            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
               ^ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_ori)
                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_or))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out
            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
               | vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_andi)
                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_and))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out
            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
               & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_trap
        = (1U & (~ ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui)
                    | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_auipc)
                       | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal)
                          | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr)
                             | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_beq)
                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bne)
                                   | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_blt)
                                      | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bge)
                                         | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bltu)
                                            | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bgeu)
                                               | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lb)
                                                  | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lh)
                                                     | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lw)
                                                        | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lbu)
                                                           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lhu)
                                                              | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sb)
                                                                 | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sh)
                                                                    | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sw)
                                                                       | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_addi)
                                                                          | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slti)
                                                                             | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltiu)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xori)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_ori)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_andi)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slli)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srli)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srai)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_add)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sub)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sll)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slt)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltu)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xor)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srl)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sra)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_or)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_and)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_rdcycle_rdcycleh_rdinstr_rdinstrh)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_fence)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_getq)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_setq)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_retirq)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_maskirq)
                                                                                | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_waitirq)
                                                                                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_timer)))))))))))))))))))))))))))))))))))))))))))))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer)
            ? vlSelfRef.mem_rdata : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q);
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done
        = ((IData)(vlSelfRef.rst_n) & (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
                                        & (3U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state)))
                                       | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer)
                                          & ((0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state))
                                             & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)
                                                | (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1))))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted
        = ((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr))
           & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 0U;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr = 0U;
    if ((1U & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter)))) {
        if ((1U & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit)))) {
            if ((1U & (~ (IData)(vlSelfRef.external_input_valid)))) {
                if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                      & (0x40000000U == (0xffff0000U
                                         & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                     & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
                } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                             & (0x40000000U == (0xffff0000U
                                                & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                            & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
                } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                            & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
                } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                            & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
                }
            }
        }
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 0U;
    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 7U;
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 8U;
    } else if (vlSelfRef.external_input_valid) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.external_input_value;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 9U;
    } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                 & (0x40000000U == (0xffff0000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.mem_rdata;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 5U;
    } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                 & (0x40000000U == (0xffff0000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 6U;
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 3U;
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.mem_rdata;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 4U;
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid)
                & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 1U;
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 0U;
    }
    if (vlSelfRef.property_fail_valid) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_commit_index;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_pc;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr
            = vlSelfRef.property_id;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data
            = vlSelfRef.property_signature;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type = 0x0aU;
    } else {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type;
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid
        = ((IData)(vlSelfRef.property_fail_valid) | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail = 0U;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id = 0U;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature = 0U;
    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid) {
        if ((((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
              & (0x40000004U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
             & (0x00000064U < vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature
                = (0xac700001U ^ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
                                  ^ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index));
        } else if (((7U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                    & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__critical_section_active))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id = 2U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature
                = (0x1a1e0002U ^ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc
                                  ^ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index));
        } else if ((((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                     & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active))
                    & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count)))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id = 3U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature
                = (0x5e050003U ^ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc
                                  ^ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index));
        } else if ((((3U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                     & (0x00001000U <= vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                    & (0x00001400U > vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id = 4U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature
                = (0x57ac0004U ^ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr
                                  ^ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data));
        } else if (((((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                      & (0x40000004U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                     & (0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))
                    & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__safe_config_seen)))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail = 1U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id = 5U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature
                = (0x0d0e0005U ^ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
                                  ^ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index));
        }
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__classifier_keep_event
        = ((8U & (IData)(vlSelfRef.capture_mode)) ? (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)
            : ((4U & (IData)(vlSelfRef.capture_mode))
                ? (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)
                : ((2U & (IData)(vlSelfRef.capture_mode))
                    ? ((1U & (IData)(vlSelfRef.capture_mode))
                        ? (((IData)(vlSelfRef.capsule_overflow)
                            | (0U != (3U & (0x005fdc54U
                                            >> ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)
                                                << 1U)))))
                           & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid))
                        : (((0x005fdc54U >> ((IData)(1U)
                                             + ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)
                                                << 1U)))
                            | ((0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count))
                               | (0x0aU == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))))
                           & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)))
                    : ((1U & (IData)(vlSelfRef.capture_mode))
                        ? (((0x0aU == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                            | ((5U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                               | ((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                  | ((7U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                     | ((8U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                        | (9U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)))))))
                           & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid))
                        : (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[0U]
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[1U]
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[2U]
        = (IData)((((QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index))
                    << 0x00000020U) | (QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[3U]
        = (IData)(((((QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index))
                     << 0x00000020U) | (QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc)))
                   >> 0x00000020U));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[4U]
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[5U]
        = (0x000000ffU & (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)
                           << 4U) | (((1U < (0x0000001fU
                                             & ((1U
                                                 & (- (IData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid))))
                                                + (
                                                   (1U
                                                    & (- (IData)(
                                                                 ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid)
                                                                  & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken)))))
                                                   +
                                                   ((1U
                                                     & (- (IData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted))))
                                                    +
                                                    ((1U
                                                      & (- (IData)((IData)(vlSelfRef.external_input_valid))))
                                                     +
                                                     ((1U
                                                       & (- (IData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit))))
                                                      +
                                                      (1U
                                                       & (- (IData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter)))))))))))
                                      << 3U) | ((6U
                                                 & ((0x005fdc54U
                                                     >>
                                                     ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)
                                                      << 1U))
                                                    << 1U))
                                                | (IData)(vlSelfRef.capsule_overflow)))));
}

VL_ATTR_COLD bool Vreplaycapsule_verilator_top___024root___eval_phase__stl(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_phase__stl\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VstlExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__stl
        vlSelfRef.__VstlTriggered[0U] = ((0xfffffffffffffffeULL
                                          & vlSelfRef.__VstlTriggered[0U])
                                         | (IData)((IData)(vlSelfRef.__VstlFirstIteration)));
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vreplaycapsule_verilator_top___024root___dump_triggers__stl(vlSelfRef.__VstlTriggered, "stl"s);
    }
#endif
    __VstlExecute = Vreplaycapsule_verilator_top___024root___trigger_anySet__stl(vlSelfRef.__VstlTriggered);
    if (__VstlExecute) {
        {
            // Inlined CFunc: _eval_stl
            if ((1ULL & vlSelfRef.__VstlTriggered[0U])) {
                Vreplaycapsule_verilator_top___024root___stl_sequent__TOP__0(vlSelf);
            }
        }
    }
    return (__VstlExecute);
}

bool Vreplaycapsule_verilator_top___024root___trigger_anySet__ico(const VlUnpacked<QData/*63:0*/, 2> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___dump_triggers__ico(const VlUnpacked<QData/*63:0*/, 2> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___dump_triggers__ico\n"); );
    // Body
    if ((1U & (~ (IData)(Vreplaycapsule_verilator_top___024root___trigger_anySet__ico(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @( clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @( rst_n)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 2U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 2 is active: @( clear)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 3U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 3 is active: @( capture_mode)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 4U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 4 is active: @( mem_ready)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 5U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 5 is active: @( mem_rdata)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 6U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 6 is active: @( irq)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 7U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 7 is active: @( external_input_valid)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 8U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 8 is active: @( external_input_value)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 9U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 9 is active: @( capsule_read_addr)\n");
    }
    if ((1U & (IData)(triggers[1U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 64 is active: Internal 'ico' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

bool Vreplaycapsule_verilator_top___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in);

#ifdef VL_DEBUG
VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(Vreplaycapsule_verilator_top___024root___trigger_anySet__act(triggers))))) {
        VL_DBG_MSGS("         No '" + tag + "' region triggers active\n");
    }
    if ((1U & (IData)(triggers[0U]))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 0 is active: @(posedge clk)\n");
    }
    if ((1U & (IData)((triggers[0U] >> 1U)))) {
        VL_DBG_MSGS("         '" + tag + "' region trigger index 1 is active: @(negedge rst_n)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___ctor_var_reset(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___ctor_var_reset\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->vlNamep);
    vlSelf->clk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16707436170211756652ull);
    vlSelf->rst_n = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1638864771569018232ull);
    vlSelf->clear = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11731883408449213572ull);
    vlSelf->capture_mode = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 17005515237445581212ull);
    vlSelf->trap = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18214934560881419504ull);
    vlSelf->mem_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1551974250180885553ull);
    vlSelf->mem_instr = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1406578376079151150ull);
    vlSelf->mem_ready = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6248464876150524742ull);
    vlSelf->mem_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 326597072690670135ull);
    vlSelf->mem_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5431754401481461448ull);
    vlSelf->mem_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 8859681292774497410ull);
    vlSelf->mem_rdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 9659133473039683418ull);
    vlSelf->irq = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14145092342636110857ull);
    vlSelf->eoi = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13895818346295942146ull);
    vlSelf->external_input_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18403796643108711208ull);
    vlSelf->external_input_value = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15798109498180834560ull);
    vlSelf->capsule_read_addr = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15246549966032130409ull);
    vlSelf->capsule_word0 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12194617861950284996ull);
    vlSelf->capsule_word1 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2042844032345033697ull);
    vlSelf->capsule_word2 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6340263473201842321ull);
    vlSelf->capsule_word3 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16983722803233738139ull);
    vlSelf->capsule_word4 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2897611262678557474ull);
    vlSelf->capsule_word5 = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 6954346091540129031ull);
    vlSelf->capsule_frozen = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11902943422459311965ull);
    vlSelf->capsule_overflow = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7559444040547237397ull);
    vlSelf->capsule_event_count = VL_SCOPED_RAND_RESET_I(9, __VscopeHash, 6092674473491670767ull);
    vlSelf->running_signature = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18265418649703996459ull);
    vlSelf->property_fail_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5129913436578716862ull);
    vlSelf->property_id = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 11515992418748523562ull);
    vlSelf->property_signature = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11387578450223560062ull);
    vlSelf->commit_count = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6582548623341971739ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 171543386510400022ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14275484755531392713ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 10175408325074849313ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5324588103921904067ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1421068817848565220ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6231357047808238086ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 16871466823890779034ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17169617879392646420ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data = VL_SCOPED_RAND_RESET_Q(36, __VscopeHash, 353473044410709852ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 11664373200045634356ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__fetch_context_pc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 14138401562773321117ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8378910626029135929ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2834622860933210542ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 303860135919606203ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3421018839886805057ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid = 0;
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_read = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15793327195579853013ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16185094500715045822ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6788522771829405107ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wstrb = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 4600042039883678493ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 14812472241419793417ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr = VL_SCOPED_RAND_RESET_Q(64, __VscopeHash, 15181042898545002985ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10299796616107387089ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10261523555235822281ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15224593065619375753ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13887785377635143763ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 18188756168875184135ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 295029858636418566ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_delay = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7338401030189276203ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5308956985014521318ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4792803410731531826ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8582250130103253301ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5679283527969076011ull);
    for (int __Vi0 = 0; __Vi0 < 36; ++__Vi0) {
        vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[__Vi0] = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6673823883203377140ull);
    }
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 14606382198742554440ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 2255951460659486980ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10410426272887921891ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 15660804702347072268ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6967723827878669274ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17338810034053140408ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13997142408952756510ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 683313506231304927ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13396663595963600663ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6559111584535085293ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10665649257331863429ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16348779560516678321ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_auipc = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 109645268038620078ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18268973256843334027ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16647817625049709771ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_beq = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3989384874797283319ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bne = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8868342759637474694ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_blt = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14585012181253741881ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bge = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10412003108859905031ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bltu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13685005517934405897ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bgeu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14503059949471526358ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lb = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11560225648410961313ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lh = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9231600410044379233ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lw = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8998524236270310066ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lbu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7567448838495848533ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lhu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13908367218198870865ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sb = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12338520434875129242ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sh = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16794874362439241436ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sw = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5863495319918720138ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_addi = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3719532668445987424ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slti = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9927275223331724155ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltiu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17011666913419702898ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xori = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16737081783882885708ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_ori = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12968866183182773912ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_andi = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4041155017476871800ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slli = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1401554487517513619ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srli = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7421621587156980607ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srai = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1682897101138423702ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_add = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4599782779813421505ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sub = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13436803396862817996ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sll = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18380749812225105208ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slt = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 616363373420338108ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12738764449836377448ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xor = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12702709827004439359ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srl = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14271774091197417059ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sra = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 911159397424225697ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_or = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3406827296295564865ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_and = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5324634964764260285ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycle = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18065182361563608289ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycleh = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2661103801232985122ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstr = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6252701525609401280ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstrh = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1423034083160532370ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_fence = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17577144056450211117ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_getq = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17885046544203566887ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_setq = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14736179227797123098ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_retirq = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4200165266283903849ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_maskirq = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14942718869238077006ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_waitirq = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15177830393897384669ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_timer = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17588743927247806568ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_trap = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 13042045834903295146ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rd = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 15841896314486236858ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1 = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 4909918030395155810ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2 = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 6118949010542886550ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 6040962713269680766ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10194059977350780162ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6527759593270956688ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15646272304517445555ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__compressed_instr = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15464451973012036055ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14128452384827465376ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 6029548704492914699ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slli_srli_srai = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16269601353735961612ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_jalr_addi_slti_sltiu_xori_ori_andi = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 522542824534929884ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16459563749337332299ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sll_srl_sra = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9630651212382806886ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal_jalr_addi_add_sub = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 10941464400606396112ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slti_blt_slt = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1681077655731743409ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sltiu_bltu_sltu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17766873404077364033ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12684064813836352292ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lbu_lhu_lw = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17275220393640327201ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9436252676818975319ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17096986465700069394ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_compare = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18215249759122248788ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_rdcycle_rdcycleh_rdinstr_rdinstrh = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 769347053236505208ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 13221141168320485924ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state = VL_SCOPED_RAND_RESET_I(2, __VscopeHash, 10599266671186266551ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15107978854693145808ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4387743394181670792ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3325281329554740871ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 9460215263329809132ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_trace = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 7476826505372681163ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1630317665576822944ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2522582531305722754ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 18211682979734393744ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd = VL_SCOPED_RAND_RESET_I(6, __VscopeHash, 8708711562043879933ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 8578204967352643382ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1207841324066175569ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17826505001396899611ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_q = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13497596894273091661ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 12451435987796776512ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16404810924511310257ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 3427752920257797791ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 12171460131302382293ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2 = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 7639204826619122276ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2869075592474288952ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 14772513614833686293ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17135299883324645356ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 2616294201583220055ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10932939034127490509ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 5403818765962913503ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__critical_section_active = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 16383990456654411155ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_commit_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 979593089564051683ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_pc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 10692628394984869724ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 10823674693608766006ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 13389462542173978450ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 5773019427713278193ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 17476145905171705012ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 676504288907958223ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3444994749177803491ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__classifier_keep_event = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8342102961369476646ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 1701681888993964016ull);
    VL_SCOPED_RAND_RESET_W(168, vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet, __VscopeHash, 11176024674962078652ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 15251370181332428779ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__safe_config_seen = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8450300701931662060ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3476672823172156179ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 5635199476285715800ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature = VL_SCOPED_RAND_RESET_I(32, __VscopeHash, 4345252690911930273ull);
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count = VL_SCOPED_RAND_RESET_I(5, __VscopeHash, 7600252529559665566ull);
    for (int __Vi0 = 0; __Vi0 < 256; ++__Vi0) {
        VL_SCOPED_RAND_RESET_W(168, vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem[__Vi0], __VscopeHash, 2162330299275526821ull);
    }
    vlSelf->replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 10836705818203353425ull);
    vlSelf->__VdfgRegularize_h6e95ff9d_0_1 = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1 = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2 = 0;
    vlSelf->__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VstlTriggered[__Vi0] = 0;
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->__VicoTriggered[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__clk__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__rst_n__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__clear__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__capture_mode__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__mem_ready__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__mem_rdata__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__irq__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__external_input_valid__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__external_input_value__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__capsule_read_addr__0 = 0;
    vlSelf->__VicoDidInit = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VactTriggered[__Vi0] = 0;
    }
    vlSelf->__Vtrigprevexpr___TOP__clk__1 = 0;
    vlSelf->__Vtrigprevexpr___TOP__rst_n__1 = 0;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        vlSelf->__VnbaTriggered[__Vi0] = 0;
    }
}
