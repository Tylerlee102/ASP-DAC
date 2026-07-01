`include "../event_pkg.sv"

module hazard3_replaycapsule_v2_wrapper #(
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
  output logic [31:0] replay_consume_consumed_count,

  output logic [31:0] record_irq_entry_count,
  output logic [31:0] replay_irq_entry_count,
  output logic [31:0] record_mmio_read_count,
  output logic [31:0] replay_mmio_read_count,
  output logic [31:0] replay_mmio_drive_count,
  output logic [31:0] replay_irq_drive_count
);
  `include "../event_defs.svh"

  localparam logic [31:0] MMIO_IRQ_ACK  = 32'h4000_0014;
  localparam logic [31:0] MMIO_ISR_MARK = 32'h4000_0010;

  logic pwrup_req;
  logic clk_en;
  logic unblock_out;
  logic [31:0] haddr;
  logic hwrite;
  logic [1:0] htrans;
  logic [2:0] hsize;
  logic [2:0] hburst;
  logic [3:0] hprot;
  logic hmastlock;
  logic [7:0] hmaster;
  logic hexcl;
  logic [31:0] hwdata;
  logic [31:0] core_hrdata;
  logic core_hready;
  logic hresp;
  logic hexokay;
  logic fence_i_vld;
  logic fence_d_vld;
  logic dbg_halted;
  logic dbg_running;
  logic [31:0] dbg_data0_wdata;
  logic dbg_data0_wen;
  logic dbg_instr_data_rdy;
  logic dbg_instr_caught_exception;
  logic dbg_instr_caught_ebreak;
  logic dbg_sbus_rdy;
  logic dbg_sbus_err;
  logic [31:0] dbg_sbus_rdata;

  logic        dph_valid;
  logic        dph_write;
  logic        dph_instr;
  logic [2:0]  dph_size;
  logic [31:0] dph_addr;
  logic        dph_mmio;
  logic        data_phase_done;
  logic        core_mem_write;
  logic        core_mem_read;
  logic        mem_accepted;
  logic        commit_valid;
  logic [31:0] commit_index;
  logic [31:0] recorder_mem_rdata;
  logic        interrupt_enter;
  logic        interrupt_exit;
  logic        replay_drive_active;
  logic        replay_irq_level;
  logic        replay_mmio_read_fire;

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

  logic        captured_event_valid;
  logic [3:0]  captured_event_type;
  logic [31:0] captured_event_commit_index;
  logic [31:0] captured_event_addr;
  logic [31:0] captured_event_data;
  logic [31:0] captured_event_payload_hash;
  logic        replay_consume_mmio_valid;
  logic [31:0] replay_consume_mmio_addr_token;
  logic [31:0] replay_consume_mmio_value;
  logic        replay_consume_irq_valid;
  logic [7:0]  replay_consume_irq_cause;

  function automatic logic [3:0] hazard3_wstrb(
    input logic [2:0] size,
    input logic [1:0] addr
  );
    begin
      unique case (size)
        3'b010: hazard3_wstrb = 4'b1111;
        3'b001: hazard3_wstrb = addr[1] ? 4'b1100 : 4'b0011;
        default: hazard3_wstrb = 4'b0001 << addr;
      endcase
    end
  endfunction

  assign core_hready = !dph_valid || mem_ready;
  assign hresp = 1'b0;
  assign hexokay = 1'b1;
  assign data_phase_done = dph_valid && mem_ready;
  assign dph_mmio = dph_addr[31:16] == 16'h4000;
  assign core_mem_write = dph_valid && dph_write;
  assign core_mem_read = dph_valid && !dph_write;
  assign mem_valid = dph_valid;
  assign mem_instr = dph_instr;
  assign mem_addr = dph_addr;
  assign mem_wdata = hwdata;
  assign mem_wstrb = dph_write ? hazard3_wstrb(dph_size, dph_addr[1:0]) : 4'h0;
  assign replay_mmio_read_fire = replay_drive_active && data_phase_done && core_mem_read && dph_mmio && replay_consume_mmio_valid;
  assign recorder_mem_rdata = replay_mmio_read_fire ? replay_consume_mmio_value : mem_rdata;
  assign core_hrdata = (replay_drive_active && core_mem_read && dph_mmio && replay_consume_mmio_valid) ? replay_consume_mmio_value : mem_rdata;
  assign mem_accepted = data_phase_done && !dph_instr;
  assign commit_valid = data_phase_done && dph_instr;
  assign interrupt_enter = data_phase_done && core_mem_write && dph_addr == MMIO_ISR_MARK;
  assign interrupt_exit = data_phase_done && core_mem_write && dph_addr == MMIO_IRQ_ACK;
  assign trap = 1'b0;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      dph_valid <= 1'b0;
      dph_write <= 1'b0;
      dph_instr <= 1'b0;
      dph_size <= 3'b000;
      dph_addr <= 32'h0;
      commit_index <= 32'h0;
      replay_drive_active <= 1'b0;
      replay_irq_level <= 1'b0;
      record_irq_entry_count <= 32'h0;
      replay_irq_entry_count <= 32'h0;
      record_mmio_read_count <= 32'h0;
      replay_mmio_read_count <= 32'h0;
      replay_mmio_drive_count <= 32'h0;
      replay_irq_drive_count <= 32'h0;
    end else if (clear) begin
      dph_valid <= 1'b0;
      dph_write <= 1'b0;
      dph_instr <= 1'b0;
      dph_size <= 3'b000;
      dph_addr <= 32'h0;
      commit_index <= 32'h0;
      replay_drive_active <= 1'b0;
      replay_irq_level <= 1'b0;
      record_irq_entry_count <= 32'h0;
      replay_irq_entry_count <= 32'h0;
      record_mmio_read_count <= 32'h0;
      replay_mmio_read_count <= 32'h0;
      replay_mmio_drive_count <= 32'h0;
      replay_irq_drive_count <= 32'h0;
    end else begin
      if (core_hready) begin
        dph_valid <= htrans[1];
        dph_write <= hwrite;
        dph_instr <= hprot[0] == 1'b0;
        dph_size <= hsize;
        dph_addr <= haddr;
      end

      if (commit_valid) begin
        commit_index <= commit_index + 32'h1;
      end

      if (replay_consume_start) begin
        replay_drive_active <= 1'b1;
        replay_irq_level <= 1'b0;
      end else if (replay_consume_all_events || replay_consume_error) begin
        replay_drive_active <= 1'b0;
        replay_irq_level <= 1'b0;
      end

      if (replay_drive_active && replay_consume_irq_valid) begin
        replay_irq_level <= replay_consume_irq_cause != 8'h0;
        if (replay_consume_irq_cause != 8'h0) begin
          replay_irq_drive_count <= replay_irq_drive_count + 32'h1;
        end
      end

      if (interrupt_enter) begin
        if (replay_drive_active) begin
          replay_irq_entry_count <= replay_irq_entry_count + 32'h1;
        end else begin
          record_irq_entry_count <= record_irq_entry_count + 32'h1;
        end
      end
      if (data_phase_done && core_mem_read && dph_mmio) begin
        if (replay_drive_active) begin
          replay_mmio_read_count <= replay_mmio_read_count + 32'h1;
        end else begin
          record_mmio_read_count <= record_mmio_read_count + 32'h1;
        end
      end
      if (replay_mmio_read_fire) begin
        replay_mmio_drive_count <= replay_mmio_drive_count + 32'h1;
      end
    end
  end

  hazard3_cpu_1port #(
    .RESET_VECTOR(PROGADDR_RESET),
    .MTVEC_INIT(32'h0000_0010),
    .EXTENSION_A(0),
    .EXTENSION_C(0),
    .EXTENSION_M(0),
    .CSR_COUNTER(0),
    .DEBUG_SUPPORT(0),
    .RESET_REGFILE(1)
  ) u_core (
    .clk(clk),
    .clk_always_on(clk),
    .rst_n(rst_n && core_run_enable),
    .pwrup_req(pwrup_req),
    .pwrup_ack(1'b1),
    .clk_en(clk_en),
    .unblock_out(unblock_out),
    .unblock_in(1'b0),
    .haddr(haddr),
    .hwrite(hwrite),
    .htrans(htrans),
    .hsize(hsize),
    .hburst(hburst),
    .hprot(hprot),
    .hmastlock(hmastlock),
    .hmaster(hmaster),
    .hexcl(hexcl),
    .hready(core_hready),
    .hresp(hresp),
    .hexokay(hexokay),
    .hwdata(hwdata),
    .hrdata(core_hrdata),
    .fence_i_vld(fence_i_vld),
    .fence_d_vld(fence_d_vld),
    .fence_rdy(1'b1),
    .dbg_req_halt(1'b0),
    .dbg_req_halt_on_reset(1'b0),
    .dbg_req_resume(1'b0),
    .dbg_halted(dbg_halted),
    .dbg_running(dbg_running),
    .dbg_data0_rdata(32'h0),
    .dbg_data0_wdata(dbg_data0_wdata),
    .dbg_data0_wen(dbg_data0_wen),
    .dbg_instr_data(32'h0),
    .dbg_instr_data_vld(1'b0),
    .dbg_instr_data_rdy(dbg_instr_data_rdy),
    .dbg_instr_caught_exception(dbg_instr_caught_exception),
    .dbg_instr_caught_ebreak(dbg_instr_caught_ebreak),
    .dbg_sbus_addr(32'h0),
    .dbg_sbus_write(1'b0),
    .dbg_sbus_size(2'b00),
    .dbg_sbus_vld(1'b0),
    .dbg_sbus_rdy(dbg_sbus_rdy),
    .dbg_sbus_err(dbg_sbus_err),
    .dbg_sbus_wdata(32'h0),
    .dbg_sbus_rdata(dbg_sbus_rdata),
    .mhartid_val(32'h0),
    .eco_version(4'h0),
    .irq(replay_drive_active ? replay_irq_level : |irq),
    .soft_irq(1'b0),
    .timer_irq(1'b0)
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
    .commit_pc(dph_addr),
    .commit_instr(recorder_mem_rdata),
    .commit_index(commit_index),
    .branch_taken(1'b0),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_write),
    .mem_addr(dph_addr),
    .mem_wdata(hwdata),
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
    .commit_pc(dph_addr),
    .commit_instr(recorder_mem_rdata),
    .commit_index(commit_index),
    .branch_taken(1'b0),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_write),
    .mem_addr(dph_addr),
    .mem_wdata(hwdata),
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
    .commit_pc(dph_addr),
    .commit_instr(recorder_mem_rdata),
    .commit_index(commit_index),
    .branch_taken(1'b0),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_write),
    .mem_addr(dph_addr),
    .mem_wdata(hwdata),
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
    captured_event_valid = v2_core_captured_event_valid;
    captured_event_type = v2_core_captured_event_type;
    captured_event_commit_index = v2_core_captured_event_commit_index;
    captured_event_addr = v2_core_captured_event_addr;
    captured_event_data = v2_core_captured_event_data;
    captured_event_payload_hash = v2_core_captured_event_payload_hash;

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
        captured_event_valid = v2_hashed_captured_event_valid;
        captured_event_type = v2_hashed_captured_event_type;
        captured_event_commit_index = v2_hashed_captured_event_commit_index;
        captured_event_addr = v2_hashed_captured_event_addr;
        captured_event_data = v2_hashed_captured_event_data;
        captured_event_payload_hash = v2_hashed_captured_event_payload_hash;
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
        captured_event_valid = v2_full_captured_event_valid;
        captured_event_type = v2_full_captured_event_type;
        captured_event_commit_index = v2_full_captured_event_commit_index;
        captured_event_addr = v2_full_captured_event_addr;
        captured_event_data = v2_full_captured_event_data;
        captured_event_payload_hash = v2_full_captured_event_payload_hash;
      end
      default: begin
      end
    endcase
  end

  assign replay_consume_observed_valid = captured_event_valid;

  rcv2_replay_consumer #(
    .EVENT_COUNT(0),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .STRICT_ORDER(1'b1),
    .IRQ_REPLAY_LEAD(15)
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
    .observed_event_type(captured_event_type),
    .observed_commit_index(captured_event_commit_index),
    .observed_addr(captured_event_addr),
    .observed_data(captured_event_data),
    .observed_payload_hash(captured_event_payload_hash),
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

  logic unused_hazard3_outputs;
  logic [31:0] unused_replay_mmio_addr_token;
  logic [1:0] unused_recorder_config_select;
  assign unused_hazard3_outputs = pwrup_req ^ clk_en ^ unblock_out ^ fence_i_vld ^ fence_d_vld ^
                                  dbg_halted ^ dbg_running ^ dbg_data0_wen ^ dbg_instr_data_rdy ^
                                  dbg_instr_caught_exception ^ dbg_instr_caught_ebreak ^
                                  dbg_sbus_rdy ^ dbg_sbus_err ^ hmastlock ^ hexcl ^ ^hburst ^
                                  ^hprot ^ ^hmaster ^ ^dbg_data0_wdata ^ ^dbg_sbus_rdata;
  assign unused_replay_mmio_addr_token = replay_consume_mmio_addr_token;
  assign unused_recorder_config_select = recorder_config_select;
endmodule
