`include "../event_pkg.sv"

module femtorv32_replaycapsule_wrapper #(
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
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
  logic [31:0] core_mem_addr;
  logic [31:0] core_mem_wdata;
  logic [3:0]  core_mem_wmask;
  logic [31:0] core_mem_rdata;
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

  assign core_mem_read = core_mem_rstrb;
  assign core_mem_write = core_mem_wmask != 4'h0;
  assign core_mem_mmio = core_mem_addr[31:16] == 16'h4000;
  assign core_mem_rom_fetch = core_mem_read && !core_mem_mmio && core_mem_addr < 32'h0000_2000;
  assign mem_valid = core_mem_read || core_mem_write;
  assign mem_instr = core_mem_rom_fetch;
  assign mem_addr = core_mem_addr;
  assign mem_wdata = core_mem_wdata;
  assign mem_wstrb = core_mem_wmask;
  assign core_mem_rdata = mem_rdata;
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
    end else if (clear) begin
      commit_index <= 32'h0;
    end else if (commit_valid) begin
      commit_index <= commit_index + 32'h1;
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      irq_line_q <= 1'b0;
    end else if (clear) begin
      irq_line_q <= 1'b0;
    end else begin
      irq_line_q <= irq_line;
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
    .mem_rdata(core_mem_rdata),
    .mem_rstrb(core_mem_rstrb),
    .mem_rbusy(core_mem_rbusy),
    .mem_wbusy(core_mem_wbusy),
    .reset(rst_n)
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
    .commit_valid(commit_valid),
    .commit_pc(core_mem_addr),
    .commit_instr(core_mem_rdata),
    .commit_index(commit_index),
    .branch_taken(1'b0),
    .jump_taken(1'b0),
    .mem_valid(mem_accepted),
    .mem_write(core_mem_write),
    .mem_addr(core_mem_addr),
    .mem_wdata(core_mem_wdata),
    .mem_rdata(core_mem_rdata),
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
