// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vreplaycapsule_verilator_top.h for the primary calling header

#include "Vreplaycapsule_verilator_top__pch.h"

bool Vreplaycapsule_verilator_top___024root___trigger_anySet__ico(const VlUnpacked<QData/*63:0*/, 2> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___trigger_anySet__ico\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((2U > n));
    return (0U);
}

void Vreplaycapsule_verilator_top___024root___ico_comb__TOP__3(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___ico_comb__TOP__3\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 1U;
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
    } else if (vlSelfRef.external_input_valid) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.external_input_value;
    } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                 & (0x40000000U == (0xffff0000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.mem_rdata;
    } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                 & (0x40000000U == (0xffff0000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata;
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata;
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data
            = vlSelfRef.mem_rdata;
    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid)
                & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data = 0U;
    }
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
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data
        = ((IData)(vlSelfRef.property_fail_valid) ? vlSelfRef.property_signature
            : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data);
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

void Vreplaycapsule_verilator_top___024root___eval_ico(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_ico\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((0x0000000000000200ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_sequent__TOP__0
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
            vlSelfRef.capsule_word5 = (0x000000ffU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem
                                       [vlSelfRef.capsule_read_addr][5U]);
        }
    }
    if ((0x0000000000000020ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_sequent__TOP__1
            if ((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
                    = vlSelfRef.mem_rdata;
            } else if ((1U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
                    = ((2U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)
                        ? (vlSelfRef.mem_rdata >> 0x10U)
                        : (0x0000ffffU & vlSelfRef.mem_rdata));
            } else if ((2U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
                    = ((2U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)
                        ? ((1U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)
                            ? (vlSelfRef.mem_rdata
                               >> 0x18U) : (0x000000ffU
                                            & (vlSelfRef.mem_rdata
                                               >> 0x10U)))
                        : ((1U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)
                            ? (0x000000ffU & (vlSelfRef.mem_rdata
                                              >> 8U))
                            : (0x000000ffU & vlSelfRef.mem_rdata)));
            }
        }
    }
    if ((2ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_sequent__TOP__2
            CData/*0:0*/ __Vinline_0__ico_sequent__TOP__2___VdfgRegularize_h6e95ff9d_0_2;
            __Vinline_0__ico_sequent__TOP__2___VdfgRegularize_h6e95ff9d_0_2 = 0;
            __Vinline_0__ico_sequent__TOP__2___VdfgRegularize_h6e95ff9d_0_2
                = ((~ (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state)))
                   & (IData)(vlSelfRef.rst_n));
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write
                = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)
                   & __Vinline_0__ico_sequent__TOP__2___VdfgRegularize_h6e95ff9d_0_2);
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_read
                = (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch)
                    | (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1))
                   & __Vinline_0__ico_sequent__TOP__2___VdfgRegularize_h6e95ff9d_0_2);
        }
    }
    if ((0x0000000000000010ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_sequent__TOP__3
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer
                = ((IData)(vlSelfRef.mem_ready) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid));
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted
                = ((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr))
                   & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer));
        }
    }
    if ((0x0000000000000030ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_comb__TOP__0
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer)
                    ? vlSelfRef.mem_rdata : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q);
        }
    }
    if ((0x0000000000000012ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_comb__TOP__1
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done
                = ((IData)(vlSelfRef.rst_n) & (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
                                                & (3U
                                                   == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state)))
                                               | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer)
                                                  & ((0U
                                                      != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state))
                                                     & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)
                                                        | (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1))))));
        }
    }
    if ((0x0000000000000090ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_comb__TOP__2
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
                                     & (0x40000000U
                                        == (0xffff0000U
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
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 0U;
            if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 7U;
            } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 8U;
            } else if (vlSelfRef.external_input_valid) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 9U;
            } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                         & (0x40000000U == (0xffff0000U
                                            & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                        & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 5U;
            } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                         & (0x40000000U == (0xffff0000U
                                            & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr)))
                        & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 6U;
            } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                        & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 3U;
            } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted)
                        & (0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb)))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 4U;
            } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid)
                        & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 1U;
            } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type = 0U;
            }
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid
                = ((IData)(vlSelfRef.property_fail_valid)
                   | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid));
            if (vlSelfRef.property_fail_valid) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr
                    = vlSelfRef.property_id;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type = 0x0aU;
            } else {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type;
            }
        }
    }
    if ((0x00000000000001b0ULL & vlSelfRef.__VicoTriggered[0U])) {
        Vreplaycapsule_verilator_top___024root___ico_comb__TOP__3(vlSelf);
    }
    if ((0x0000000000000098ULL & vlSelfRef.__VicoTriggered[0U])) {
        {
            // Inlined CFunc: _ico_comb__TOP__4
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__classifier_keep_event
                = ((8U & (IData)(vlSelfRef.capture_mode))
                    ? (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)
                    : ((4U & (IData)(vlSelfRef.capture_mode))
                        ? (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)
                        : ((2U & (IData)(vlSelfRef.capture_mode))
                            ? ((1U & (IData)(vlSelfRef.capture_mode))
                                ? (((IData)(vlSelfRef.capsule_overflow)
                                    | (0U != (3U &
                                              (0x005fdc54U
                                               >> ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)
                                                   << 1U)))))
                                   & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid))
                                : (((0x005fdc54U >>
                                     ((IData)(1U) +
                                      ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)
                                       << 1U))) | (
                                                   (0U
                                                    != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count))
                                                   | (0x0aU
                                                      == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))))
                                   & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)))
                            : ((1U & (IData)(vlSelfRef.capture_mode))
                                ? (((0x0aU == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                    | ((5U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                       | ((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                          | ((7U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                             | ((8U
                                                 == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type))
                                                | (9U
                                                   == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type)))))))
                                   & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid))
                                : (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid)))));
        }
    }
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___dump_triggers__ico(const VlUnpacked<QData/*63:0*/, 2> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vreplaycapsule_verilator_top___024root___eval_phase__ico(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_phase__ico\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VicoExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__ico
        vlSelfRef.__VicoTriggered[0U] = (QData)((IData)(
                                                        (((((IData)(vlSelfRef.capsule_read_addr)
                                                            != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__capsule_read_addr__0))
                                                           << 9U)
                                                          | ((vlSelfRef.external_input_value
                                                              != vlSelfRef.__Vtrigprevexpr___TOP__external_input_value__0)
                                                             << 8U))
                                                         | (((((((IData)(vlSelfRef.external_input_valid)
                                                                 != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__external_input_valid__0))
                                                                << 3U)
                                                               | ((vlSelfRef.irq
                                                                   != vlSelfRef.__Vtrigprevexpr___TOP__irq__0)
                                                                  << 2U))
                                                              | (((vlSelfRef.mem_rdata
                                                                   != vlSelfRef.__Vtrigprevexpr___TOP__mem_rdata__0)
                                                                  << 1U)
                                                                 | ((IData)(vlSelfRef.mem_ready)
                                                                    != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__mem_ready__0))))
                                                             << 4U)
                                                            | (((((IData)(vlSelfRef.capture_mode)
                                                                  != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__capture_mode__0))
                                                                 << 3U)
                                                                | (((IData)(vlSelfRef.clear)
                                                                    != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__clear__0))
                                                                   << 2U))
                                                               | ((((IData)(vlSelfRef.rst_n)
                                                                    != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0))
                                                                   << 1U)
                                                                  | ((IData)(vlSelfRef.clk)
                                                                     != (IData)(vlSelfRef.__Vtrigprevexpr___TOP__clk__0))))))));
        vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
        vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0 = vlSelfRef.rst_n;
        vlSelfRef.__Vtrigprevexpr___TOP__clear__0 = vlSelfRef.clear;
        vlSelfRef.__Vtrigprevexpr___TOP__capture_mode__0
            = vlSelfRef.capture_mode;
        vlSelfRef.__Vtrigprevexpr___TOP__mem_ready__0
            = vlSelfRef.mem_ready;
        vlSelfRef.__Vtrigprevexpr___TOP__mem_rdata__0
            = vlSelfRef.mem_rdata;
        vlSelfRef.__Vtrigprevexpr___TOP__irq__0 = vlSelfRef.irq;
        vlSelfRef.__Vtrigprevexpr___TOP__external_input_valid__0
            = vlSelfRef.external_input_valid;
        vlSelfRef.__Vtrigprevexpr___TOP__external_input_value__0
            = vlSelfRef.external_input_value;
        vlSelfRef.__Vtrigprevexpr___TOP__capsule_read_addr__0
            = vlSelfRef.capsule_read_addr;
        if (VL_UNLIKELY(((1U & (~ (IData)(vlSelfRef.__VicoDidInit)))))) {
            vlSelfRef.__VicoDidInit = 1U;
            vlSelfRef.__VicoTriggered[0U] = (1ULL | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (2ULL | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (4ULL | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (8ULL | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (0x0000000000000010ULL
                                             | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (0x0000000000000020ULL
                                             | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (0x0000000000000040ULL
                                             | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (0x0000000000000080ULL
                                             | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (0x0000000000000100ULL
                                             | vlSelfRef.__VicoTriggered[0U]);
            vlSelfRef.__VicoTriggered[0U] = (0x0000000000000200ULL
                                             | vlSelfRef.__VicoTriggered[0U]);
        }
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vreplaycapsule_verilator_top___024root___dump_triggers__ico(vlSelfRef.__VicoTriggered, "ico"s);
    }
#endif
    __VicoExecute = Vreplaycapsule_verilator_top___024root___trigger_anySet__ico(vlSelfRef.__VicoTriggered);
    if (__VicoExecute) {
        Vreplaycapsule_verilator_top___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

bool Vreplaycapsule_verilator_top___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___trigger_anySet__act\n"); );
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

void Vreplaycapsule_verilator_top___024root___nba_sequent__TOP__1(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___nba_sequent__TOP__1\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index = 0;
    IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id = 0;
    CData/*7:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count = 0;
    CData/*4:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count = 0;
    CData/*7:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr = 0;
    SData/*8:0*/ __Vdly__capsule_event_count;
    __Vdly__capsule_event_count = 0;
    IData/*31:0*/ __Vdly__running_signature;
    __Vdly__running_signature = 0;
    VlWide<6>/*167:0*/ __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0;
    VL_ZERO_W(168, __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0);
    CData/*7:0*/ __VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0;
    __VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0 = 0;
    CData/*0:0*/ __VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0;
    __VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0 = 0;
    // Body
    __Vdly__running_signature = vlSelfRef.running_signature;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr;
    __Vdly__capsule_event_count = vlSelfRef.capsule_event_count;
    __VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0 = 0U;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
    if (vlSelfRef.rst_n) {
        if (vlSelfRef.clear) {
            __Vdly__running_signature = 0x52435256U;
            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count = 0U;
            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id = 0U;
            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count = 0U;
            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index = 0U;
            vlSelfRef.property_id = 0U;
            vlSelfRef.property_signature = 0U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_pc = 0U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_commit_index = 0U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__critical_section_active = 0U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__safe_config_seen = 0U;
            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr = 0U;
            __Vdly__capsule_event_count = 0U;
            vlSelfRef.capsule_overflow = 0U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q = 0U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__fetch_context_pc = 0x00000080U;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active = 0U;
            vlSelfRef.capsule_frozen = 0U;
        } else {
            if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__classifier_keep_event) {
                __Vdly__running_signature = (0x9e3779b9U
                                             ^ (((vlSelfRef.running_signature
                                                  << 5U)
                                                 | (vlSelfRef.running_signature
                                                    >> 0x1bU))
                                                ^ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id
                                                   ^
                                                   (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index
                                                    ^
                                                    (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc
                                                     ^
                                                     (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr
                                                      ^
                                                      (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data
                                                       ^
                                                       (0x000000ffU
                                                        & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[5U]))))))));
            }
            if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__classifier_keep_event)
                 & (~ (IData)(vlSelfRef.capsule_frozen)))) {
                __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id
                    = ((IData)(1U) + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id);
                if ((0x0100U > (IData)(vlSelfRef.capsule_event_count))) {
                    __Vdly__capsule_event_count = (0x000001ffU
                                                   & ((IData)(1U)
                                                      + (IData)(vlSelfRef.capsule_event_count)));
                    __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[0U]
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[0U];
                    __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[1U]
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[1U];
                    __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[2U]
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[2U];
                    __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[3U]
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[3U];
                    __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[4U]
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[4U];
                    __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[5U]
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet[5U];
                    __VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr;
                    __VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0 = 1U;
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr
                        = (0x000000ffU & ((IData)(1U)
                                          + (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr)));
                } else {
                    vlSelfRef.capsule_overflow = 1U;
                }
            }
            if (vlSelfRef.property_fail_valid) {
                __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count = 0x10U;
                vlSelfRef.capsule_frozen = 1U;
            } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid)
                        & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count)))) {
                __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count
                    = (0x0000001fU & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count)
                                      - (IData)(1U)));
            }
            if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid) {
                if ((((5U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                      & (0x40000000U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                     & (0x000002bcU < vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))) {
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count = 0x10U;
                }
                if ((((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                      & (0x40000004U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                     & (0x00000064U >= vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))) {
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count = 0U;
                } else if ((((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                             & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active))
                            & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count)))) {
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count
                        = (0x000000ffU & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count)
                                          - (IData)(1U)));
                }
                if ((((5U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                      & (0x40000000U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                     & (0x000002bcU < vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active = 1U;
                }
                if ((((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                      & (0x40000004U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                     & (0x00000064U >= vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active = 0U;
                }
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_pc
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_commit_index
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
                if (((((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                       & (0x4000000cU == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                      & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data)
                     & (0x0000feedU != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__critical_section_active = 1U;
                } else if (((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                            & (0x40000008U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__critical_section_active = 0U;
                }
                if ((((6U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type))
                      & (0x40000008U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr))
                     & (0x0000cafeU == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__safe_config_seen = 1U;
                }
            }
            if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid)
                 & (~ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                       >> 0x00000021U)))) {
                __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index
                    = ((IData)(1U) + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index);
            }
            vlSelfRef.property_id = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id;
            vlSelfRef.property_signature = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature;
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi;
            if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid)
                  & (IData)(vlSelfRef.mem_ready)) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__fetch_context_pc
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
            }
        }
    } else {
        __Vdly__running_signature = 0x52435256U;
        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count = 0U;
        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id = 0U;
        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count = 0U;
        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index = 0U;
        vlSelfRef.property_id = 0U;
        vlSelfRef.property_signature = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_pc = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_commit_index = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__critical_section_active = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__safe_config_seen = 0U;
        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr = 0U;
        __Vdly__capsule_event_count = 0U;
        vlSelfRef.capsule_overflow = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__fetch_context_pc = 0x00000080U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active = 0U;
        vlSelfRef.capsule_frozen = 0U;
    }
    vlSelfRef.running_signature = __Vdly__running_signature;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr;
    vlSelfRef.capsule_event_count = __Vdly__capsule_event_count;
    if (__VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem[__VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0][0U]
            = __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[0U];
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem[__VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0][1U]
            = __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[1U];
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem[__VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0][2U]
            = __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[2U];
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem[__VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0][3U]
            = __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[3U];
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem[__VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0][4U]
            = __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[4U];
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem[__VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0][5U]
            = __VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem__v0[5U];
    }
    vlSelfRef.commit_count = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
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
    vlSelfRef.property_fail_valid = ((IData)(vlSelfRef.rst_n)
                                     && ((1U & (~ (IData)(vlSelfRef.clear)))
                                         && (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail)));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index
        = ((IData)(vlSelfRef.property_fail_valid) ? vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_commit_index
            : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index);
}

void Vreplaycapsule_verilator_top___024root___nba_sequent__TOP__2(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___nba_sequent__TOP__2\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rinst;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rinst = 0;
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rdata;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rdata = 0;
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_wdata;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_wdata = 0;
    IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending = 0;
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq = 0;
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu = 0;
    CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts = 0;
    CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_2;
    __VdfgRegularize_h6e95ff9d_0_2 = 0;
    CData/*4:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh = 0;
    IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out = 0;
    QData/*63:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle = 0;
    CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger = 0;
    CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger = 0;
    CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq = 0;
    // Body
    if ((1U & (~ ((~ (IData)(vlSelfRef.rst_n)) | (IData)(vlSelfRef.trap))))) {
        if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_read)
             | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr
                = ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch)
                     | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst))
                     ? ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store)
                          & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch))
                          ? (0xfffffffeU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out)
                          : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc)
                        >> 2U) : (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                                  >> 2U)) << 2U);
        }
    }
    if ((1U & ((~ (IData)(vlSelfRef.rst_n)) | (IData)(vlSelfRef.trap)))) {
        if ((1U & (~ (IData)(vlSelfRef.rst_n)))) {
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state = 0U;
        }
        if ((1U & ((~ (IData)(vlSelfRef.rst_n)) | (IData)(vlSelfRef.mem_ready)))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid = 0U;
        }
    } else {
        if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_read)
             | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write))) {
            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb
                = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wstrb)
                   & (- (IData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write))));
        }
        if ((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state))) {
            if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch)
                  | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst))
                 | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr
                    = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch)
                       | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst));
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state = 1U;
            }
            if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid = 1U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state = 2U;
            }
        } else if ((1U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state))) {
            if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state
                    = (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
                        | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata))
                        ? 0U : 3U);
            }
        } else if ((2U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state))) {
            if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state = 0U;
            }
        } else if ((3U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state))) {
            if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst) {
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state = 0U;
            }
        }
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state;
    vlSelfRef.mem_addr = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
    __VdfgRegularize_h6e95ff9d_0_2 = ((~ (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state)))
                                      & (IData)(vlSelfRef.rst_n));
    vlSelfRef.mem_wstrb = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb;
    vlSelfRef.mem_instr = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr;
    vlSelfRef.mem_valid = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid;
    vlSelfRef.trap = 0U;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh = 0U;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out = 0U;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rinst = 0U;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rdata = 0U;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_wdata = 0U;
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
           & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done));
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger = 0U;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq = 0U;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid = 0U;
    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle
        = ((IData)(vlSelfRef.rst_n) ? (1ULL + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle)
            : 0ULL);
    if ((0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer)) {
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer
            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer
               - (IData)(1U));
    }
    if (vlSelfRef.rst_n) {
        if (((((((((0x80U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))
                   | (0x40U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state)))
                  | (0x20U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state)))
                 | (0x10U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state)))
                | (8U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state)))
               | (4U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state)))
              | (2U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state)))
             | (1U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state)))) {
            if ((0x80U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
                vlSelfRef.trap = 1U;
            } else if ((0x40U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
                    = (1U & ((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger))
                             & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq))));
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb = 0U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc;
                if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc
                        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store)
                            ? (0xfffffffeU & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu)
                                               ? vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_q
                                               : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out))
                            : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc);
                } else if ((1U & (~ ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store)
                                     & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch)))))) {
                    if ((1U & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state))) {
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc = 0x00000010U;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active = 1U;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 1U;
                    } else if ((2U & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state))) {
                        replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
                            = (replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
                               & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask);
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending
                               & (~ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask));
                    }
                }
                if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_trace) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_trace = 0U;
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid = 1U;
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch)
                            ? (0x0000000100000000ULL
                               | (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active)
                                    ? 0x0000000800000000ULL
                                    : 0ULL) | (0x00000000fffffffeULL
                                               & (QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc)))))
                            : (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active)
                                 ? 0x0000000800000000ULL
                                 : 0ULL) | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu)
                                             ? (QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_q))
                                             : (QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out)))));
                }
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 0U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu = 0U;
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rd;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__compressed_instr;
                if ((((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger)
                        & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active)))
                       & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_delay)))
                      & (0U != (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending
                                & (~ vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask))))
                     | (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state)))) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state
                        = ((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state))
                            ? 1U : ((1U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state))
                                     ? 2U : 0U));
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd
                        = (0x20U | (1U & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state)));
                } else if ((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger)
                             | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq))
                            & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_waitirq))) {
                    if ((0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending)) {
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending;
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc
                               + ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__compressed_instr)
                                   ? 2U : 4U));
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 1U;
                    } else {
                        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq = 1U;
                    }
                } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr
                        = (1ULL + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr);
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_delay
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active;
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc
                        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc
                           + ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__compressed_instr)
                               ? 2U : 4U));
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_trace = 1U;
                    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 1U;
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc
                               + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j);
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch = 1U;
                    } else {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 0U;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch
                            = (1U & ((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr))
                                     & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_retirq))));
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x20U;
                    }
                }
            } else if ((0x20U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1 = 0U;
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2 = 0U;
                if (((((((((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_trap)
                           | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_rdcycle_rdcycleh_rdinstr_rdinstrh))
                          | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal))
                         | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_getq))
                        | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_setq))
                       | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_retirq))
                      | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_maskirq))
                     | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_timer))) {
                    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_trap) {
                        if ((1U & ((~ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask
                                       >> 1U)) & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active))))) {
                            replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
                                = (2U | replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending);
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                        } else {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x80U;
                        }
                    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_rdcycle_rdcycleh_rdinstr_rdinstrh) {
                        if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycle) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle);
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycleh) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = (IData)((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle
                                           >> 0x20U));
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstr) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr);
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstrh) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = (IData)((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr
                                           >> 0x20U));
                        }
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui)
                                ? 0U : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc);
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
                            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 8U;
                    } else {
                        if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_getq) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_setq) {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd
                                = (0x20U | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd));
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_retirq) {
                            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi = 0U;
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active = 0U;
                            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch = 1U;
                            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = (0xfffffffeU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1);
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_maskirq) {
                            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask;
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask
                                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                        } else {
                            vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer;
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer
                                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                        }
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                    }
                } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu)
                            & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_trap)))) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 1U;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 1U;
                } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slli_srli_srai) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 4U;
                } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_jalr_addi_slti_sltiu_xori_ori_andi) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 8U;
                } else {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh
                        = (0x0000001fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2);
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2;
                    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 2U;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 1U;
                    } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sll_srl_sra) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 4U;
                    } else {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
                            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 8U;
                    }
                }
            } else if ((0x10U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
                __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh
                    = (0x0000001fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2);
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2;
                if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 2U;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 1U;
                } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sll_srl_sra) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 4U;
                } else {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 8U;
                }
            } else if ((8U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
                __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                    = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc
                       + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm);
                if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu) {
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd = 0U;
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0;
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0;
                    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                    }
                    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0) {
                        replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rinst = 1U;
                        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger = 0U;
                    }
                } else {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr;
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu = 1U;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                }
            } else if ((4U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                if ((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh))) {
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
                    vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                } else if ((4U <= (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh))) {
                    if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slli)
                         | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sll))) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                               << 4U);
                    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srli)
                                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srl))) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                               >> 4U);
                    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srai)
                                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sra))) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = VL_SHIFTRS_III(32,32,32, vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1, 4U);
                    }
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh
                        = (0x0000001fU & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh)
                                          - (IData)(4U)));
                } else {
                    if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slli)
                         | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sll))) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                               << 1U);
                    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srli)
                                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srl))) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                               >> 1U);
                    } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srai)
                                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sra))) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = VL_SHIFTRS_III(32,32,32, vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1, 1U);
                    }
                    __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh
                        = (0x0000001fU & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh)
                                          - (IData)(1U)));
                }
            } else if ((2U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state))) {
                __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                    = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2;
                if ((1U & ((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch))
                           | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done)))) {
                    if ((1U & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)))) {
                        replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_wdata = 1U;
                        if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sb) {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 2U;
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sh) {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 1U;
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sw) {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 0U;
                        }
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid = 1U;
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                            = (0x0000000200000000ULL
                               | (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active)
                                    ? 0x0000000800000000ULL
                                    : 0ULL) | (0x00000000ffffffffULL
                                               & ((QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1))
                                                  + (QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm))))));
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                               + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm);
                    }
                    if (((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch))
                         & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done))) {
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger = 1U;
                        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger = 1U;
                    }
                }
            } else {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
                if ((1U & ((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch))
                           | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done)))) {
                    if (((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch))
                         & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done))) {
                        if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word;
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = VL_EXTENDS_II(32,16,
                                                (0x0000ffffU
                                                 & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word));
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb) {
                            __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                                = VL_EXTENDS_II(32,8,
                                                (0x000000ffU
                                                 & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word));
                        }
                        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger = 1U;
                        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger = 1U;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
                    }
                    if ((1U & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata)))) {
                        replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rdata = 1U;
                        if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lb)
                             | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lbu))) {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 2U;
                        } else if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lh)
                                    | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lhu))) {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 1U;
                        } else if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lw) {
                            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize = 0U;
                        }
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu
                            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lbu_lhu_lw;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh
                            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lh;
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb
                            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lb;
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid = 1U;
                        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                            = (0x0000000200000000ULL
                               | (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active)
                                    ? 0x0000000800000000ULL
                                    : 0ULL) | (0x00000000ffffffffULL
                                               & ((QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1))
                                                  + (QData)((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm))))));
                        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                            = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                               + vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm);
                    }
                }
            }
        }
    } else {
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr = 0ULL;
        replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc = 0x00000080U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc = 0x00000080U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_trace = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_delay = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask = 0xffffffffU;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd = 2U;
        __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out = 0x00002000U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x40U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store = 1U;
    }
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
        = (replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
           | vlSelfRef.irq);
    if ((0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer)) {
        if ((0U == (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer
                    - (IData)(1U)))) {
            replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
                = (1U | replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending);
        }
    }
    if (((IData)(vlSelfRef.rst_n) & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata)
                                     | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)))) {
        if (((0U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))
             & (0U != (3U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)))) {
            if ((1U & ((~ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask
                           >> 2U)) & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active))))) {
                replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
                    = (4U | replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending);
            } else {
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x80U;
            }
        }
        if (((1U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize))
             & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)) {
            if ((1U & ((~ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask
                           >> 2U)) & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active))))) {
                replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
                    = (4U | replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending);
            } else {
                vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x80U;
            }
        }
    }
    if ((((IData)(vlSelfRef.rst_n) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst))
         & (0U != (3U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc)))) {
        if ((1U & ((~ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask
                       >> 2U)) & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active))))) {
            replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending
                = (4U | replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending);
        } else {
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state = 0x80U;
        }
    }
    if ((1U & ((~ (IData)(vlSelfRef.rst_n)) | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done)))) {
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch = 0U;
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata = 0U;
    }
    if (replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rinst) {
        vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst = 1U;
    }
    if (replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_rdata) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata = 1U;
    }
    if (replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__set_mem_do_wdata) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata = 1U;
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending
        = replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__next_irq_pending;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc = 0U;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs
           [vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1]
           & (- (IData)(((0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1))
                         & (0x23U >= (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1))))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)
           & (IData)(__VdfgRegularize_h6e95ff9d_0_2));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write = 0U;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_q
        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out;
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
            if ((2U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1)) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word
                    = (vlSelfRef.mem_rdata >> 0x10U);
            }
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
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_eq
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
           == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_lts
        = VL_LTS_III(32, vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1, vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_ltu
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
           < vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2);
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid
        = (IData)(((~ (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                       >> 0x00000021U)) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid)));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid)
           & (0U != (1U & (IData)((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                                   >> 0x00000020U)))));
    vlSelfRef.eoi = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lbu_lhu_lw
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lbu)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lhu)
              | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lw)));
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
    if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
         & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__compressed_instr = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rd
            = (0x0000001fU & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                              >> 7U));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2
            = (0x0000001fU & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                              >> 0x14U));
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2
        = (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs
           [vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2]
           & (- (IData)((0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2)))));
    if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger)
         & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_getq
            = (IData)((0x0000000bU == (0xfe00007fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_setq
            = (IData)((0x0200000bU == (0xfe00007fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_maskirq
            = (IData)((0x0600000bU == (0xfe00007fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_timer
            = (IData)((0x0a00000bU == (0xfe00007fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycle
            = ((IData)((0xc0002073U == (0xfffff07fU
                                        & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)))
               | (IData)((0xc0102073U == (0xfffff07fU
                                          & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycleh
            = ((IData)((0xc8002073U == (0xfffff07fU
                                        & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)))
               | (IData)((0xc8102073U == (0xfffff07fU
                                          & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstr
            = (IData)((0xc0202073U == (0xfffff07fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstrh
            = (IData)((0xc8202073U == (0xfffff07fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_rdcycle_rdcycleh_rdinstr_rdinstrh
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycle)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycleh)
              | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstr)
                 | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstrh))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_auipc)
              | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal)));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal_jalr_addi_add_sub
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_auipc)
              | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal)
                 | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr)
                    | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_addi)
                       | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_add)
                          | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sub)))))));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slti_blt_slt
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slti)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_blt)
              | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slt)));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sltiu_bltu_sltu
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltiu)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bltu)
              | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltu)));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_compare
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
           | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slti)
              | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slt)
                 | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltiu)
                    | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltu)))));
    if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger)
         & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_beq
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
               & (0U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bne
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
               & (0x00001000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_blt
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
               & (0x00004000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bge
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
               & (0x00005000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bltu
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
               & (0x00006000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bgeu
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
               & (0x00007000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lb
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu)
               & (0U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lh
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu)
               & (0x00001000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lw
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu)
               & (0x00002000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lbu
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu)
               & (0x00004000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lhu
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu)
               & (0x00005000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sb
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw)
               & (0U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sh
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw)
               & (0x00001000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sw
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw)
               & (0x00002000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_addi
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slti
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x00002000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltiu
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x00003000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xori
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x00004000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_ori
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x00006000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_andi
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x00007000U == (0x00007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slli
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x00001000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srli
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x00005000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srai
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & (0x40005000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slli_srli_srai
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
               & ((IData)((0x00001000U == (0xfe007000U
                                           & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)))
                  | ((IData)((0x00005000U == (0xfe007000U
                                              & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)))
                     | (IData)((0x40005000U == (0xfe007000U
                                                & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q))))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_jalr_addi_slti_sltiu_xori_ori_andi
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr)
               | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)
                  & ((0U == (7U & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                   >> 0x0cU))) | ((2U
                                                   ==
                                                   (7U
                                                    & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                       >> 0x0cU)))
                                                  | ((3U
                                                      ==
                                                      (7U
                                                       & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                          >> 0x0cU)))
                                                     | ((4U
                                                         ==
                                                         (7U
                                                          & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                             >> 0x0cU)))
                                                        | ((6U
                                                            ==
                                                            (7U
                                                             & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                                >> 0x0cU)))
                                                           | (7U
                                                              ==
                                                              (7U
                                                               & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                                  >> 0x0cU))))))))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal_jalr_addi_add_sub = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_compare = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal)
                ? vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j
                : (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui)
                    | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_auipc))
                    ? (0xfffff000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)
                    : (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr)
                        | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu)
                           | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm)))
                        ? VL_EXTENDS_II(32,12, (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                >> 0x14U))
                        : ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu)
                            ? VL_EXTENDS_II(32,13,
                                            ((((2U
                                                & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                   >> 0x0000001eU))
                                               | (1U
                                                  & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                     >> 7U)))
                                              << 0x0000000bU)
                                             | ((0x000007e0U
                                                 & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                    >> 0x00000014U))
                                                | (0x0000001eU
                                                   & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                      >> 7U)))))
                            : ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw)
                                ? VL_EXTENDS_II(32,12,
                                                ((0x00000fe0U
                                                  & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                     >> 0x00000014U))
                                                 | (0x0000001fU
                                                    & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                                       >> 7U))))
                                : 0U)))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_add
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sub
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x40000000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sll
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x00001000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slt
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x00002000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltu
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x00003000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xor
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x00004000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srl
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x00005000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sra
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x40005000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_or
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x00006000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_and
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & (0x00007000U == (0xfe007000U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sll_srl_sra
            = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg)
               & ((IData)((0x00001000U == (0xfe007000U
                                           & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)))
                  | ((IData)((0x00005000U == (0xfe007000U
                                              & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q)))
                     | (IData)((0x40005000U == (0xfe007000U
                                                & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q))))));
    }
    if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
         & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_waitirq
            = (IData)((0x0800000bU == (0xfe00007fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_retirq
            = (IData)((0x0400000bU == (0xfe00007fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm
            = (0x13U == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu
            = (3U == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw
            = (0x23U == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j
            = ((0x000fffffU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j)
               | (0xfff00000U & VL_EXTENDS_II(32,21,
                                              (0x001ffffeU
                                               & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                                                  >> 0x0000000bU)))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j
            = ((0xfffff801U & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j)
               | (0x000007feU & (VL_EXTENDS_II(32,21,
                                               (0x001ffffeU
                                                & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                                                   >> 0x0000000bU)))
                                 >> 9U)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j
            = ((0xfffff7ffU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j)
               | (0x00000800U & (VL_EXTENDS_II(32,21,
                                               (0x001ffffeU
                                                & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                                                   >> 0x0000000bU)))
                                 << 2U)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j
            = ((0xfff00fffU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j)
               | (0x000ff000U & (VL_EXTENDS_II(32,21,
                                               (0x001ffffeU
                                                & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                                                   >> 0x0000000bU)))
                                 << 0x0000000bU)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j
            = ((0xfffffffeU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j)
               | (1U & VL_EXTENDS_II(1,21, (0x001ffffeU
                                            & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                                               >> 0x0000000bU)))));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu
            = (0x63U == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_auipc
            = (0x17U == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui
            = (0x37U == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal
            = (0x6fU == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr
            = (IData)((0x00000067U == (0x0000707fU
                                       & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle)));
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg
            = (0x33U == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle));
    }
    if ((1U & (~ (IData)(vlSelfRef.rst_n)))) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_compare = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_beq = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bne = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_blt = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bge = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bltu = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bgeu = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_addi = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slti = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltiu = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xori = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_ori = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_andi = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_add = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sub = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sll = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slt = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltu = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xor = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srl = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sra = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_or = 0U;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_and = 0U;
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger;
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger
        = __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger;
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
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
        = vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst;
    if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer) {
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
            = vlSelfRef.mem_rdata;
    }
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer
        = ((IData)(vlSelfRef.mem_ready) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
        = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer)
            ? vlSelfRef.mem_rdata : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q);
    vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1 = ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
                                                | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted
        = ((~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr))
           & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_read
        = (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch)
            | (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1))
           & (IData)(__VdfgRegularize_h6e95ff9d_0_2));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done
        = ((IData)(vlSelfRef.rst_n) & (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
                                        & (3U == (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state)))
                                       | ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer)
                                          & ((0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state))
                                             & ((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata)
                                                | (IData)(vlSelfRef.__VdfgRegularize_h6e95ff9d_0_1))))));
}

void Vreplaycapsule_verilator_top___024root___nba_comb__TOP__0(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___nba_comb__TOP__0\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc
        = ((0U != (1U & (IData)((vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data
                                 >> 0x00000020U))))
            ? (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data)
            : vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__fetch_context_pc);
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter
        = ((0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi)
           & (0U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q));
    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit
        = ((0U == vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi)
           & (0U != vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q));
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
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc
            = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_pc;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr
            = vlSelfRef.property_id;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data
            = vlSelfRef.property_signature;
        vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type = 0x0aU;
    } else {
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

void Vreplaycapsule_verilator_top___024root___eval_nba(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_nba\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
        {
            // Inlined CFunc: _nba_sequent__TOP__0
            CData/*4:0*/ __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh = 0;
            IData/*31:0*/ __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out = 0;
            QData/*63:0*/ __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle = 0;
            CData/*0:0*/ __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger = 0;
            CData/*0:0*/ __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger = 0;
            CData/*0:0*/ __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq = 0;
            IData/*31:0*/ __Vinline_0__nba_sequent__TOP__0___VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0;
            __Vinline_0__nba_sequent__TOP__0___VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0 = 0;
            CData/*5:0*/ __Vinline_0__nba_sequent__TOP__0___VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0;
            __Vinline_0__nba_sequent__TOP__0___VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0 = 0;
            CData/*0:0*/ __Vinline_0__nba_sequent__TOP__0___VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0;
            __Vinline_0__nba_sequent__TOP__0___VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0 = 0;
            __Vinline_0__nba_sequent__TOP__0___VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0 = 0U;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize;
            __Vinline_0__nba_sequent__TOP__0___Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1;
            vlSelfRef.__Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state
                = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state;
            if ((((IData)(vlSelfRef.rst_n) & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write))
                 & (0U != (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd)))) {
                if ((0x23U >= (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd))) {
                    __Vinline_0__nba_sequent__TOP__0___VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata;
                    __Vinline_0__nba_sequent__TOP__0___VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd;
                    __Vinline_0__nba_sequent__TOP__0___VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0 = 1U;
                }
            }
            if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst)
                 & (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1
                    = (0x0000001fU & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle
                                      >> 0x0fU));
                if ((IData)((0x0000000bU == (0xfe00007fU
                                             & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle)))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1
                        = (0x00000020U | (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1));
                }
                if ((IData)((0x0400000bU == (0xfe00007fU
                                             & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle)))) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1 = 0x20U;
                }
            }
            if (((IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger)
                 & (~ (IData)(vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger)))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_fence
                    = ((0x0fU == (0x0000007fU & vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q))
                       & (~ (0U != (7U & (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q
                                          >> 0x0cU)))));
            }
            if ((1U & (~ (IData)(vlSelfRef.rst_n)))) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_fence = 0U;
            }
            if ((1U & (~ ((~ (IData)(vlSelfRef.rst_n))
                          | (IData)(vlSelfRef.trap))))) {
                if (vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write) {
                    vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata
                        = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wdata;
                }
            }
            if (__Vinline_0__nba_sequent__TOP__0___VdlySet__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0) {
                vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs[__Vinline_0__nba_sequent__TOP__0___VdlyDim0__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0]
                    = __Vinline_0__nba_sequent__TOP__0___VdlyVal__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs__v0;
            }
            vlSelfRef.mem_wdata = vlSelfRef.replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata;
        }
    }
    if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vreplaycapsule_verilator_top___024root___nba_sequent__TOP__1(vlSelf);
    }
    if ((1ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vreplaycapsule_verilator_top___024root___nba_sequent__TOP__2(vlSelf);
    }
    if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
        Vreplaycapsule_verilator_top___024root___nba_comb__TOP__0(vlSelf);
    }
}

void Vreplaycapsule_verilator_top___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___trigger_orInto__act_vec_vec\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = (out[n] | in[n]);
        n = ((IData)(1U) + n);
    } while ((0U >= n));
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vreplaycapsule_verilator_top___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vreplaycapsule_verilator_top___024root___eval_phase__act(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_phase__act\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((((~ (IData)(vlSelfRef.rst_n))
                                                           & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__rst_n__1))
                                                          << 1U)
                                                         | ((IData)(vlSelfRef.clk)
                                                            & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__clk__1))))));
        vlSelfRef.__Vtrigprevexpr___TOP__clk__1 = vlSelfRef.clk;
        vlSelfRef.__Vtrigprevexpr___TOP__rst_n__1 = vlSelfRef.rst_n;
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vreplaycapsule_verilator_top___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vreplaycapsule_verilator_top___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    return (0U);
}

