`timescale 1ns/1ps
`include "../../rtl/event_pkg.sv"

module tb_capsule_buffer;
  import replaycapsule_event_pkg::*;

  localparam int DEPTH = 4;
  localparam int ADDR_W = 2;

  logic clk;
  logic rst_n;
  logic clear;
  logic event_valid;
  logic [RC_EVENT_WIDTH-1:0] event_packet;
  logic fail_freeze;
  logic [ADDR_W-1:0] read_addr;
  logic [RC_EVENT_WIDTH-1:0] read_data;
  logic frozen;
  logic overflow;
  logic [ADDR_W:0] write_count;

  capsule_buffer #(
    .EVENT_WIDTH(RC_EVENT_WIDTH),
    .DEPTH(DEPTH),
    .ADDR_W(ADDR_W)
  ) u_capsule_buffer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(event_valid),
    .event_packet(event_packet),
    .fail_freeze(fail_freeze),
    .read_addr(read_addr),
    .read_data(read_data),
    .frozen(frozen),
    .overflow(overflow),
    .write_count(write_count)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    event_valid = 1'b0;
    event_packet = '0;
    fail_freeze = 1'b0;
    read_addr = '0;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);

    push_packet(32'd0);
    #1;
    if (write_count != 3'd1) begin
      $fatal(1, "capsule buffer did not accept first packet");
    end

    @(posedge clk);
    fail_freeze <= 1'b1;
    @(posedge clk);
    fail_freeze <= 1'b0;
    #1;
    if (!frozen) begin
      $fatal(1, "capsule buffer did not freeze");
    end

    push_packet(32'd1);
    #1;
    if (write_count != 3'd1) begin
      $fatal(1, "frozen capsule buffer accepted a later packet");
    end

    $finish;
  end

  task automatic push_packet(input logic [31:0] event_id);
    begin
      @(posedge clk);
      event_packet <= rc_pack_event(EV_COMMIT, 4'h0, event_id, event_id, 32'h80, 32'h0, 32'h13);
      event_valid <= 1'b1;
      @(posedge clk);
      event_valid <= 1'b0;
    end
  endtask
endmodule
