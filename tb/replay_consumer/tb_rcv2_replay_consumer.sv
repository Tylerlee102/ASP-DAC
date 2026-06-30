`timescale 1ns/1ps

module tb_rcv2_replay_consumer;
  `include "../../rtl/event_defs.svh"
  `include "../../rtl/replaycapsule_v2/rcv2_config.svh"

  logic clk;
  logic rst_n;
  logic clear;
  logic start;
  logic capsule_valid;
  logic capsule_ready;
  logic [63:0] capsule_word;
  logic stream_done;
  logic observed_valid;
  logic [3:0] observed_event_type;
  logic [31:0] observed_commit_index;
  logic [31:0] observed_addr;
  logic [31:0] observed_data;
  logic [31:0] observed_payload_hash;
  logic mmio_replay_valid;
  logic [31:0] mmio_replay_addr_token;
  logic [31:0] mmio_replay_value;
  logic irq_replay_valid;
  logic [7:0] irq_replay_cause;
  logic consumed_all_events;
  logic replay_error;
  logic [7:0] replay_error_code;
  logic [31:0] consumed_count;
  integer passed_count;
  integer total_count;

  rcv2_replay_consumer #(
    .EVENT_COUNT(3),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .STRICT_ORDER(1'b1)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .start(start),
    .expected_event_count(32'd0),
    .capsule_valid(capsule_valid),
    .capsule_ready(capsule_ready),
    .capsule_word(capsule_word),
    .stream_done(stream_done),
    .observed_valid(observed_valid),
    .observed_event_type(observed_event_type),
    .observed_commit_index(observed_commit_index),
    .observed_addr(observed_addr),
    .observed_data(observed_data),
    .observed_payload_hash(observed_payload_hash),
    .mmio_replay_valid(mmio_replay_valid),
    .mmio_replay_addr_token(mmio_replay_addr_token),
    .mmio_replay_value(mmio_replay_value),
    .irq_replay_valid(irq_replay_valid),
    .irq_replay_cause(irq_replay_cause),
    .consumed_all_events(consumed_all_events),
    .replay_error(replay_error),
    .replay_error_code(replay_error_code),
    .consumed_count(consumed_count)
  );

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  function automatic logic [63:0] pack_word(
    input logic [3:0] event_type,
    input logic [3:0] flags,
    input logic [7:0] delta,
    input logic [7:0] addr_token,
    input logic [31:0] payload,
    input logic [7:0] debug_context
  );
    begin
      pack_word = {event_type, flags, delta, addr_token, payload, debug_context};
    end
  endfunction

  task automatic reset_case;
    begin
      rst_n = 1'b0;
      clear = 1'b0;
      start = 1'b0;
      capsule_valid = 1'b0;
      capsule_word = 64'h0;
      stream_done = 1'b0;
      observed_valid = 1'b0;
      observed_event_type = 4'h0;
      observed_commit_index = 32'h0;
      observed_addr = 32'h0;
      observed_data = 32'h0;
      observed_payload_hash = 32'h0;
      repeat (2) @(posedge clk);
      rst_n = 1'b1;
      @(posedge clk);
      start = 1'b1;
      @(posedge clk);
      start = 1'b0;
      @(posedge clk);
    end
  endtask

  task automatic feed_event(
    input logic [63:0] word,
    input logic observed_ok,
    input logic [3:0] obs_type,
    input logic [31:0] obs_commit,
    input logic [31:0] obs_addr,
    input logic [31:0] obs_data,
    input logic [31:0] obs_hash
  );
    begin
      @(negedge clk);
      capsule_word = word;
      capsule_valid = 1'b1;
      observed_valid = observed_ok;
      observed_event_type = obs_type;
      observed_commit_index = obs_commit;
      observed_addr = obs_addr;
      observed_data = obs_data;
      observed_payload_hash = obs_hash;
      @(posedge clk);
      @(negedge clk);
      capsule_valid = 1'b0;
      observed_valid = 1'b0;
      observed_event_type = 4'h0;
      observed_commit_index = 32'h0;
      observed_addr = 32'h0;
      observed_data = 32'h0;
      observed_payload_hash = 32'h0;
    end
  endtask

  task automatic send_done;
    begin
      @(negedge clk);
      stream_done = 1'b1;
      @(posedge clk);
      @(negedge clk);
      stream_done = 1'b0;
    end
  endtask

  task automatic report_result(
    input string test_name,
    input string expected_result,
    input string actual_result,
    input logic [7:0] expected_error
  );
    logic ok;
    begin
      ok = 1'b0;
      if (expected_result == "PASS") begin
        ok = (actual_result == "PASS") && consumed_all_events && !replay_error;
      end else begin
        ok = (actual_result == "REJECT") && replay_error && replay_error_code == expected_error;
      end
      total_count = total_count + 1;
      if (ok) begin
        passed_count = passed_count + 1;
      end
      $display("RESULT,%s,%s,%s,%0d,%0d", test_name, expected_result, actual_result, ok, replay_error_code);
    end
  endtask

  task automatic valid_three_events;
    logic [63:0] w0;
    logic [63:0] w1;
    logic [63:0] w2;
    begin
      w0 = pack_word(EV_MMIO_READ, 4'b0000, 8'd4, 8'h44, 32'h0000_1111, 8'h00);
      w1 = pack_word(EV_INTERRUPT_ENTER, 4'b0000, 8'd1, 8'h00, 32'h0000_0003, 8'h03);
      w2 = pack_word(EV_PROPERTY_FAIL, 4'b0000, 8'd1, 8'h0a, 32'ha5a5_0001, 8'h2a);
      feed_event(w0, 1'b1, EV_MMIO_READ, 32'd4, 32'h0000_0044, 32'h0000_1111, 32'h0);
      feed_event(w1, 1'b1, EV_INTERRUPT_ENTER, 32'd5, 32'h0, 32'h0000_0003, 32'h0);
      feed_event(w2, 1'b1, EV_PROPERTY_FAIL, 32'd6, 32'h0, 32'ha5a5_0001, 32'h0);
    end
  endtask

  task automatic valid_dict_hit_mmio_events;
    logic [63:0] w0;
    logic [63:0] w1;
    logic [63:0] w2;
    begin
      w0 = pack_word(EV_MMIO_WRITE, 4'b0000, 8'd15, 8'h0c, 32'h0000_0001, 8'h00);
      w1 = pack_word(EV_MMIO_WRITE, 4'b0000, 8'd1, 8'h08, 32'h0000_cafe, 8'h00);
      w2 = pack_word(EV_MMIO_WRITE, 4'b0100, 8'd1, 8'h00, 32'h0000_0000, 8'h00);
      feed_event(w0, 1'b1, EV_MMIO_WRITE, 32'd15, 32'h4000_000c, 32'h0000_0001, 32'h0);
      feed_event(w1, 1'b1, EV_MMIO_WRITE, 32'd16, 32'h4000_0008, 32'h0000_cafe, 32'h0);
      feed_event(w2, 1'b1, EV_MMIO_WRITE, 32'd17, 32'h4000_000c, 32'h0000_0000, 32'h0);
    end
  endtask

  initial begin
    passed_count = 0;
    total_count = 0;

    reset_case();
    valid_three_events();
    report_result("valid_capsule_consumes_all_events", "PASS", replay_error ? "REJECT" : "PASS", RCV2_ERR_NONE);

    reset_case();
    valid_dict_hit_mmio_events();
    report_result("dict_hit_mmio_consumes_observed_address", "PASS", replay_error ? "REJECT" : "PASS", RCV2_ERR_NONE);

    reset_case();
    feed_event(pack_word(EV_MMIO_READ, 4'b0000, 8'd4, 8'h44, 32'h0000_1111, 8'h00), 1'b0, EV_MMIO_READ, 32'd4, 32'h44, 32'h1111, 32'h0);
    report_result("missing_event_rejects", "REJECT", replay_error ? "REJECT" : "PASS", RCV2_ERR_MISSING_EVENT);

    reset_case();
    valid_three_events();
    feed_event(pack_word(EV_MMIO_READ, 4'b0000, 8'd1, 8'h44, 32'h0000_1111, 8'h00), 1'b1, EV_MMIO_READ, 32'd7, 32'h44, 32'h1111, 32'h0);
    report_result("duplicate_event_rejects", "REJECT", replay_error ? "REJECT" : "PASS", RCV2_ERR_DUPLICATE_EVENT);

    reset_case();
    feed_event(pack_word(EV_MMIO_READ, 4'b0000, 8'd4, 8'h44, 32'h0000_1111, 8'h00), 1'b1, EV_INTERRUPT_ENTER, 32'd4, 32'h44, 32'h1111, 32'h0);
    report_result("reordered_event_rejects", "REJECT", replay_error ? "REJECT" : "PASS", RCV2_ERR_REORDERED_EVENT);

    reset_case();
    feed_event(pack_word(EV_MMIO_READ, 4'b0000, 8'd4, 8'h44, 32'h0000_1111, 8'h00), 1'b1, EV_MMIO_READ, 32'd4, 32'h44, 32'h0000_2222, 32'h0);
    report_result("wrong_mmio_value_rejects", "REJECT", replay_error ? "REJECT" : "PASS", RCV2_ERR_WRONG_MMIO_VALUE);

    reset_case();
    feed_event(pack_word(EV_INTERRUPT_ENTER, 4'b0000, 8'd4, 8'h00, 32'h0000_0003, 8'h03), 1'b1, EV_INTERRUPT_ENTER, 32'd4, 32'h0, 32'h0000_0004, 32'h0);
    report_result("wrong_interrupt_cause_rejects", "REJECT", replay_error ? "REJECT" : "PASS", RCV2_ERR_WRONG_IRQ_CAUSE);

    reset_case();
    feed_event(pack_word(EV_MMIO_READ, 4'b0010, 8'd4, 8'h44, 32'h0000_abcd, 8'h00), 1'b1, EV_MMIO_READ, 32'd4, 32'h44, 32'h0000_abcd, 32'h0000_1234);
    report_result("wrong_payload_hash_rejects", "REJECT", replay_error ? "REJECT" : "PASS", RCV2_ERR_WRONG_PAYLOAD_HASH);

    reset_case();
    feed_event(pack_word(EV_MMIO_READ, 4'b0000, 8'd4, 8'h44, 32'h0000_1111, 8'h00), 1'b1, EV_MMIO_READ, 32'd4, 32'h44, 32'h1111, 32'h0);
    feed_event(pack_word(EV_INTERRUPT_ENTER, 4'b0000, 8'd1, 8'h00, 32'h0000_0003, 8'h03), 1'b1, EV_INTERRUPT_ENTER, 32'd5, 32'h0, 32'h3, 32'h0);
    send_done();
    report_result("truncated_capsule_rejects", "REJECT", replay_error ? "REJECT" : "PASS", RCV2_ERR_TRUNCATED_CAPSULE);

    $display("SUMMARY,%0d,%0d", passed_count, total_count);
    if (passed_count != total_count) begin
      $finish(1);
    end
    $finish(0);
  end
endmodule
