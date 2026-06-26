`timescale 1ns/1ps
`include "../../rtl/event_pkg.sv"

module tb_replay_control;
  import replaycapsule_event_pkg::*;

  logic clk;
  logic rst_n;
  logic clear;
  logic replay_enable;
  logic commit_index_mode;
  logic [31:0] current_cycle;
  logic [31:0] current_commit_index;
  logic replay_event_valid;
  logic [RC_EVENT_WIDTH-1:0] replay_event_packet;
  logic replay_event_consume;
  logic inject_mmio_valid;
  logic [31:0] inject_mmio_value;
  logic inject_interrupt_enter;
  logic inject_interrupt_exit;
  logic replay_underflow;

  replay_control #(
    .EVENT_WIDTH(RC_EVENT_WIDTH)
  ) u_replay_control (
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

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    replay_enable = 1'b0;
    commit_index_mode = 1'b1;
    current_cycle = 32'h0;
    current_commit_index = 32'h0;
    replay_event_valid = 1'b0;
    replay_event_packet = '0;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);

    replay_enable = 1'b1;
    commit_index_mode = 1'b1;
    current_commit_index = 32'd7;
    current_cycle = 32'd11;
    replay_event_valid = 1'b1;
    replay_event_packet = rc_pack_event(EV_MMIO_READ, 4'h0, 32'd1, 32'd7, 32'h80, 32'h4000_0000, 32'h1234_5678);
    #1;
    expect_mmio_value(32'h1234_5678, "commit-index MMIO replay did not inject read data");

    current_commit_index = 32'd8;
    #1;
    expect_idle("mismatched commit index consumed a replay event");

    commit_index_mode = 1'b0;
    current_cycle = 32'd42;
    replay_event_packet = rc_pack_event(EV_INTERRUPT_ENTER, 4'h0, 32'd42, 32'd9, 32'h80, 32'h0, 32'h0);
    #1;
    if (!replay_event_consume || !inject_interrupt_enter || inject_interrupt_exit || inject_mmio_valid) begin
      $fatal(1, "cycle-mode interrupt-enter replay did not inject exactly one enter pulse");
    end

    replay_event_packet = rc_pack_event(EV_INTERRUPT_EXIT, 4'h0, 32'd42, 32'd9, 32'h80, 32'h0, 32'h0);
    #1;
    if (!replay_event_consume || inject_interrupt_enter || !inject_interrupt_exit || inject_mmio_valid) begin
      $fatal(1, "cycle-mode interrupt-exit replay did not inject exactly one exit pulse");
    end

    replay_event_packet = rc_pack_event(EV_STORE, 4'h0, 32'd42, 32'd9, 32'h80, 32'h2000_0000, 32'hffff_ffff);
    #1;
    expect_idle("non-injectable event type was consumed");

    replay_enable = 1'b0;
    replay_event_packet = rc_pack_event(EV_EXTERNAL_INPUT, 4'h0, 32'd42, 32'd9, 32'h80, 32'h4000_0000, 32'h0000_00aa);
    #1;
    expect_idle("disabled replay injected an event");

    replay_enable = 1'b1;
    replay_event_valid = 1'b0;
    @(posedge clk);
    #1;
    if (!replay_underflow) begin
      $fatal(1, "replay underflow did not become sticky when enabled stream was empty");
    end

    clear = 1'b1;
    @(posedge clk);
    #1;
    if (replay_underflow) begin
      $fatal(1, "clear did not reset replay underflow");
    end

    $finish;
  end

  task automatic expect_mmio_value(input logic [31:0] expected, input string message);
    begin
      if (!replay_event_consume || !inject_mmio_valid || inject_mmio_value != expected ||
          inject_interrupt_enter || inject_interrupt_exit) begin
        $fatal(1, "%s", message);
      end
    end
  endtask

  task automatic expect_idle(input string message);
    begin
      if (replay_event_consume || inject_mmio_valid || inject_interrupt_enter || inject_interrupt_exit) begin
        $fatal(1, "%s", message);
      end
    end
  endtask
endmodule
