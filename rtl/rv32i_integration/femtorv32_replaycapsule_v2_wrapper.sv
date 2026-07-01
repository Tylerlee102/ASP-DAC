`include "../event_pkg.sv"

module femtorv32_replaycapsule_v2_wrapper #(
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
  parameter int          CAPSULE_DEPTH  = 256,
  parameter int          CAPSULE_ADDR_W = $clog2(CAPSULE_DEPTH),
  parameter bit          ENABLE_WATCHDOG = 1'b0
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        watchdog_enable,
  input  logic        core_run_enable,
  input  logic [1:0]  recorder_config_select,

  input  logic        replay_consume_start,
  input  logic [31:0] replay_consume_expected_count,
  input  logic        replay_consume_valid,
  input  logic [63:0] replay_consume_word,
  input  logic        replay_consume_stream_done,
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

  input  logic        external_input_valid,
  input  logic [31:0] external_input_value,

  input  logic [CAPSULE_ADDR_W-1:0] capsule_read_addr,
  output logic [63:0] capsule_read_data,
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
  output logic [31:0] replay_consume_consumed_count
);
  `include "../event_defs.svh"

  logic [31:0] core_mem_addr;
  logic [31:0] core_mem_wdata;
  logic [3:0]  core_mem_wmask;
  logic [31:0] core_mem_rdata_to_core;
  logic [31:0] recorder_mem_rdata;
  logic        core_mem_rstrb;
  logic        core_mem_rbusy;
  logic        core_mem_wbusy;
  logic        core_mem_write;
  logic        core_mem_read;
  logic        core_mem_mmio;
  logic        core_mem_rom_fetch;
  logic        mem_accepted;
  logic        commit_valid;
  logic [31:0] commit_index;
  logic        irq_line;
  logic        irq_line_q;
  logic        interrupt_enter;
  logic        interrupt_exit;
  logic        replay_drive_active;
  logic        replay_mmio_hold_valid;
  logic [31:0] replay_mmio_hold_value;

  logic [63:0] v2_core_capsule_read_data;
  logic        v2_core_capsule_frozen;
  logic        v2_core_capsule_overflow;
  logic [CAPSULE_ADDR_W:0] v2_core_capsule_event_count;
  logic [31:0] v2_core_running_signature;
  logic        v2_core_property_fail_valid;
  logic [7:0]  v2_core_property_id;
  logic [31:0] v2_core_property_signature;
  logic        v2_core_captured_event_valid;
  logic [3:0]  v2_core_captured_event_type;
  logic [31:0] v2_core_captured_event_commit_index;
  logic [31:0] v2_core_captured_event_addr;
  logic [31:0] v2_core_captured_event_data;
  logic [31:0] v2_core_captured_event_payload_hash;
  logic        v2_core_stream_ready;
  logic        v2_core_stream_valid;
  logic [63:0] v2_core_stream_word;
  logic [31:0] v2_core_stream_event_count;
  logic [31:0] v2_core_stream_sent_count;
  logic [31:0] v2_core_replay_critical_event_count;
  logic [31:0] v2_core_stream_stall_count;
  logic [31:0] v2_core_dropped_diagnostic_count;
  logic [31:0] v2_core_replay_critical_overflow_count;
  logic [CAPSULE_ADDR_W:0] v2_core_stream_fifo_level;

  logic [63:0] v2_hashed_capsule_read_data;
  logic        v2_hashed_capsule_frozen;
  logic        v2_hashed_capsule_overflow;
  logic [CAPSULE_ADDR_W:0] v2_hashed_capsule_event_count;
  logic [31:0] v2_hashed_running_signature;
  logic        v2_hashed_property_fail_valid;
  logic [7:0]  v2_hashed_property_id;
  logic [31:0] v2_hashed_property_signature;
  logic        v2_hashed_captured_event_valid;
  logic [3:0]  v2_hashed_captured_event_type;
  logic [31:0] v2_hashed_captured_event_commit_index;
  logic [31:0] v2_hashed_captured_event_addr;
  logic [31:0] v2_hashed_captured_event_data;
  logic [31:0] v2_hashed_captured_event_payload_hash;
  logic        v2_hashed_stream_ready;
  logic        v2_hashed_stream_valid;
  logic [63:0] v2_hashed_stream_word;
  logic [31:0] v2_hashed_stream_event_count;
  logic [31:0] v2_hashed_stream_sent_count;
  logic [31:0] v2_hashed_replay_critical_event_count;
  logic [31:0] v2_hashed_stream_stall_count;
  logic [31:0] v2_hashed_dropped_diagnostic_count;
  logic [31:0] v2_hashed_replay_critical_overflow_count;
  logic [CAPSULE_ADDR_W:0] v2_hashed_stream_fifo_level;

  logic [63:0] v2_full_capsule_read_data;
  logic        v2_full_capsule_frozen;
  logic        v2_full_capsule_overflow;
  logic [CAPSULE_ADDR_W:0] v2_full_capsule_event_count;
  logic [31:0] v2_full_running_signature;
  logic        v2_full_property_fail_valid;
  logic [7:0]  v2_full_property_id;
  logic [31:0] v2_full_property_signature;
  logic        v2_full_captured_event_valid;
  logic [3:0]  v2_full_captured_event_type;
  logic [31:0] v2_full_captured_event_commit_index;
  logic [31:0] v2_full_captured_event_addr;
  logic [31:0] v2_full_captured_event_data;
  logic [31:0] v2_full_captured_event_payload_hash;
  logic        v2_full_stream_ready;
  logic        v2_full_stream_valid;
  logic [63:0] v2_full_stream_word;
  logic [31:0] v2_full_stream_event_count;
  logic [31:0] v2_full_stream_sent_count;
  logic [31:0] v2_full_replay_critical_event_count;
  logic [31:0] v2_full_stream_stall_count;
  logic [31:0] v2_full_dropped_diagnostic_count;
  logic [31:0] v2_full_replay_critical_overflow_count;
  logic [CAPSULE_ADDR_W:0] v2_full_stream_fifo_level;

  logic        selected_captured_event_valid;
  logic [3:0]  selected_captured_event_type;
  logic [31:0] selected_captured_event_commit_index;
  logic [31:0] selected_captured_event_addr;
  logic [31:0] selected_captured_event_data;
  logic [31:0] selected_captured_event_payload_hash;
  logic        replay_consume_mmio_valid;
  logic [31:0] replay_consume_mmio_addr_token;
  logic [31:0] replay_consume_mmio_value;
  logic        replay_consume_irq_valid;
  logic [7:0]  replay_consume_irq_cause;

  assign core_mem_read = core_mem_rstrb;
  assign core_mem_write = core_mem_wmask != 4'h0;
  assign core_mem_mmio = core_mem_addr[31:16] == 16'h4000;
  assign core_mem_rom_fetch = core_mem_read && !core_mem_mmio && core_mem_addr < 32'h0000_2000;
  assign mem_valid = core_mem_read || core_mem_write;
  assign mem_instr = core_mem_rom_fetch;
  assign mem_addr = core_mem_addr;
  assign mem_wdata = core_mem_wdata;
  assign mem_wstrb = core_mem_wmask;
  assign recorder_mem_rdata =
    (replay_drive_active && core_mem_read && core_mem_mmio && replay_consume_mmio_valid) ?
      replay_consume_mmio_value :
      mem_rdata;
  assign core_mem_rdata_to_core =
    (replay_drive_active && core_mem_read && core_mem_mmio && replay_consume_mmio_valid) ?
      replay_consume_mmio_value :
      (replay_drive_active && replay_mmio_hold_valid) ?
        replay_mmio_hold_value :
        mem_rdata;
  assign mem_accepted = mem_valid && mem_ready && !core_mem_rom_fetch;
  assign commit_valid = mem_valid && mem_ready && core_mem_rom_fetch;
  assign core_mem_rbusy = core_mem_read && !mem_ready;
  assign core_mem_wbusy = core_mem_write && !mem_ready;
  assign trap = 1'b0;
  assign irq_line = |irq;
  assign interrupt_enter = irq_line && !irq_line_q;
  assign interrupt_exit = !irq_line && irq_line_q;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      commit_index <= 32'h0;
      irq_line_q <= 1'b0;
      replay_drive_active <= 1'b0;
      replay_mmio_hold_valid <= 1'b0;
      replay_mmio_hold_value <= 32'h0;
    end else if (clear) begin
      commit_index <= 32'h0;
      irq_line_q <= 1'b0;
      replay_drive_active <= 1'b0;
      replay_mmio_hold_valid <= 1'b0;
      replay_mmio_hold_value <= 32'h0;
    end else begin
      replay_mmio_hold_valid <= 1'b0;
      if (replay_drive_active && core_mem_read && core_mem_mmio && replay_consume_mmio_valid && mem_ready) begin
        replay_mmio_hold_valid <= 1'b1;
        replay_mmio_hold_value <= replay_consume_mmio_value;
      end
      if (commit_valid) begin
        commit_index <= commit_index + 32'h1;
      end
      irq_line_q <= irq_line;
      if (replay_consume_start) begin
        replay_drive_active <= 1'b1;
      end else if (replay_consume_all_events || replay_consume_error) begin
        replay_drive_active <= 1'b0;
      end
    end
  end

  FemtoRV32 #(
    .RESET_ADDR(PROGADDR_RESET),
    .ADDR_WIDTH(32)
  ) u_femtorv32 (
    .clk(clk),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_wmask(core_mem_wmask),
    .mem_rdata(core_mem_rdata_to_core),
    .mem_rstrb(core_mem_rstrb),
    .mem_rbusy(core_mem_rbusy),
    .mem_wbusy(core_mem_wbusy),
    .reset(rst_n && core_run_enable)
  );

  rcv2_recorder #(
    .REPLAYCAPSULE_CONFIG(1),
    .BUFFER_DEPTH(CAPSULE_DEPTH),
    .MEMORY_WORDS(CAPSULE_DEPTH),
    .MEMORY_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_DIAGNOSTICS(1'b1),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .ENABLE_ADDRESS_DICTIONARY(1'b1),
    .ENABLE_BRAM_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(1'b1),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_rcv2_core (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .commit_valid(commit_valid),
    .commit_pc(core_mem_addr),
    .commit_instr(recorder_mem_rdata),
    .commit_index(commit_index),
    .branch_taken(1'b0),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_write),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(recorder_mem_rdata),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(1'b0),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(v2_core_capsule_read_data),
    .capsule_frozen(v2_core_capsule_frozen),
    .capsule_overflow(v2_core_capsule_overflow),
    .capsule_event_count(v2_core_capsule_event_count),
    .running_signature(v2_core_running_signature),
    .property_fail_valid(v2_core_property_fail_valid),
    .property_id(v2_core_property_id),
    .property_signature(v2_core_property_signature),
    .captured_event_valid(v2_core_captured_event_valid),
    .captured_event_type(v2_core_captured_event_type),
    .captured_event_commit_index(v2_core_captured_event_commit_index),
    .captured_event_addr(v2_core_captured_event_addr),
    .captured_event_data(v2_core_captured_event_data),
    .captured_event_payload_hash(v2_core_captured_event_payload_hash),
    .capsule_stream_ready(v2_core_stream_ready),
    .capsule_stream_valid(v2_core_stream_valid),
    .capsule_stream_word(v2_core_stream_word),
    .stream_event_count(v2_core_stream_event_count),
    .stream_event_sent_count(v2_core_stream_sent_count),
    .replay_critical_event_count(v2_core_replay_critical_event_count),
    .stream_stall_count(v2_core_stream_stall_count),
    .dropped_diagnostic_count(v2_core_dropped_diagnostic_count),
    .replay_critical_overflow_count(v2_core_replay_critical_overflow_count),
    .stream_fifo_level(v2_core_stream_fifo_level)
  );

  rcv2_recorder #(
    .REPLAYCAPSULE_CONFIG(2),
    .BUFFER_DEPTH(CAPSULE_DEPTH),
    .MEMORY_WORDS(CAPSULE_DEPTH),
    .MEMORY_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_DIAGNOSTICS(1'b1),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .ENABLE_ADDRESS_DICTIONARY(1'b1),
    .ENABLE_BRAM_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(1'b1),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_rcv2_hashed (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .commit_valid(commit_valid),
    .commit_pc(core_mem_addr),
    .commit_instr(recorder_mem_rdata),
    .commit_index(commit_index),
    .branch_taken(1'b0),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_write),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(recorder_mem_rdata),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(1'b0),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(v2_hashed_capsule_read_data),
    .capsule_frozen(v2_hashed_capsule_frozen),
    .capsule_overflow(v2_hashed_capsule_overflow),
    .capsule_event_count(v2_hashed_capsule_event_count),
    .running_signature(v2_hashed_running_signature),
    .property_fail_valid(v2_hashed_property_fail_valid),
    .property_id(v2_hashed_property_id),
    .property_signature(v2_hashed_property_signature),
    .captured_event_valid(v2_hashed_captured_event_valid),
    .captured_event_type(v2_hashed_captured_event_type),
    .captured_event_commit_index(v2_hashed_captured_event_commit_index),
    .captured_event_addr(v2_hashed_captured_event_addr),
    .captured_event_data(v2_hashed_captured_event_data),
    .captured_event_payload_hash(v2_hashed_captured_event_payload_hash),
    .capsule_stream_ready(v2_hashed_stream_ready),
    .capsule_stream_valid(v2_hashed_stream_valid),
    .capsule_stream_word(v2_hashed_stream_word),
    .stream_event_count(v2_hashed_stream_event_count),
    .stream_event_sent_count(v2_hashed_stream_sent_count),
    .replay_critical_event_count(v2_hashed_replay_critical_event_count),
    .stream_stall_count(v2_hashed_stream_stall_count),
    .dropped_diagnostic_count(v2_hashed_dropped_diagnostic_count),
    .replay_critical_overflow_count(v2_hashed_replay_critical_overflow_count),
    .stream_fifo_level(v2_hashed_stream_fifo_level)
  );

  rcv2_recorder #(
    .REPLAYCAPSULE_CONFIG(4),
    .BUFFER_DEPTH(CAPSULE_DEPTH),
    .MEMORY_WORDS(CAPSULE_DEPTH),
    .MEMORY_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_DIAGNOSTICS(1'b1),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .ENABLE_ADDRESS_DICTIONARY(1'b1),
    .ENABLE_BRAM_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(1'b1),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_rcv2_full (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .commit_valid(commit_valid),
    .commit_pc(core_mem_addr),
    .commit_instr(recorder_mem_rdata),
    .commit_index(commit_index),
    .branch_taken(1'b0),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_write),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(recorder_mem_rdata),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(1'b0),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(v2_full_capsule_read_data),
    .capsule_frozen(v2_full_capsule_frozen),
    .capsule_overflow(v2_full_capsule_overflow),
    .capsule_event_count(v2_full_capsule_event_count),
    .running_signature(v2_full_running_signature),
    .property_fail_valid(v2_full_property_fail_valid),
    .property_id(v2_full_property_id),
    .property_signature(v2_full_property_signature),
    .captured_event_valid(v2_full_captured_event_valid),
    .captured_event_type(v2_full_captured_event_type),
    .captured_event_commit_index(v2_full_captured_event_commit_index),
    .captured_event_addr(v2_full_captured_event_addr),
    .captured_event_data(v2_full_captured_event_data),
    .captured_event_payload_hash(v2_full_captured_event_payload_hash),
    .capsule_stream_ready(v2_full_stream_ready),
    .capsule_stream_valid(v2_full_stream_valid),
    .capsule_stream_word(v2_full_stream_word),
    .stream_event_count(v2_full_stream_event_count),
    .stream_event_sent_count(v2_full_stream_sent_count),
    .replay_critical_event_count(v2_full_replay_critical_event_count),
    .stream_stall_count(v2_full_stream_stall_count),
    .dropped_diagnostic_count(v2_full_dropped_diagnostic_count),
    .replay_critical_overflow_count(v2_full_replay_critical_overflow_count),
    .stream_fifo_level(v2_full_stream_fifo_level)
  );

  assign v2_core_stream_ready = (recorder_config_select != 2'd0) || capsule_stream_ready;
  assign v2_hashed_stream_ready = (recorder_config_select != 2'd1) || capsule_stream_ready;
  assign v2_full_stream_ready = (recorder_config_select != 2'd2) || capsule_stream_ready;

  always_comb begin
    capsule_read_data = v2_core_capsule_read_data;
    capsule_frozen = v2_core_capsule_frozen;
    capsule_overflow = v2_core_capsule_overflow;
    capsule_event_count = v2_core_capsule_event_count;
    running_signature = v2_core_running_signature;
    property_fail_valid = v2_core_property_fail_valid;
    property_id = v2_core_property_id;
    property_signature = v2_core_property_signature;
    capsule_stream_valid = v2_core_stream_valid;
    capsule_stream_word = v2_core_stream_word;
    capsule_stream_event_count = v2_core_stream_event_count;
    capsule_stream_sent_count = v2_core_stream_sent_count;
    capsule_replay_critical_event_count = v2_core_replay_critical_event_count;
    capsule_stream_stall_count = v2_core_stream_stall_count;
    capsule_dropped_diagnostic_count = v2_core_dropped_diagnostic_count;
    capsule_replay_critical_overflow_count = v2_core_replay_critical_overflow_count;
    capsule_stream_fifo_level = v2_core_stream_fifo_level;
    selected_captured_event_valid = v2_core_captured_event_valid;
    selected_captured_event_type = v2_core_captured_event_type;
    selected_captured_event_commit_index = v2_core_captured_event_commit_index;
    selected_captured_event_addr = v2_core_captured_event_addr;
    selected_captured_event_data = v2_core_captured_event_data;
    selected_captured_event_payload_hash = v2_core_captured_event_payload_hash;

    case (recorder_config_select)
      2'd1: begin
        capsule_read_data = v2_hashed_capsule_read_data;
        capsule_frozen = v2_hashed_capsule_frozen;
        capsule_overflow = v2_hashed_capsule_overflow;
        capsule_event_count = v2_hashed_capsule_event_count;
        running_signature = v2_hashed_running_signature;
        property_fail_valid = v2_hashed_property_fail_valid;
        property_id = v2_hashed_property_id;
        property_signature = v2_hashed_property_signature;
        capsule_stream_valid = v2_hashed_stream_valid;
        capsule_stream_word = v2_hashed_stream_word;
        capsule_stream_event_count = v2_hashed_stream_event_count;
        capsule_stream_sent_count = v2_hashed_stream_sent_count;
        capsule_replay_critical_event_count = v2_hashed_replay_critical_event_count;
        capsule_stream_stall_count = v2_hashed_stream_stall_count;
        capsule_dropped_diagnostic_count = v2_hashed_dropped_diagnostic_count;
        capsule_replay_critical_overflow_count = v2_hashed_replay_critical_overflow_count;
        capsule_stream_fifo_level = v2_hashed_stream_fifo_level;
        selected_captured_event_valid = v2_hashed_captured_event_valid;
        selected_captured_event_type = v2_hashed_captured_event_type;
        selected_captured_event_commit_index = v2_hashed_captured_event_commit_index;
        selected_captured_event_addr = v2_hashed_captured_event_addr;
        selected_captured_event_data = v2_hashed_captured_event_data;
        selected_captured_event_payload_hash = v2_hashed_captured_event_payload_hash;
      end
      2'd2: begin
        capsule_read_data = v2_full_capsule_read_data;
        capsule_frozen = v2_full_capsule_frozen;
        capsule_overflow = v2_full_capsule_overflow;
        capsule_event_count = v2_full_capsule_event_count;
        running_signature = v2_full_running_signature;
        property_fail_valid = v2_full_property_fail_valid;
        property_id = v2_full_property_id;
        property_signature = v2_full_property_signature;
        capsule_stream_valid = v2_full_stream_valid;
        capsule_stream_word = v2_full_stream_word;
        capsule_stream_event_count = v2_full_stream_event_count;
        capsule_stream_sent_count = v2_full_stream_sent_count;
        capsule_replay_critical_event_count = v2_full_replay_critical_event_count;
        capsule_stream_stall_count = v2_full_stream_stall_count;
        capsule_dropped_diagnostic_count = v2_full_dropped_diagnostic_count;
        capsule_replay_critical_overflow_count = v2_full_replay_critical_overflow_count;
        capsule_stream_fifo_level = v2_full_stream_fifo_level;
        selected_captured_event_valid = v2_full_captured_event_valid;
        selected_captured_event_type = v2_full_captured_event_type;
        selected_captured_event_commit_index = v2_full_captured_event_commit_index;
        selected_captured_event_addr = v2_full_captured_event_addr;
        selected_captured_event_data = v2_full_captured_event_data;
        selected_captured_event_payload_hash = v2_full_captured_event_payload_hash;
      end
      default: begin
      end
    endcase
  end

  assign replay_consume_observed_valid = selected_captured_event_valid;

  rcv2_replay_consumer #(
    .EVENT_COUNT(0),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .STRICT_ORDER(1'b1)
  ) u_rcv2_replay_consumer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .start(replay_consume_start),
    .expected_event_count(replay_consume_expected_count),
    .capsule_valid(replay_consume_valid),
    .capsule_ready(replay_consume_ready),
    .capsule_word(replay_consume_word),
    .stream_done(replay_consume_stream_done),
    .current_commit_index(commit_index),
    .observed_valid(replay_consume_observed_valid),
    .observed_event_type(selected_captured_event_type),
    .observed_commit_index(selected_captured_event_commit_index),
    .observed_addr(selected_captured_event_addr),
    .observed_data(selected_captured_event_data),
    .observed_payload_hash(selected_captured_event_payload_hash),
    .mmio_replay_valid(replay_consume_mmio_valid),
    .mmio_replay_addr_token(replay_consume_mmio_addr_token),
    .mmio_replay_value(replay_consume_mmio_value),
    .irq_replay_valid(replay_consume_irq_valid),
    .irq_replay_cause(replay_consume_irq_cause),
    .consumed_all_events(replay_consume_all_events),
    .replay_error(replay_consume_error),
    .replay_error_code(replay_consume_error_code),
    .consumed_count(replay_consume_consumed_count)
  );

  logic unused_replay_irq_valid;
  logic [7:0] unused_replay_irq_cause;
  logic [31:0] unused_replay_mmio_addr_token;
  assign unused_replay_irq_valid = replay_consume_irq_valid;
  assign unused_replay_irq_cause = replay_consume_irq_cause;
  assign unused_replay_mmio_addr_token = replay_consume_mmio_addr_token;
endmodule
