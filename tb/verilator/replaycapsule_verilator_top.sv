`include "../../rtl/event_pkg.sv"

module replaycapsule_verilator_top #(
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
  parameter logic [31:0] PROGADDR_IRQ   = 32'h0000_0010,
  parameter logic [31:0] STACKADDR      = 32'h0000_2000,
  parameter int          CAPSULE_DEPTH  = 256,
  parameter int          CAPSULE_ADDR_W = $clog2(CAPSULE_DEPTH),
  parameter bit          ENABLE_WATCHDOG = 1'b0
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        watchdog_enable,
  input  logic [3:0]  capture_mode,
  input  logic [1:0]  arch_select,
  input  logic [1:0]  recorder_config_select,
  input  logic        replay_consume_start,
  input  logic [31:0] replay_consume_expected_count,
  input  logic        replay_consume_valid,
  input  logic [63:0] replay_consume_word,
  input  logic        replay_consume_stream_done,

  output logic        trap,
  output logic        mem_valid,
  output logic        mem_instr,
  input  logic        mem_ready,
  output logic [31:0] mem_addr,
  output logic [31:0] mem_wdata,
  output logic [3:0]  mem_wstrb,
  input  logic [31:0] mem_rdata,

  input  logic [31:0] irq,
  output logic [31:0] eoi,

  input  logic        external_input_valid,
  input  logic [31:0] external_input_value,

  input  logic [CAPSULE_ADDR_W-1:0] capsule_read_addr,
  output logic [31:0] capsule_word0,
  output logic [31:0] capsule_word1,
  output logic [31:0] capsule_word2,
  output logic [31:0] capsule_word3,
  output logic [31:0] capsule_word4,
  output logic [7:0]  capsule_word5,
  output logic        capsule_frozen,
  output logic        capsule_overflow,
  output logic [CAPSULE_ADDR_W:0] capsule_event_count,
  output logic [31:0] running_signature,
  output logic        property_fail_valid,
  output logic [7:0]  property_id,
  output logic [31:0] property_signature,
  output logic        replay_consume_ready,
  output logic        replay_consume_observed_valid,
  output logic        replay_consume_all_events,
  output logic        replay_consume_error,
  output logic [7:0]  replay_consume_error_code,
  output logic [31:0] replay_consume_consumed_count,
  output logic [31:0] commit_count
);
  logic [167:0] capsule_read_data;

  picorv32_replaycapsule_wrapper #(
    .PROGADDR_RESET(PROGADDR_RESET),
    .PROGADDR_IRQ(PROGADDR_IRQ),
    .STACKADDR(STACKADDR),
    .CAPSULE_DEPTH(CAPSULE_DEPTH),
    .CAPSULE_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .capture_mode(capture_mode),
    .arch_select(arch_select),
    .recorder_config_select(recorder_config_select),
    .replay_consume_start(replay_consume_start),
    .replay_consume_expected_count(replay_consume_expected_count),
    .replay_consume_valid(replay_consume_valid),
    .replay_consume_word(replay_consume_word),
    .replay_consume_stream_done(replay_consume_stream_done),
    .trap(trap),
    .mem_valid(mem_valid),
    .mem_instr(mem_instr),
    .mem_ready(mem_ready),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wstrb(mem_wstrb),
    .mem_rdata(mem_rdata),
    .irq(irq),
    .eoi(eoi),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(capsule_read_data),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .capsule_event_count(capsule_event_count),
    .running_signature(running_signature),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .replay_consume_ready(replay_consume_ready),
    .replay_consume_observed_valid(replay_consume_observed_valid),
    .replay_consume_all_events(replay_consume_all_events),
    .replay_consume_error(replay_consume_error),
    .replay_consume_error_code(replay_consume_error_code),
    .replay_consume_consumed_count(replay_consume_consumed_count)
  );

  assign capsule_word0 = capsule_read_data[31:0];
  assign capsule_word1 = capsule_read_data[63:32];
  assign capsule_word2 = capsule_read_data[95:64];
  assign capsule_word3 = capsule_read_data[127:96];
  assign capsule_word4 = capsule_read_data[159:128];
  assign capsule_word5 = capsule_read_data[167:160];
  assign commit_count = u_dut.commit_index;
endmodule
