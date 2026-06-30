`include "../event_pkg.sv"

module picorv32_replaycapsule_wrapper #(
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
  parameter logic [31:0] PROGADDR_IRQ   = 32'h0000_0010,
  parameter logic [31:0] STACKADDR      = 32'h0000_2000,
  parameter int          CAPSULE_DEPTH  = 256,
  parameter int          CAPSULE_ADDR_W = $clog2(CAPSULE_DEPTH),
  parameter bit          ENABLE_WATCHDOG = 1'b0,
  parameter bit          ENABLE_V2_RECORDERS = 1'b1
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
  output logic [167:0] capsule_read_data,
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
  logic [3:0] core_mem_wstrb;
  logic core_mem_valid;
  logic core_mem_instr;
  logic [31:0] core_eoi;
  logic [31:0] core_eoi_q;
  logic core_trace_valid;
  logic [35:0] core_trace_data;
  logic [31:0] commit_index;
  logic [31:0] fetch_context_pc;
  logic [31:0] trace_payload;
  logic [31:0] trace_context_pc;
  logic [3:0] trace_kind;
  logic trace_is_branch;
  logic trace_is_addr;
  logic branch_taken;
  logic jump_taken;
  logic interrupt_enter;
  logic interrupt_exit;
  logic mem_accepted;
  logic [167:0] v1_capsule_read_data;
  logic v1_capsule_frozen;
  logic v1_capsule_overflow;
  logic [CAPSULE_ADDR_W:0] v1_capsule_event_count;
  logic [31:0] v1_running_signature;
  logic v1_property_fail_valid;
  logic [7:0] v1_property_id;
  logic [31:0] v1_property_signature;
  logic [63:0] v2_core_capsule_read_data;
  logic v2_core_capsule_frozen;
  logic v2_core_capsule_overflow;
  logic [CAPSULE_ADDR_W:0] v2_core_capsule_event_count;
  logic [31:0] v2_core_running_signature;
  logic v2_core_property_fail_valid;
  logic [7:0] v2_core_property_id;
  logic [31:0] v2_core_property_signature;
  logic v2_core_captured_event_valid;
  logic [3:0] v2_core_captured_event_type;
  logic [31:0] v2_core_captured_event_commit_index;
  logic [31:0] v2_core_captured_event_addr;
  logic [31:0] v2_core_captured_event_data;
  logic [31:0] v2_core_captured_event_payload_hash;
  logic v2_core_stream_ready;
  logic v2_core_stream_valid;
  logic [63:0] v2_core_stream_word;
  logic [31:0] v2_core_stream_event_count;
  logic [31:0] v2_core_stream_sent_count;
  logic [31:0] v2_core_replay_critical_event_count;
  logic [31:0] v2_core_stream_stall_count;
  logic [31:0] v2_core_replay_critical_overflow_count;
  logic [CAPSULE_ADDR_W:0] v2_core_stream_fifo_level;
  logic [31:0] v2_core_dropped_diagnostic_count;
  logic [63:0] v2_hashed_capsule_read_data;
  logic v2_hashed_capsule_frozen;
  logic v2_hashed_capsule_overflow;
  logic [CAPSULE_ADDR_W:0] v2_hashed_capsule_event_count;
  logic [31:0] v2_hashed_running_signature;
  logic v2_hashed_property_fail_valid;
  logic [7:0] v2_hashed_property_id;
  logic [31:0] v2_hashed_property_signature;
  logic v2_hashed_captured_event_valid;
  logic [3:0] v2_hashed_captured_event_type;
  logic [31:0] v2_hashed_captured_event_commit_index;
  logic [31:0] v2_hashed_captured_event_addr;
  logic [31:0] v2_hashed_captured_event_data;
  logic [31:0] v2_hashed_captured_event_payload_hash;
  logic v2_hashed_stream_ready;
  logic v2_hashed_stream_valid;
  logic [63:0] v2_hashed_stream_word;
  logic [31:0] v2_hashed_stream_event_count;
  logic [31:0] v2_hashed_stream_sent_count;
  logic [31:0] v2_hashed_replay_critical_event_count;
  logic [31:0] v2_hashed_stream_stall_count;
  logic [31:0] v2_hashed_replay_critical_overflow_count;
  logic [CAPSULE_ADDR_W:0] v2_hashed_stream_fifo_level;
  logic [31:0] v2_hashed_dropped_diagnostic_count;
  logic [63:0] v2_full_capsule_read_data;
  logic v2_full_capsule_frozen;
  logic v2_full_capsule_overflow;
  logic [CAPSULE_ADDR_W:0] v2_full_capsule_event_count;
  logic [31:0] v2_full_running_signature;
  logic v2_full_property_fail_valid;
  logic [7:0] v2_full_property_id;
  logic [31:0] v2_full_property_signature;
  logic v2_full_captured_event_valid;
  logic [3:0] v2_full_captured_event_type;
  logic [31:0] v2_full_captured_event_commit_index;
  logic [31:0] v2_full_captured_event_addr;
  logic [31:0] v2_full_captured_event_data;
  logic [31:0] v2_full_captured_event_payload_hash;
  logic v2_full_stream_ready;
  logic v2_full_stream_valid;
  logic [63:0] v2_full_stream_word;
  logic [31:0] v2_full_stream_event_count;
  logic [31:0] v2_full_stream_sent_count;
  logic [31:0] v2_full_replay_critical_event_count;
  logic [31:0] v2_full_stream_stall_count;
  logic [31:0] v2_full_replay_critical_overflow_count;
  logic [CAPSULE_ADDR_W:0] v2_full_stream_fifo_level;
  logic [31:0] v2_full_dropped_diagnostic_count;
  logic selected_v2_captured_event_valid;
  logic [3:0] selected_v2_captured_event_type;
  logic [31:0] selected_v2_captured_event_commit_index;
  logic [31:0] selected_v2_captured_event_addr;
  logic [31:0] selected_v2_captured_event_data;
  logic [31:0] selected_v2_captured_event_payload_hash;
  logic replay_consume_mmio_valid;
  logic [31:0] replay_consume_mmio_addr_token;
  logic [31:0] replay_consume_mmio_value;
  logic replay_consume_irq_valid;
  logic [7:0] replay_consume_irq_cause;
  logic use_v2;
  logic v2_capture_enabled;

  localparam logic [3:0] TRACE_BRANCH_FLAG = 4'b0001;
  localparam logic [3:0] TRACE_ADDR_FLAG   = 4'b0010;

  assign mem_valid = core_mem_valid;
  assign mem_instr = core_mem_instr;
  assign mem_addr = core_mem_addr;
  assign mem_wdata = core_mem_wdata;
  assign mem_wstrb = core_mem_wstrb;
  assign eoi = core_eoi;

  assign trace_kind = core_trace_data[35:32];
  assign trace_payload = core_trace_data[31:0];
  assign trace_is_branch = (trace_kind & TRACE_BRANCH_FLAG) != 4'h0;
  assign trace_is_addr = (trace_kind & TRACE_ADDR_FLAG) != 4'h0;
  assign trace_context_pc = trace_is_branch ? trace_payload : fetch_context_pc;
  assign branch_taken = core_trace_valid && trace_is_branch;
  assign jump_taken = 1'b0;
  assign interrupt_enter = core_eoi != 32'h0 && core_eoi_q == 32'h0;
  assign interrupt_exit = core_eoi == 32'h0 && core_eoi_q != 32'h0;
  assign mem_accepted = core_mem_valid && mem_ready && !core_mem_instr;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      commit_index <= 32'h0;
    end else if (clear) begin
      commit_index <= 32'h0;
    end else if (core_trace_valid && !trace_is_addr) begin
      commit_index <= commit_index + 32'h1;
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      fetch_context_pc <= PROGADDR_RESET;
    end else if (clear) begin
      fetch_context_pc <= PROGADDR_RESET;
    end else if (core_mem_valid && mem_ready && core_mem_instr) begin
      fetch_context_pc <= core_mem_addr;
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      core_eoi_q <= 32'h0;
    end else if (clear) begin
      core_eoi_q <= 32'h0;
    end else begin
      core_eoi_q <= core_eoi;
    end
  end

  picorv32 #(
    .ENABLE_COUNTERS(1),
    .ENABLE_COUNTERS64(1),
    .ENABLE_REGS_16_31(1),
    .ENABLE_REGS_DUALPORT(1),
    .LATCHED_MEM_RDATA(0),
    .TWO_STAGE_SHIFT(1),
    .BARREL_SHIFTER(0),
    .TWO_CYCLE_COMPARE(0),
    .TWO_CYCLE_ALU(0),
    .COMPRESSED_ISA(0),
    .CATCH_MISALIGN(1),
    .CATCH_ILLINSN(1),
    .ENABLE_PCPI(0),
    .ENABLE_MUL(0),
    .ENABLE_FAST_MUL(0),
    .ENABLE_DIV(0),
    .ENABLE_IRQ(1),
    .ENABLE_IRQ_QREGS(1),
    .ENABLE_IRQ_TIMER(1),
    .ENABLE_TRACE(1),
    .REGS_INIT_ZERO(1),
    .MASKED_IRQ(32'h0000_0000),
    .LATCHED_IRQ(32'hffff_ffff),
    .PROGADDR_RESET(PROGADDR_RESET),
    .PROGADDR_IRQ(PROGADDR_IRQ),
    .STACKADDR(STACKADDR)
  ) u_picorv32 (
    .clk(clk),
    .resetn(rst_n),
    .trap(trap),
    .mem_valid(core_mem_valid),
    .mem_instr(core_mem_instr),
    .mem_ready(mem_ready),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_wstrb(core_mem_wstrb),
    .mem_rdata(mem_rdata),
    .mem_la_read(),
    .mem_la_write(),
    .mem_la_addr(),
    .mem_la_wdata(),
    .mem_la_wstrb(),
    .pcpi_valid(),
    .pcpi_insn(),
    .pcpi_rs1(),
    .pcpi_rs2(),
    .pcpi_wr(1'b0),
    .pcpi_rd(32'h0),
    .pcpi_wait(1'b0),
    .pcpi_ready(1'b0),
    .irq(irq),
    .eoi(core_eoi),
    .trace_valid(core_trace_valid),
    .trace_data(core_trace_data)
  );

  replay_capsule_top #(
    .CAPSULE_DEPTH(CAPSULE_DEPTH),
    .ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_replay_capsule_top (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .capture_mode(capture_mode),
    .commit_valid(core_trace_valid && !trace_is_addr),
    .commit_pc(trace_context_pc),
    .commit_instr(32'h0),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_wstrb != 4'h0),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(1'b0),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(v1_capsule_read_data),
    .capsule_frozen(v1_capsule_frozen),
    .capsule_overflow(v1_capsule_overflow),
    .capsule_event_count(v1_capsule_event_count),
    .running_signature(v1_running_signature),
    .property_fail_valid(v1_property_fail_valid),
    .property_id(v1_property_id),
    .property_signature(v1_property_signature),
    .captured_event_valid(),
    .captured_event_type()
  );

  generate
    if (ENABLE_V2_RECORDERS) begin : g_v2_recorders
  rcv2_recorder #(
    .REPLAYCAPSULE_CONFIG(1),
    .BUFFER_DEPTH(CAPSULE_DEPTH),
    .MEMORY_WORDS(CAPSULE_DEPTH),
    .MEMORY_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_DIAGNOSTICS(1'b1),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .ENABLE_ADDRESS_DICTIONARY(1'b1),
    .ENABLE_BRam_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(1'b1),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_rcv2_core (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .commit_valid(v2_capture_enabled && core_trace_valid && !trace_is_addr),
    .commit_pc(trace_context_pc),
    .commit_instr(32'h0),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(v2_capture_enabled && mem_accepted),
    .mem_write(core_mem_wstrb != 4'h0),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(v2_capture_enabled && external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(v2_capture_enabled && interrupt_enter),
    .interrupt_exit(v2_capture_enabled && interrupt_exit),
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
    .ENABLE_BRam_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(1'b1),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_rcv2_hashed (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .commit_valid(v2_capture_enabled && core_trace_valid && !trace_is_addr),
    .commit_pc(trace_context_pc),
    .commit_instr(32'h0),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(v2_capture_enabled && mem_accepted),
    .mem_write(core_mem_wstrb != 4'h0),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(v2_capture_enabled && external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(v2_capture_enabled && interrupt_enter),
    .interrupt_exit(v2_capture_enabled && interrupt_exit),
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
    .ENABLE_BRam_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(1'b1),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_rcv2_full (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .commit_valid(v2_capture_enabled && core_trace_valid && !trace_is_addr),
    .commit_pc(trace_context_pc),
    .commit_instr(32'h0),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(v2_capture_enabled && mem_accepted),
    .mem_write(core_mem_wstrb != 4'h0),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(v2_capture_enabled && external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(v2_capture_enabled && interrupt_enter),
    .interrupt_exit(v2_capture_enabled && interrupt_exit),
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
    end else begin : g_no_v2_recorders
      assign v2_core_capsule_read_data = '0;
      assign v2_core_capsule_frozen = 1'b0;
      assign v2_core_capsule_overflow = 1'b0;
      assign v2_core_capsule_event_count = '0;
      assign v2_core_running_signature = 32'h0;
      assign v2_core_property_fail_valid = 1'b0;
      assign v2_core_property_id = 8'h0;
      assign v2_core_property_signature = 32'h0;
      assign v2_core_captured_event_valid = 1'b0;
      assign v2_core_captured_event_type = 4'h0;
      assign v2_core_captured_event_commit_index = 32'h0;
      assign v2_core_captured_event_addr = 32'h0;
      assign v2_core_captured_event_data = 32'h0;
      assign v2_core_captured_event_payload_hash = 32'h0;
      assign v2_core_stream_valid = 1'b0;
      assign v2_core_stream_word = 64'h0;
      assign v2_core_stream_event_count = 32'h0;
      assign v2_core_stream_sent_count = 32'h0;
      assign v2_core_replay_critical_event_count = 32'h0;
      assign v2_core_stream_stall_count = 32'h0;
      assign v2_core_replay_critical_overflow_count = 32'h0;
      assign v2_core_stream_fifo_level = '0;
      assign v2_core_dropped_diagnostic_count = 32'h0;
      assign v2_hashed_capsule_read_data = '0;
      assign v2_hashed_capsule_frozen = 1'b0;
      assign v2_hashed_capsule_overflow = 1'b0;
      assign v2_hashed_capsule_event_count = '0;
      assign v2_hashed_running_signature = 32'h0;
      assign v2_hashed_property_fail_valid = 1'b0;
      assign v2_hashed_property_id = 8'h0;
      assign v2_hashed_property_signature = 32'h0;
      assign v2_hashed_captured_event_valid = 1'b0;
      assign v2_hashed_captured_event_type = 4'h0;
      assign v2_hashed_captured_event_commit_index = 32'h0;
      assign v2_hashed_captured_event_addr = 32'h0;
      assign v2_hashed_captured_event_data = 32'h0;
      assign v2_hashed_captured_event_payload_hash = 32'h0;
      assign v2_hashed_stream_valid = 1'b0;
      assign v2_hashed_stream_word = 64'h0;
      assign v2_hashed_stream_event_count = 32'h0;
      assign v2_hashed_stream_sent_count = 32'h0;
      assign v2_hashed_replay_critical_event_count = 32'h0;
      assign v2_hashed_stream_stall_count = 32'h0;
      assign v2_hashed_replay_critical_overflow_count = 32'h0;
      assign v2_hashed_stream_fifo_level = '0;
      assign v2_hashed_dropped_diagnostic_count = 32'h0;
      assign v2_full_capsule_read_data = '0;
      assign v2_full_capsule_frozen = 1'b0;
      assign v2_full_capsule_overflow = 1'b0;
      assign v2_full_capsule_event_count = '0;
      assign v2_full_running_signature = 32'h0;
      assign v2_full_property_fail_valid = 1'b0;
      assign v2_full_property_id = 8'h0;
      assign v2_full_property_signature = 32'h0;
      assign v2_full_captured_event_valid = 1'b0;
      assign v2_full_captured_event_type = 4'h0;
      assign v2_full_captured_event_commit_index = 32'h0;
      assign v2_full_captured_event_addr = 32'h0;
      assign v2_full_captured_event_data = 32'h0;
      assign v2_full_captured_event_payload_hash = 32'h0;
      assign v2_full_stream_valid = 1'b0;
      assign v2_full_stream_word = 64'h0;
      assign v2_full_stream_event_count = 32'h0;
      assign v2_full_stream_sent_count = 32'h0;
      assign v2_full_replay_critical_event_count = 32'h0;
      assign v2_full_stream_stall_count = 32'h0;
      assign v2_full_replay_critical_overflow_count = 32'h0;
      assign v2_full_stream_fifo_level = '0;
      assign v2_full_dropped_diagnostic_count = 32'h0;
    end
  endgenerate

  assign use_v2 = arch_select == 2'd2;
  assign v2_capture_enabled = capture_mode != 4'h4;
  assign v2_core_stream_ready = !(use_v2 && recorder_config_select == 2'd0) || capsule_stream_ready;
  assign v2_hashed_stream_ready = !(use_v2 && recorder_config_select == 2'd1) || capsule_stream_ready;
  assign v2_full_stream_ready = !(use_v2 && recorder_config_select == 2'd2) || capsule_stream_ready;

  always_comb begin
    selected_v2_captured_event_valid = v2_core_captured_event_valid;
    selected_v2_captured_event_type = v2_core_captured_event_type;
    selected_v2_captured_event_commit_index = v2_core_captured_event_commit_index;
    selected_v2_captured_event_addr = v2_core_captured_event_addr;
    selected_v2_captured_event_data = v2_core_captured_event_data;
    selected_v2_captured_event_payload_hash = v2_core_captured_event_payload_hash;

    case (recorder_config_select)
      2'd1: begin
        selected_v2_captured_event_valid = v2_hashed_captured_event_valid;
        selected_v2_captured_event_type = v2_hashed_captured_event_type;
        selected_v2_captured_event_commit_index = v2_hashed_captured_event_commit_index;
        selected_v2_captured_event_addr = v2_hashed_captured_event_addr;
        selected_v2_captured_event_data = v2_hashed_captured_event_data;
        selected_v2_captured_event_payload_hash = v2_hashed_captured_event_payload_hash;
      end
      2'd2: begin
        selected_v2_captured_event_valid = v2_full_captured_event_valid;
        selected_v2_captured_event_type = v2_full_captured_event_type;
        selected_v2_captured_event_commit_index = v2_full_captured_event_commit_index;
        selected_v2_captured_event_addr = v2_full_captured_event_addr;
        selected_v2_captured_event_data = v2_full_captured_event_data;
        selected_v2_captured_event_payload_hash = v2_full_captured_event_payload_hash;
      end
      default: begin
      end
    endcase
  end

  assign replay_consume_observed_valid = use_v2 && selected_v2_captured_event_valid;

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
    .capsule_valid(use_v2 && replay_consume_valid),
    .capsule_ready(replay_consume_ready),
    .capsule_word(replay_consume_word),
    .stream_done(replay_consume_stream_done),
    .observed_valid(replay_consume_observed_valid),
    .observed_event_type(selected_v2_captured_event_type),
    .observed_commit_index(selected_v2_captured_event_commit_index),
    .observed_addr(selected_v2_captured_event_addr),
    .observed_data(selected_v2_captured_event_data),
    .observed_payload_hash(selected_v2_captured_event_payload_hash),
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

  always_comb begin
    capsule_read_data = v1_capsule_read_data;
    capsule_frozen = v1_capsule_frozen;
    capsule_overflow = v1_capsule_overflow;
    capsule_event_count = v1_capsule_event_count;
    running_signature = v1_running_signature;
    property_fail_valid = v1_property_fail_valid;
    property_id = v1_property_id;
    property_signature = v1_property_signature;
    capsule_stream_valid = 1'b0;
    capsule_stream_word = 64'h0;
    capsule_stream_event_count = 32'h0;
    capsule_stream_sent_count = 32'h0;
    capsule_replay_critical_event_count = 32'h0;
    capsule_stream_stall_count = 32'h0;
    capsule_dropped_diagnostic_count = 32'h0;
    capsule_replay_critical_overflow_count = 32'h0;
    capsule_stream_fifo_level = '0;

    if (use_v2) begin
      case (recorder_config_select)
        2'd1: begin
          capsule_read_data = {104'h0, v2_hashed_capsule_read_data};
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
        end
        2'd2: begin
          capsule_read_data = {104'h0, v2_full_capsule_read_data};
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
        end
        default: begin
          capsule_read_data = {104'h0, v2_core_capsule_read_data};
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
        end
      endcase
    end
  end

  logic unused_v2_dropped;
  assign unused_v2_dropped =
    (|v2_core_dropped_diagnostic_count) |
    (|v2_hashed_dropped_diagnostic_count) |
    (|v2_full_dropped_diagnostic_count);
endmodule
