`timescale 1ns/1ps

module tb_rcv1_capsule_replay_checker;
  localparam int EVENT_WIDTH = 168;
  localparam logic [7:0] RCV1_ERR_PACKET_MISMATCH = 8'h01;
  localparam logic [7:0] RCV1_ERR_EXTRA_PACKET = 8'h02;
  localparam logic [7:0] RCV1_ERR_COUNT_MISMATCH = 8'h03;

  logic clk;
  logic rst_n;
  logic clear;
  logic start;
  logic [31:0] expected_event_count;
  logic check_valid;
  logic [EVENT_WIDTH-1:0] expected_packet;
  logic [EVENT_WIDTH-1:0] observed_packet;
  logic finish;
  logic active;
  logic consumed_all_events;
  logic replay_error;
  logic [7:0] replay_error_code;
  logic [31:0] consumed_count;
  logic [31:0] mismatch_index;
  integer passed_count;
  integer total_count;

  rcv1_capsule_replay_checker dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .start(start),
    .expected_event_count(expected_event_count),
    .check_valid(check_valid),
    .expected_packet(expected_packet),
    .observed_packet(observed_packet),
    .finish(finish),
    .active(active),
    .consumed_all_events(consumed_all_events),
    .replay_error(replay_error),
    .replay_error_code(replay_error_code),
    .consumed_count(consumed_count),
    .mismatch_index(mismatch_index)
  );

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  function automatic logic [EVENT_WIDTH-1:0] pkt(
    input logic [3:0] event_type,
    input logic [31:0] event_id,
    input logic [31:0] commit_index,
    input logic [31:0] pc,
    input logic [31:0] addr,
    input logic [31:0] data
  );
    begin
      pkt = {event_type, 4'h0, event_id, commit_index, pc, addr, data};
    end
  endfunction

  task automatic reset_case;
    input logic [31:0] count;
    begin
      rst_n = 1'b0;
      clear = 1'b0;
      start = 1'b0;
      expected_event_count = count;
      check_valid = 1'b0;
      expected_packet = '0;
      observed_packet = '0;
      finish = 1'b0;
      repeat (2) @(posedge clk);
      rst_n = 1'b1;
      @(negedge clk);
      start = 1'b1;
      @(posedge clk);
      @(negedge clk);
      start = 1'b0;
    end
  endtask

  task automatic feed_pair;
    input logic [EVENT_WIDTH-1:0] expected;
    input logic [EVENT_WIDTH-1:0] observed;
    begin
      @(negedge clk);
      expected_packet = expected;
      observed_packet = observed;
      check_valid = 1'b1;
      @(posedge clk);
      @(negedge clk);
      check_valid = 1'b0;
    end
  endtask

  task automatic finish_case;
    begin
      @(negedge clk);
      finish = 1'b1;
      @(posedge clk);
      @(negedge clk);
      finish = 1'b0;
    end
  endtask

  task automatic report_result;
    input string test_name;
    input logic expect_pass;
    input logic [7:0] expected_error;
    logic ok;
    begin
      if (expect_pass) begin
        ok = consumed_all_events && !replay_error;
      end else begin
        ok = replay_error && replay_error_code == expected_error;
      end
      total_count = total_count + 1;
      if (ok) begin
        passed_count = passed_count + 1;
      end
      $display("RESULT,%s,%0d,%0d,%0d,%0d", test_name, expect_pass, ok, replay_error_code, consumed_count);
    end
  endtask

  initial begin
    passed_count = 0;
    total_count = 0;

    reset_case(32'd3);
    feed_pair(pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd850), pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd850));
    feed_pair(pkt(4'h6, 32'd1, 32'd5, 32'h84, 32'h4000_0004, 32'd1), pkt(4'h6, 32'd1, 32'd5, 32'h84, 32'h4000_0004, 32'd1));
    feed_pair(pkt(4'ha, 32'd2, 32'd6, 32'h88, 32'h0000_0003, 32'h5e05_00c2), pkt(4'ha, 32'd2, 32'd6, 32'h88, 32'h0000_0003, 32'h5e05_00c2));
    finish_case();
    report_result("valid_stream_consumes_all_packets", 1'b1, 8'h00);

    reset_case(32'd1);
    feed_pair(pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd850), pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd851));
    report_result("packet_mismatch_rejects", 1'b0, RCV1_ERR_PACKET_MISMATCH);

    reset_case(32'd1);
    feed_pair(pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd850), pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd850));
    feed_pair(pkt(4'h6, 32'd1, 32'd5, 32'h84, 32'h4000_0004, 32'd1), pkt(4'h6, 32'd1, 32'd5, 32'h84, 32'h4000_0004, 32'd1));
    report_result("extra_packet_rejects", 1'b0, RCV1_ERR_EXTRA_PACKET);

    reset_case(32'd2);
    feed_pair(pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd850), pkt(4'h5, 32'd0, 32'd4, 32'h80, 32'h4000_0000, 32'd850));
    finish_case();
    report_result("truncated_stream_rejects", 1'b0, RCV1_ERR_COUNT_MISMATCH);

    if (passed_count != total_count) begin
      $fatal(1, "RCV1_CAPSULE_REPLAY_CHECKER_FAIL passed=%0d total=%0d", passed_count, total_count);
    end
    $display("RCV1_CAPSULE_REPLAY_CHECKER_PASS passed=%0d total=%0d", passed_count, total_count);
    $finish;
  end

  logic unused_active;
  logic [31:0] unused_mismatch_index;
  assign unused_active = active;
  assign unused_mismatch_index = mismatch_index;
endmodule
