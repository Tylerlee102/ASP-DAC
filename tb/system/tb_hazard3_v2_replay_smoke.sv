`timescale 1ns/1ps

module tb_hazard3_v2_replay_smoke;
  localparam int MEM_WORDS = 8192;
  localparam int MAX_REPLAY_WORDS = 256;
  localparam logic [31:0] SENSOR_ADDR = 32'h4000_0000;
  localparam logic [31:0] IRQ_ACK_ADDR = 32'h4000_0014;
  localparam logic [31:0] DONE_ADDR = 32'h4000_0008;
  localparam logic [31:0] COMMAND_ADDR = 32'h4000_000c;
  localparam logic [31:0] ISR_MARK_ADDR = 32'h4000_0010;
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
  logic [31:0] record_irq_entry_count;
  logic [31:0] replay_irq_entry_count;
  logic [31:0] record_mmio_read_count;
  logic [31:0] replay_mmio_read_count;
  logic [31:0] replay_mmio_drive_count;
  logic [31:0] replay_irq_drive_count;
  logic core_run_enable;
  logic irq_drive;
  logic [31:0] memory [0:MEM_WORDS-1];
  logic [63:0] replay_words [0:MAX_REPLAY_WORDS-1];

  string memfile;
  integer expected_property;
  integer sensor_value;
  integer replay_sensor_value;
  integer recorder_config_select_value;
  integer watchdog_enable_value;
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
  logic [31:0] record_irq_entry_snapshot;
  logic [31:0] record_mmio_read_snapshot;

  hazard3_replaycapsule_v2_wrapper u_wrapper (
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
    .replay_consume_consumed_count(replay_consume_consumed_count),
    .record_irq_entry_count(record_irq_entry_count),
    .replay_irq_entry_count(replay_irq_entry_count),
    .record_mmio_read_count(record_mmio_read_count),
    .replay_mmio_read_count(replay_mmio_read_count),
    .replay_mmio_drive_count(replay_mmio_drive_count),
    .replay_irq_drive_count(replay_irq_drive_count)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;
  assign capsule_stream_ready = 1'b1;
  assign replay_consume_stream_done = 1'b0;
  assign mem_ready = 1'b1;
  assign irq = {31'h0, irq_drive};

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
      memfile = "build/hazard3_replay_smoke/hazard3_replay_smoke.mem";
      expected_property = 2;
      sensor_value = 650;
      replay_sensor_value = 1;
      recorder_config_select_value = 0;
      watchdog_enable_value = 0;
      require_signature_match = 1;
      trace_events = 0;
      max_cycles = 4000;
      if (!$value$plusargs("MEMFILE=%s", memfile)) begin end
      if (!$value$plusargs("EXPECTED_PROPERTY=%d", expected_property)) begin end
      if (!$value$plusargs("SENSOR_VALUE=%d", sensor_value)) begin end
      if (!$value$plusargs("REPLAY_SENSOR_VALUE=%d", replay_sensor_value)) begin end
      if (!$value$plusargs("RECORDER_CONFIG_SELECT=%d", recorder_config_select_value)) begin end
      if (!$value$plusargs("WATCHDOG_ENABLE=%d", watchdog_enable_value)) begin end
      if (!$value$plusargs("REQUIRE_SIGNATURE_MATCH=%d", require_signature_match)) begin end
      if (!$value$plusargs("TRACE_EVENTS=%d", trace_events)) begin end
      if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin end
      if (recorder_config_select_value < 0 || recorder_config_select_value > 2) begin
        $fatal(1, "Hazard3 replay smoke supports RECORDER_CONFIG_SELECT values 0, 1, or 2");
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
      replay_consume_start = 1'b0;
      replay_started = 0;
      replay_feed_index = 0;
      repeat (6) @(posedge clk);
      clear = 1'b0;
      rst_n = 1'b1;
    end
  endtask

  always_comb begin
    mem_rdata = NOP;
    if (mem_addr[31:16] == 16'h4000) begin
      if (mem_addr == SENSOR_ADDR || mem_addr == PROFILE2_SENSOR_ADDR) begin
        mem_rdata = (phase == 0) ? sensor_value[31:0] : replay_sensor_value[31:0];
      end else begin
        mem_rdata = 32'h0;
      end
    end else if (mem_addr[31:2] < MEM_WORDS) begin
      mem_rdata = memory[mem_addr[31:2]];
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      irq_drive <= 1'b0;
    end else if (clear) begin
      irq_drive <= 1'b0;
    end else if (mem_valid && mem_ready && mem_wstrb != 4'h0) begin
      if (mem_addr[31:16] == 16'h4000) begin
        if (trace_events != 0) begin
          $display("RC_HAZARD3_V2_TRACE_WRITE phase=%0d cycle=%0d addr=%08x data=%08x wstrb=%0h", phase, cycle_index, mem_addr, mem_wdata, mem_wstrb);
        end
        if (phase == 0 && (mem_addr == COMMAND_ADDR || mem_addr == PROFILE2_COMMAND_ADDR) && mem_wdata != 32'h0) begin
          irq_drive <= 1'b1;
        end else if (phase == 0 && mem_addr == IRQ_ACK_ADDR) begin
          irq_drive <= 1'b0;
        end
      end else if (mem_addr[31:2] < MEM_WORDS) begin
        if (mem_wstrb[0]) memory[mem_addr[31:2]][7:0] <= mem_wdata[7:0];
        if (mem_wstrb[1]) memory[mem_addr[31:2]][15:8] <= mem_wdata[15:8];
        if (mem_wstrb[2]) memory[mem_addr[31:2]][23:16] <= mem_wdata[23:16];
        if (mem_wstrb[3]) memory[mem_addr[31:2]][31:24] <= mem_wdata[31:24];
      end
    end
  end

  always_ff @(posedge clk) begin
    if (rst_n && phase == 0 && capsule_stream_valid && capsule_stream_ready) begin
      if (replay_word_count >= MAX_REPLAY_WORDS) begin
        $fatal(1, "captured Hazard3 v2 stream exceeds testbench storage");
      end
      replay_words[replay_word_count] <= capsule_stream_word;
      if (trace_events != 0) begin
        $display("RC_HAZARD3_V2_TRACE_CAPTURE index=%0d word=%016h", replay_word_count, capsule_stream_word);
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
            $display("RC_HAZARD3_V2_TRACE_FEED index=%0d word=%016h", replay_feed_index, replay_consume_word);
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
  end

  initial begin
    configure_test();
    rst_n = 1'b0;
    clear = 1'b0;
    phase = 0;
    cycle_index = 0;
    replay_word_count = 0;
    replay_feed_index = 0;
    replay_started = 0;
    replay_consume_start = 1'b0;
    core_run_enable = 1'b1;
    replay_consume_expected_count = 32'h0;
    recorded_property_id = 8'h0;
    recorded_property_signature = 32'h0;
    replay_observed_property_id = 8'h0;
    replay_observed_property_signature = 32'h0;
    record_irq_entry_snapshot = 32'h0;
    record_mmio_read_snapshot = 32'h0;

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
          repeat (24) @(posedge clk);
          #1;
          record_irq_entry_snapshot = record_irq_entry_count;
          record_mmio_read_snapshot = record_mmio_read_count;
          if (replay_word_count == 0) begin
            $fatal(1, "Hazard3 v2 stream did not capture any replay words");
          end
          if (record_irq_entry_snapshot == 32'h0 || record_mmio_read_snapshot == 32'h0) begin
            $fatal(1, "Hazard3 record did not observe both MMIO read and ISR entry record_irq=%0d record_mmio=%0d", record_irq_entry_snapshot, record_mmio_read_snapshot);
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
            $fatal(1, "Hazard3 replay property mismatch record=%0d replay=%0d", recorded_property_id, property_id);
          end
          if (require_signature_match != 0 && replay_observed_property_signature != recorded_property_signature) begin
            $fatal(
              1,
              "Hazard3 replay signature mismatch: record=%08x replay=%08x",
              recorded_property_signature,
              replay_observed_property_signature
            );
          end
          repeat (4) @(posedge clk);
          #1;
          if (replay_consume_error || !replay_consume_all_events || replay_consume_consumed_count != replay_word_count[31:0]) begin
            $fatal(
              1,
              "Hazard3 v2 replay consumer did not consume the stream error=%0b code=%0d consumed=%0d expected=%0d all=%0b",
              replay_consume_error,
              replay_consume_error_code,
              replay_consume_consumed_count,
              replay_word_count,
              replay_consume_all_events
            );
          end
          if (
            replay_irq_entry_count == 32'h0 ||
            replay_mmio_read_count == 32'h0 ||
            replay_mmio_drive_count == 32'h0 ||
            replay_irq_drive_count == 32'h0
          ) begin
            $fatal(
              1,
              "Hazard3 replay did not prove both replay-driven MMIO and IRQ record_irq=%0d replay_irq=%0d record_mmio=%0d replay_mmio=%0d mmio_drive=%0d irq_drive=%0d",
              record_irq_entry_snapshot,
              replay_irq_entry_count,
              record_mmio_read_snapshot,
              replay_mmio_read_count,
              replay_mmio_drive_count,
              replay_irq_drive_count
            );
          end
          $display(
            "RC_HAZARD3_V2_REPLAY_SMOKE_PASS cycles=%0d config=%0d property=%0d words=%0d consumed=%0d record_signature=%08x replay_signature=%08x signature_match=%0d record_irq_entries=%0d replay_irq_entries=%0d record_mmio_reads=%0d replay_mmio_reads=%0d replay_mmio_drives=%0d replay_irq_drives=%0d external_irq_replay=%0d sensor_value=%0d replay_sensor_value=%0d",
            cycle_index,
            recorder_config_select_value,
            replay_observed_property_id,
            replay_word_count,
            replay_consume_consumed_count,
            recorded_property_signature,
            replay_observed_property_signature,
            replay_observed_property_signature == recorded_property_signature,
            record_irq_entry_snapshot,
            replay_irq_entry_count,
            record_mmio_read_snapshot,
            replay_mmio_read_count,
            replay_mmio_drive_count,
            replay_irq_drive_count,
            irq_drive,
            sensor_value,
            replay_sensor_value
          );
          $finish;
        end
      end
      if (replay_consume_error) begin
        if (trace_events != 0) begin
          $display(
            "RC_HAZARD3_V2_TRACE_ERROR code=%0d consumed=%0d feed_index=%0d obs_valid=%0b obs_type=%0h obs_commit=%0d obs_addr=%08x obs_data=%08x obs_hash=%08x current_commit=%0d pending_word=%016h",
            replay_consume_error_code,
            replay_consume_consumed_count,
            replay_feed_index,
            replay_consume_observed_valid,
            u_wrapper.captured_event_type,
            u_wrapper.captured_event_commit_index,
            u_wrapper.captured_event_addr,
            u_wrapper.captured_event_data,
            u_wrapper.captured_event_payload_hash,
            u_wrapper.commit_index,
            u_wrapper.u_rcv2_replay_consumer.pending_word
          );
        end
        $fatal(1, "Hazard3 v2 replay consumer error code %0d", replay_consume_error_code);
      end
      if (cycle_index >= max_cycles) begin
        $fatal(1, "Hazard3 v2 replay smoke timed out phase=%0d words=%0d consumed=%0d", phase, replay_word_count, replay_consume_consumed_count);
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
        "RC_HAZARD3_V2_TRACE_OBS consumed=%0d feed_index=%0d ready=%0b valid=%0b type=%0h commit=%0d addr=%08x data=%08x hash=%08x current_commit=%0d",
        replay_consume_consumed_count,
        replay_feed_index,
        replay_consume_ready,
        replay_consume_valid,
        u_wrapper.captured_event_type,
        u_wrapper.captured_event_commit_index,
        u_wrapper.captured_event_addr,
        u_wrapper.captured_event_data,
        u_wrapper.captured_event_payload_hash,
        u_wrapper.commit_index
      );
    end
  end
endmodule
