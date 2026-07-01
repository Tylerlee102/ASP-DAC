`timescale 1ns/1ps

module tb_rcv2_capsule_source;
  logic clk;
  logic rst_n;
  logic clear;
  logic store_clear;
  logic capture_enable;
  logic capture_valid;
  logic [63:0] capture_word;
  logic load_valid;
  logic [2:0] load_addr;
  logic [63:0] load_word;
  logic start;
  logic [31:0] expected_count;
  logic capsule_ready;
  logic capture_ready;
  logic capture_overflow;
  logic [31:0] captured_count;
  logic capsule_valid;
  logic [63:0] capsule_word;
  logic stream_done;
  logic active;
  logic underflow;
  logic [31:0] sent_count;

  localparam logic [63:0] DIAG_WORD      = 64'h1003_0000_0000_0000;
  localparam logic [63:0] DIAG_WORD_2    = 64'h1004_0000_0000_0000;
  localparam logic [63:0] MMIO_RAW_WORD  = 64'h5002_11aa_aa00_0000;
  localparam logic [63:0] IRQ_RAW_WORD   = 64'h7001_22bb_bb00_0000;
  localparam logic [63:0] FAIL_RAW_WORD  = 64'ha001_33cc_cc00_0000;
  localparam logic [63:0] MMIO_REPLAY_WORD = 64'h5005_11aa_aa00_0000;
  localparam logic [63:0] IRQ_REPLAY_WORD  = 64'h7005_22bb_bb00_0000;
  localparam logic [63:0] FAIL_REPLAY_WORD = 64'ha001_33cc_cc00_0000;

  rcv2_capsule_source #(
    .WORDS(4),
    .ADDR_W(3)
  ) u_source (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .store_clear(store_clear),
    .capture_enable(capture_enable),
    .capture_valid(capture_valid),
    .capture_word(capture_word),
    .load_valid(load_valid),
    .load_addr(load_addr),
    .load_word(load_word),
    .start(start),
    .expected_count(expected_count),
    .capsule_ready(capsule_ready),
    .capture_ready(capture_ready),
    .capture_overflow(capture_overflow),
    .captured_count(captured_count),
    .capsule_valid(capsule_valid),
    .capsule_word(capsule_word),
    .stream_done(stream_done),
    .active(active),
    .underflow(underflow),
    .sent_count(sent_count)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  task automatic capture(input logic [63:0] word);
    begin
      @(negedge clk);
      capture_word = word;
      capture_valid = 1'b1;
      @(posedge clk);
      #1;
      capture_valid = 1'b0;
    end
  endtask

  task automatic expect_stream(input logic [63:0] word);
    begin
      @(negedge clk);
      capsule_ready = 1'b1;
      #1;
      if (!capsule_valid || capsule_word != word) begin
        $fatal(1, "capsule source streamed wrong word: got %h expected %h", capsule_word, word);
      end
      @(posedge clk);
      #1;
    end
  endtask

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    store_clear = 1'b1;
    capture_enable = 1'b0;
    capture_valid = 1'b0;
    capture_word = 64'h0;
    load_valid = 1'b0;
    load_addr = 3'h0;
    load_word = 64'h0;
    start = 1'b0;
    expected_count = 32'h0;
    capsule_ready = 1'b0;

    repeat (3) @(posedge clk);
    store_clear = 1'b0;
    rst_n = 1'b1;
    repeat (2) @(posedge clk);

    capture_enable = 1'b1;
    capture(DIAG_WORD);
    if (captured_count != 32'd0) begin
      $fatal(1, "diagnostic word should not be captured for replay");
    end

    capture(MMIO_RAW_WORD);
    capture(DIAG_WORD_2);
    capture(IRQ_RAW_WORD);
    capture(FAIL_RAW_WORD);
    if (captured_count != 32'd3 || !capture_ready || capture_overflow) begin
      $fatal(1, "capture store count/ready/overflow state is wrong");
    end

    rst_n = 1'b0;
    repeat (3) @(posedge clk);
    if (captured_count != 32'd3) begin
      $fatal(1, "capture store did not retain count across reset");
    end
    rst_n = 1'b1;
    repeat (2) @(posedge clk);

    @(negedge clk);
    expected_count = captured_count;
    start = 1'b1;
    @(posedge clk);
    #1;
    start = 1'b0;
    if (!active || stream_done || underflow) begin
      $fatal(1, "capsule source did not start from retained capture store");
    end

    expect_stream(MMIO_REPLAY_WORD);
    expect_stream(IRQ_REPLAY_WORD);
    expect_stream(FAIL_REPLAY_WORD);
    @(negedge clk);
    capsule_ready = 1'b0;
    #1;
    if (!stream_done || active || sent_count != 32'd3) begin
      $fatal(1, "capsule source did not finish retained stream cleanly");
    end

    store_clear = 1'b1;
    @(posedge clk);
    #1;
    if (captured_count != 32'd0 || capture_overflow) begin
      $fatal(1, "store_clear did not reset capture metadata");
    end
    $finish;
  end
endmodule
