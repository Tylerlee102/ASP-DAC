`include "event_pkg.sv"

module replay_capsule_top #(
  parameter int CAPSULE_DEPTH = 256,
  parameter int ADDR_W = $clog2(CAPSULE_DEPTH),
  parameter bit ENABLE_WATCHDOG = 1'b0
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic [3:0]  capture_mode,

  input  logic        commit_valid,
  input  logic [31:0] commit_pc,
  input  logic [31:0] commit_instr,
  input  logic [31:0] commit_index,
  input  logic        branch_taken,
  input  logic        jump_taken,

  input  logic        mem_valid,
  input  logic        mem_write,
  input  logic [31:0] mem_addr,
  input  logic [31:0] mem_wdata,
  input  logic [31:0] mem_rdata,

  input  logic        external_input_valid,
  input  logic [31:0] external_input_value,
  input  logic        interrupt_enter,
  input  logic        interrupt_exit,
  input  logic        checkpoint_hash_req,

  input  logic [ADDR_W-1:0] capsule_read_addr,
  output logic [167:0] capsule_read_data,

  output logic        capsule_frozen,
  output logic        capsule_overflow,
  output logic [ADDR_W:0] capsule_event_count,
  output logic [31:0] running_signature,
  output logic        property_fail_valid,
  output logic [7:0]  property_id,
  output logic [31:0] property_signature,
  output logic        captured_event_valid,
  output logic [3:0]  captured_event_type
);
  `include "event_defs.svh"

  localparam int EVENT_WIDTH = RC_EVENT_WIDTH;

  logic raw_event_valid;
  logic [3:0] raw_event_type;
  logic [31:0] raw_event_commit_index;
  logic [31:0] raw_event_pc;
  logic [31:0] raw_event_addr;
  logic [31:0] raw_event_data;
  logic raw_multievent_pending;

  logic sensor_deadline_active;
  logic critical_section_active;
  logic property_window_active;
  logic slicer_keep_context_event;

  logic [31:0] last_commit_index;
  logic [31:0] last_pc;

  logic [3:0] final_event_type;
  logic [31:0] final_commit_index;
  logic [31:0] final_pc;
  logic [31:0] final_addr;
  logic [31:0] final_data;
  logic final_event_valid;

  logic classifier_keep_event;
  logic event_is_nondeterministic;
  logic event_is_property_relevant;
  logic kept_event_valid;
  logic [31:0] event_id;
  logic [EVENT_WIDTH-1:0] event_packet;

  event_tap u_event_tap (
    .clk(clk),
    .rst_n(rst_n),
    .commit_valid(commit_valid),
    .commit_pc(commit_pc),
    .commit_instr(commit_instr),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(mem_valid),
    .mem_write(mem_write),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .event_valid(raw_event_valid),
    .event_type(raw_event_type),
    .event_commit_index(raw_event_commit_index),
    .event_pc(raw_event_pc),
    .event_addr(raw_event_addr),
    .event_data(raw_event_data),
    .multievent_pending(raw_multievent_pending)
  );

  property_checker #(
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_property_checker (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(raw_event_valid),
    .event_type(raw_event_type),
    .event_commit_index(raw_event_commit_index),
    .event_pc(raw_event_pc),
    .event_addr(raw_event_addr),
    .event_data(raw_event_data),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .sensor_deadline_active(sensor_deadline_active),
    .critical_section_active(critical_section_active)
  );

  event_slicer u_event_slicer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(raw_event_valid),
    .event_type(raw_event_type),
    .property_fail_valid(property_fail_valid),
    .capture_mode(capture_mode),
    .property_window_active(property_window_active),
    .keep_context_event(slicer_keep_context_event)
  );

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      last_commit_index <= 32'h0;
      last_pc <= 32'h0;
    end else if (clear) begin
      last_commit_index <= 32'h0;
      last_pc <= 32'h0;
    end else if (raw_event_valid) begin
      last_commit_index <= raw_event_commit_index;
      last_pc <= raw_event_pc;
    end
  end

  always_comb begin
    final_event_valid = raw_event_valid;
    final_event_type = raw_event_type;
    final_commit_index = raw_event_commit_index;
    final_pc = raw_event_pc;
    final_addr = raw_event_addr;
    final_data = raw_event_data;

    if (property_fail_valid) begin
      final_event_valid = 1'b1;
      final_event_type = EV_PROPERTY_FAIL;
      final_commit_index = last_commit_index;
      final_pc = last_pc;
      final_addr = {24'h0, property_id};
      final_data = property_signature;
    end else if (checkpoint_hash_req) begin
      final_event_valid = 1'b1;
      final_event_type = EV_CHECKPOINT_HASH;
      final_commit_index = commit_index;
      final_pc = commit_pc;
      final_addr = 32'h0;
      final_data = running_signature;
    end
  end

  event_classifier u_event_classifier (
    .event_valid(final_event_valid),
    .event_type(final_event_type),
    .capture_mode(capture_mode),
    .property_window_active(property_window_active),
    .overflow_guard(capsule_overflow),
    .keep_event(classifier_keep_event),
    .event_is_nondeterministic(event_is_nondeterministic),
    .event_is_property_relevant(event_is_property_relevant)
  );

  assign kept_event_valid = classifier_keep_event;
  assign captured_event_valid = kept_event_valid;
  assign captured_event_type = final_event_type;

  assign event_packet = rc_pack_event(
    final_event_type,
    {raw_multievent_pending, event_is_nondeterministic, event_is_property_relevant, capsule_overflow},
    event_id,
    final_commit_index,
    final_pc,
    final_addr,
    final_data
  );

  capsule_buffer #(
    .EVENT_WIDTH(EVENT_WIDTH),
    .DEPTH(CAPSULE_DEPTH),
    .ADDR_W(ADDR_W)
  ) u_capsule_buffer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(kept_event_valid),
    .event_packet(event_packet),
    .fail_freeze(property_fail_valid),
    .read_addr(capsule_read_addr),
    .read_data(capsule_read_data),
    .frozen(capsule_frozen),
    .overflow(capsule_overflow),
    .write_count(capsule_event_count)
  );

  hash_signature #(
    .EVENT_WIDTH(EVENT_WIDTH)
  ) u_hash_signature (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(kept_event_valid),
    .event_packet(event_packet),
    .signature(running_signature)
  );

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      event_id <= 32'h0;
    end else if (clear) begin
      event_id <= 32'h0;
    end else if (kept_event_valid && !capsule_frozen) begin
      event_id <= event_id + 32'h1;
    end
  end

  logic unused_slicer_keep;
  logic unused_sensor_deadline_active;
  logic unused_critical_section_active;
  assign unused_slicer_keep = slicer_keep_context_event;
  assign unused_sensor_deadline_active = sensor_deadline_active;
  assign unused_critical_section_active = critical_section_active;
endmodule
