`timescale 1ns/1ps
`include "../../rtl/event_defs.svh"
`include "../../rtl/replaycapsule_v2/rcv2_config.svh"

module tb_rcv2_minimal_recorder;
  localparam int EXPECTED_EVENTS = 5;

  logic clk;
  logic rst_n;
  logic clear;
  logic watchdog_enable;
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
  logic checkpoint_hash_req;
  logic [2:0] capsule_read_addr;
  logic [63:0] capsule_read_data;
  logic capsule_frozen;
  logic capsule_overflow;
  logic [3:0] capsule_event_count;
  logic [31:0] running_signature;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic captured_event_valid;
  logic [3:0] captured_event_type;
  logic [31:0] captured_event_commit_index;
  logic [31:0] captured_event_addr;
  logic [31:0] captured_event_data;
  logic [31:0] captured_event_payload_hash;
  logic capsule_stream_ready;
  logic capsule_stream_valid;
  logic [63:0] capsule_stream_word;
  logic [31:0] stream_event_count;
  logic [31:0] stream_event_sent_count;
  logic [31:0] replay_critical_event_count;
  logic [31:0] stream_stall_count;
  logic [31:0] dropped_diagnostic_count;
  logic [31:0] replay_critical_overflow_count;
  logic [3:0] stream_fifo_level;

  logic replay_clear;
  logic replay_start;
  logic [31:0] replay_expected_count;
  logic replay_capsule_valid;
  logic replay_capsule_ready;
  logic [63:0] replay_capsule_word;
  logic replay_stream_done;
  logic replay_observed_valid;
  logic [3:0] replay_observed_type;
  logic [31:0] replay_observed_commit;
  logic [31:0] replay_observed_addr;
  logic [31:0] replay_observed_data;
  logic [31:0] replay_observed_payload_hash;
  logic replay_mmio_valid;
  logic [31:0] replay_mmio_addr_token;
  logic [31:0] replay_mmio_value;
  logic replay_irq_valid;
  logic [7:0] replay_irq_cause;
  logic replay_consumed_all_events;
  logic replay_error;
  logic [7:0] replay_error_code;
  logic [31:0] replay_consumed_count;

  logic [63:0] saved_word [0:4];
  logic [3:0] saved_type [0:4];
  logic [31:0] saved_commit [0:4];
  logic [31:0] saved_addr [0:4];
  logic [31:0] saved_data [0:4];
  logic [31:0] saved_payload_hash [0:4];
  int saved_count;
  int last_recorded_commit;

  rcv2_recorder #(
    .REPLAYCAPSULE_CONFIG(RCV2_CFG_MINIMAL),
    .BUFFER_DEPTH(8),
    .MEMORY_WORDS(8),
    .MEMORY_ADDR_W(3),
    .ENABLE_DIAGNOSTICS(1'b0),
    .ENABLE_PAYLOAD_HASH(1'b0),
    .ENABLE_ADDRESS_DICTIONARY(1'b0),
    .ENABLE_BRam_FIFO(1'b0),
    .ENABLE_BRAM_FIFO(1'b0),
    .ENABLE_ADAPTIVE_WINDOW(1'b0),
    .ENABLE_STREAMING(1'b1),
    .ENABLE_WATCHDOG(1'b0),
    .ENABLE_PROPERTY_CHECKER(1'b0),
    .ENABLE_CONTEXT_SLICER(1'b0),
    .ENABLE_EVENT_BUFFER(1'b0),
    .ENABLE_SIGNATURE(1'b0),
    .ENABLE_STATUS_COUNTERS(1'b0),
    .ENABLE_MINIMAL_EVENT_TAP(1'b1)
  ) u_recorder (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
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
    .checkpoint_hash_req(checkpoint_hash_req),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(capsule_read_data),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .capsule_event_count(capsule_event_count),
    .running_signature(running_signature),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .captured_event_valid(captured_event_valid),
    .captured_event_type(captured_event_type),
    .captured_event_commit_index(captured_event_commit_index),
    .captured_event_addr(captured_event_addr),
    .captured_event_data(captured_event_data),
    .captured_event_payload_hash(captured_event_payload_hash),
    .capsule_stream_ready(capsule_stream_ready),
    .capsule_stream_valid(capsule_stream_valid),
    .capsule_stream_word(capsule_stream_word),
    .stream_event_count(stream_event_count),
    .stream_event_sent_count(stream_event_sent_count),
    .replay_critical_event_count(replay_critical_event_count),
    .stream_stall_count(stream_stall_count),
    .dropped_diagnostic_count(dropped_diagnostic_count),
    .replay_critical_overflow_count(replay_critical_overflow_count),
    .stream_fifo_level(stream_fifo_level)
  );

  rcv2_replay_consumer #(
    .EVENT_COUNT(0),
    .ENABLE_PAYLOAD_HASH(1'b0),
    .STRICT_ORDER(1'b1)
  ) u_consumer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(replay_clear),
    .start(replay_start),
    .expected_event_count(replay_expected_count),
    .capsule_valid(replay_capsule_valid),
    .capsule_ready(replay_capsule_ready),
    .capsule_word(replay_capsule_word),
    .stream_done(replay_stream_done),
    .observed_valid(replay_observed_valid),
    .observed_event_type(replay_observed_type),
    .observed_commit_index(replay_observed_commit),
    .observed_addr(replay_observed_addr),
    .observed_data(replay_observed_data),
    .observed_payload_hash(replay_observed_payload_hash),
    .mmio_replay_valid(replay_mmio_valid),
    .mmio_replay_addr_token(replay_mmio_addr_token),
    .mmio_replay_value(replay_mmio_value),
    .irq_replay_valid(replay_irq_valid),
    .irq_replay_cause(replay_irq_cause),
    .consumed_all_events(replay_consumed_all_events),
    .replay_error(replay_error),
    .replay_error_code(replay_error_code),
    .consumed_count(replay_consumed_count)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  task automatic drive_idle;
    begin
      commit_valid = 1'b0;
      commit_pc = 32'h0000_0080;
      commit_instr = 32'h0000_0013;
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
      checkpoint_hash_req = 1'b0;
    end
  endtask

  task automatic expect_no_event(input [31:0] idx);
    begin
      commit_index = idx;
      #1;
      if (captured_event_valid || capsule_stream_valid) begin
        $fatal(1, "minimal recorder captured a non-boundary event at commit %0d", idx);
      end
      @(posedge clk);
      drive_idle();
    end
  endtask

  task automatic save_expected_event(
    input [3:0] expected_type,
    input [31:0] expected_commit,
    input [31:0] expected_addr,
    input [31:0] expected_data
  );
    int expected_delta;
    begin
      #1;
      expected_delta = expected_commit - last_recorded_commit;
      if (!captured_event_valid || !capsule_stream_valid) begin
        $fatal(1, "minimal recorder did not emit expected event type %0d", expected_type);
      end
      if (captured_event_type != expected_type ||
          captured_event_commit_index != expected_commit ||
          captured_event_addr != expected_addr ||
          captured_event_data != expected_data ||
          captured_event_payload_hash != expected_data) begin
        $fatal(1, "captured minimal event fields do not match expected replay boundary");
      end
      if (rcv2_word_type(capsule_stream_word) != expected_type ||
          rcv2_word_delta(capsule_stream_word) != expected_delta[7:0] ||
          rcv2_word_addr_token(capsule_stream_word) != expected_addr[7:0] ||
          rcv2_word_payload(capsule_stream_word) != expected_data ||
          rcv2_word_flags(capsule_stream_word) != 4'h0) begin
        $fatal(1, "packed minimal event word is not replay-consumer compatible");
      end
      saved_word[saved_count] = capsule_stream_word;
      saved_type[saved_count] = captured_event_type;
      saved_commit[saved_count] = captured_event_commit_index;
      saved_addr[saved_count] = captured_event_addr;
      saved_data[saved_count] = captured_event_data;
      saved_payload_hash[saved_count] = captured_event_payload_hash;
      saved_count++;
      last_recorded_commit = expected_commit;
      @(posedge clk);
      drive_idle();
    end
  endtask

  task automatic feed_saved_event(input int index);
    begin
      @(negedge clk);
      replay_capsule_word = saved_word[index];
      replay_capsule_valid = 1'b1;
      replay_observed_valid = 1'b1;
      replay_observed_type = saved_type[index];
      replay_observed_commit = saved_commit[index];
      replay_observed_addr = saved_addr[index];
      replay_observed_data = saved_data[index];
      replay_observed_payload_hash = saved_payload_hash[index];
      #1;
      if (!replay_capsule_ready) begin
        $fatal(1, "minimal replay consumer was not ready for saved event %0d", index);
      end
      @(posedge clk);
      #1;
      if (replay_error) begin
        $fatal(1, "minimal replay consumer rejected saved event %0d with error %0d", index, replay_error_code);
      end
      @(negedge clk);
      replay_capsule_valid = 1'b0;
      replay_observed_valid = 1'b0;
    end
  endtask

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    replay_clear = 1'b0;
    replay_start = 1'b0;
    replay_expected_count = 32'h0;
    replay_capsule_valid = 1'b0;
    replay_capsule_word = 64'h0;
    replay_stream_done = 1'b0;
    replay_observed_valid = 1'b0;
    replay_observed_type = 4'h0;
    replay_observed_commit = 32'h0;
    replay_observed_addr = 32'h0;
    replay_observed_data = 32'h0;
    replay_observed_payload_hash = 32'h0;
    watchdog_enable = 1'b0;
    capsule_stream_ready = 1'b1;
    capsule_read_addr = 3'h0;
    commit_index = 32'h0;
    saved_count = 0;
    last_recorded_commit = 0;
    drive_idle();

    repeat (3) @(posedge clk);
    rst_n = 1'b1;
    repeat (2) @(posedge clk);

    commit_valid = 1'b1;
    expect_no_event(32'd1);

    mem_valid = 1'b1;
    mem_write = 1'b0;
    mem_addr = 32'h2000_0000;
    mem_rdata = 32'h1111_2222;
    expect_no_event(32'd3);

    mem_valid = 1'b1;
    mem_write = 1'b0;
    mem_addr = 32'h4000_0000;
    mem_rdata = 32'hcafe_babe;
    commit_index = 32'd5;
    save_expected_event(EV_MMIO_READ, 32'd5, 32'h4000_0000, 32'hcafe_babe);

    mem_valid = 1'b1;
    mem_write = 1'b1;
    mem_addr = 32'h4000_0004;
    mem_wdata = 32'h0000_0055;
    commit_index = 32'd7;
    save_expected_event(EV_MMIO_WRITE, 32'd7, 32'h4000_0004, 32'h0000_0055);

    external_input_valid = 1'b1;
    external_input_value = 32'h1234_abcd;
    commit_index = 32'd9;
    save_expected_event(EV_EXTERNAL_INPUT, 32'd9, 32'h0, 32'h1234_abcd);

    interrupt_enter = 1'b1;
    commit_index = 32'd12;
    save_expected_event(EV_INTERRUPT_ENTER, 32'd12, 32'h0, 32'h1);

    interrupt_exit = 1'b1;
    commit_index = 32'd14;
    save_expected_event(EV_INTERRUPT_EXIT, 32'd14, 32'h0, 32'h0);

    if (property_fail_valid || property_id != 8'h0 || property_signature != 32'h0 ||
        running_signature != 32'h0 || capsule_event_count != 4'h0 ||
        stream_event_count != 32'h0 || replay_critical_event_count != 32'h0 ||
        stream_fifo_level != 4'h0 || capsule_overflow) begin
      $fatal(1, "disabled minimal-recorder diagnostics/status logic produced state");
    end

    @(negedge clk);
    if (saved_count != EXPECTED_EVENTS) begin
      $fatal(1, "minimal recorder emitted %0d events, expected %0d", saved_count, EXPECTED_EVENTS);
    end
    replay_expected_count = 32'd5;
    replay_start = 1'b1;
    @(posedge clk);
    #1;
    if (!replay_capsule_ready) begin
      $fatal(1, "minimal replay consumer did not start for saved event stream");
    end
    @(negedge clk);
    replay_start = 1'b0;

    feed_saved_event(0);
    feed_saved_event(1);
    feed_saved_event(2);
    feed_saved_event(3);
    feed_saved_event(4);

    @(negedge clk);
    #1;
    if (!replay_consumed_all_events || replay_error || replay_error_code != RCV2_ERR_NONE ||
        replay_consumed_count != 32'd5) begin
      $fatal(1, "minimal recorder words were not accepted by replay consumer");
    end

    $finish;
  end
endmodule
