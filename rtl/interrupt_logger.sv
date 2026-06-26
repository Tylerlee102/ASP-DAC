`include "event_pkg.sv"

module interrupt_logger (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        trap_enter,
  input  logic        trap_exit,
  input  logic [31:0] commit_index,
  input  logic [31:0] pc,

  output logic        event_valid,
  output logic [3:0]  event_type,
  output logic [31:0] event_commit_index,
  output logic [31:0] event_pc,
  output logic [31:0] event_data,
  output logic        unpaired_exit,
  output logic [7:0]  active_depth
);
  `include "event_defs.svh"

  always_comb begin
    event_valid = trap_enter || trap_exit;
    event_type = trap_enter ? EV_INTERRUPT_ENTER : EV_INTERRUPT_EXIT;
    event_commit_index = commit_index;
    event_pc = pc;
    event_data = {24'h0, active_depth};
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active_depth <= 8'h0;
      unpaired_exit <= 1'b0;
    end else if (clear) begin
      active_depth <= 8'h0;
      unpaired_exit <= 1'b0;
    end else begin
      if (trap_enter && !trap_exit) begin
        active_depth <= active_depth + 8'h1;
      end else if (trap_exit && !trap_enter) begin
        if (active_depth == 8'h0) begin
          unpaired_exit <= 1'b1;
        end else begin
          active_depth <= active_depth - 8'h1;
        end
      end
    end
  end
endmodule
