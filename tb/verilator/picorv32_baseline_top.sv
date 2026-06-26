module picorv32_baseline_top #(
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
  parameter logic [31:0] PROGADDR_IRQ   = 32'h0000_0010,
  parameter logic [31:0] STACKADDR      = 32'h0000_2000
) (
  input  logic        clk,
  input  logic        rst_n,

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
  output logic [31:0] commit_count
);
  logic core_trace_valid;
  logic [35:0] core_trace_data;
  logic [3:0] trace_kind;
  logic trace_is_addr;

  localparam logic [3:0] TRACE_ADDR_FLAG = 4'b0010;

  assign trace_kind = core_trace_data[35:32];
  assign trace_is_addr = (trace_kind & TRACE_ADDR_FLAG) != 4'h0;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      commit_count <= 32'h0;
    end else if (core_trace_valid && !trace_is_addr) begin
      commit_count <= commit_count + 32'h1;
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
endmodule
