`timescale 1ns/1ps
`include "../../rtl/event_pkg.sv"

module tb_event_tap;
  import replaycapsule_event_pkg::*;

  logic clk;
  logic rst_n;
  logic commit_valid;
  logic [31:0] commit_pc;
  logic [31:0] commit_instr;
  logic [31:0] commit_index;
  logic branch_taken;
  logic jump_taken;
  logic mem_valid;
  logic mem_write;
  logic [31:0] mem_addr;
  logic [31:0] mem_wdata;
  logic [31:0] mem_rdata;
  logic external_input_valid;
  logic [31:0] external_input_value;
  logic interrupt_enter;
  logic interrupt_exit;
  logic event_valid;
  logic [3:0] event_type;
  logic [31:0] event_commit_index;
  logic [31:0] event_pc;
  logic [31:0] event_addr;
  logic [31:0] event_data;
  logic multievent_pending;

  event_tap u_event_tap (
    .clk(clk),
    .rst_n(rst_n),
    .commit_valid(commit_valid),
    .commit_pc(commit_pc),
    .commit_instr(commit_instr),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(mem_valid),
    .mem_write(mem_write),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .event_valid(event_valid),
    .event_type(event_type),
    .event_commit_index(event_commit_index),
    .event_pc(event_pc),
    .event_addr(event_addr),
    .event_data(event_data),
    .multievent_pending(multievent_pending)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b1;
    clear_inputs();
    #1;
    if (event_valid || multievent_pending) begin
      $fatal(1, "idle tap produced an event");
    end

    commit_valid = 1'b1;
    #1;
    expect_event(EV_COMMIT, 32'h0, commit_instr, 1'b0, "plain commit was not emitted");

    branch_taken = 1'b1;
    #1;
    expect_event(EV_BRANCH, 32'h0, commit_instr, 1'b1, "branch event or multievent flag was incorrect");

    branch_taken = 1'b0;
    jump_taken = 1'b1;
    #1;
    expect_event(EV_JUMP, 32'h0, commit_instr, 1'b1, "jump event or multievent flag was incorrect");

    clear_inputs();
    mem_valid = 1'b1;
    mem_write = 1'b1;
    mem_addr = 32'h2000_0010;
    mem_wdata = 32'hdead_beef;
    #1;
    expect_event(EV_STORE, mem_addr, mem_wdata, 1'b0, "ordinary store was not emitted");

    mem_write = 1'b0;
    mem_rdata = 32'hcafe_f00d;
    #1;
    expect_event(EV_LOAD, mem_addr, mem_rdata, 1'b0, "ordinary load was not emitted");

    mem_addr = 32'h4000_0020;
    #1;
    expect_event(EV_MMIO_READ, mem_addr, mem_rdata, 1'b0, "MMIO read was not emitted");

    mem_write = 1'b1;
    mem_wdata = 32'h0000_00a5;
    #1;
    expect_event(EV_MMIO_WRITE, mem_addr, mem_wdata, 1'b0, "MMIO write was not emitted");

    external_input_valid = 1'b1;
    external_input_value = 32'h0000_1234;
    #1;
    expect_event(EV_EXTERNAL_INPUT, 32'h0, external_input_value, 1'b1, "external input did not outrank memory event");

    interrupt_exit = 1'b1;
    #1;
    expect_event(EV_INTERRUPT_EXIT, 32'h0, 32'h0, 1'b1, "interrupt exit did not outrank external input");

    interrupt_enter = 1'b1;
    #1;
    expect_event(EV_INTERRUPT_ENTER, 32'h0, 32'h1, 1'b1, "interrupt enter did not have highest priority");

    clear_inputs();
    interrupt_exit = 1'b1;
    #1;
    expect_event(EV_INTERRUPT_EXIT, 32'h0, 32'h0, 1'b0, "single interrupt exit was not emitted");

    $finish;
  end

  task automatic clear_inputs();
    begin
      commit_valid = 1'b0;
      commit_pc = 32'h0000_0080;
      commit_instr = 32'h0000_0013;
      commit_index = 32'd17;
      branch_taken = 1'b0;
      jump_taken = 1'b0;
      mem_valid = 1'b0;
      mem_write = 1'b0;
      mem_addr = 32'h0;
      mem_wdata = 32'h0;
      mem_rdata = 32'h0;
      external_input_valid = 1'b0;
      external_input_value = 32'h0;
      interrupt_enter = 1'b0;
      interrupt_exit = 1'b0;
    end
  endtask

  task automatic expect_event(
    input logic [3:0] expected_type,
    input logic [31:0] expected_addr,
    input logic [31:0] expected_data,
    input logic expected_multievent,
    input string message
  );
    begin
      if (!event_valid ||
          event_type != expected_type ||
          event_commit_index != commit_index ||
          event_pc != commit_pc ||
          event_addr != expected_addr ||
          event_data != expected_data ||
          multievent_pending != expected_multievent) begin
        $fatal(
          1,
          "%s: type=%0h addr=%08x data=%08x multi=%0b",
          message,
          event_type,
          event_addr,
          event_data,
          multievent_pending
        );
      end
    end
  endtask
endmodule
