`include "../event_pkg.sv"

module picorv32_replaycapsule_wrapper #(
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
  output logic [31:0] property_signature
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
    .capsule_read_data(capsule_read_data),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .capsule_event_count(capsule_event_count),
    .running_signature(running_signature),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .captured_event_valid(),
    .captured_event_type()
  );
endmodule
