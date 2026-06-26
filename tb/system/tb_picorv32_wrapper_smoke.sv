`timescale 1ns/1ps

module tb_picorv32_wrapper_smoke;
  localparam int MEM_WORDS = 256;
  localparam logic [31:0] RESET_PC = 32'h0000_0080;
  localparam logic [31:0] SENSOR_ADDR = 32'h4000_0000;
  localparam logic [31:0] SENSOR_HIGH = 32'd850;

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

  picorv32_replaycapsule_wrapper u_wrapper (
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
    $readmemh("firmware/build/sensor_threshold_bug/failing.mem", imem);
  end

  always_comb begin
    mem_ready = mem_valid;
    mem_rdata = 32'h0000_0013;
    if (mem_valid && mem_instr) begin
      mem_rdata = imem[(mem_addr - RESET_PC) >> 2];
    end else if (mem_valid && mem_wstrb == 4'h0 && mem_addr == SENSOR_ADDR) begin
      mem_rdata = SENSOR_HIGH;
    end
  end

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    irq = 32'h0;
    capsule_read_addr = 8'h0;

    repeat (5) @(posedge clk);
    rst_n = 1'b1;

    repeat (500) begin
      @(posedge clk);
      if (property_fail_valid) begin
        if (property_id != 8'd3) begin
          $fatal(1, "expected sensor deadline property failure, got id %0d", property_id);
        end
        @(posedge clk);
        #1;
        if (!capsule_frozen) begin
          $fatal(1, "capsule did not freeze on property failure");
        end
        if (capsule_event_count == 9'h0) begin
          $fatal(1, "capsule did not record any events");
        end
        $finish;
      end
    end

    $fatal(1, "PicoRV32 wrapper did not raise the expected property failure");
  end

  logic unused_trap;
  logic [31:0] unused_mem_wdata;
  logic [31:0] unused_eoi;
  logic [167:0] unused_capsule_read_data;
  logic unused_capsule_overflow;
  logic [31:0] unused_running_signature;
  logic [31:0] unused_property_signature;

  assign unused_trap = trap;
  assign unused_mem_wdata = mem_wdata;
  assign unused_eoi = eoi;
  assign unused_capsule_read_data = capsule_read_data;
  assign unused_capsule_overflow = capsule_overflow;
  assign unused_running_signature = running_signature;
  assign unused_property_signature = property_signature;
endmodule
