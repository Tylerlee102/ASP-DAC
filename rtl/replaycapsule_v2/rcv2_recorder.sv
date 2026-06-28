module rcv2_recorder #(
  parameter int REPLAYCAPSULE_CONFIG = 1,
  parameter int BUFFER_DEPTH = 256,
  parameter int MEMORY_WORDS = 512,
  parameter int MEMORY_ADDR_W = (MEMORY_WORDS <= 2) ? 1 : $clog2(MEMORY_WORDS),
  parameter bit ENABLE_DIAGNOSTICS = 1'b1,
  parameter bit ENABLE_PAYLOAD_HASH = 1'b1,
  parameter bit ENABLE_ADDRESS_DICTIONARY = 1'b1,
  parameter bit ENABLE_BRam_FIFO = 1'b1,
  parameter bit ENABLE_BRAM_FIFO = ENABLE_BRam_FIFO,
  parameter bit ENABLE_ADAPTIVE_WINDOW = 1'b1,
  parameter bit ENABLE_WATCHDOG = 1'b0
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        watchdog_enable,

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

  input  logic [MEMORY_ADDR_W-1:0] capsule_read_addr,
  output logic [63:0] capsule_read_data,

  output logic        capsule_frozen,
  output logic        capsule_overflow,
  output logic [MEMORY_ADDR_W:0] capsule_event_count,
  output logic [31:0] running_signature,
  output logic        property_fail_valid,
  output logic [7:0]  property_id,
  output logic [31:0] property_signature,
  output logic        captured_event_valid,
  output logic [3:0]  captured_event_type,
  output logic [31:0] dropped_diagnostic_count
);
  `include "../event_defs.svh"
  `include "rcv2_config.svh"

  localparam bit CFG_HASH = rcv2_config_has_hash(REPLAYCAPSULE_CONFIG);
  localparam bit CFG_DIAG = rcv2_config_has_diagnostics(REPLAYCAPSULE_CONFIG);
  localparam bit EFF_HASH = ENABLE_PAYLOAD_HASH && CFG_HASH;
  localparam bit EFF_DIAG = ENABLE_DIAGNOSTICS && CFG_DIAG;
  localparam logic [3:0] CAPTURE_MODE = rcv2_capture_mode_for_config(REPLAYCAPSULE_CONFIG);

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
  logic event_is_replay_critical;
  logic dict_lookup_valid;
  logic dict_hit;
  logic [2:0] dict_index;
  logic [31:0] payload_hash;
  logic hash_valid;
  logic adaptive_capture_event;
  logic diagnostics_enabled_eff;
  logic adaptive_drop;
  logic packed_valid;
  logic [63:0] packed_word;
  logic delta_saturated;
  logic fifo_write_valid;

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
    .watchdog_enable(watchdog_enable),
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
    .capture_mode(CAPTURE_MODE),
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
    .capture_mode(CAPTURE_MODE),
    .property_window_active(property_window_active),
    .overflow_guard(capsule_overflow),
    .keep_event(classifier_keep_event),
    .event_is_nondeterministic(event_is_nondeterministic),
    .event_is_property_relevant(event_is_property_relevant)
  );

  assign event_is_replay_critical =
    event_is_nondeterministic ||
    final_event_type == EV_MMIO_WRITE ||
    final_event_type == EV_PROPERTY_FAIL ||
    final_event_type == EV_CHECKPOINT_HASH;

  assign dict_lookup_valid = final_event_valid && (final_event_type == EV_MMIO_READ || final_event_type == EV_MMIO_WRITE);

  rcv2_address_dictionary #(
    .ENTRIES(8),
    .INDEX_W(3)
  ) u_address_dictionary (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .lookup_valid(dict_lookup_valid),
    .allocate(ENABLE_ADDRESS_DICTIONARY && classifier_keep_event),
    .lookup_addr(final_addr),
    .dict_hit(dict_hit),
    .dict_index(dict_index)
  );

  rcv2_payload_hasher u_payload_hasher (
    .enable(EFF_HASH),
    .event_valid(final_event_valid),
    .event_type(final_event_type),
    .commit_index(final_commit_index),
    .addr(final_addr),
    .data(final_data),
    .hash_valid(hash_valid),
    .payload_hash(payload_hash)
  );

  rcv2_adaptive_window #(
    .COUNT_W(MEMORY_ADDR_W + 1),
    .HIGH_WATERMARK_MARGIN(16)
  ) u_adaptive_window (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(classifier_keep_event),
    .event_is_replay_critical(event_is_replay_critical),
    .diagnostics_requested(EFF_DIAG || !ENABLE_ADAPTIVE_WINDOW),
    .used_words(capsule_event_count),
    .capacity_words((MEMORY_ADDR_W + 1)'(MEMORY_WORDS)),
    .capture_event(adaptive_capture_event),
    .diagnostics_enabled_eff(diagnostics_enabled_eff),
    .adaptive_drop(adaptive_drop),
    .dropped_diagnostic_count(dropped_diagnostic_count)
  );

  rcv2_event_packer #(
    .ENABLE_DIAGNOSTICS(EFF_DIAG),
    .ENABLE_PAYLOAD_HASH(EFF_HASH),
    .ENABLE_ADDRESS_DICTIONARY(ENABLE_ADDRESS_DICTIONARY)
  ) u_event_packer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(classifier_keep_event && adaptive_capture_event),
    .event_type(final_event_type),
    .event_flags({raw_multievent_pending, event_is_nondeterministic, event_is_property_relevant, capsule_overflow}),
    .commit_index(final_commit_index),
    .pc(final_pc),
    .addr(final_addr),
    .data(final_data),
    .property_id(property_id),
    .dict_hit(dict_hit),
    .dict_index(dict_index),
    .payload_hash(payload_hash),
    .diagnostics_enabled_eff(diagnostics_enabled_eff),
    .packed_valid(packed_valid),
    .packed_word(packed_word),
    .delta_saturated(delta_saturated)
  );

  assign fifo_write_valid = packed_valid && hash_valid;
  assign captured_event_valid = fifo_write_valid;
  assign captured_event_type = final_event_type;

  rcv2_event_fifo_bram #(
    .WORD_WIDTH(64),
    .MEMORY_WORDS(MEMORY_WORDS),
    .ADDR_W(MEMORY_ADDR_W)
  ) u_event_fifo (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .write_valid(fifo_write_valid),
    .write_data(packed_word),
    .freeze(property_fail_valid),
    .read_addr(capsule_read_addr),
    .read_data(capsule_read_data),
    .frozen(capsule_frozen),
    .overflow(capsule_overflow),
    .used_words(capsule_event_count)
  );

  hash_signature #(
    .EVENT_WIDTH(64)
  ) u_hash_signature (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(fifo_write_valid),
    .event_packet(packed_word),
    .signature(running_signature)
  );

  logic unused_enable_bram_fifo;
  logic unused_buffer_depth;
  logic unused_slicer_keep;
  logic unused_sensor_deadline_active;
  logic unused_critical_section_active;
  logic unused_adaptive_drop;
  logic unused_delta_saturated;
  assign unused_enable_bram_fifo = ENABLE_BRAM_FIFO;
  assign unused_buffer_depth = (BUFFER_DEPTH != 0);
  assign unused_slicer_keep = slicer_keep_context_event;
  assign unused_sensor_deadline_active = sensor_deadline_active;
  assign unused_critical_section_active = critical_section_active;
  assign unused_adaptive_drop = adaptive_drop;
  assign unused_delta_saturated = delta_saturated;
endmodule
