module replaycapsule_v2_self_replay_soc #(
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
  parameter logic [31:0] PROGADDR_IRQ   = 32'h0000_0010,
  parameter logic [31:0] STACKADDR      = 32'h0000_2000,
  parameter int          MEM_WORDS      = 256,
  parameter int          MEM_ADDR_W     = $clog2(MEM_WORDS),
  parameter int          CAPSULE_DEPTH  = 256,
  parameter int          CAPSULE_ADDR_W = $clog2(CAPSULE_DEPTH),
  parameter bit          ENABLE_WATCHDOG = 1'b0
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,

  input  logic        imem_load_valid,
  input  logic [MEM_ADDR_W-1:0] imem_load_addr,
  input  logic [31:0] imem_load_data,

  input  logic        watchdog_enable,
  input  logic [3:0]  capture_mode,
  input  logic [1:0]  arch_select,
  input  logic [1:0]  recorder_config_select,
  input  logic        replay_phase,
  input  logic        replay_controller_arm_record,
  input  logic        replay_controller_start,

  input  logic [31:0] sensor_value,
  input  logic [31:0] command_value,
  input  logic        irq_after_command,
  input  logic [31:0] irq_pulse_cycles,

  input  logic [CAPSULE_ADDR_W-1:0] capsule_read_addr,
  output logic [167:0] capsule_read_data,
  output logic        capsule_frozen,
  output logic        capsule_overflow,
  output logic [CAPSULE_ADDR_W:0] capsule_event_count,
  output logic [31:0] running_signature,
  output logic        property_fail_valid,
  output logic [7:0]  property_id,
  output logic [31:0] property_signature,
  output logic        capsule_stream_valid,
  output logic [63:0] capsule_stream_word,
  output logic [31:0] capsule_stream_event_count,
  output logic [31:0] capsule_stream_sent_count,
  output logic [31:0] capsule_replay_critical_event_count,
  output logic [31:0] capsule_stream_stall_count,
  output logic [31:0] capsule_dropped_diagnostic_count,
  output logic [31:0] capsule_replay_critical_overflow_count,
  output logic [CAPSULE_ADDR_W:0] capsule_stream_fifo_level,
  output logic        replay_consume_ready,
  output logic        replay_consume_observed_valid,
  output logic        replay_consume_all_events,
  output logic        replay_consume_error,
  output logic [7:0]  replay_consume_error_code,
  output logic [31:0] replay_consume_consumed_count,
  output logic        replay_source_active,
  output logic        replay_source_stream_done,
  output logic        replay_source_underflow,
  output logic        replay_source_capture_ready,
  output logic        replay_source_capture_overflow,
  output logic [31:0] replay_source_captured_count,
  output logic [31:0] replay_source_sent_count,
  output logic        replay_controller_busy,
  output logic        replay_controller_record_active,
  output logic        replay_controller_replay_active,
  output logic        replay_controller_done,
  output logic        replay_controller_error,
  output logic [7:0]  replay_controller_state,
  output logic [7:0]  replay_controller_error_code,
  output logic [31:0] commit_count,

  output logic        trap,
  output logic        mem_valid,
  output logic        mem_instr,
  output logic [31:0] mem_addr,
  output logic [31:0] mem_wdata,
  output logic [3:0]  mem_wstrb,
  output logic [31:0] eoi,
  output logic        irq_drive
);
  localparam logic [31:0] SENSOR_ADDR = 32'h4000_0000;
  localparam logic [31:0] COMMAND_ADDR = 32'h4000_000c;
  localparam logic [31:0] PROFILE2_SENSOR_ADDR = 32'h4000_0040;
  localparam logic [31:0] PROFILE2_COMMAND_ADDR = 32'h4000_004c;
  localparam logic [31:0] NOP = 32'h0000_0013;

  logic [31:0] imem [0:MEM_WORDS-1];
  logic [31:0] mem_rdata;
  logic mem_ready;
  logic [31:0] irq;
  logic [31:0] imem_index;
  logic [31:0] irq_pulse_remaining;
  integer init_index;

  initial begin
    for (init_index = 0; init_index < MEM_WORDS; init_index = init_index + 1) begin
      imem[init_index] = NOP;
    end
  end

  assign mem_ready = mem_valid;
  assign irq = {31'h0, irq_drive};

  always_ff @(posedge clk) begin
    if (imem_load_valid) begin
      imem[imem_load_addr] <= imem_load_data;
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      irq_drive <= 1'b0;
      irq_pulse_remaining <= 32'h0;
    end else if (clear || replay_phase) begin
      irq_drive <= 1'b0;
      irq_pulse_remaining <= 32'h0;
    end else begin
      if (irq_pulse_remaining != 32'h0) begin
        irq_drive <= 1'b1;
        irq_pulse_remaining <= irq_pulse_remaining - 32'h1;
      end else begin
        irq_drive <= 1'b0;
        if (
          irq_after_command &&
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

  always_comb begin
    imem_index = (mem_addr - PROGADDR_RESET) >> 2;
    mem_rdata = NOP;
    if (mem_valid && mem_instr) begin
      if (imem_index < MEM_WORDS[31:0]) begin
        mem_rdata = imem[imem_index[MEM_ADDR_W-1:0]];
      end
    end else if (
      mem_valid &&
      mem_wstrb == 4'h0 &&
      (mem_addr == SENSOR_ADDR || mem_addr == PROFILE2_SENSOR_ADDR)
    ) begin
      mem_rdata = replay_phase ? 32'hdead_beef : sensor_value;
    end else if (
      mem_valid &&
      mem_wstrb == 4'h0 &&
      (mem_addr == COMMAND_ADDR || mem_addr == PROFILE2_COMMAND_ADDR)
    ) begin
      mem_rdata = command_value;
    end
  end

  replaycapsule_v2_self_replay_top #(
    .PROGADDR_RESET(PROGADDR_RESET),
    .PROGADDR_IRQ(PROGADDR_IRQ),
    .STACKADDR(STACKADDR),
    .CAPSULE_DEPTH(CAPSULE_DEPTH),
    .CAPSULE_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_top (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
    .capture_mode(capture_mode),
    .arch_select(arch_select),
    .recorder_config_select(recorder_config_select),
    .replay_consume_start(1'b0),
    .replay_consume_expected_count(32'd0),
    .replay_consume_valid(1'b0),
    .replay_consume_word(64'h0),
    .replay_consume_stream_done(1'b0),
    .replay_consume_use_source(1'b0),
    .replay_source_store_clear(1'b0),
    .replay_source_capture_enable(1'b0),
    .replay_source_load_valid(1'b0),
    .replay_source_load_addr({CAPSULE_ADDR_W{1'b0}}),
    .replay_source_load_word(64'h0),
    .replay_controller_enable(1'b1),
    .replay_controller_arm_record(replay_controller_arm_record),
    .replay_controller_start(replay_controller_start),
    .capsule_stream_ready(1'b1),
    .trap(trap),
    .mem_valid(mem_valid),
    .mem_instr(mem_instr),
    .mem_ready(mem_ready),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wstrb(mem_wstrb),
    .mem_rdata(mem_rdata),
    .irq(irq),
    .eoi(eoi),
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
    .commit_count(commit_count)
  );
endmodule
