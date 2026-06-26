`include "event_pkg.sv"

module replay_control #(
  parameter int EVENT_WIDTH = replaycapsule_event_pkg::RC_EVENT_WIDTH
) (
  input  logic                   clk,
  input  logic                   rst_n,
  input  logic                   clear,
  input  logic                   replay_enable,
  input  logic                   commit_index_mode,
  input  logic [31:0]            current_cycle,
  input  logic [31:0]            current_commit_index,

  input  logic                   replay_event_valid,
  input  logic [EVENT_WIDTH-1:0] replay_event_packet,
  output logic                   replay_event_consume,

  output logic                   inject_mmio_valid,
  output logic [31:0]            inject_mmio_value,
  output logic                   inject_interrupt_enter,
  output logic                   inject_interrupt_exit,
  output logic                   replay_underflow
);
  `include "event_defs.svh"

  logic [3:0] replay_type;
  logic [31:0] replay_time;
  logic [31:0] replay_data;
  logic time_match;

  assign replay_type = rc_get_type(replay_event_packet);
  assign replay_time = commit_index_mode ? rc_get_commit_index(replay_event_packet) : rc_get_event_id(replay_event_packet);
  assign replay_data = rc_get_data(replay_event_packet);
  assign time_match = commit_index_mode ? (replay_time == current_commit_index) : (replay_time == current_cycle);

  always_comb begin
    replay_event_consume = 1'b0;
    inject_mmio_valid = 1'b0;
    inject_mmio_value = 32'h0;
    inject_interrupt_enter = 1'b0;
    inject_interrupt_exit = 1'b0;

    if (replay_enable && replay_event_valid && time_match) begin
      unique case (replay_type)
        EV_MMIO_READ,
        EV_EXTERNAL_INPUT: begin
          replay_event_consume = 1'b1;
          inject_mmio_valid = 1'b1;
          inject_mmio_value = replay_data;
        end
        EV_INTERRUPT_ENTER: begin
          replay_event_consume = 1'b1;
          inject_interrupt_enter = 1'b1;
        end
        EV_INTERRUPT_EXIT: begin
          replay_event_consume = 1'b1;
          inject_interrupt_exit = 1'b1;
        end
        default: begin
          replay_event_consume = 1'b0;
        end
      endcase
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      replay_underflow <= 1'b0;
    end else if (clear) begin
      replay_underflow <= 1'b0;
    end else if (replay_enable && !replay_event_valid) begin
      replay_underflow <= 1'b1;
    end
  end
endmodule
