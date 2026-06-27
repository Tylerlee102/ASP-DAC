// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vreplaycapsule_verilator_top.h for the primary calling header

#ifndef VERILATED_VREPLAYCAPSULE_VERILATOR_TOP___024ROOT_H_
#define VERILATED_VREPLAYCAPSULE_VERILATOR_TOP___024ROOT_H_  // guard

#include "verilated.h"


class Vreplaycapsule_verilator_top__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vreplaycapsule_verilator_top___024root final {
  public:

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        VL_IN8(clk,0,0);
        VL_IN8(rst_n,0,0);
        VL_IN8(clear,0,0);
        VL_IN8(capture_mode,3,0);
        VL_OUT8(trap,0,0);
        VL_OUT8(mem_valid,0,0);
        VL_OUT8(mem_instr,0,0);
        VL_IN8(mem_ready,0,0);
        VL_OUT8(mem_wstrb,3,0);
        VL_IN8(external_input_valid,0,0);
        VL_IN8(capsule_read_addr,7,0);
        VL_OUT8(capsule_word5,7,0);
        VL_OUT8(capsule_frozen,0,0);
        VL_OUT8(capsule_overflow,0,0);
        VL_OUT8(property_fail_valid,0,0);
        VL_OUT8(property_id,7,0);
        CData/*3:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wstrb;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_valid;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_instr;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_valid;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__branch_taken;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_enter;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__interrupt_exit;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__mem_accepted;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT____Vcellinp__u_replay_capsule_top__commit_valid;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_read;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_write;
        CData/*3:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wstrb;
        CData/*4:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_sh;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_delay;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active;
        CData/*1:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state;
        CData/*1:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rdata;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_wdata;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_xfer;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_done;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lui;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_auipc;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jal;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_jalr;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_beq;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bne;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_blt;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bge;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bltu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_bgeu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lb;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lh;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lw;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lbu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_lhu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sb;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sh;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sw;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_addi;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slti;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltiu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xori;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_ori;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_andi;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slli;
    };
    struct {
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srli;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srai;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_add;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sub;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sll;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_slt;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sltu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_xor;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_srl;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_sra;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_or;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_and;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycle;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdcycleh;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstr;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_rdinstrh;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_fence;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_getq;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_setq;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_retirq;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_maskirq;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_waitirq;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_timer;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__instr_trap;
        CData/*5:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rd;
        CData/*5:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs1;
        CData/*4:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_rs2;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_trigger;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoder_pseudo_trigger;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__compressed_instr;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lb_lh_lw_lbu_lhu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slli_srli_srai;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_jalr_addi_slti_sltiu_xori_ori_andi;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sb_sh_sw;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sll_srl_sra;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lui_auipc_jal_jalr_addi_add_sub;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_slti_blt_slt;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_sltiu_bltu_sltu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_beq_bne_blt_bge_bltu_bgeu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_lbu_lhu_lw;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_imm;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_alu_reg_reg;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_compare;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__is_rdcycle_rdcycleh_rdinstr_rdinstrh;
        CData/*7:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state;
        CData/*1:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_store;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_stalu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_branch;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_trace;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb;
        CData/*5:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__do_waitirq;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_0;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_write;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_valid;
        CData/*3:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_type;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__sensor_deadline_active;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__critical_section_active;
        CData/*3:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_type;
    };
    struct {
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_event_valid;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__classifier_keep_event;
        CData/*7:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__deadline_count;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__safe_config_seen;
        CData/*0:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_fail;
        CData/*7:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_property_id;
        CData/*4:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_event_slicer__DOT__context_count;
        CData/*7:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__write_ptr;
        CData/*0:0*/ __VdfgRegularize_h6e95ff9d_0_1;
        CData/*1:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_state;
        CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_rinst;
        CData/*1:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_wordsize;
        CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lu;
        CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lh;
        CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_is_lb;
        CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_active;
        CData/*5:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_rd;
        CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__latched_compr;
        CData/*1:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_state;
        CData/*0:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_do_prefetch;
        CData/*7:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpu_state;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VstlPhaseResult;
        CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__clear__0;
        CData/*3:0*/ __Vtrigprevexpr___TOP__capture_mode__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__mem_ready__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__external_input_valid__0;
        CData/*7:0*/ __Vtrigprevexpr___TOP__capsule_read_addr__0;
        CData/*0:0*/ __VicoDidInit;
        CData/*0:0*/ __VicoPhaseResult;
        CData/*0:0*/ __Vtrigprevexpr___TOP__clk__1;
        CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__1;
        CData/*0:0*/ __VactPhaseResult;
        CData/*0:0*/ __VnbaPhaseResult;
        VL_OUT16(capsule_event_count,8,0);
        VL_OUT(mem_addr,31,0);
        VL_OUT(mem_wdata,31,0);
        VL_IN(mem_rdata,31,0);
        VL_IN(irq,31,0);
        VL_OUT(eoi,31,0);
        VL_IN(external_input_value,31,0);
        VL_OUT(capsule_word0,31,0);
        VL_OUT(capsule_word1,31,0);
        VL_OUT(capsule_word2,31,0);
        VL_OUT(capsule_word3,31,0);
        VL_OUT(capsule_word4,31,0);
        VL_OUT(running_signature,31,0);
        VL_OUT(property_signature,31,0);
        VL_OUT(commit_count,31,0);
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_addr;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_mem_wdata;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_eoi_q;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__commit_index;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__fetch_context_pc;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_la_wdata;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_next_pc;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_out;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask;
    };
    struct {
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_pending;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_word;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_q;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__mem_rdata_latched_noshuffle;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__decoded_imm_j;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__current_pc;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__alu_out_q;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_wrdata;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs1;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs_rs2;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_pc;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_addr;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__raw_event_data;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_commit_index;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__last_pc;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_commit_index;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_pc;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_addr;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__final_data;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_id;
        VlWide<6>/*167:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__event_packet;
        IData/*31:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_property_checker__DOT__detected_signature;
        IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__timer;
        IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_pc;
        IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op1;
        IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__reg_op2;
        IData/*31:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__irq_mask;
        IData/*31:0*/ __Vtrigprevexpr___TOP__mem_rdata__0;
        IData/*31:0*/ __Vtrigprevexpr___TOP__irq__0;
        IData/*31:0*/ __Vtrigprevexpr___TOP__external_input_value__0;
        IData/*31:0*/ __VactIterCount;
        QData/*35:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__core_trace_data;
        QData/*63:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_cycle;
        QData/*63:0*/ replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr;
        QData/*63:0*/ __Vdly__replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__count_instr;
        VlUnpacked<IData/*31:0*/, 36> replaycapsule_verilator_top__DOT__u_dut__DOT__u_picorv32__DOT__cpuregs;
        VlUnpacked<VlWide<6>/*167:0*/, 256> replaycapsule_verilator_top__DOT__u_dut__DOT__u_replay_capsule_top__DOT__u_capsule_buffer__DOT__mem;
        VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
        VlUnpacked<QData/*63:0*/, 2> __VicoTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
        VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;
    };

    // INTERNAL VARIABLES
    Vreplaycapsule_verilator_top__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vreplaycapsule_verilator_top___024root(Vreplaycapsule_verilator_top__Syms* symsp, const char* namep);
    ~Vreplaycapsule_verilator_top___024root();
    VL_UNCOPYABLE(Vreplaycapsule_verilator_top___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
