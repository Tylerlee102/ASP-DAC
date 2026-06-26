`timescale 1ns/1ps
`include "../../rtl/event_pkg.sv"

module tb_mmio_interrupt_loggers;
  import replaycapsule_event_pkg::*;

  logic clk;
  logic rst_n;
  logic clear;

  logic bus_valid;
  logic bus_write;
  logic [31:0] bus_addr;
  logic [31:0] bus_wdata;
  logic [31:0] bus_rdata;
  logic [31:0] mmio_commit_index;
  logic [31:0] mmio_pc;
  logic mmio_event_valid;
  logic [3:0] mmio_event_type;
  logic [31:0] mmio_event_commit_index;
  logic [31:0] mmio_event_pc;
  logic [31:0] mmio_event_addr;
  logic [31:0] mmio_event_data;

  logic trap_enter;
  logic trap_exit;
  logic [31:0] irq_commit_index;
  logic [31:0] irq_pc;
  logic irq_event_valid;
  logic [3:0] irq_event_type;
  logic [31:0] irq_event_commit_index;
  logic [31:0] irq_event_pc;
  logic [31:0] irq_event_data;
  logic unpaired_exit;
  logic [7:0] active_depth;

  mmio_logger u_mmio_logger (
    .bus_valid(bus_valid),
    .bus_write(bus_write),
    .bus_addr(bus_addr),
    .bus_wdata(bus_wdata),
    .bus_rdata(bus_rdata),
    .commit_index(mmio_commit_index),
    .pc(mmio_pc),
    .event_valid(mmio_event_valid),
    .event_type(mmio_event_type),
    .event_commit_index(mmio_event_commit_index),
    .event_pc(mmio_event_pc),
    .event_addr(mmio_event_addr),
    .event_data(mmio_event_data)
  );

  interrupt_logger u_interrupt_logger (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .trap_enter(trap_enter),
    .trap_exit(trap_exit),
    .commit_index(irq_commit_index),
    .pc(irq_pc),
    .event_valid(irq_event_valid),
    .event_type(irq_event_type),
    .event_commit_index(irq_event_commit_index),
    .event_pc(irq_event_pc),
    .event_data(irq_event_data),
    .unpaired_exit(unpaired_exit),
    .active_depth(active_depth)
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
    bus_rdata = 32'h0;
    mmio_commit_index = 32'd11;
    mmio_pc = 32'h0000_0080;
    trap_enter = 1'b0;
    trap_exit = 1'b0;
    irq_commit_index = 32'd21;
    irq_pc = 32'h0000_0100;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);
    #1;
    if (active_depth != 8'h0 || unpaired_exit) begin
      $fatal(1, "interrupt logger did not reset depth and unpaired-exit flag");
    end

    bus_valid = 1'b1;
    bus_write = 1'b0;
    bus_addr = 32'h2000_0004;
    bus_rdata = 32'h1234_5678;
    #1;
    if (mmio_event_valid) begin
      $fatal(1, "non-MMIO bus read produced an MMIO event");
    end

    bus_addr = 32'h4000_0004;
    #1;
    expect_mmio(EV_MMIO_READ, bus_addr, bus_rdata, "MMIO read event was incorrect");

    bus_write = 1'b1;
    bus_wdata = 32'hdead_beef;
    #1;
    expect_mmio(EV_MMIO_WRITE, bus_addr, bus_wdata, "MMIO write event was incorrect");

    trap_enter = 1'b1;
    #1;
    expect_irq(EV_INTERRUPT_ENTER, 32'h0, "interrupt enter event was incorrect");
    @(posedge clk);
    #1;
    trap_enter = 1'b0;
    if (active_depth != 8'd1 || unpaired_exit) begin
      $fatal(1, "interrupt enter did not increment active depth");
    end

    trap_exit = 1'b1;
    #1;
    expect_irq(EV_INTERRUPT_EXIT, 32'h1, "interrupt exit event did not report current active depth");
    @(posedge clk);
    #1;
    trap_exit = 1'b0;
    if (active_depth != 8'd0 || unpaired_exit) begin
      $fatal(1, "paired interrupt exit did not decrement active depth cleanly");
    end

    trap_exit = 1'b1;
    @(posedge clk);
    #1;
    trap_exit = 1'b0;
    if (!unpaired_exit || active_depth != 8'd0) begin
      $fatal(1, "unpaired interrupt exit was not detected");
    end

    clear = 1'b1;
    @(posedge clk);
    #1;
    clear = 1'b0;
    if (unpaired_exit || active_depth != 8'd0) begin
      $fatal(1, "clear did not reset interrupt logger state");
    end

    $finish;
  end

  task automatic expect_mmio(
    input logic [3:0] expected_type,
    input logic [31:0] expected_addr,
    input logic [31:0] expected_data,
    input string message
  );
    begin
      if (!mmio_event_valid ||
          mmio_event_type != expected_type ||
          mmio_event_commit_index != mmio_commit_index ||
          mmio_event_pc != mmio_pc ||
          mmio_event_addr != expected_addr ||
          mmio_event_data != expected_data) begin
        $fatal(1, "%s", message);
      end
    end
  endtask

  task automatic expect_irq(
    input logic [3:0] expected_type,
    input logic [31:0] expected_data,
    input string message
  );
    begin
      if (!irq_event_valid ||
          irq_event_type != expected_type ||
          irq_event_commit_index != irq_commit_index ||
          irq_event_pc != irq_pc ||
          irq_event_data != expected_data) begin
        $fatal(1, "%s", message);
      end
    end
  endtask
endmodule
