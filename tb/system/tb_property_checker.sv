`timescale 1ns/1ps
`include "../../rtl/event_pkg.sv"

module tb_property_checker;
  import replaycapsule_event_pkg::*;

  logic clk;
  logic rst_n;
  logic clear;
  logic event_valid;
  logic [3:0] event_type;
  logic [31:0] event_commit_index;
  logic [31:0] event_pc;
  logic [31:0] event_addr;
  logic [31:0] event_data;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic sensor_deadline_active;
  logic critical_section_active;

  property_checker u_property_checker (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(1'b0),
    .event_valid(event_valid),
    .event_type(event_type),
    .event_commit_index(event_commit_index),
    .event_pc(event_pc),
    .event_addr(event_addr),
    .event_data(event_data),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .sensor_deadline_active(sensor_deadline_active),
    .critical_section_active(critical_section_active)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    event_valid = 1'b0;
    event_type = EV_COMMIT;
    event_commit_index = 32'h0;
    event_pc = 32'h0;
    event_addr = 32'h0;
    event_data = 32'h0;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);

    drive_event(EV_MMIO_WRITE, 32'h0000_00b0, 32'h4000_0004, 32'd250, 32'd1);
    @(posedge clk);
    if (!property_fail_valid || property_id != 8'd1) begin
      $fatal(1, "actuator-limit property did not fail as expected");
    end

    drive_event(EV_STORE, 32'h0000_00e0, 32'h0000_1010, 32'hdead_beef, 32'd2);
    @(posedge clk);
    if (!property_fail_valid || property_id != 8'd4) begin
      $fatal(1, "stack-protection property did not fail as expected");
    end

    $finish;
  end

  task automatic drive_event(
    input logic [3:0] next_type,
    input logic [31:0] next_pc,
    input logic [31:0] next_addr,
    input logic [31:0] next_data,
    input logic [31:0] next_commit
  );
    begin
      @(posedge clk);
      event_valid <= 1'b1;
      event_type <= next_type;
      event_pc <= next_pc;
      event_addr <= next_addr;
      event_data <= next_data;
      event_commit_index <= next_commit;
      @(posedge clk);
      event_valid <= 1'b0;
    end
  endtask
endmodule
