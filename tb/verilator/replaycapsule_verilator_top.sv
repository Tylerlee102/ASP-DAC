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
  input  logic        replay_consume_use_source,
  input  logic        replay_source_store_clear,
  input  logic        replay_source_capture_enable,
  input  logic        replay_source_load_valid,
  input  logic [CAPSULE_ADDR_W-1:0] replay_source_load_addr,
  input  logic [63:0] replay_source_load_word,
  input  logic        replay_controller_enable,
  input  logic        replay_controller_arm_record,
  input  logic        replay_controller_start,
  input  logic        capsule_stream_ready,

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
  output logic        capsule_stream_valid,
  output logic [63:0] capsule_stream_word,
  output logic [31:0] capsule_stream_event_count,
  output logic [31:0] capsule_stream_sent_count,
  output logic [31:0] capsule_replay_critical_event_count,
  output logic [31:0] capsule_stream_stall_count,
  output logic [31:0] capsule_dropped_diagnostic_count,
  output logic [31:0] capsule_replay_critical_overflow_count,
  output logic [CAPSULE_ADDR_W:0] capsule_stream_fifo_level,
  output logic        replay_consume_ready,
  output logic        replay_consume_observed_valid,
  output logic        replay_consume_all_events,
  output logic        replay_consume_error,
  output logic [7:0]  replay_consume_error_code,
  output logic [31:0] replay_consume_consumed_count,
  output logic        replay_source_active,
  output logic        replay_source_stream_done,
  output logic        replay_source_underflow,
  output logic        replay_source_capture_ready,
  output logic        replay_source_capture_overflow,
  output logic [31:0] replay_source_captured_count,
  output logic [31:0] replay_source_sent_count,
  output logic        replay_controller_busy,
  output logic        replay_controller_record_active,
  output logic        replay_controller_replay_active,
  output logic        replay_controller_done,
  output logic        replay_controller_error,
  output logic [7:0]  replay_controller_state,
  output logic [7:0]  replay_controller_error_code,
  output logic [31:0] commit_count
);
  logic [167:0] capsule_read_data;
  logic replay_source_valid;
  logic [63:0] replay_source_word;
  logic replay_consume_ready_internal;
  logic replay_consume_valid_selected;
  logic [63:0] replay_consume_word_selected;
  logic replay_consume_stream_done_selected;
  logic selected_replay_consume_start;
  logic [31:0] selected_replay_consume_expected_count;
  logic selected_replay_consume_use_source;
  logic selected_replay_source_store_clear;
  logic selected_replay_source_capture_enable;
  logic controller_replay_consume_start;
  logic [31:0] controller_replay_consume_expected_count;
  logic controller_replay_consume_use_source;
  logic controller_replay_source_store_clear;
  logic controller_replay_source_capture_enable;

  rcv2_replay_mode_controller u_replay_mode_controller (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .enable(replay_controller_enable),
    .arm_record(replay_controller_arm_record),
    .start_replay(replay_controller_start),
    .captured_count(replay_source_captured_count),
    .capture_overflow(replay_source_capture_overflow),
    .source_underflow(replay_source_underflow),
    .consume_all_events(replay_consume_all_events),
    .consume_error(replay_consume_error),
    .source_store_clear(controller_replay_source_store_clear),
    .source_capture_enable(controller_replay_source_capture_enable),
    .consume_use_source(controller_replay_consume_use_source),
    .consume_start(controller_replay_consume_start),
    .consume_expected_count(controller_replay_consume_expected_count),
    .busy(replay_controller_busy),
    .record_active(replay_controller_record_active),
    .replay_active(replay_controller_replay_active),
    .done(replay_controller_done),
    .error(replay_controller_error),
    .state(replay_controller_state),
    .error_code(replay_controller_error_code)
  );

  assign selected_replay_consume_start =
    replay_controller_enable ? controller_replay_consume_start : replay_consume_start;
  assign selected_replay_consume_expected_count =
    replay_controller_enable ? controller_replay_consume_expected_count : replay_consume_expected_count;
  assign selected_replay_consume_use_source =
    replay_controller_enable ? controller_replay_consume_use_source : replay_consume_use_source;
  assign selected_replay_source_store_clear =
    replay_controller_enable ? controller_replay_source_store_clear : replay_source_store_clear;
  assign selected_replay_source_capture_enable =
    replay_controller_enable ? controller_replay_source_capture_enable : replay_source_capture_enable;

  rcv2_capsule_source #(
    .WORDS(CAPSULE_DEPTH),
    .ADDR_W(CAPSULE_ADDR_W)
  ) u_replay_source (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .store_clear(selected_replay_source_store_clear),
    .capture_enable(selected_replay_source_capture_enable),
    .capture_valid(capsule_stream_valid && capsule_stream_ready),
    .capture_word(capsule_stream_word),
    .load_valid(replay_source_load_valid),
    .load_addr(replay_source_load_addr),
    .load_word(replay_source_load_word),
    .start(selected_replay_consume_start && selected_replay_consume_use_source),
    .expected_count(selected_replay_consume_expected_count),
    .capsule_ready(selected_replay_consume_use_source && replay_consume_ready_internal),
    .capture_ready(replay_source_capture_ready),
    .capture_overflow(replay_source_capture_overflow),
    .captured_count(replay_source_captured_count),
    .capsule_valid(replay_source_valid),
    .capsule_word(replay_source_word),
    .stream_done(replay_source_stream_done),
    .active(replay_source_active),
    .underflow(replay_source_underflow),
    .sent_count(replay_source_sent_count)
  );

  assign replay_consume_valid_selected =
    selected_replay_consume_use_source ? replay_source_valid : replay_consume_valid;
  assign replay_consume_word_selected =
    selected_replay_consume_use_source ? replay_source_word : replay_consume_word;
  assign replay_consume_stream_done_selected =
    selected_replay_consume_use_source ? replay_source_stream_done : replay_consume_stream_done;
  assign replay_consume_ready = replay_consume_ready_internal;

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
    .replay_consume_start(selected_replay_consume_start),
    .replay_consume_expected_count(selected_replay_consume_expected_count),
    .replay_consume_valid(replay_consume_valid_selected),
    .replay_consume_word(replay_consume_word_selected),
    .replay_consume_stream_done(replay_consume_stream_done_selected),
    .capsule_stream_ready(capsule_stream_ready),
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
    .capsule_stream_valid(capsule_stream_valid),
    .capsule_stream_word(capsule_stream_word),
    .capsule_stream_event_count(capsule_stream_event_count),
    .capsule_stream_sent_count(capsule_stream_sent_count),
    .capsule_replay_critical_event_count(capsule_replay_critical_event_count),
    .capsule_stream_stall_count(capsule_stream_stall_count),
    .capsule_dropped_diagnostic_count(capsule_dropped_diagnostic_count),
    .capsule_replay_critical_overflow_count(capsule_replay_critical_overflow_count),
    .capsule_stream_fifo_level(capsule_stream_fifo_level),
    .replay_consume_ready(replay_consume_ready_internal),
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
