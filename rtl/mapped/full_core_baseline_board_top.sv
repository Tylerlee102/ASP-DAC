module full_core_baseline_board_top #(
  parameter int          MEM_WORDS      = 2048,
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
  logic [31:0] commit_count;
  logic [7:0] memory_gpio_out;
  logic memory_uart_tx;
  logic [31:0] io_status;
  (* keep = "true" *) logic [31:0] baseline_status_mix;

  assign irq = {24'h0, gpio_in, 3'b000, uart_rx};

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
    .trace_valid(),
    .trace_data()
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

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      commit_count <= 32'h0;
    end else if (mem_valid && mem_ready && mem_instr) begin
      commit_count <= commit_count + 32'h1;
    end
  end

  assign baseline_status_mix = commit_count ^ mem_addr ^ mem_wdata ^ mem_rdata ^ io_status ^ eoi;
  assign gpio_out = memory_gpio_out ^ baseline_status_mix[7:0];
  assign uart_tx = memory_uart_tx ^ trap ^ baseline_status_mix[8];
  assign status_led = {trap, mem_valid, mem_instr, |mem_wstrb} ^ baseline_status_mix[3:0];
  assign capsule_event_seen = |commit_count;
  assign recorder_overflow_seen = trap;
  assign recorder_status_xor = ^baseline_status_mix;
endmodule
