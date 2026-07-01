`timescale 1ns/1ps

module tb_femtorv32_wrapper_smoke;
  localparam int MEM_WORDS = 65536;
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
  logic mem_ready;
  logic [31:0] mem_addr;
  logic [31:0] mem_wdata;
  logic [3:0] mem_wstrb;
  logic [31:0] mem_rdata;
  logic [31:0] irq;
  logic irq_drive;
  logic [7:0] capsule_read_addr;
  logic [167:0] capsule_read_data;
  logic capsule_frozen;
  logic capsule_overflow;
  logic [8:0] capsule_event_count;
  logic [31:0] running_signature;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic watchdog_enable_signal;
  logic [31:0] memory [0:MEM_WORDS-1];
  string memfile;
  integer expected_property;
  integer sensor_value;
  integer command_value;
  integer watchdog_enable_value;
  integer irq_after_command_value;
  integer irq_pulse_cycles;
  integer irq_pulse_remaining;
  integer capture_mode_value;
  integer max_cycles;
  integer dump_capsule;
  integer replay_from_capture;
  integer replay_packet_index;
  integer trace_mem;
  integer cycle_index;
  integer phase;
  integer recorded_count;
  integer replay_sensor_value;
  integer replay_command_value;
  integer found_sensor_packet;
  integer found_command_packet;
  logic [7:0] observed_property_id;
  logic [31:0] observed_property_signature;
  logic [7:0] recorded_property_id;
  logic [31:0] recorded_property_signature;
  logic [167:0] recorded_capsule [0:255];
  logic [3:0] capture_mode_signal;
  logic v1_checker_start;
  logic [31:0] v1_checker_expected_count;
  logic v1_checker_check_valid;
  logic [167:0] v1_checker_expected_packet;
  logic [167:0] v1_checker_observed_packet;
  logic v1_checker_finish;
  logic v1_checker_active;
  logic v1_checker_consumed_all_events;
  logic v1_checker_replay_error;
  logic [7:0] v1_checker_replay_error_code;
  logic [31:0] v1_checker_consumed_count;
  logic [31:0] v1_checker_mismatch_index;
  logic v1_mmio_store_clear;
  logic v1_mmio_load_valid;
  logic [7:0] v1_mmio_load_addr;
  logic [167:0] v1_mmio_load_packet;
  logic v1_mmio_observed_valid;
  logic v1_mmio_observed_read;
  logic v1_mmio_replay_valid;
  logic [31:0] v1_mmio_replay_value;
  logic [31:0] v1_mmio_loaded_count;
  logic [31:0] v1_mmio_hit_count;
  logic v1_mmio_replay_miss;

  assign capture_mode_signal = capture_mode_value[3:0];

  femtorv32_replaycapsule_wrapper u_wrapper (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable_signal),
    .capture_mode(capture_mode_signal),
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
    .property_signature(property_signature)
  );

  rcv1_capsule_replay_checker u_v1_replay_checker (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .start(v1_checker_start),
    .expected_event_count(v1_checker_expected_count),
    .check_valid(v1_checker_check_valid),
    .expected_packet(v1_checker_expected_packet),
    .observed_packet(v1_checker_observed_packet),
    .finish(v1_checker_finish),
    .active(v1_checker_active),
    .consumed_all_events(v1_checker_consumed_all_events),
    .replay_error(v1_checker_replay_error),
    .replay_error_code(v1_checker_replay_error_code),
    .consumed_count(v1_checker_consumed_count),
    .mismatch_index(v1_checker_mismatch_index)
  );

  rcv1_mmio_replay_driver #(
    .DEPTH(256),
    .ADDR_W(8),
    .EVENT_WIDTH(168)
  ) u_v1_mmio_replay_driver (
    .clk(clk),
    .rst_n(1'b1),
    .store_clear(v1_mmio_store_clear),
    .load_valid(v1_mmio_load_valid),
    .load_addr(v1_mmio_load_addr),
    .load_packet(v1_mmio_load_packet),
    .replay_enable(phase != 0),
    .observed_valid(v1_mmio_observed_valid),
    .observed_mmio_read(v1_mmio_observed_read),
    .observed_addr(mem_addr),
    .replay_valid(v1_mmio_replay_valid),
    .replay_value(v1_mmio_replay_value),
    .loaded_count(v1_mmio_loaded_count),
    .hit_count(v1_mmio_hit_count),
    .replay_miss(v1_mmio_replay_miss)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;
  assign watchdog_enable_signal = (watchdog_enable_value != 0);
  assign irq = {31'h0, irq_drive};

  task automatic load_memory;
    integer load_index;
    begin
      for (load_index = 0; load_index < MEM_WORDS; load_index = load_index + 1) begin
        memory[load_index] = 32'h0000_0013;
      end
      $readmemh(memfile, memory);
    end
  endtask

  task automatic configure_test;
    begin
      memfile = "firmware/build/sensor_threshold_bug/failing.hex";
      expected_property = 3;
      sensor_value = 850;
      command_value = 0;
      watchdog_enable_value = 0;
      irq_after_command_value = 0;
      irq_pulse_cycles = 24;
      irq_pulse_remaining = 0;
      capture_mode_value = 3;
      max_cycles = 700;
      dump_capsule = 0;
      replay_from_capture = 0;
      replay_packet_index = 1;
      trace_mem = 0;
      if (!$value$plusargs("MEMFILE=%s", memfile)) begin end
      if (!$value$plusargs("EXPECTED_PROPERTY=%d", expected_property)) begin end
      if (!$value$plusargs("SENSOR_VALUE=%d", sensor_value)) begin end
      if (!$value$plusargs("COMMAND_VALUE=%d", command_value)) begin end
      if (!$value$plusargs("WATCHDOG_ENABLE=%d", watchdog_enable_value)) begin end
      if (!$value$plusargs("IRQ_AFTER_COMMAND=%d", irq_after_command_value)) begin end
      if (!$value$plusargs("IRQ_PULSE_CYCLES=%d", irq_pulse_cycles)) begin end
      if (!$value$plusargs("CAPTURE_MODE=%d", capture_mode_value)) begin end
      if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin end
      if (!$value$plusargs("DUMP_CAPSULE=%d", dump_capsule)) begin end
      if (!$value$plusargs("REPLAY_FROM_CAPTURE=%d", replay_from_capture)) begin end
      if (!$value$plusargs("REPLAY_PACKET_INDEX=%d", replay_packet_index)) begin end
      if (!$value$plusargs("TRACE_MEM=%d", trace_mem)) begin end
      load_memory();
      if (replay_from_capture != 0 && expected_property == 0) begin
        $fatal(1, "REPLAY_FROM_CAPTURE requires an expected property failure");
      end
      if (replay_packet_index < 0 || replay_packet_index > 255) begin
        $fatal(1, "REPLAY_PACKET_INDEX is outside the capsule read range");
      end
      if (irq_pulse_cycles < 1) begin
        $fatal(1, "IRQ_PULSE_CYCLES must be positive");
      end
      if (capture_mode_value < 0 || capture_mode_value > 3) begin
        $fatal(1, "CAPTURE_MODE must be 0 all, 1 mmio/interrupt, 2 property-aware, or 3 ReplayCapsule default");
      end
    end
  endtask

  task automatic reset_wrapper;
    begin
      rst_n = 1'b0;
      clear = 1'b1;
      capsule_read_addr = 8'h0;
      cycle_index = 0;
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
          mem_addr == COMMAND_ADDR &&
          mem_wdata[0]
        ) begin
          irq_pulse_remaining <= irq_pulse_cycles;
        end
      end
    end
  end

  task automatic dump_capsule_events;
    input logic [7:0] dump_property_id;
    input logic [31:0] dump_property_signature;
    integer dump_index;
    begin
      $display(
        "RC_FEMTO_CAPSULE_BEGIN count=%0d property=%0d signature=%08x frozen=%0b overflow=%0b",
        capsule_event_count,
        dump_property_id,
        dump_property_signature,
        capsule_frozen,
        capsule_overflow
      );
      for (dump_index = 0; dump_index < capsule_event_count; dump_index = dump_index + 1) begin
        capsule_read_addr = dump_index[7:0];
        #1;
        $display("RC_FEMTO_CAPSULE_EVENT index=%0d packet=%042h", dump_index, capsule_read_data);
      end
      $display("RC_FEMTO_CAPSULE_END");
    end
  endtask

  task automatic record_current_capsule;
    integer record_index;
    begin
      if (capsule_event_count > 9'd256) begin
        $fatal(1, "captured capsule has more events than the replay smoke can compare");
      end
      recorded_count = capsule_event_count;
      recorded_property_id = observed_property_id;
      recorded_property_signature = observed_property_signature;
      for (record_index = 0; record_index < recorded_count; record_index = record_index + 1) begin
        capsule_read_addr = record_index[7:0];
        #1;
        recorded_capsule[record_index] = capsule_read_data;
      end
    end
  endtask

  task automatic derive_replay_stimulus_from_record;
    integer scan_index;
    logic [3:0] event_type;
    logic [31:0] event_addr;
    logic [31:0] event_data;
    begin
      found_sensor_packet = 0;
      found_command_packet = 0;
      replay_sensor_value = sensor_value;
      replay_command_value = command_value;
      for (scan_index = 0; scan_index < recorded_count; scan_index = scan_index + 1) begin
        event_type = recorded_capsule[scan_index][167:164];
        event_addr = recorded_capsule[scan_index][63:32];
        event_data = recorded_capsule[scan_index][31:0];
        if (event_type == 4'h5 && (event_addr == SENSOR_ADDR || event_addr == PROFILE2_SENSOR_ADDR)) begin
          replay_sensor_value = event_data;
          found_sensor_packet = 1;
        end
        if (event_type == 4'h5 && (event_addr == COMMAND_ADDR || event_addr == PROFILE2_COMMAND_ADDR)) begin
          replay_command_value = event_data;
          found_command_packet = 1;
        end
      end
      sensor_value = replay_sensor_value;
      command_value = replay_command_value;
    end
  endtask

  task automatic load_mmio_replay_driver_from_record;
    integer load_packet_index;
    begin
      v1_mmio_store_clear = 1'b1;
      @(posedge clk);
      #1;
      v1_mmio_store_clear = 1'b0;
      for (load_packet_index = 0; load_packet_index < recorded_count; load_packet_index = load_packet_index + 1) begin
        v1_mmio_load_addr = load_packet_index[7:0];
        v1_mmio_load_packet = recorded_capsule[load_packet_index];
        v1_mmio_load_valid = 1'b1;
        @(posedge clk);
        #1;
      end
      v1_mmio_load_valid = 1'b0;
      v1_mmio_load_addr = 8'h0;
      v1_mmio_load_packet = 168'h0;
      if (v1_mmio_loaded_count != recorded_count[31:0]) begin
        $fatal(1, "v1 MMIO replay driver loaded_count=%0d expected=%0d", v1_mmio_loaded_count, recorded_count);
      end
    end
  endtask

  task automatic compare_current_capsule_to_record;
    integer compare_index;
    begin
      if (capsule_event_count != recorded_count[8:0]) begin
        $fatal(1, "replay capsule count mismatch: record %0d replay %0d", recorded_count, capsule_event_count);
      end
      if (observed_property_id != recorded_property_id) begin
        $fatal(1, "replay property id mismatch: record %0d replay %0d", recorded_property_id, observed_property_id);
      end
      if (observed_property_signature != recorded_property_signature) begin
        $fatal(
          1,
          "replay signature mismatch: record %08x replay %08x",
          recorded_property_signature,
          observed_property_signature
        );
      end
      v1_checker_expected_count = recorded_count[31:0];
      v1_checker_start = 1'b1;
      @(posedge clk);
      #1;
      v1_checker_start = 1'b0;
      for (compare_index = 0; compare_index < recorded_count; compare_index = compare_index + 1) begin
        capsule_read_addr = compare_index[7:0];
        #1;
        v1_checker_expected_packet = recorded_capsule[compare_index];
        v1_checker_observed_packet = capsule_read_data;
        v1_checker_check_valid = 1'b1;
        @(posedge clk);
        #1;
        v1_checker_check_valid = 1'b0;
        if (v1_checker_replay_error) begin
          $fatal(
            1,
            "v1 replay checker error code %0d at index %0d: record %042h replay %042h",
            v1_checker_replay_error_code,
            v1_checker_mismatch_index,
            v1_checker_expected_packet,
            v1_checker_observed_packet
          );
        end
      end
      v1_checker_finish = 1'b1;
      @(posedge clk);
      #1;
      v1_checker_finish = 1'b0;
      if (v1_checker_replay_error || !v1_checker_consumed_all_events || v1_checker_consumed_count != recorded_count[31:0]) begin
        $fatal(
          1,
          "v1 replay checker did not consume all packets error=%0b code=%0d consumed=%0d expected=%0d all=%0b",
          v1_checker_replay_error,
          v1_checker_replay_error_code,
          v1_checker_consumed_count,
          recorded_count,
          v1_checker_consumed_all_events
        );
      end
    end
  endtask

  always_comb begin
    mem_ready = mem_valid;
    mem_rdata = 32'h0000_0013;
    if ((phase != 0) && v1_mmio_observed_read) begin
      mem_rdata = v1_mmio_replay_valid ? v1_mmio_replay_value : 32'h0;
    end else if (mem_addr == SENSOR_ADDR || mem_addr == PROFILE2_SENSOR_ADDR) begin
      mem_rdata = sensor_value[31:0];
    end else if (mem_addr == COMMAND_ADDR || mem_addr == PROFILE2_COMMAND_ADDR) begin
      mem_rdata = command_value[31:0];
    end else if (mem_addr < MEM_WORDS) begin
      mem_rdata = memory[mem_addr[15:0]];
    end
  end

  always_comb begin
    v1_mmio_observed_valid = (phase != 0) && rst_n && mem_valid && mem_ready;
    v1_mmio_observed_read = v1_mmio_observed_valid && !mem_instr && mem_wstrb == 4'h0 && mem_addr[31:16] == 16'h4000;
  end

  always_ff @(posedge clk) begin
    if (mem_valid && mem_ready && mem_wstrb != 4'h0 && mem_addr < MEM_WORDS) begin
      if (mem_wstrb[0]) memory[mem_addr[15:0]][7:0] <= mem_wdata[7:0];
      if (mem_wstrb[1]) memory[mem_addr[15:0]][15:8] <= mem_wdata[15:8];
      if (mem_wstrb[2]) memory[mem_addr[15:0]][23:16] <= mem_wdata[23:16];
      if (mem_wstrb[3]) memory[mem_addr[15:0]][31:24] <= mem_wdata[31:24];
    end
  end

  always @(negedge clk) begin
    if (trace_mem != 0 && rst_n && mem_valid && mem_ready) begin
      $display(
        "RC_FEMTO_MEM_PRE cycle=%0d instr=%0b write=%0b addr=%08x wdata=%08x rdata=%08x count=%0d frozen=%0b prop=%0b/%0d",
        cycle_index,
        mem_instr,
        mem_wstrb != 4'h0,
        mem_addr,
        mem_wdata,
        mem_rdata,
        capsule_event_count,
        capsule_frozen,
        property_fail_valid,
        property_id
      );
    end
  end

  initial begin
    configure_test();
    rst_n = 1'b0;
    clear = 1'b0;
    irq_drive = 1'b0;
    capsule_read_addr = 8'h0;
    cycle_index = 0;
    phase = 0;
    recorded_count = 0;
    replay_sensor_value = 0;
    replay_command_value = 0;
    found_sensor_packet = 0;
    found_command_packet = 0;
    observed_property_id = 8'h0;
    observed_property_signature = 32'h0;
    recorded_property_id = 8'h0;
    recorded_property_signature = 32'h0;
    v1_checker_start = 1'b0;
    v1_checker_expected_count = 32'h0;
    v1_checker_check_valid = 1'b0;
    v1_checker_expected_packet = 168'h0;
    v1_checker_observed_packet = 168'h0;
    v1_checker_finish = 1'b0;
    v1_mmio_store_clear = 1'b1;
    v1_mmio_load_valid = 1'b0;
    v1_mmio_load_addr = 8'h0;
    v1_mmio_load_packet = 168'h0;

    reset_wrapper();
    @(posedge clk);
    #1;
    v1_mmio_store_clear = 1'b0;

    forever begin
      @(posedge clk);
      #1;
      cycle_index = cycle_index + 1;
      if (trace_mem != 0 && mem_valid && mem_ready) begin
        $display(
          "RC_FEMTO_MEM cycle=%0d instr=%0b write=%0b addr=%08x wdata=%08x rdata=%08x count=%0d frozen=%0b prop=%0b/%0d",
          cycle_index,
          mem_instr,
          mem_wstrb != 4'h0,
          mem_addr,
          mem_wdata,
          mem_rdata,
          capsule_event_count,
          capsule_frozen,
          property_fail_valid,
          property_id
        );
      end
      if (property_fail_valid) begin
        observed_property_id = property_id;
        observed_property_signature = property_signature;
        if (expected_property == 0) begin
          $fatal(1, "unexpected property failure id %0d", observed_property_id);
        end
        if (observed_property_id != expected_property[7:0]) begin
          $fatal(1, "expected property id %0d, got id %0d", expected_property, observed_property_id);
        end
        @(posedge clk);
        #1;
        if (!capsule_frozen) begin
          $fatal(1, "capsule did not freeze on property failure");
        end
        if (capsule_event_count == 9'h0) begin
          $fatal(1, "capsule did not record any events");
        end
        if (dump_capsule != 0) begin
          dump_capsule_events(observed_property_id, observed_property_signature);
        end
        if (replay_from_capture != 0 && phase == 0) begin
          record_current_capsule();
          derive_replay_stimulus_from_record();
          load_mmio_replay_driver_from_record();
          phase = 1;
          load_memory();
          reset_wrapper();
        end else begin
          if (replay_from_capture != 0) begin
            compare_current_capsule_to_record();
            $display(
              "RC_FEMTO_REPLAY_SMOKE_PASS property=%0d count=%0d signature=%08x replay_sensor=%0d replay_command=%0d capture_mode=%0d sensor_packet=%0d command_packet=%0d checker_consumed=%0d mmio_driver_hits=%0d",
              observed_property_id,
              capsule_event_count,
              observed_property_signature,
              replay_sensor_value,
              replay_command_value,
              capture_mode_value,
              found_sensor_packet,
              found_command_packet,
              v1_checker_consumed_count,
              v1_mmio_hit_count
            );
          end else begin
            $display(
              "RC_FEMTO_SMOKE_PASS property=%0d count=%0d signature=%08x",
              observed_property_id,
              capsule_event_count,
              observed_property_signature
            );
          end
          $finish;
        end
      end
      if (phase != 0 && v1_mmio_replay_miss) begin
        $fatal(1, "v1 MMIO replay driver missed observed read addr=%08x", mem_addr);
      end

      if (cycle_index >= max_cycles) begin
        if (expected_property == 0) begin
          if (capsule_event_count == 9'h0) begin
            $fatal(1, "no-failure smoke did not record any events");
          end
          if (dump_capsule != 0) begin
            dump_capsule_events(8'h0, 32'h0);
          end
          $display("RC_FEMTO_SMOKE_PASS no_failure count=%0d", capsule_event_count);
          $finish;
        end
        if (phase == 0) begin
          $fatal(1, "FemtoRV32 wrapper did not raise the expected property failure");
        end else begin
          $fatal(1, "FemtoRV32 wrapper did not reproduce the captured property failure");
        end
      end
    end
  end

  logic unused_trap;
  logic [31:0] unused_mem_wdata;
  logic [167:0] unused_capsule_read_data;
  logic unused_capsule_overflow;
  logic [31:0] unused_running_signature;
  logic unused_v1_checker_active;

  assign unused_trap = trap;
  assign unused_mem_wdata = mem_wdata;
  assign unused_capsule_read_data = capsule_read_data;
  assign unused_capsule_overflow = capsule_overflow;
  assign unused_running_signature = running_signature;
  assign unused_v1_checker_active = v1_checker_active;
endmodule
