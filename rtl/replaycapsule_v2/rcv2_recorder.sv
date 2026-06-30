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
  parameter bit ENABLE_STREAMING = 1'b1,
  parameter bit ENABLE_WATCHDOG = 1'b0,
  parameter bit ENABLE_PROPERTY_CHECKER = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit ENABLE_CONTEXT_SLICER = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit ENABLE_EVENT_BUFFER = 1'b1,
  parameter bit ENABLE_SIGNATURE = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit ENABLE_STATUS_COUNTERS = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit ENABLE_MINIMAL_EVENT_TAP = (REPLAYCAPSULE_CONFIG == 0)
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
  output logic [31:0] captured_event_commit_index,
  output logic [31:0] captured_event_addr,
  output logic [31:0] captured_event_data,
  output logic [31:0] captured_event_payload_hash,
  input  logic        capsule_stream_ready,
  output logic        capsule_stream_valid,
  output logic [63:0] capsule_stream_word,
  output logic [31:0] stream_event_count,
  output logic [31:0] stream_event_sent_count,
  output logic [31:0] replay_critical_event_count,
  output logic [31:0] stream_stall_count,
  output logic [31:0] dropped_diagnostic_count,
  output logic [31:0] replay_critical_overflow_count,
  output logic [MEMORY_ADDR_W:0] stream_fifo_level
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
  logic store_write_ready;
  logic packer_event_valid;
  logic capture_request;
  logic diagnostic_fifo_drop;
  logic critical_overflow_event;
  logic [31:0] adaptive_dropped_diagnostic_count;
  logic [31:0] fifo_dropped_diagnostic_count;
  logic stream_output_fire;
  logic legacy_capsule_overflow;
  logic streaming_fifo_overflow;
  logic [MEMORY_ADDR_W:0] saturated_stream_event_count;

  generate
    if (ENABLE_MINIMAL_EVENT_TAP) begin : g_minimal_event_tap
      logic is_mmio;
      logic [2:0] candidate_count;

      assign is_mmio = (mem_addr & 32'hffff_0000) == 32'h4000_0000;

      always_comb begin
        candidate_count = 3'd0;
        candidate_count = candidate_count + ((interrupt_enter) ? 3'd1 : 3'd0);
        candidate_count = candidate_count + ((interrupt_exit) ? 3'd1 : 3'd0);
        candidate_count = candidate_count + ((external_input_valid) ? 3'd1 : 3'd0);
        candidate_count = candidate_count + ((mem_valid && is_mmio) ? 3'd1 : 3'd0);
      end

      assign raw_multievent_pending = candidate_count > 3'd1;

      always_comb begin
        raw_event_valid = 1'b0;
        raw_event_type = EV_COMMIT;
        raw_event_commit_index = commit_index;
        raw_event_pc = commit_pc;
        raw_event_addr = 32'h0;
        raw_event_data = 32'h0;

        if (interrupt_enter) begin
          raw_event_valid = 1'b1;
          raw_event_type = EV_INTERRUPT_ENTER;
          raw_event_data = 32'h1;
        end else if (interrupt_exit) begin
          raw_event_valid = 1'b1;
          raw_event_type = EV_INTERRUPT_EXIT;
          raw_event_data = 32'h0;
        end else if (external_input_valid) begin
          raw_event_valid = 1'b1;
          raw_event_type = EV_EXTERNAL_INPUT;
          raw_event_data = external_input_value;
        end else if (mem_valid && is_mmio && !mem_write) begin
          raw_event_valid = 1'b1;
          raw_event_type = EV_MMIO_READ;
          raw_event_addr = mem_addr;
          raw_event_data = mem_rdata;
        end else if (mem_valid && is_mmio && mem_write) begin
          raw_event_valid = 1'b1;
          raw_event_type = EV_MMIO_WRITE;
          raw_event_addr = mem_addr;
          raw_event_data = mem_wdata;
        end
      end

      logic unused_minimal_commit_valid;
      logic unused_minimal_commit_instr;
      logic unused_minimal_branch_taken;
      logic unused_minimal_jump_taken;
      assign unused_minimal_commit_valid = commit_valid;
      assign unused_minimal_commit_instr = |commit_instr;
      assign unused_minimal_branch_taken = branch_taken;
      assign unused_minimal_jump_taken = jump_taken;
    end else begin : g_full_event_tap
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
    end
  endgenerate

  generate
    if (ENABLE_PROPERTY_CHECKER) begin : g_property_checker
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
    end else begin : g_no_property_checker
      assign property_fail_valid = 1'b0;
      assign property_id = 8'h0;
      assign property_signature = 32'h0;
      assign sensor_deadline_active = 1'b0;
      assign critical_section_active = 1'b0;
    end
  endgenerate

  generate
    if (ENABLE_CONTEXT_SLICER) begin : g_context_slicer
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
    end else begin : g_no_context_slicer
      assign property_window_active = 1'b0;
      assign slicer_keep_context_event = 1'b0;
    end
  endgenerate

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

  generate
    if (ENABLE_MINIMAL_EVENT_TAP) begin : g_minimal_classifier
      assign event_is_nondeterministic =
        final_event_type == EV_MMIO_READ ||
        final_event_type == EV_INTERRUPT_ENTER ||
        final_event_type == EV_INTERRUPT_EXIT ||
        final_event_type == EV_EXTERNAL_INPUT;
      assign event_is_property_relevant =
        event_is_nondeterministic ||
        final_event_type == EV_MMIO_WRITE ||
        final_event_type == EV_PROPERTY_FAIL ||
        final_event_type == EV_CHECKPOINT_HASH;
      assign classifier_keep_event =
        final_event_valid && (
          event_is_nondeterministic ||
          final_event_type == EV_MMIO_WRITE ||
          final_event_type == EV_PROPERTY_FAIL ||
          final_event_type == EV_CHECKPOINT_HASH
        );
    end else begin : g_event_classifier
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
    end
  endgenerate

  assign event_is_replay_critical =
    event_is_nondeterministic ||
    final_event_type == EV_MMIO_READ ||
    final_event_type == EV_MMIO_WRITE ||
    final_event_type == EV_INTERRUPT_ENTER ||
    final_event_type == EV_INTERRUPT_EXIT ||
    final_event_type == EV_PROPERTY_FAIL ||
    final_event_type == EV_CHECKPOINT_HASH;

  assign dict_lookup_valid = final_event_valid && (final_event_type == EV_MMIO_READ || final_event_type == EV_MMIO_WRITE);

  generate
    if (ENABLE_ADDRESS_DICTIONARY) begin : g_address_dictionary
      rcv2_address_dictionary #(
        .ENTRIES(8),
        .INDEX_W(3)
      ) u_address_dictionary (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .lookup_valid(dict_lookup_valid),
        .allocate(classifier_keep_event),
        .lookup_addr(final_addr),
        .dict_hit(dict_hit),
        .dict_index(dict_index)
      );
    end else begin : g_no_address_dictionary
      assign dict_hit = 1'b0;
      assign dict_index = 3'h0;
    end
  endgenerate

  generate
    if (EFF_HASH) begin : g_payload_hasher
      rcv2_payload_hasher u_payload_hasher (
        .enable(1'b1),
        .event_valid(final_event_valid),
        .event_type(final_event_type),
        .commit_index(final_commit_index),
        .addr(final_addr),
        .data(final_data),
        .hash_valid(hash_valid),
        .payload_hash(payload_hash)
      );
    end else begin : g_no_payload_hasher
      assign hash_valid = 1'b1;
      assign payload_hash = final_data;
    end
  endgenerate

  generate
    if (ENABLE_ADAPTIVE_WINDOW) begin : g_adaptive_window
      rcv2_adaptive_window #(
        .COUNT_W(MEMORY_ADDR_W + 1),
        .HIGH_WATERMARK_MARGIN(16)
      ) u_adaptive_window (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .event_valid(classifier_keep_event),
        .event_is_replay_critical(event_is_replay_critical),
        .diagnostics_requested(EFF_DIAG),
        .used_words(stream_fifo_level),
        .capacity_words((MEMORY_ADDR_W + 1)'(MEMORY_WORDS)),
        .capture_event(adaptive_capture_event),
        .diagnostics_enabled_eff(diagnostics_enabled_eff),
        .adaptive_drop(adaptive_drop),
        .dropped_diagnostic_count(adaptive_dropped_diagnostic_count)
      );
    end else begin : g_no_adaptive_window
      assign adaptive_capture_event = 1'b1;
      assign diagnostics_enabled_eff = EFF_DIAG;
      assign adaptive_drop = 1'b0;
      assign adaptive_dropped_diagnostic_count = 32'h0;
    end
  endgenerate

  assign capture_request = classifier_keep_event && adaptive_capture_event;
  assign diagnostic_fifo_drop = ENABLE_STREAMING && capture_request && !event_is_replay_critical && !store_write_ready;
  assign critical_overflow_event = ENABLE_STREAMING && capture_request && event_is_replay_critical && !store_write_ready;
  assign packer_event_valid = capture_request && (!ENABLE_STREAMING || store_write_ready);

  rcv2_event_packer #(
    .ENABLE_DIAGNOSTICS(EFF_DIAG),
    .ENABLE_PAYLOAD_HASH(EFF_HASH),
    .ENABLE_ADDRESS_DICTIONARY(ENABLE_ADDRESS_DICTIONARY)
  ) u_event_packer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(packer_event_valid),
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
  assign captured_event_commit_index = final_commit_index;
  assign captured_event_addr = final_addr;
  assign captured_event_data = final_data;
  assign captured_event_payload_hash = payload_hash;

  generate
    if (!ENABLE_EVENT_BUFFER) begin : g_direct_stream
      assign store_write_ready = 1'b1;
      assign capsule_read_data = packed_word;
      assign capsule_stream_valid = fifo_write_valid;
      assign capsule_stream_word = packed_word;
      assign capsule_frozen = 1'b0;
      assign legacy_capsule_overflow = 1'b0;
      assign streaming_fifo_overflow = 1'b0;
      assign stream_fifo_level = '0;
      assign capsule_event_count = saturated_stream_event_count;
    end else if (ENABLE_STREAMING) begin : g_streaming_fifo
      rcv2_event_stream_fifo #(
        .WORD_WIDTH(64),
        .DEPTH(MEMORY_WORDS),
        .ADDR_W(MEMORY_ADDR_W)
      ) u_event_stream_fifo (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .push_valid(fifo_write_valid),
        .push_ready(store_write_ready),
        .push_data(packed_word),
        .freeze(property_fail_valid),
        .read_addr(capsule_read_addr),
        .read_data(capsule_read_data),
        .stream_valid(capsule_stream_valid),
        .stream_ready(capsule_stream_ready),
        .stream_data(capsule_stream_word),
        .frozen(capsule_frozen),
        .overflow(streaming_fifo_overflow),
        .used_words(stream_fifo_level)
      );

      assign legacy_capsule_overflow = 1'b0;
      assign capsule_event_count = saturated_stream_event_count;
    end else begin : g_legacy_fifo
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
        .overflow(legacy_capsule_overflow),
        .used_words(capsule_event_count)
      );

      assign store_write_ready = 1'b1;
      assign capsule_stream_valid = 1'b0;
      assign capsule_stream_word = 64'h0;
      assign streaming_fifo_overflow = 1'b0;
      assign stream_fifo_level = capsule_event_count;
    end
  endgenerate

  assign stream_output_fire = capsule_stream_valid && capsule_stream_ready;
  assign capsule_overflow = legacy_capsule_overflow || (replay_critical_overflow_count != 32'h0);
  assign dropped_diagnostic_count = adaptive_dropped_diagnostic_count + fifo_dropped_diagnostic_count;
  assign saturated_stream_event_count =
    (stream_event_count > {{(31 - MEMORY_ADDR_W){1'b0}}, {MEMORY_ADDR_W + 1{1'b1}}}) ?
      {MEMORY_ADDR_W + 1{1'b1}} :
      stream_event_count[MEMORY_ADDR_W:0];

  generate
    if (ENABLE_STATUS_COUNTERS) begin : g_status_counters
      always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
          stream_event_count <= 32'h0;
          stream_event_sent_count <= 32'h0;
          replay_critical_event_count <= 32'h0;
          stream_stall_count <= 32'h0;
          fifo_dropped_diagnostic_count <= 32'h0;
          replay_critical_overflow_count <= 32'h0;
        end else if (clear) begin
          stream_event_count <= 32'h0;
          stream_event_sent_count <= 32'h0;
          replay_critical_event_count <= 32'h0;
          stream_stall_count <= 32'h0;
          fifo_dropped_diagnostic_count <= 32'h0;
          replay_critical_overflow_count <= 32'h0;
        end else begin
          if (fifo_write_valid) begin
            stream_event_count <= stream_event_count + 32'h1;
            if (event_is_replay_critical) begin
              replay_critical_event_count <= replay_critical_event_count + 32'h1;
            end
          end
          if (stream_output_fire) begin
            stream_event_sent_count <= stream_event_sent_count + 32'h1;
          end
          if (ENABLE_STREAMING && capsule_stream_valid && !capsule_stream_ready) begin
            stream_stall_count <= stream_stall_count + 32'h1;
          end
          if (diagnostic_fifo_drop) begin
            fifo_dropped_diagnostic_count <= fifo_dropped_diagnostic_count + 32'h1;
          end
          if (critical_overflow_event) begin
            replay_critical_overflow_count <= replay_critical_overflow_count + 32'h1;
          end
        end
      end
    end else begin : g_no_status_counters
      assign stream_event_count = 32'h0;
      assign stream_event_sent_count = 32'h0;
      assign replay_critical_event_count = 32'h0;
      assign stream_stall_count = 32'h0;
      assign fifo_dropped_diagnostic_count = 32'h0;
      assign replay_critical_overflow_count = 32'h0;
    end
  endgenerate

  generate
    if (ENABLE_SIGNATURE) begin : g_hash_signature
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
    end else begin : g_no_hash_signature
      assign running_signature = 32'h0;
    end
  endgenerate

  logic unused_enable_bram_fifo;
  logic unused_buffer_depth;
  logic unused_watchdog_enable;
  logic unused_streaming_fifo_overflow;
  logic unused_slicer_keep;
  logic unused_sensor_deadline_active;
  logic unused_critical_section_active;
  logic unused_adaptive_drop;
  logic unused_delta_saturated;
  assign unused_enable_bram_fifo = ENABLE_BRAM_FIFO;
  assign unused_buffer_depth = (BUFFER_DEPTH != 0);
  assign unused_watchdog_enable = watchdog_enable;
  assign unused_streaming_fifo_overflow = streaming_fifo_overflow;
  assign unused_slicer_keep = slicer_keep_context_event;
  assign unused_sensor_deadline_active = sensor_deadline_active;
  assign unused_critical_section_active = critical_section_active;
  assign unused_adaptive_drop = adaptive_drop;
  assign unused_delta_saturated = delta_saturated;
endmodule
