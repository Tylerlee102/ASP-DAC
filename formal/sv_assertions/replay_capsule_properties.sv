`include "../../rtl/event_pkg.sv"

module replay_capsule_properties #(
  parameter int EVENT_WIDTH = replaycapsule_event_pkg::RC_EVENT_WIDTH
) (
  input logic clk,
  input logic rst_n,
  input logic clear,
  input logic event_valid,
  input logic [EVENT_WIDTH-1:0] event_packet,
  input logic capsule_frozen,
  input logic capsule_overflow,
  input logic property_fail_valid,
  input logic replay_enable,
  input logic replay_event_valid,
  input logic replay_event_consume
);
  import replaycapsule_event_pkg::*;

  logic [31:0] previous_event_id;
  logic previous_valid;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      previous_event_id <= 32'h0;
      previous_valid <= 1'b0;
    end else if (clear) begin
      previous_event_id <= 32'h0;
      previous_valid <= 1'b0;
    end else if (event_valid && !capsule_frozen) begin
      if (previous_valid) begin
        assert (rc_get_event_id(event_packet) >= previous_event_id);
      end
      previous_event_id <= rc_get_event_id(event_packet);
      previous_valid <= 1'b1;
    end
  end

  property fail_freezes_capsule;
    @(posedge clk) disable iff (!rst_n || clear)
      property_fail_valid |=> capsule_frozen;
  endproperty
  assert property (fail_freezes_capsule);

  property frozen_blocks_new_events;
    @(posedge clk) disable iff (!rst_n || clear)
      capsule_frozen && event_valid |=> capsule_frozen;
  endproperty
  assert property (frozen_blocks_new_events);

  property overflow_is_sticky;
    @(posedge clk) disable iff (!rst_n || clear)
      capsule_overflow |=> capsule_overflow;
  endproperty
  assert property (overflow_is_sticky);

  property replay_never_consumes_missing_event;
    @(posedge clk) disable iff (!rst_n || clear)
      replay_enable && replay_event_consume |-> replay_event_valid;
  endproperty
  assert property (replay_never_consumes_missing_event);
endmodule

