module full_core_replaycapsule_v2_board_top #(
  parameter int          MEM_WORDS      = 512,
  parameter int          CAPSULE_DEPTH  = 128,
  parameter int          CAPSULE_ADDR_W = $clog2(CAPSULE_DEPTH),
  parameter int          REPLAYCAPSULE_CONFIG = 1,
  parameter bit          ENABLE_DIAGNOSTICS = (REPLAYCAPSULE_CONFIG == 4),
  parameter bit          ENABLE_PAYLOAD_HASH = (REPLAYCAPSULE_CONFIG != 1),
  parameter bit          ENABLE_ADDRESS_DICTIONARY = 1'b0,
  parameter bit          ENABLE_ADAPTIVE_WINDOW = (REPLAYCAPSULE_CONFIG == 4),
  parameter bit          ENABLE_PROPERTY_CHECKER = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit          ENABLE_CONTEXT_SLICER = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit          ENABLE_EVENT_BUFFER = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit          ENABLE_SIGNATURE = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit          ENABLE_STATUS_COUNTERS = (REPLAYCAPSULE_CONFIG != 0),
  parameter bit          ENABLE_MINIMAL_EVENT_TAP = (REPLAYCAPSULE_CONFIG == 0),
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
  parameter logic [31:0] PROGADDR_IRQ   = 32'h0000_0010,
  parameter logic [31:0] STACKADDR      = 32'h0000_2000
) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       uart_rx,
  output logic       uart_tx,
  input  logic [3:0] gpio_in,
  output logic [7:0] gpio_out,
  output logic [3:0] status_led,
  output logic       capsule_event_seen,
  output logic       recorder_overflow_seen,
  output logic       recorder_status_xor
);
  logic trap;
  logic mem_valid;
  logic mem_instr;
  logic mem_ready;
  logic [31:0] mem_addr;
  logic [31:0] mem_wdata;
  logic [3:0] mem_wstrb;
  logic [31:0] mem_rdata;
  logic [31:0] irq;
  logic [31:0] eoi;
  logic [31:0] eoi_q;
  logic eoi_active_q;
  logic [7:0] memory_gpio_out;
  logic memory_uart_tx;
  logic [31:0] io_status;
  logic [31:0] board_counter;
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
  logic interrupt_enter;
  logic interrupt_exit;
  logic mem_accepted;
  (* keep = "true" *) logic [CAPSULE_ADDR_W-1:0] capsule_read_addr;
  (* keep = "true" *) logic [63:0] capsule_read_data;
  (* keep = "true" *) logic capsule_frozen;
  (* keep = "true" *) logic capsule_overflow;
  (* keep = "true" *) logic [CAPSULE_ADDR_W:0] capsule_event_count;
  (* keep = "true" *) logic [31:0] running_signature;
  (* keep = "true" *) logic property_fail_valid;
  (* keep = "true" *) logic [7:0] property_id;
  (* keep = "true" *) logic [31:0] property_signature;
  (* keep = "true" *) logic captured_event_valid;
  (* keep = "true" *) logic [3:0] captured_event_type;
  (* keep = "true" *) logic capsule_stream_valid;
  (* keep = "true" *) logic [63:0] capsule_stream_word;
  (* keep = "true" *) logic [31:0] stream_event_count;
  (* keep = "true" *) logic [31:0] stream_event_sent_count;
  (* keep = "true" *) logic [31:0] replay_critical_event_count;
  (* keep = "true" *) logic [31:0] stream_stall_count;
  (* keep = "true" *) logic [31:0] dropped_diagnostic_count;
  (* keep = "true" *) logic [31:0] replay_critical_overflow_count;
  (* keep = "true" *) logic [CAPSULE_ADDR_W:0] stream_fifo_level;
  (* keep = "true" *) logic [31:0] recorder_status_mix;
  localparam int CAPSULE_COUNT_PAD_W = 32 - (CAPSULE_ADDR_W + 1);
  localparam logic [3:0] TRACE_BRANCH_FLAG = 4'b0001;
  localparam logic [3:0] TRACE_ADDR_FLAG   = 4'b0010;

  assign irq = {24'h0, gpio_in, 3'b000, uart_rx};
  assign capsule_read_addr = (REPLAYCAPSULE_CONFIG == 0) ? '0 : board_counter[CAPSULE_ADDR_W-1:0];
  assign trace_kind = core_trace_data[35:32];
  assign trace_payload = core_trace_data[31:0];
  assign trace_is_branch = (trace_kind & TRACE_BRANCH_FLAG) != 4'h0;
  assign trace_is_addr = (trace_kind & TRACE_ADDR_FLAG) != 4'h0;
  assign trace_context_pc = trace_is_branch ? trace_payload : fetch_context_pc;
  assign branch_taken = core_trace_valid && trace_is_branch;
  assign interrupt_enter = (REPLAYCAPSULE_CONFIG == 0) ? (eoi != 32'h0 && !eoi_active_q) : (eoi != 32'h0 && eoi_q == 32'h0);
  assign interrupt_exit = (REPLAYCAPSULE_CONFIG == 0) ? (eoi == 32'h0 && eoi_active_q) : (eoi == 32'h0 && eoi_q != 32'h0);
  assign mem_accepted = mem_valid && mem_ready && !mem_instr;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      board_counter <= 32'h0;
      commit_index <= 32'h0;
      fetch_context_pc <= PROGADDR_RESET;
      eoi_q <= 32'h0;
      eoi_active_q <= 1'b0;
    end else begin
      if (REPLAYCAPSULE_CONFIG == 0) begin
        board_counter <= 32'h0;
      end else begin
        board_counter <= board_counter + 32'h1;
      end
      eoi_q <= eoi;
      eoi_active_q <= eoi != 32'h0;
      if (core_trace_valid && !trace_is_addr) begin
        commit_index <= commit_index + 32'h1;
      end
      if (REPLAYCAPSULE_CONFIG != 0 && mem_valid && mem_ready && mem_instr) begin
        fetch_context_pc <= mem_addr;
      end
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
    .mem_valid(mem_valid),
    .mem_instr(mem_instr),
    .mem_ready(mem_ready),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wstrb(mem_wstrb),
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
    .eoi(eoi),
    .trace_valid(core_trace_valid),
    .trace_data(core_trace_data)
  );

  mapped_memory #(
    .WORDS(MEM_WORDS)
  ) u_mapped_memory (
    .clk(clk),
    .rst_n(rst_n),
    .mem_valid(mem_valid),
    .mem_instr(mem_instr),
    .mem_ready(mem_ready),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wstrb(mem_wstrb),
    .mem_rdata(mem_rdata),
    .gpio_in(gpio_in),
    .gpio_out(memory_gpio_out),
    .uart_rx(uart_rx),
    .uart_tx(memory_uart_tx),
    .io_status(io_status)
  );

  (* keep_hierarchy = "yes" *) rcv2_recorder #(
    .REPLAYCAPSULE_CONFIG(REPLAYCAPSULE_CONFIG),
    .BUFFER_DEPTH(CAPSULE_DEPTH),
    .MEMORY_WORDS(CAPSULE_DEPTH),
    .MEMORY_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_DIAGNOSTICS(ENABLE_DIAGNOSTICS),
    .ENABLE_PAYLOAD_HASH(ENABLE_PAYLOAD_HASH),
    .ENABLE_ADDRESS_DICTIONARY(ENABLE_ADDRESS_DICTIONARY),
    .ENABLE_BRam_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(ENABLE_ADAPTIVE_WINDOW),
    .ENABLE_WATCHDOG(1'b0),
    .ENABLE_PROPERTY_CHECKER(ENABLE_PROPERTY_CHECKER),
    .ENABLE_CONTEXT_SLICER(ENABLE_CONTEXT_SLICER),
    .ENABLE_EVENT_BUFFER(ENABLE_EVENT_BUFFER),
    .ENABLE_SIGNATURE(ENABLE_SIGNATURE),
    .ENABLE_STATUS_COUNTERS(ENABLE_STATUS_COUNTERS),
    .ENABLE_MINIMAL_EVENT_TAP(ENABLE_MINIMAL_EVENT_TAP)
  ) u_rcv2_recorder (
    .clk(clk),
    .rst_n(rst_n),
    .clear(1'b0),
    .watchdog_enable(gpio_in[1]),
    .commit_valid(core_trace_valid && !trace_is_addr),
    .commit_pc((REPLAYCAPSULE_CONFIG == 0) ? 32'h0 : trace_context_pc),
    .commit_instr(32'h0000_0013),
    .commit_index(commit_index),
    .branch_taken((REPLAYCAPSULE_CONFIG == 0) ? 1'b0 : branch_taken),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(mem_wstrb != 4'h0),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid((REPLAYCAPSULE_CONFIG == 0) ? (uart_rx ^ gpio_in[0]) : (board_counter[4] ^ uart_rx ^ gpio_in[0])),
    .external_input_value((REPLAYCAPSULE_CONFIG == 0) ? {24'h0, gpio_in, 3'b000, uart_rx} : (board_counter ^ {24'h0, gpio_in, 3'b000, uart_rx})),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(1'b0),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(capsule_read_data),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .capsule_event_count(capsule_event_count),
    .running_signature(running_signature),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .captured_event_valid(captured_event_valid),
    .captured_event_type(captured_event_type),
    .captured_event_commit_index(),
    .captured_event_addr(),
    .captured_event_data(),
    .captured_event_payload_hash(),
    .capsule_stream_ready(1'b1),
    .capsule_stream_valid(capsule_stream_valid),
    .capsule_stream_word(capsule_stream_word),
    .stream_event_count(stream_event_count),
    .stream_event_sent_count(stream_event_sent_count),
    .replay_critical_event_count(replay_critical_event_count),
    .stream_stall_count(stream_stall_count),
    .dropped_diagnostic_count(dropped_diagnostic_count),
    .replay_critical_overflow_count(replay_critical_overflow_count),
    .stream_fifo_level(stream_fifo_level)
  );

  always_comb begin
    if (REPLAYCAPSULE_CONFIG == 0) begin
      recorder_status_mix =
        capsule_stream_word[31:0] ^
        capsule_stream_word[63:32] ^
        {26'h0, capsule_stream_valid, captured_event_valid, captured_event_type} ^
        mem_addr ^
        mem_wdata ^
        mem_rdata ^
        io_status ^
        eoi;
    end else begin
      recorder_status_mix =
        running_signature ^
        property_signature ^
        capsule_read_data[31:0] ^
        capsule_read_data[63:32] ^
        {{CAPSULE_COUNT_PAD_W{1'b0}}, capsule_event_count} ^
        {24'h0, property_id} ^
        {28'h0, captured_event_type} ^
        capsule_stream_word[31:0] ^
        capsule_stream_word[63:32] ^
        stream_event_count ^
        stream_event_sent_count ^
        replay_critical_event_count ^
        stream_stall_count ^
        dropped_diagnostic_count ^
        replay_critical_overflow_count ^
        {{CAPSULE_COUNT_PAD_W{1'b0}}, stream_fifo_level} ^
        mem_addr ^
        mem_wdata ^
        mem_rdata ^
        io_status ^
        eoi ^
        board_counter;
    end
  end

  assign gpio_out = memory_gpio_out ^ recorder_status_mix[7:0];
  assign uart_tx = memory_uart_tx ^ trap ^ recorder_status_mix[8];
  assign status_led = {
    capsule_frozen,
    capsule_overflow,
    property_fail_valid,
    |capsule_event_count
  } ^ recorder_status_mix[3:0];
  assign capsule_event_seen = |capsule_event_count | property_fail_valid | capsule_frozen | captured_event_valid;
  assign recorder_overflow_seen = capsule_overflow | (replay_critical_overflow_count != 32'h0);
  assign recorder_status_xor = ^recorder_status_mix;
endmodule
