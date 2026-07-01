`timescale 1ns/1ps

module tb_picorv32_standalone_self_replay_smoke;
  localparam int MEM_WORDS = 256;
  localparam logic [31:0] RESET_PC = 32'h0000_0080;
  localparam logic [31:0] SENSOR_ADDR = 32'h4000_0000;
  localparam logic [31:0] COMMAND_ADDR = 32'h4000_000c;
  localparam logic [31:0] PROFILE2_SENSOR_ADDR = 32'h4000_0040;
  localparam logic [31:0] PROFILE2_COMMAND_ADDR = 32'h4000_004c;

  logic clk;
  logic rst_n;
  logic clear;
  logic trap;
  logic mem_valid;
  logic mem_instr;
  logic [31:0] mem_addr;
  logic [31:0] mem_wdata;
  logic [3:0] mem_wstrb;
  logic irq_drive;
  logic [31:0] eoi;
  logic [7:0] capsule_read_addr;
  logic [167:0] capsule_read_data;
  logic capsule_frozen;
  logic capsule_overflow;
  logic [8:0] capsule_event_count;
  logic [31:0] running_signature;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic capsule_stream_valid;
  logic [63:0] capsule_stream_word;
  logic [31:0] capsule_stream_event_count;
  logic [31:0] capsule_stream_sent_count;
  logic [31:0] capsule_replay_critical_event_count;
  logic [31:0] capsule_stream_stall_count;
  logic [31:0] capsule_dropped_diagnostic_count;
  logic [31:0] capsule_replay_critical_overflow_count;
  logic [8:0] capsule_stream_fifo_level;
  logic replay_consume_ready;
  logic replay_consume_observed_valid;
  logic replay_consume_all_events;
  logic replay_consume_error;
  logic [7:0] replay_consume_error_code;
  logic [31:0] replay_consume_consumed_count;
  logic replay_source_active;
  logic replay_source_stream_done;
  logic replay_source_underflow;
  logic replay_source_capture_ready;
  logic replay_source_capture_overflow;
  logic [31:0] replay_source_captured_count;
  logic [31:0] replay_source_sent_count;
  logic replay_controller_busy;
  logic replay_controller_record_active;
  logic replay_controller_replay_active;
  logic replay_controller_done;
  logic replay_controller_error;
  logic [7:0] replay_controller_state;
  logic [7:0] replay_controller_error_code;
  logic [31:0] commit_count;
  logic replay_controller_arm_record;
  logic replay_controller_start;
  logic replay_phase;
  logic imem_load_valid;
  logic [7:0] imem_load_addr;
  logic [31:0] imem_load_data;
  logic [31:0] imem_image [0:MEM_WORDS-1];
  string memfile;
  integer expected_property;
  integer sensor_value;
  integer command_value;
  integer recorder_config_value;
  integer watchdog_enable_value;
  integer irq_after_command_value;
  integer irq_pulse_cycles;
  integer max_cycles;
  integer phase_cycles;
  integer load_index;
  logic [7:0] record_property_id;
  logic [31:0] record_property_signature;
  logic [7:0] replay_property_id;
  logic [31:0] replay_property_signature;
  logic [31:0] record_captured_count;
  logic [31:0] record_irq_entry_count;
  logic [31:0] replay_irq_entry_count;
  logic [31:0] irq_entry_count;
  logic [31:0] eoi_q;

  replaycapsule_v2_self_replay_soc #(
    .MEM_WORDS(MEM_WORDS),
    .MEM_ADDR_W(8),
    .CAPSULE_DEPTH(256),
    .CAPSULE_ADDR_W(8)
  ) u_soc (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .imem_load_valid(imem_load_valid),
    .imem_load_addr(imem_load_addr),
    .imem_load_data(imem_load_data),
    .watchdog_enable(watchdog_enable_value != 0),
    .capture_mode(4'h3),
    .arch_select(2'd2),
    .recorder_config_select(recorder_config_value[1:0]),
    .replay_phase(replay_phase),
    .replay_controller_arm_record(replay_controller_arm_record),
    .replay_controller_start(replay_controller_start),
    .sensor_value(sensor_value[31:0]),
    .command_value(command_value[31:0]),
    .irq_after_command(irq_after_command_value != 0),
    .irq_pulse_cycles(irq_pulse_cycles[31:0]),
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
    .replay_source_active(replay_source_active),
    .replay_source_stream_done(replay_source_stream_done),
    .replay_source_underflow(replay_source_underflow),
    .replay_source_capture_ready(replay_source_capture_ready),
    .replay_source_capture_overflow(replay_source_capture_overflow),
    .replay_source_captured_count(replay_source_captured_count),
    .replay_source_sent_count(replay_source_sent_count),
    .replay_controller_busy(replay_controller_busy),
    .replay_controller_record_active(replay_controller_record_active),
    .replay_controller_replay_active(replay_controller_replay_active),
    .replay_controller_done(replay_controller_done),
    .replay_controller_error(replay_controller_error),
    .replay_controller_state(replay_controller_state),
    .replay_controller_error_code(replay_controller_error_code),
    .commit_count(commit_count),
    .trap(trap),
    .mem_valid(mem_valid),
    .mem_instr(mem_instr),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wstrb(mem_wstrb),
    .eoi(eoi),
    .irq_drive(irq_drive)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      eoi_q <= 32'h0;
      irq_entry_count <= 32'h0;
    end else begin
      eoi_q <= eoi;
      if (eoi != 32'h0 && eoi_q == 32'h0) begin
        irq_entry_count <= irq_entry_count + 32'h1;
      end
    end
  end

  initial begin
    memfile = "firmware/build/sensor_threshold_bug/failing.mem";
    expected_property = 3;
    sensor_value = 850;
    command_value = 0;
    recorder_config_value = 0;
    watchdog_enable_value = 0;
    irq_after_command_value = 0;
    irq_pulse_cycles = 24;
    max_cycles = 900;
    if (!$value$plusargs("MEMFILE=%s", memfile)) begin end
    if (!$value$plusargs("EXPECTED_PROPERTY=%d", expected_property)) begin end
    if (!$value$plusargs("SENSOR_VALUE=%d", sensor_value)) begin end
    if (!$value$plusargs("COMMAND_VALUE=%d", command_value)) begin end
    if (!$value$plusargs("RECORDER_CONFIG_SELECT=%d", recorder_config_value)) begin end
    if (!$value$plusargs("WATCHDOG_ENABLE=%d", watchdog_enable_value)) begin end
    if (!$value$plusargs("IRQ_AFTER_COMMAND=%d", irq_after_command_value)) begin end
    if (!$value$plusargs("IRQ_PULSE_CYCLES=%d", irq_pulse_cycles)) begin end
    if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin end
    if (recorder_config_value < 0 || recorder_config_value > 2) begin
      $fatal(1, "RECORDER_CONFIG_SELECT must be 0 core, 1 hashed, or 2 full");
    end
    if (irq_pulse_cycles < 1) begin
      $fatal(1, "IRQ_PULSE_CYCLES must be positive");
    end
    for (load_index = 0; load_index < MEM_WORDS; load_index = load_index + 1) begin
      imem_image[load_index] = 32'h0000_0013;
    end
    $readmemh(memfile, imem_image);
  end

  task automatic load_soc_memory;
    integer load_word_index;
    begin
      imem_load_valid = 1'b0;
      imem_load_addr = 8'h0;
      imem_load_data = 32'h0;
      repeat (2) @(posedge clk);
      for (load_word_index = 0; load_word_index < MEM_WORDS; load_word_index = load_word_index + 1) begin
        @(negedge clk);
        imem_load_addr = load_word_index[7:0];
        imem_load_data = imem_image[load_word_index];
        imem_load_valid = 1'b1;
        @(posedge clk);
        #1;
      end
      @(negedge clk);
      imem_load_valid = 1'b0;
      imem_load_addr = 8'h0;
      imem_load_data = 32'h0;
    end
  endtask

  task automatic reset_core_only;
    begin
      rst_n = 1'b0;
      clear = 1'b0;
      capsule_read_addr = 8'h0;
      repeat (5) @(posedge clk);
      rst_n = 1'b1;
    end
  endtask

  task automatic run_until_property_failure;
    input logic expect_replay;
    begin
      phase_cycles = 0;
      while (phase_cycles < max_cycles && !property_fail_valid) begin
        @(posedge clk);
        #1;
        phase_cycles = phase_cycles + 1;
        if (replay_consume_error) begin
          $fatal(1, "replay consumer error code %0d", replay_consume_error_code);
        end
        if (replay_controller_error) begin
          $fatal(1, "replay controller error code %0d state %0d", replay_controller_error_code, replay_controller_state);
        end
      end
      if (!property_fail_valid) begin
        $fatal(
          1,
          "property failure did not occur in phase replay=%0b captured=%0d sent=%0d consumed=%0d all=%0b source_active=%0b source_done=%0b controller_state=%0d controller_done=%0b commit=%0d",
          expect_replay,
          replay_source_captured_count,
          replay_source_sent_count,
          replay_consume_consumed_count,
          replay_consume_all_events,
          replay_source_active,
          replay_source_stream_done,
          replay_controller_state,
          replay_controller_done,
          commit_count
        );
      end
      if (property_id != expected_property[7:0]) begin
        $fatal(1, "expected property id %0d, got %0d", expected_property, property_id);
      end
    end
  endtask

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    capsule_read_addr = 8'h0;
    replay_controller_arm_record = 1'b0;
    replay_controller_start = 1'b0;
    replay_phase = 1'b0;
    imem_load_valid = 1'b0;
    imem_load_addr = 8'h0;
    imem_load_data = 32'h0;
    record_property_id = 8'h0;
    record_property_signature = 32'h0;
    replay_property_id = 8'h0;
    replay_property_signature = 32'h0;
    record_captured_count = 32'h0;
    record_irq_entry_count = 32'h0;
    replay_irq_entry_count = 32'h0;

    #1;
    load_soc_memory();
    reset_core_only();
    replay_controller_arm_record = 1'b1;
    @(posedge clk);
    #1;
    replay_controller_arm_record = 1'b0;
    run_until_property_failure(1'b0);
    record_property_id = property_id;
    record_property_signature = property_signature;
    repeat (20) @(posedge clk);
    #1;
    if (!capsule_frozen) begin
      $fatal(1, "record capsule did not freeze on property failure");
    end
    if (replay_source_capture_overflow) begin
      $fatal(
        1,
        "record replay source overflowed capsule=%0b replay_critical_overflow_counter=%0d source=%0b captured=%0d stream_events=%0d sent=%0d",
        capsule_overflow,
        capsule_replay_critical_overflow_count,
        replay_source_capture_overflow,
        replay_source_captured_count,
        capsule_stream_event_count,
        capsule_stream_sent_count
      );
    end
    record_captured_count = replay_source_captured_count;
    if (record_captured_count == 0) begin
      $fatal(1, "replay source did not capture any replay-critical words");
    end
    if (record_captured_count != capsule_replay_critical_event_count) begin
      $fatal(
        1,
        "captured replay-critical count mismatch source=%0d recorder=%0d",
        record_captured_count,
        capsule_replay_critical_event_count
      );
    end

    replay_phase = 1'b1;
    record_irq_entry_count = irq_entry_count;
    if (irq_after_command_value != 0 && record_irq_entry_count == 0) begin
      $fatal(1, "record phase did not enter the PicoRV32 interrupt handler");
    end
    reset_core_only();
    replay_controller_start = 1'b1;
    @(posedge clk);
    #1;
    replay_controller_start = 1'b0;
    run_until_property_failure(1'b1);
    replay_property_id = property_id;
    replay_property_signature = property_signature;
    replay_irq_entry_count = irq_entry_count;
    repeat (5) @(posedge clk);
    #1;
    if (replay_property_id != record_property_id || replay_property_signature != record_property_signature) begin
      $fatal(
        1,
        "replay property/signature mismatch record_property=%0d replay_property=%0d record_signature=%08x replay_signature=%08x consumed=%0d expected=%0d",
        record_property_id,
        replay_property_id,
        record_property_signature,
        replay_property_signature,
        replay_consume_consumed_count,
        record_captured_count
      );
    end
    if (!replay_consume_all_events || replay_consume_consumed_count != record_captured_count) begin
      $fatal(
        1,
        "replay consumer did not consume captured store count consumed=%0d expected=%0d all=%0b",
        replay_consume_consumed_count,
        record_captured_count,
        replay_consume_all_events
      );
    end
    if (replay_source_sent_count != record_captured_count || replay_source_underflow) begin
      $fatal(1, "replay source did not stream captured store cleanly");
    end
    if (!replay_controller_done) begin
      $fatal(1, "replay controller did not reach done");
    end
    if (irq_after_command_value != 0) begin
      if (replay_irq_entry_count == 0) begin
        $fatal(1, "replay phase did not enter the PicoRV32 interrupt handler");
      end
      if (replay_irq_entry_count != record_irq_entry_count) begin
        $fatal(
          1,
          "record/replay IRQ entry count mismatch record=%0d replay=%0d",
          record_irq_entry_count,
          replay_irq_entry_count
        );
      end
    end
    $display(
      "RC_STANDALONE_SELF_REPLAY_PASS shell=rtl_self_replay_soc property=%0d captured=%0d sent=%0d consumed=%0d controller_done=%0d irq_record=%0d irq_replay=%0d signature=%08x",
      replay_property_id,
      record_captured_count,
      replay_source_sent_count,
      replay_consume_consumed_count,
      replay_controller_done,
      record_irq_entry_count,
      replay_irq_entry_count,
      replay_property_signature
    );
    $finish;
  end

  logic unused_trap;
  logic [31:0] unused_mem_wdata;
  logic [31:0] unused_eoi;
  logic [167:0] unused_capsule_read_data;
  logic [63:0] unused_capsule_stream_word;
  logic unused_replay_consume_ready;
  logic unused_replay_consume_observed_valid;
  logic unused_replay_source_active;
  logic unused_replay_source_capture_ready;
  logic unused_replay_controller_busy;
  logic unused_replay_controller_record_active;
  logic unused_replay_controller_replay_active;
  logic [31:0] unused_running_signature;
  logic [31:0] unused_commit_count;

  assign unused_trap = trap;
  assign unused_mem_wdata = mem_wdata;
  assign unused_eoi = eoi ^ eoi_q;
  assign unused_capsule_read_data = capsule_read_data;
  assign unused_capsule_stream_word = capsule_stream_word;
  assign unused_replay_consume_ready = replay_consume_ready;
  assign unused_replay_consume_observed_valid = replay_consume_observed_valid;
  assign unused_replay_source_active = replay_source_active;
  assign unused_replay_source_capture_ready = replay_source_capture_ready;
  assign unused_replay_controller_busy = replay_controller_busy;
  assign unused_replay_controller_record_active = replay_controller_record_active;
  assign unused_replay_controller_replay_active = replay_controller_replay_active;
  assign unused_running_signature = running_signature;
  assign unused_commit_count = commit_count;
endmodule
