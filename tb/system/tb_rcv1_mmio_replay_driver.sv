`timescale 1ns/1ps

module tb_rcv1_mmio_replay_driver;
  localparam int EVENT_WIDTH = 168;
  localparam int DEPTH = 8;
  localparam int ADDR_W = 3;

  logic clk;
  logic rst_n;
  logic store_clear;
  logic load_valid;
  logic [ADDR_W-1:0] load_addr;
  logic [EVENT_WIDTH-1:0] load_packet;
  logic replay_enable;
  logic observed_valid;
  logic observed_mmio_read;
  logic [31:0] observed_addr;
  logic replay_valid;
  logic [31:0] replay_value;
  logic [31:0] loaded_count;
  logic [31:0] hit_count;
  logic replay_miss;

  rcv1_mmio_replay_driver #(
    .DEPTH(DEPTH),
    .ADDR_W(ADDR_W),
    .EVENT_WIDTH(EVENT_WIDTH)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .store_clear(store_clear),
    .load_valid(load_valid),
    .load_addr(load_addr),
    .load_packet(load_packet),
    .replay_enable(replay_enable),
    .observed_valid(observed_valid),
    .observed_mmio_read(observed_mmio_read),
    .observed_addr(observed_addr),
    .replay_valid(replay_valid),
    .replay_value(replay_value),
    .loaded_count(loaded_count),
    .hit_count(hit_count),
    .replay_miss(replay_miss)
  );

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  function automatic logic [EVENT_WIDTH-1:0] pkt(
    input logic [3:0] event_type,
    input logic [31:0] addr,
    input logic [31:0] data
  );
    begin
      pkt = {event_type, 4'h0, 32'h0, 32'h4, 32'h80, addr, data};
    end
  endfunction

  task automatic load_one;
    input logic [ADDR_W-1:0] addr;
    input logic [EVENT_WIDTH-1:0] packet;
    begin
      @(negedge clk);
      load_addr = addr;
      load_packet = packet;
      load_valid = 1'b1;
      @(posedge clk);
      @(negedge clk);
      load_valid = 1'b0;
    end
  endtask

  task automatic observe_read;
    input logic [31:0] addr;
    begin
      @(negedge clk);
      observed_addr = addr;
      observed_mmio_read = 1'b1;
      observed_valid = 1'b1;
      @(posedge clk);
      @(negedge clk);
      observed_valid = 1'b0;
      observed_mmio_read = 1'b0;
    end
  endtask

  initial begin
    rst_n = 1'b0;
    store_clear = 1'b0;
    load_valid = 1'b0;
    load_addr = '0;
    load_packet = '0;
    replay_enable = 1'b0;
    observed_valid = 1'b0;
    observed_mmio_read = 1'b0;
    observed_addr = 32'h0;
    repeat (2) @(posedge clk);
    rst_n = 1'b1;

    load_one(3'd0, pkt(4'h5, 32'h4000_0000, 32'd850));
    load_one(3'd1, pkt(4'h6, 32'h4000_0004, 32'd1));
    load_one(3'd2, pkt(4'h5, 32'h4000_000c, 32'd85));
    if (loaded_count != 32'd3) begin
      $fatal(1, "expected loaded_count=3 got %0d", loaded_count);
    end

    replay_enable = 1'b1;
    observed_addr = 32'h4000_0000;
    observed_mmio_read = 1'b1;
    observed_valid = 1'b1;
    #1;
    if (!replay_valid || replay_value != 32'd850) begin
      $fatal(1, "sensor replay lookup failed valid=%0b value=%0d", replay_valid, replay_value);
    end
    @(posedge clk);
    @(negedge clk);
    observed_valid = 1'b0;
    observed_mmio_read = 1'b0;

    observe_read(32'h4000_000c);
    if (hit_count != 32'd2) begin
      $fatal(1, "expected two replay hits, got %0d", hit_count);
    end

    observe_read(32'h4000_0040);
    if (!replay_miss) begin
      $fatal(1, "expected miss for uncaptured MMIO address");
    end

    store_clear = 1'b1;
    @(posedge clk);
    @(negedge clk);
    store_clear = 1'b0;
    if (loaded_count != 32'd0 || hit_count != 32'd0 || replay_miss) begin
      $fatal(1, "store_clear did not reset driver state");
    end

    $display("RCV1_MMIO_REPLAY_DRIVER_PASS");
    $finish;
  end
endmodule
