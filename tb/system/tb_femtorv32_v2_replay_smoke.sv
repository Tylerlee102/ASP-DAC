`timescale 1ns/1ps

module tb_femtorv32_v2_replay_smoke;
  localparam int MEM_WORDS = 65536;
  localparam int MAX_REPLAY_WORDS = 256;
  localparam logic [31:0] SENSOR_ADDR = 32'h4000_0000;
  localparam logic [31:0] COMMAND_ADDR = 32'h4000_000c;
  localparam logic [31:0] PROFILE2_SENSOR_ADDR = 32'h4000_0040;
  localparam logic [31:0] PROFILE2_COMMAND_ADDR = 32'h4000_004c;
  localparam logic [31:0] NOP = 32'h0000_0013;

  logic clk;
  logic rst_n;
  logic clear;
  logic trap;
  logic mem_valid;
  logic mem_instr;
  logic mem_ready;
  logic [31:0] mem_addr;
  logic [31:0] mem_wdata;
  logic [3:0] mem_wstrb;
  logic [31:0] mem_rdata;
  logic [31:0] irq;
  logic [7:0] capsule_read_addr;
  logic [63:0] capsule_read_data;
  logic capsule_frozen;
  logic capsule_overflow;
  logic [8:0] capsule_event_count;
  logic [31:0] running_signature;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic capsule_stream_ready;
  logic capsule_stream_valid;
  logic [63:0] capsule_stream_word;
  logic [31:0] capsule_stream_event_count;
  logic [31:0] capsule_stream_sent_count;
  logic [31:0] capsule_replay_critical_event_count;
  logic [31:0] capsule_stream_stall_count;
  logic [31:0] capsule_dropped_diagnostic_count;
  logic [31:0] capsule_replay_critical_overflow_count;
  logic [8:0] capsule_stream_fifo_level;
  logic replay_consume_start;
  logic [31:0] replay_consume_expected_count;
  logic replay_consume_valid;
  logic [63:0] replay_consume_word;
  logic replay_consume_stream_done;
  logic replay_consume_ready;
  logic replay_consume_observed_valid;
  logic replay_consume_all_events;
  logic replay_consume_error;
  logic [7:0] replay_consume_error_code;
  logic [31:0] replay_consume_consumed_count;
  logic core_run_enable;
  logic irq_drive;
  logic [31:0] memory [0:MEM_WORDS-1];
  logic [63:0] replay_words [0:MAX_REPLAY_WORDS-1];

  string memfile;
  integer expected_property;
  integer seed_value;
  integer sensor_value;
  integer replay_sensor_value;
  integer command_value;
  integer replay_command_value;
  integer watchdog_enable_value;
  integer irq_after_command_value;
  integer irq_pulse_cycles;
  integer irq_pulse_remaining;
  integer recorder_config_select_value;
  integer require_signature_match;
  integer trace_events;
  integer max_cycles;
  integer cycle_index;
  integer phase;
  integer replay_word_count;
  integer replay_feed_index;
  integer replay_started;
  logic [7:0] recorded_property_id;
  logic [31:0] recorded_property_signature;
  logic [7:0] replay_observed_property_id;
  logic [31:0] replay_observed_property_signature;

  femtorv32_replaycapsule_v2_wrapper u_wrapper (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable_value != 0),
    .core_run_enable(core_run_enable),
    .recorder_config_select(recorder_config_select_value[1:0]),
    .replay_consume_start(replay_consume_start),
    .replay_consume_expected_count(replay_consume_expected_count),
    .replay_consume_valid(replay_consume_valid),
    .replay_consume_word(replay_consume_word),
    .replay_consume_stream_done(replay_consume_stream_done),
    .capsule_stream_ready(capsule_stream_ready),
    .trap(trap),
    .mem_valid(mem_valid),
    .mem_instr(mem_instr),
    .mem_ready(mem_ready),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wstrb(mem_wstrb),
    .mem_rdata(mem_rdata),
    .irq(irq),
    .external_input_valid(1'b0),
    .external_input_value(32'h0),
    .capsule_read_addr(capsule_read_addr),
    .capsule_read_data(capsule_read_data),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .capsule_event_count(capsule_event_count),
    .running_signature(running_signature),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .capsule_stream_valid(capsule_stream_valid),
    .capsule_stream_word(capsule_stream_word),
    .capsule_stream_event_count(capsule_stream_event_count),
    .capsule_stream_sent_count(capsule_stream_sent_count),
    .capsule_replay_critical_event_count(capsule_replay_critical_event_count),
    .capsule_stream_stall_count(capsule_stream_stall_count),
    .capsule_dropped_diagnostic_count(capsule_dropped_diagnostic_count),
    .capsule_replay_critical_overflow_count(capsule_replay_critical_overflow_count),
    .capsule_stream_fifo_level(capsule_stream_fifo_level),
    .replay_consume_ready(replay_consume_ready),
    .replay_consume_observed_valid(replay_consume_observed_valid),
    .replay_consume_all_events(replay_consume_all_events),
    .replay_consume_error(replay_consume_error),
    .replay_consume_error_code(replay_consume_error_code),
    .replay_consume_consumed_count(replay_consume_consumed_count)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;
  assign irq = {31'h0, irq_drive};
  assign capsule_stream_ready = 1'b1;

  task automatic load_memory;
    integer load_index;
    begin
      for (load_index = 0; load_index < MEM_WORDS; load_index = load_index + 1) begin
        memory[load_index] = NOP;
      end
      $readmemh(memfile, memory);
    end
  endtask

  task automatic configure_test;
    begin
      memfile = "firmware/build/sensor_threshold_bug/failing.hex";
      expected_property = 3;
      seed_value = 1;
      sensor_value = 850;
      replay_sensor_value = 0;
      command_value = 0;
      replay_command_value = 0;
      watchdog_enable_value = 0;
      irq_after_command_value = 0;
      irq_pulse_cycles = 24;
      irq_pulse_remaining = 0;
      recorder_config_select_value = 0;
      require_signature_match = 1;
      trace_events = 0;
      max_cycles = 1200;
      if (!$value$plusargs("MEMFILE=%s", memfile)) begin end
      if (!$value$plusargs("EXPECTED_PROPERTY=%d", expected_property)) begin end
      if (!$value$plusargs("SEED=%d", seed_value)) begin end
      if (!$value$plusargs("SENSOR_VALUE=%d", sensor_value)) begin end
      if (!$value$plusargs("REPLAY_SENSOR_VALUE=%d", replay_sensor_value)) begin end
      if (!$value$plusargs("COMMAND_VALUE=%d", command_value)) begin end
      if (!$value$plusargs("REPLAY_COMMAND_VALUE=%d", replay_command_value)) begin
        replay_command_value = command_value;
      end
      if (!$value$plusargs("WATCHDOG_ENABLE=%d", watchdog_enable_value)) begin end
      if (!$value$plusargs("IRQ_AFTER_COMMAND=%d", irq_after_command_value)) begin end
      if (!$value$plusargs("IRQ_PULSE_CYCLES=%d", irq_pulse_cycles)) begin end
      if (!$value$plusargs("RECORDER_CONFIG_SELECT=%d", recorder_config_select_value)) begin end
      if (!$value$plusargs("REQUIRE_SIGNATURE_MATCH=%d", require_signature_match)) begin end
      if (!$value$plusargs("TRACE_EVENTS=%d", trace_events)) begin end
      if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin end
      if (recorder_config_select_value < 0 || recorder_config_select_value > 2) begin
        $fatal(1, "RECORDER_CONFIG_SELECT must be 0 core, 1 hashed, or 2 full");
      end
      if (irq_pulse_cycles < 1) begin
        $fatal(1, "IRQ_PULSE_CYCLES must be positive");
      end
      load_memory();
    end
  endtask

  task automatic reset_wrapper;
    begin
      rst_n = 1'b0;
      clear = 1'b1;
      capsule_read_addr = 8'h0;
      irq_drive = 1'b0;
      irq_pulse_remaining = 0;
      repeat (5) @(posedge clk);
      clear = 1'b0;
      rst_n = 1'b1;
    end
  endtask

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      irq_drive <= 1'b0;
      irq_pulse_remaining <= 0;
    end else if (clear) begin
      irq_drive <= 1'b0;
      irq_pulse_remaining <= 0;
    end else begin
      if (irq_pulse_remaining > 0) begin
        irq_drive <= 1'b1;
        irq_pulse_remaining <= irq_pulse_remaining - 1;
      end else begin
        irq_drive <= 1'b0;
        if (
          irq_after_command_value != 0 &&
          mem_valid &&
          mem_ready &&
          !mem_instr &&
          mem_wstrb != 4'h0 &&
          (mem_addr == COMMAND_ADDR || mem_addr == PROFILE2_COMMAND_ADDR) &&
          mem_wdata[0]
        ) begin
          irq_pulse_remaining <= irq_pulse_cycles;
        end
      end
    end
  end

  always_comb begin
    mem_ready = mem_valid;
    mem_rdata = NOP;
    if (mem_addr == SENSOR_ADDR || mem_addr == PROFILE2_SENSOR_ADDR) begin
      mem_rdata = (phase == 0) ? sensor_value[31:0] : replay_sensor_value[31:0];
    end else if (mem_addr == COMMAND_ADDR || mem_addr == PROFILE2_COMMAND_ADDR) begin
      mem_rdata = (phase == 0) ? command_value[31:0] : replay_command_value[31:0];
    end else if (mem_addr < MEM_WORDS) begin
      mem_rdata = memory[mem_addr[15:0]];
    end
  end

  always_ff @(posedge clk) begin
    if (mem_valid && mem_ready && mem_wstrb != 4'h0 && mem_addr < MEM_WORDS) begin
      if (mem_wstrb[0]) memory[mem_addr[15:0]][7:0] <= mem_wdata[7:0];
      if (mem_wstrb[1]) memory[mem_addr[15:0]][15:8] <= mem_wdata[15:8];
      if (mem_wstrb[2]) memory[mem_addr[15:0]][23:16] <= mem_wdata[23:16];
      if (mem_wstrb[3]) memory[mem_addr[15:0]][31:24] <= mem_wdata[31:24];
    end
  end

  always_ff @(posedge clk) begin
    if (rst_n && phase == 0 && capsule_stream_valid && capsule_stream_ready) begin
      if (replay_word_count >= MAX_REPLAY_WORDS) begin
        $fatal(1, "captured v2 stream exceeds testbench storage");
      end
      replay_words[replay_word_count] <= capsule_stream_word;
      if (trace_events != 0) begin
        $display("RC_FEMTO_V2_TRACE_CAPTURE index=%0d word=%016h", replay_word_count, capsule_stream_word);
      end
      replay_word_count <= replay_word_count + 1;
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      replay_consume_start <= 1'b0;
      replay_feed_index <= 0;
      replay_started <= 0;
    end else if (clear) begin
      replay_consume_start <= 1'b0;
      replay_feed_index <= 0;
      replay_started <= 0;
    end else begin
      replay_consume_start <= 1'b0;
      if (phase != 0) begin
        if (replay_started == 0) begin
          replay_consume_start <= 1'b1;
          replay_started <= 1;
        end else if (replay_consume_valid && replay_consume_ready) begin
          if (trace_events != 0) begin
            $display("RC_FEMTO_V2_TRACE_FEED index=%0d word=%016h", replay_feed_index, replay_consume_word);
          end
          if (replay_feed_index == 0) begin
            core_run_enable <= 1'b1;
          end
          replay_feed_index <= replay_feed_index + 1;
        end
      end
    end
  end

  always_comb begin
    replay_consume_valid = phase != 0 && replay_started != 0 && replay_feed_index < replay_word_count && replay_consume_ready;
    replay_consume_word = (replay_feed_index < replay_word_count) ? replay_words[replay_feed_index] : 64'h0;
    replay_consume_stream_done = 1'b0;
  end

  initial begin
    configure_test();
    rst_n = 1'b0;
    clear = 1'b0;
    irq_drive = 1'b0;
    phase = 0;
    cycle_index = 0;
    replay_word_count = 0;
    replay_feed_index = 0;
    replay_started = 0;
    replay_consume_start = 1'b0;
    irq_pulse_remaining = 0;
    core_run_enable = 1'b1;
    replay_consume_expected_count = 32'h0;
    recorded_property_id = 8'h0;
    recorded_property_signature = 32'h0;
    replay_observed_property_id = 8'h0;
    replay_observed_property_signature = 32'h0;

    reset_wrapper();

    forever begin
      @(posedge clk);
      #1;
      cycle_index = cycle_index + 1;
      if (property_fail_valid) begin
        if (property_id != expected_property[7:0]) begin
          $fatal(1, "expected property id %0d, got id %0d", expected_property, property_id);
        end
        if (phase == 0) begin
          recorded_property_id = property_id;
          recorded_property_signature = property_signature;
          repeat (20) @(posedge clk);
          #1;
          if (replay_word_count == 0) begin
            $fatal(1, "v2 stream did not capture any replay words");
          end
          replay_consume_expected_count = replay_word_count[31:0];
          phase = 1;
          core_run_enable = 1'b0;
          load_memory();
          reset_wrapper();
        end else begin
          replay_observed_property_id = property_id;
          replay_observed_property_signature = property_signature;
          if (property_id != recorded_property_id) begin
            $fatal(1, "replay property mismatch record=%0d replay=%0d", recorded_property_id, property_id);
          end
          if (require_signature_match != 0 && replay_observed_property_signature != recorded_property_signature) begin
            $fatal(
              1,
              "replay signature mismatch: record=%08x replay=%08x",
              recorded_property_signature,
              replay_observed_property_signature
            );
          end
          repeat (2) @(posedge clk);
          #1;
          if (replay_consume_error || !replay_consume_all_events || replay_consume_consumed_count != replay_word_count[31:0]) begin
            $fatal(
              1,
              "v2 Femto replay consumer did not consume the stream error=%0b code=%0d consumed=%0d expected=%0d all=%0b",
              replay_consume_error,
              replay_consume_error_code,
              replay_consume_consumed_count,
              replay_word_count,
              replay_consume_all_events
            );
          end
          $display(
            "RC_FEMTO_V2_REPLAY_SMOKE_PASS seed=%0d config=%0d property=%0d words=%0d consumed=%0d record_signature=%08x replay_signature=%08x signature_match=%0d replay_sensor_input=%0d changed_input=%0d replay_command_input=%0d changed_command=%0d require_signature_match=%0d",
            seed_value,
            recorder_config_select_value,
            replay_observed_property_id,
            replay_word_count,
            replay_consume_consumed_count,
            recorded_property_signature,
            replay_observed_property_signature,
            replay_observed_property_signature == recorded_property_signature,
            replay_sensor_value,
            replay_sensor_value != sensor_value,
            replay_command_value,
            replay_command_value != command_value,
            require_signature_match
          );
          $finish;
        end
      end
      if (replay_consume_error) begin
        if (trace_events != 0) begin
          $display(
            "RC_FEMTO_V2_TRACE_ERROR code=%0d consumed=%0d feed_index=%0d obs_valid=%0b obs_type=%0h obs_commit=%0d obs_addr=%08x obs_data=%08x obs_hash=%08x current_commit=%0d pending_word=%016h",
            replay_consume_error_code,
            replay_consume_consumed_count,
            replay_feed_index,
            replay_consume_observed_valid,
            u_wrapper.selected_captured_event_type,
            u_wrapper.selected_captured_event_commit_index,
            u_wrapper.selected_captured_event_addr,
            u_wrapper.selected_captured_event_data,
            u_wrapper.selected_captured_event_payload_hash,
            u_wrapper.commit_index,
            u_wrapper.u_rcv2_replay_consumer.pending_word
          );
        end
        $fatal(1, "v2 Femto replay consumer error code %0d", replay_consume_error_code);
      end
      if (cycle_index >= max_cycles) begin
        $fatal(1, "v2 Femto replay smoke timed out phase=%0d words=%0d consumed=%0d", phase, replay_word_count, replay_consume_consumed_count);
      end
    end
  end

  logic unused_trap;
  logic [63:0] unused_capsule_read_data;
  logic [31:0] unused_running_signature;
  logic [31:0] unused_stream_stats;
  assign unused_trap = trap;
  assign unused_capsule_read_data = capsule_read_data;
  assign unused_running_signature = running_signature;
  assign unused_stream_stats =
    capsule_stream_event_count ^
    capsule_stream_sent_count ^
    capsule_replay_critical_event_count ^
    capsule_stream_stall_count ^
    capsule_dropped_diagnostic_count ^
    capsule_replay_critical_overflow_count ^
    {23'h0, capsule_stream_fifo_level};

  always_ff @(posedge clk) begin
    if (trace_events != 0 && rst_n && phase != 0 && replay_consume_observed_valid) begin
      $display(
        "RC_FEMTO_V2_TRACE_OBS consumed=%0d feed_index=%0d ready=%0b valid=%0b type=%0h commit=%0d addr=%08x data=%08x hash=%08x current_commit=%0d",
        replay_consume_consumed_count,
        replay_feed_index,
        replay_consume_ready,
        replay_consume_valid,
        u_wrapper.selected_captured_event_type,
        u_wrapper.selected_captured_event_commit_index,
        u_wrapper.selected_captured_event_addr,
        u_wrapper.selected_captured_event_data,
        u_wrapper.selected_captured_event_payload_hash,
        u_wrapper.commit_index
      );
    end
  end
endmodule