void Vreplaycapsule_verilator_top___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vreplaycapsule_verilator_top___024root___eval_phase__nba(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_phase__nba\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vreplaycapsule_verilator_top___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        Vreplaycapsule_verilator_top___024root___eval_nba(vlSelf);
        Vreplaycapsule_verilator_top___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vreplaycapsule_verilator_top___024root___eval(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VicoIterCount;
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VicoIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VicoIterCount)))) {
#ifdef VL_DEBUG
            Vreplaycapsule_verilator_top___024root___dump_triggers__ico(vlSelfRef.__VicoTriggered, "ico"s);
#endif
            VL_FATAL_MT("tb/verilator\\replaycapsule_verilator_top.sv", 3, "", "DIDNOTCONVERGE: Input combinational region did not converge after '--converge-limit' of 10000 tries");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        vlSelfRef.__VicoPhaseResult = Vreplaycapsule_verilator_top___024root___eval_phase__ico(vlSelf);
    } while (vlSelfRef.__VicoPhaseResult);
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vreplaycapsule_verilator_top___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("tb/verilator\\replaycapsule_verilator_top.sv", 3, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vreplaycapsule_verilator_top___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                VL_FATAL_MT("tb/verilator\\replaycapsule_verilator_top.sv", 3, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U)
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactPhaseResult = Vreplaycapsule_verilator_top___024root___eval_phase__act(vlSelf);
        } while (vlSelfRef.__VactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vreplaycapsule_verilator_top___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

#ifdef VL_DEBUG
void Vreplaycapsule_verilator_top___024root___eval_debug_assertions(Vreplaycapsule_verilator_top___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vreplaycapsule_verilator_top___024root___eval_debug_assertions\n"); );
    Vreplaycapsule_verilator_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.clk & 0xfeU)))) {
        Verilated::overWidthError("clk");
    }
    if (VL_UNLIKELY(((vlSelfRef.rst_n & 0xfeU)))) {
        Verilated::overWidthError("rst_n");
    }
    if (VL_UNLIKELY(((vlSelfRef.clear & 0xfeU)))) {
        Verilated::overWidthError("clear");
    }
    if (VL_UNLIKELY(((vlSelfRef.capture_mode & 0xf0U)))) {
        Verilated::overWidthError("capture_mode");
    }
    if (VL_UNLIKELY(((vlSelfRef.mem_ready & 0xfeU)))) {
        Verilated::overWidthError("mem_ready");
    }
    if (VL_UNLIKELY(((vlSelfRef.external_input_valid
                      & 0xfeU)))) {
        Verilated::overWidthError("external_input_valid");
    }
}
#endif  // VL_DEBUG
