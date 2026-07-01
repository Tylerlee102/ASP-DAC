`timescale 1ns/1ps

module tb_rcv2_replay_mode_controller;
  logic clk;
  logic rst_n;
  logic clear;
  logic enable;
  logic arm_record;
  logic start_replay;
  logic [31:0] captured_count;
  logic capture_overflow;
  logic source_underflow;
  logic consume_all_events;
  logic consume_error;
  logic source_store_clear;
  logic source_capture_enable;
  logic consume_use_source;
  logic consume_start;
  logic [31:0] consume_expected_count;
  logic busy;
  logic record_active;
  logic replay_active;
  logic done;
  logic error;
  logic [7:0] state;
  logic [7:0] error_code;

  rcv2_replay_mode_controller u_controller (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .enable(enable),
    .arm_record(arm_record),
    .start_replay(start_replay),
    .captured_count(captured_count),
    .capture_overflow(capture_overflow),
    .source_underflow(source_underflow),
    .consume_all_events(consume_all_events),
    .consume_error(consume_error),
    .source_store_clear(source_store_clear),
    .source_capture_enable(source_capture_enable),
    .consume_use_source(consume_use_source),
    .consume_start(consume_start),
    .consume_expected_count(consume_expected_count),
    .busy(busy),
    .record_active(record_active),
    .replay_active(replay_active),
    .done(done),
    .error(error),
    .state(state),
    .error_code(error_code)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    enable = 1'b0;
    arm_record = 1'b0;
    start_replay = 1'b0;
    captured_count = 32'h0;
    capture_overflow = 1'b0;
    source_underflow = 1'b0;
    consume_all_events = 1'b0;
    consume_error = 1'b0;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    enable = 1'b1;
    @(posedge clk);

    arm_record = 1'b1;
    #1;
    if (!source_store_clear || !source_capture_enable) begin
      $fatal(1, "arm_record did not clear and enable capture store");
    end
    @(posedge clk);
    arm_record = 1'b0;
    @(posedge clk);
    if (!record_active || !busy || !source_capture_enable) begin
      $fatal(1, "controller did not remain in record state");
    end

    @(negedge clk);
    captured_count = 32'd4;
    start_replay = 1'b1;
    #1;
    if (!consume_start) begin
      $fatal(1, "controller did not pulse consume_start from state %0d", state);
    end
    if (!consume_use_source) begin
      $fatal(1, "controller did not select RTL source for replay");
    end
    if (consume_expected_count != 32'd4) begin
      $fatal(1, "controller expected count was %0d, not 4", consume_expected_count);
    end
    if (source_capture_enable) begin
      $fatal(1, "controller left capture enabled while starting replay");
    end
    @(posedge clk);
    @(negedge clk);
    start_replay = 1'b0;
    @(posedge clk);
    if (!replay_active || !busy || !consume_use_source) begin
      $fatal(1, "controller did not enter replay state");
    end

    consume_all_events = 1'b1;
    @(posedge clk);
    consume_all_events = 1'b0;
    @(posedge clk);
    if (!done || busy || error) begin
      $fatal(1, "controller did not complete clean replay");
    end

    @(negedge clk);
    captured_count = 32'h0;
    start_replay = 1'b1;
    #1;
    if (!consume_start || consume_expected_count != 32'h0) begin
      $fatal(1, "zero-count replay did not start cleanly");
    end
    @(posedge clk);
    @(negedge clk);
    start_replay = 1'b0;
    @(posedge clk);
    consume_all_events = 1'b1;
    @(posedge clk);
    consume_all_events = 1'b0;
    @(posedge clk);
    if (!done || error) begin
      $fatal(1, "zero-count replay did not complete cleanly");
    end

    arm_record = 1'b1;
    @(posedge clk);
    arm_record = 1'b0;
    @(posedge clk);
    capture_overflow = 1'b1;
    @(posedge clk);
    capture_overflow = 1'b0;
    @(posedge clk);
    if (!error || error_code != 8'd1) begin
      $fatal(1, "capture overflow did not report ERR_OVERFLOW");
    end

    $finish;
  end
endmodule
