`default_nettype none

module event_tap_bmc_harness (
  input logic clk
);
  `include "../../rtl/event_defs.svh"

  localparam logic [31:0] MMIO_BASE = 32'h4000_0000;
  localparam logic [31:0] MMIO_MASK = 32'hffff_0000;

  (* anyseq *) logic rst_n;
  (* anyseq *) logic commit_valid;
  (* anyseq *) logic [31:0] commit_pc;
  (* anyseq *) logic [31:0] commit_instr;
  (* anyseq *) logic [31:0] commit_index;
  (* anyseq *) logic branch_taken;
  (* anyseq *) logic jump_taken;
  (* anyseq *) logic mem_valid;
  (* anyseq *) logic mem_write;
  (* anyseq *) logic [31:0] mem_addr;
  (* anyseq *) logic [31:0] mem_wdata;
  (* anyseq *) logic [31:0] mem_rdata;
  (* anyseq *) logic external_input_valid;
  (* anyseq *) logic [31:0] external_input_value;
  (* anyseq *) logic interrupt_enter;
  (* anyseq *) logic interrupt_exit;

  logic event_valid;
  logic [3:0] event_type;
  logic [31:0] event_commit_index;
  logic [31:0] event_pc;
  logic [31:0] event_addr;
  logic [31:0] event_data;
  logic multievent_pending;
  logic is_mmio;
  logic [4:0] candidate_count;

  assign is_mmio = (mem_addr & MMIO_MASK) == (MMIO_BASE & MMIO_MASK);

  always_comb begin
    candidate_count = 5'd0;
    candidate_count = candidate_count + (commit_valid ? 5'd1 : 5'd0);
    candidate_count = candidate_count + ((commit_valid && branch_taken) ? 5'd1 : 5'd0);
    candidate_count = candidate_count + ((commit_valid && jump_taken) ? 5'd1 : 5'd0);
    candidate_count = candidate_count + (mem_valid ? 5'd1 : 5'd0);
    candidate_count = candidate_count + (external_input_valid ? 5'd1 : 5'd0);
    candidate_count = candidate_count + (interrupt_enter ? 5'd1 : 5'd0);
    candidate_count = candidate_count + (interrupt_exit ? 5'd1 : 5'd0);
  end

  event_tap #(
    .MMIO_BASE(MMIO_BASE),
    .MMIO_MASK(MMIO_MASK)
  ) dut (
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
    .event_valid(event_valid),
    .event_type(event_type),
    .event_commit_index(event_commit_index),
    .event_pc(event_pc),
    .event_addr(event_addr),
    .event_data(event_data),
    .multievent_pending(multievent_pending)
  );

  always_ff @(posedge clk) begin
    assert(multievent_pending == (candidate_count > 5'd1));
    assert(event_commit_index == commit_index);
    assert(event_pc == commit_pc);

    if (interrupt_enter) begin
      assert(event_valid);
      assert(event_type == EV_INTERRUPT_ENTER);
      assert(event_data == 32'h1);
    end else if (interrupt_exit) begin
      assert(event_valid);
      assert(event_type == EV_INTERRUPT_EXIT);
      assert(event_data == 32'h0);
    end else if (external_input_valid) begin
      assert(event_valid);
      assert(event_type == EV_EXTERNAL_INPUT);
      assert(event_data == external_input_value);
    end else if (mem_valid && is_mmio && !mem_write) begin
      assert(event_valid);
      assert(event_type == EV_MMIO_READ);
      assert(event_addr == mem_addr);
      assert(event_data == mem_rdata);
    end else if (mem_valid && is_mmio && mem_write) begin
      assert(event_valid);
      assert(event_type == EV_MMIO_WRITE);
      assert(event_addr == mem_addr);
      assert(event_data == mem_wdata);
    end else if (mem_valid && mem_write) begin
      assert(event_valid);
      assert(event_type == EV_STORE);
      assert(event_addr == mem_addr);
      assert(event_data == mem_wdata);
    end else if (mem_valid && !mem_write) begin
      assert(event_valid);
      assert(event_type == EV_LOAD);
      assert(event_addr == mem_addr);
      assert(event_data == mem_rdata);
    end else if (commit_valid && branch_taken) begin
      assert(event_valid);
      assert(event_type == EV_BRANCH);
      assert(event_data == commit_instr);
    end else if (commit_valid && jump_taken) begin
      assert(event_valid);
      assert(event_type == EV_JUMP);
      assert(event_data == commit_instr);
    end else if (commit_valid) begin
      assert(event_valid);
      assert(event_type == EV_COMMIT);
      assert(event_data == commit_instr);
    end else begin
      assert(!event_valid);
    end

    cover(interrupt_enter && event_valid && event_type == EV_INTERRUPT_ENTER);
    cover(mem_valid && is_mmio && !mem_write && event_valid && event_type == EV_MMIO_READ);
    cover(mem_valid && !is_mmio && mem_write && event_valid && event_type == EV_STORE);
    cover(commit_valid && branch_taken && event_valid && event_type == EV_BRANCH);
    cover(multievent_pending);
  end

  logic unused_rst_n;
  assign unused_rst_n = rst_n;
endmodule

`default_nettype wire
