`timescale 1ns/1ps

module tb_registers;
  localparam logic [31:0] BASE_ADDR = 32'h4001_0000;
  localparam logic [31:0] REG_CONTROL = BASE_ADDR + 32'h00;
  localparam logic [31:0] REG_STATUS = BASE_ADDR + 32'h04;
  localparam logic [31:0] REG_COUNT = BASE_ADDR + 32'h08;
  localparam logic [31:0] REG_SIG = BASE_ADDR + 32'h0c;

  logic clk;
  logic rst_n;
  logic clear;
  logic bus_valid;
  logic bus_write;
  logic [31:0] bus_addr;
  logic [31:0] bus_wdata;
  logic bus_ready;
  logic [31:0] bus_rdata;
  logic capsule_frozen;
  logic capsule_overflow;
  logic [31:0] event_count;
  logic [31:0] failure_signature;
  logic [3:0] capture_mode;
  logic capsule_clear;
  logic replay_enable;

  registers #(
    .BASE_ADDR(BASE_ADDR)
  ) u_registers (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .bus_valid(bus_valid),
    .bus_write(bus_write),
    .bus_addr(bus_addr),
    .bus_wdata(bus_wdata),
    .bus_ready(bus_ready),
    .bus_rdata(bus_rdata),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .event_count(event_count),
    .failure_signature(failure_signature),
    .capture_mode(capture_mode),
    .capsule_clear(capsule_clear),
    .replay_enable(replay_enable)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    bus_valid = 1'b0;
    bus_write = 1'b0;
    bus_addr = 32'h0;
    bus_wdata = 32'h0;
    capsule_frozen = 1'b1;
    capsule_overflow = 1'b1;
    event_count = 32'd37;
    failure_signature = 32'habcd_1234;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);
    #1;
    if (capture_mode != 4'h3 || replay_enable || capsule_clear) begin
      $fatal(1, "register reset defaults were incorrect");
    end

    read_reg(32'h4002_0000, 32'h0, 1'b0, "unselected read should not respond");
    read_reg(REG_STATUS, 32'h3, 1'b1, "status register read was incorrect");
    read_reg(REG_COUNT, event_count, 1'b1, "event-count register read was incorrect");
    read_reg(REG_SIG, failure_signature, 1'b1, "failure-signature register read was incorrect");

    bus_valid = 1'b1;
    bus_write = 1'b1;
    bus_addr = REG_CONTROL;
    bus_wdata = 32'h0000_0112;
    @(posedge clk);
    #1;
    if (capture_mode != 4'h2 || !replay_enable || !capsule_clear) begin
      $fatal(1, "control register write did not update mode, replay, and clear pulse");
    end

    bus_valid = 1'b0;
    @(posedge clk);
    #1;
    if (capture_mode != 4'h2 || !replay_enable || capsule_clear) begin
      $fatal(1, "capsule_clear did not pulse for exactly one cycle after control write");
    end

    read_reg(REG_CONTROL, 32'h12, 1'b1, "control register readback was incorrect");

    bus_valid = 1'b1;
    bus_write = 1'b1;
    bus_addr = REG_STATUS;
    bus_wdata = 32'hffff_ffff;
    @(posedge clk);
    #1;
    bus_valid = 1'b0;
    if (capture_mode != 4'h2 || !replay_enable || capsule_clear) begin
      $fatal(1, "write to non-control register changed writable control state");
    end

    clear = 1'b1;
    @(posedge clk);
    #1;
    if (capture_mode != 4'h3 || replay_enable || !capsule_clear) begin
      $fatal(1, "global clear did not restore defaults and pulse capsule clear");
    end

    clear = 1'b0;
    @(posedge clk);
    #1;
    if (capsule_clear) begin
      $fatal(1, "capsule_clear remained asserted after global clear deasserted");
    end

    $finish;
  end

  task automatic read_reg(
    input logic [31:0] addr,
    input logic [31:0] expected_data,
    input logic expected_ready,
    input string message
  );
    begin
      bus_valid = 1'b1;
      bus_write = 1'b0;
      bus_addr = addr;
      #1;
      if (bus_ready != expected_ready || bus_rdata != expected_data) begin
        $fatal(1, "%s: ready=%0b data=%08x", message, bus_ready, bus_rdata);
      end
      bus_valid = 1'b0;
      #1;
    end
  endtask
endmodule
