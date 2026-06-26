`timescale 1ns/1ps
`include "../../rtl/event_pkg.sv"

module tb_hash_signature;
  import replaycapsule_event_pkg::*;

  localparam logic [31:0] RESET_SEED = 32'h5243_5256;

  logic clk;
  logic rst_n;
  logic clear;
  logic event_valid;
  logic [RC_EVENT_WIDTH-1:0] event_packet;
  logic [31:0] signature;

  hash_signature #(
    .EVENT_WIDTH(RC_EVENT_WIDTH),
    .RESET_SEED(RESET_SEED)
  ) u_hash_signature (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(event_valid),
    .event_packet(event_packet),
    .signature(signature)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    event_valid = 1'b0;
    event_packet = '0;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);
    #1;
    expect_signature(RESET_SEED, "reset seed was not visible after reset release");

    event_packet = '1;
    @(posedge clk);
    #1;
    expect_signature(RESET_SEED, "signature changed while event_valid was low");

    event_packet = rc_pack_event(EV_MMIO_READ, 4'h0, 32'd1, 32'd7, 32'h80, 32'h4000_0000, 32'h1234_5678);
    event_valid = 1'b1;
    @(posedge clk);
    #1;
    expect_signature(32'h8469_65dd, "first packet signature update was incorrect");

    event_packet = rc_pack_event(EV_MMIO_WRITE, 4'h0, 32'd2, 32'd8, 32'h84, 32'h2000_0000, 32'haaaa_aaaa);
    @(posedge clk);
    #1;
    expect_signature(32'h99b1_684d, "second packet signature update was incorrect");

    clear = 1'b1;
    event_valid = 1'b1;
    event_packet = '0;
    @(posedge clk);
    #1;
    expect_signature(RESET_SEED, "clear did not reset signature before event update");

    clear = 1'b0;
    @(posedge clk);
    #1;
    expect_signature(32'hd65d_3373, "zero-packet signature update after clear was incorrect");

    $finish;
  end

  task automatic expect_signature(input logic [31:0] expected, input string message);
    begin
      if (signature !== expected) begin
        $fatal(1, "%s: got %08x expected %08x", message, signature, expected);
      end
    end
  endtask
endmodule
