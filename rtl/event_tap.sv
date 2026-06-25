`include "event_pkg.sv"

module event_tap #(
  parameter logic [31:0] MMIO_BASE = 32'h4000_0000,
  parameter logic [31:0] MMIO_MASK = 32'hffff_0000
) (
  input  logic        clk,
  input  logic        rst_n,

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

  output logic        event_valid,
  output logic [3:0]  event_type,
  output logic [31:0] event_commit_index,
  output logic [31:0] event_pc,
  output logic [31:0] event_addr,
  output logic [31:0] event_data,
  output logic        multievent_pending
);
  import replaycapsule_event_pkg::*;

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

  assign multievent_pending = candidate_count > 5'd1;

  always_comb begin
    event_valid        = 1'b0;
    event_type         = EV_COMMIT;
    event_commit_index = commit_index;
    event_pc           = commit_pc;
    event_addr         = 32'h0;
    event_data         = commit_instr;

    if (interrupt_enter) begin
      event_valid = 1'b1;
      event_type  = EV_INTERRUPT_ENTER;
      event_data  = 32'h1;
    end else if (interrupt_exit) begin
      event_valid = 1'b1;
      event_type  = EV_INTERRUPT_EXIT;
      event_data  = 32'h0;
    end else if (external_input_valid) begin
      event_valid = 1'b1;
      event_type  = EV_EXTERNAL_INPUT;
      event_data  = external_input_value;
    end else if (mem_valid && is_mmio && !mem_write) begin
      event_valid = 1'b1;
      event_type  = EV_MMIO_READ;
      event_addr  = mem_addr;
      event_data  = mem_rdata;
    end else if (mem_valid && is_mmio && mem_write) begin
      event_valid = 1'b1;
      event_type  = EV_MMIO_WRITE;
      event_addr  = mem_addr;
      event_data  = mem_wdata;
    end else if (mem_valid && mem_write) begin
      event_valid = 1'b1;
      event_type  = EV_STORE;
      event_addr  = mem_addr;
      event_data  = mem_wdata;
    end else if (mem_valid && !mem_write) begin
      event_valid = 1'b1;
      event_type  = EV_LOAD;
      event_addr  = mem_addr;
      event_data  = mem_rdata;
    end else if (commit_valid && branch_taken) begin
      event_valid = 1'b1;
      event_type  = EV_BRANCH;
      event_data  = commit_instr;
    end else if (commit_valid && jump_taken) begin
      event_valid = 1'b1;
      event_type  = EV_JUMP;
      event_data  = commit_instr;
    end else if (commit_valid) begin
      event_valid = 1'b1;
      event_type  = EV_COMMIT;
      event_data  = commit_instr;
    end
  end

  logic unused_clk;
  logic unused_rst_n;
  assign unused_clk = clk;
  assign unused_rst_n = rst_n;
endmodule

