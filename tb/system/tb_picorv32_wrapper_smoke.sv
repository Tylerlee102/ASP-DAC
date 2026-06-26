`timescale 1ns/1ps

module tb_picorv32_wrapper_smoke;
`ifdef RC_ENABLE_WATCHDOG
  localparam bit ENABLE_WATCHDOG = 1'b1;
`else
  localparam bit ENABLE_WATCHDOG = 1'b0;
`endif

  localparam int MEM_WORDS = 256;
  localparam logic [31:0] RESET_PC = 32'h0000_0080;
`ifdef RC_IRQ_VECTOR_WORD_INDEX
  localparam logic [31:0] IRQ_VECTOR_PC = RESET_PC + (`RC_IRQ_VECTOR_WORD_INDEX * 32'd4);
`else
  localparam logic [31:0] IRQ_VECTOR_PC = 32'h0000_0010;
`endif
  localparam logic [31:0] SENSOR_ADDR = 32'h4000_0000;
  localparam logic [31:0] COMMAND_ADDR = 32'h4000_000c;

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
  logic [31:0] imem [0:MEM_WORDS-1];
  string memfile;
  integer expected_property;
  integer sensor_value;
  integer command_value;
  integer max_cycles;
  integer irq_start_cycle;
  integer irq_end_cycle;
  integer irq_after_command;
  integer irq_pulse_cycles;
  integer irq_pulse_remaining;
  integer dump_capsule;
  integer cycle_index;
  integer mmio_wait_cycles;
  integer mmio_wait_count;
  logic mmio_wait_access;

  picorv32_replaycapsule_wrapper #(
    .PROGADDR_IRQ(IRQ_VECTOR_PC),
    .ENABLE_WATCHDOG(ENABLE_WATCHDOG)
  ) u_wrapper (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .capture_mode(4'h3),
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
    .property_signature(property_signature)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    memfile = "firmware/build/sensor_threshold_bug/failing.mem";
    expected_property = 3;
    sensor_value = 850;
    command_value = 0;
    max_cycles = 500;
    irq_start_cycle = -1;
    irq_end_cycle = -1;
    irq_after_command = 0;
    irq_pulse_cycles = 24;
    dump_capsule = 0;
    mmio_wait_cycles = 0;
    if (!$value$plusargs("MEMFILE=%s", memfile)) begin end
    if (!$value$plusargs("EXPECTED_PROPERTY=%d", expected_property)) begin end
    if (!$value$plusargs("SENSOR_VALUE=%d", sensor_value)) begin end
    if (!$value$plusargs("COMMAND_VALUE=%d", command_value)) begin end
    if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin end
    if (!$value$plusargs("IRQ_START_CYCLE=%d", irq_start_cycle)) begin end
    if (!$value$plusargs("IRQ_END_CYCLE=%d", irq_end_cycle)) begin end
    if (!$value$plusargs("IRQ_AFTER_COMMAND=%d", irq_after_command)) begin end
    if (!$value$plusargs("IRQ_PULSE_CYCLES=%d", irq_pulse_cycles)) begin end
    if (!$value$plusargs("DUMP_CAPSULE=%d", dump_capsule)) begin end
    if (!$value$plusargs("MMIO_WAIT_CYCLES=%d", mmio_wait_cycles)) begin end
    $readmemh(memfile, imem);
  end

  task automatic dump_capsule_events;
    integer dump_index;
    begin
      $display(
        "RC_CAPSULE_BEGIN count=%0d property=%0d signature=%08x frozen=%0b overflow=%0b",
        capsule_event_count,
        property_id,
        property_signature,
        capsule_frozen,
        capsule_overflow
      );
      for (dump_index = 0; dump_index < capsule_event_count; dump_index = dump_index + 1) begin
        capsule_read_addr = dump_index[7:0];
        #1;
        $display("RC_CAPSULE_EVENT index=%0d packet=%042h", dump_index, capsule_read_data);
      end
      $display("RC_CAPSULE_END");
    end
  endtask

  assign mmio_wait_access = mem_valid && !mem_instr && (mem_addr == SENSOR_ADDR || mem_addr == COMMAND_ADDR);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      mmio_wait_count <= 0;
    end else if (!mem_valid || mem_ready) begin
      mmio_wait_count <= 0;
    end else if (mmio_wait_access && mmio_wait_count < mmio_wait_cycles) begin
      mmio_wait_count <= mmio_wait_count + 1;
    end
  end

  always_comb begin
    mem_ready = mem_valid && (!mmio_wait_access || mmio_wait_count >= mmio_wait_cycles);
    mem_rdata = 32'h0000_0013;
    if (mem_valid && mem_instr) begin
      mem_rdata = imem[(mem_addr - RESET_PC) >> 2];
    end else if (mem_valid && mem_wstrb == 4'h0 && mem_addr == SENSOR_ADDR) begin
      mem_rdata = sensor_value[31:0];
    end else if (mem_valid && mem_wstrb == 4'h0 && mem_addr == COMMAND_ADDR) begin
      mem_rdata = command_value[31:0];
    end
  end

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    irq = 32'h0;
    capsule_read_addr = 8'h0;
    irq_pulse_remaining = 0;
    cycle_index = 0;

    repeat (5) @(posedge clk);
    rst_n = 1'b1;

    repeat (max_cycles) begin
      @(posedge clk);
      #1;
      cycle_index = cycle_index + 1;
      if (irq_after_command != 0 && mem_valid && mem_ready && !mem_instr && mem_wstrb != 4'h0 &&
          mem_addr == COMMAND_ADDR && mem_wdata[0]) begin
        irq_pulse_remaining = irq_pulse_cycles;
      end
      if (irq_after_command != 0) begin
        if (irq_pulse_remaining > 0) begin
          irq = 32'h1;
          irq_pulse_remaining = irq_pulse_remaining - 1;
        end else begin
          irq = 32'h0;
        end
      end else if (irq_start_cycle >= 0 && cycle_index >= irq_start_cycle && cycle_index < irq_end_cycle) begin
        irq = 32'h1;
      end else begin
        irq = 32'h0;
      end
      if (property_fail_valid) begin
        if (expected_property == 0) begin
          $fatal(1, "unexpected property failure id %0d", property_id);
        end
        if (property_id != expected_property[7:0]) begin
          $fatal(1, "expected property id %0d, got id %0d", expected_property, property_id);
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
          dump_capsule_events();
        end
        $finish;
      end
    end

    if (expected_property == 0) begin
      if (capsule_event_count == 9'h0) begin
        $fatal(1, "no-failure smoke did not record any events");
      end
      if (dump_capsule != 0) begin
        dump_capsule_events();
      end
      $finish;
    end

    $fatal(1, "PicoRV32 wrapper did not raise the expected property failure");
  end

  logic unused_trap;
  logic [31:0] unused_mem_wdata;
  logic [31:0] unused_eoi;
  logic [167:0] unused_capsule_read_data;
  logic unused_capsule_overflow;
  logic [31:0] unused_running_signature;

  assign unused_trap = trap;
  assign unused_mem_wdata = mem_wdata;
  assign unused_eoi = eoi;
  assign unused_capsule_read_data = capsule_read_data;
  assign unused_capsule_overflow = capsule_overflow;
  assign unused_running_signature = running_signature;
endmodule
