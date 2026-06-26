`default_nettype none

module replay_control_bmc_harness (
  input logic clk
);
  `include "../../rtl/event_defs.svh"

  localparam int FORMAL_EVENT_WIDTH = RC_EVENT_WIDTH;

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic clear_any;
  (* anyseq *) logic replay_enable;
  (* anyseq *) logic commit_index_mode;
  (* anyseq *) logic [31:0] current_cycle;
  (* anyseq *) logic [31:0] current_commit_index;
  (* anyseq *) logic replay_event_valid;
  (* anyseq *) logic [FORMAL_EVENT_WIDTH-1:0] replay_event_packet;

  logic clear;
  logic replay_event_consume;
  logic inject_mmio_valid;
  logic [31:0] inject_mmio_value;
  logic inject_interrupt_enter;
  logic inject_interrupt_exit;
  logic replay_underflow;

  assign clear = rst_n && clear_any;

  replay_control #(
    .EVENT_WIDTH(FORMAL_EVENT_WIDTH)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .replay_enable(replay_enable),
    .commit_index_mode(commit_index_mode),
    .current_cycle(current_cycle),
    .current_commit_index(current_commit_index),
    .replay_event_valid(replay_event_valid),
    .replay_event_packet(replay_event_packet),
    .replay_event_consume(replay_event_consume),
    .inject_mmio_valid(inject_mmio_valid),
    .inject_mmio_value(inject_mmio_value),
    .inject_interrupt_enter(inject_interrupt_enter),
    .inject_interrupt_exit(inject_interrupt_exit),
    .replay_underflow(replay_underflow)
  );

  logic [3:0] packet_type;
  logic [31:0] packet_time;
  logic [31:0] packet_data;
  logic time_match;
  logic past_valid = 1'b0;

  assign packet_type = rc_get_type(replay_event_packet);
  assign packet_time = commit_index_mode ? rc_get_commit_index(replay_event_packet) : rc_get_event_id(replay_event_packet);
  assign packet_data = rc_get_data(replay_event_packet);
  assign time_match = commit_index_mode ? (packet_time == current_commit_index) : (packet_time == current_cycle);

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;

    if (rst_n) begin
      if (!replay_enable || !replay_event_valid || !time_match) begin
        assert(!replay_event_consume);
        assert(!inject_mmio_valid);
        assert(!inject_interrupt_enter);
        assert(!inject_interrupt_exit);
      end else if (packet_type == EV_MMIO_READ || packet_type == EV_EXTERNAL_INPUT) begin
        assert(replay_event_consume);
        assert(inject_mmio_valid);
        assert(inject_mmio_value == packet_data);
        assert(!inject_interrupt_enter);
        assert(!inject_interrupt_exit);
      end else if (packet_type == EV_INTERRUPT_ENTER) begin
        assert(replay_event_consume);
        assert(!inject_mmio_valid);
        assert(inject_interrupt_enter);
        assert(!inject_interrupt_exit);
      end else if (packet_type == EV_INTERRUPT_EXIT) begin
        assert(replay_event_consume);
        assert(!inject_mmio_valid);
        assert(!inject_interrupt_enter);
        assert(inject_interrupt_exit);
      end else begin
        assert(!replay_event_consume);
        assert(!inject_mmio_valid);
        assert(!inject_interrupt_enter);
        assert(!inject_interrupt_exit);
      end
    end

    if (past_valid && rst_n && $past(rst_n)) begin
      if ($past(clear)) begin
        assert(!replay_underflow);
      end

      if (!clear && !$past(clear)) begin
        if ($past(replay_enable) && !$past(replay_event_valid)) begin
          assert(replay_underflow);
        end

        if ($past(replay_underflow)) begin
          assert(replay_underflow);
        end
      end
    end

    cover(rst_n && replay_enable && replay_event_valid && time_match && packet_type == EV_MMIO_READ && inject_mmio_valid);
    cover(rst_n && replay_enable && replay_event_valid && time_match && packet_type == EV_INTERRUPT_ENTER && inject_interrupt_enter);
    cover(rst_n && replay_underflow);
  end
endmodule

`default_nettype wire
