module full_core_replaycapsule_board_top #(
  parameter int          MEM_WORDS      = 2048,
  parameter int          CAPSULE_DEPTH  = 64,
  parameter int          CAPSULE_ADDR_W = $clog2(CAPSULE_DEPTH),
  parameter logic [31:0] PROGADDR_RESET = 32'h0000_0080,
  parameter logic [31:0] PROGADDR_IRQ   = 32'h0000_0010,
  parameter logic [31:0] STACKADDR      = 32'h0000_2000
) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       uart_rx,
  output logic       uart_tx,
  input  logic [3:0] gpio_in,
  output logic [7:0] gpio_out,
  output logic [3:0] status_led,
  output logic       capsule_event_seen,
  output logic       recorder_overflow_seen,
  output logic       recorder_status_xor
);
  logic clear;
  logic watchdog_enable;
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
  logic [7:0] memory_gpio_out;
  logic memory_uart_tx;
  logic [31:0] io_status;
  logic [31:0] board_counter;
  (* keep = "true" *) logic [CAPSULE_ADDR_W-1:0] capsule_read_addr;
  (* keep = "true" *) logic [167:0] capsule_read_data;
  (* keep = "true" *) logic capsule_frozen;
  (* keep = "true" *) logic capsule_overflow;
  (* keep = "true" *) logic [CAPSULE_ADDR_W:0] capsule_event_count;
  (* keep = "true" *) logic [31:0] running_signature;
  (* keep = "true" *) logic property_fail_valid;
  (* keep = "true" *) logic [7:0] property_id;
  (* keep = "true" *) logic [31:0] property_signature;
  (* keep = "true" *) logic [31:0] recorder_status_mix;
  localparam int CAPSULE_COUNT_PAD_W = 32 - (CAPSULE_ADDR_W + 1);

  assign clear = 1'b0;
  assign watchdog_enable = gpio_in[1];
  assign irq = {24'h0, gpio_in, 3'b000, uart_rx};
  assign capsule_read_addr = board_counter[CAPSULE_ADDR_W-1:0];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      board_counter <= 32'h0;
    end else begin
      board_counter <= board_counter + 32'h1;
    end
  end

  (* keep_hierarchy = "yes" *) picorv32_replaycapsule_wrapper #(
    .PROGADDR_RESET(PROGADDR_RESET),
    .PROGADDR_IRQ(PROGADDR_IRQ),
    .STACKADDR(STACKADDR),
    .CAPSULE_DEPTH(CAPSULE_DEPTH),
    .CAPSULE_ADDR_W(CAPSULE_ADDR_W),
    .ENABLE_WATCHDOG(1'b0)
  ) u_full_core_replaycapsule (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(watchdog_enable),
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
    .external_input_valid(board_counter[4] ^ uart_rx ^ gpio_in[0]),
    .external_input_value(board_counter ^ {24'h0, gpio_in, 3'b000, uart_rx}),
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

  mapped_memory #(
    .WORDS(MEM_WORDS)
  ) u_mapped_memory (
    .clk(clk),
    .rst_n(rst_n),
    .mem_valid(mem_valid),
    .mem_instr(mem_instr),
    .mem_ready(mem_ready),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_wstrb(mem_wstrb),
    .mem_rdata(mem_rdata),
    .gpio_in(gpio_in),
    .gpio_out(memory_gpio_out),
    .uart_rx(uart_rx),
    .uart_tx(memory_uart_tx),
    .io_status(io_status)
  );

  assign recorder_status_mix =
    running_signature ^
    property_signature ^
    capsule_read_data[31:0] ^
    capsule_read_data[63:32] ^
    capsule_read_data[95:64] ^
    capsule_read_data[127:96] ^
    capsule_read_data[159:128] ^
    {24'h0, capsule_read_data[167:160]} ^
    {{CAPSULE_COUNT_PAD_W{1'b0}}, capsule_event_count} ^
    {24'h0, property_id} ^
    mem_addr ^
    mem_wdata ^
    mem_rdata ^
    io_status ^
    eoi ^
    board_counter;

  assign gpio_out = memory_gpio_out ^ recorder_status_mix[7:0];
  assign uart_tx = memory_uart_tx ^ trap ^ recorder_status_mix[8];
  assign status_led = {
    capsule_frozen,
    capsule_overflow,
    property_fail_valid,
    |capsule_event_count
  } ^ recorder_status_mix[3:0];
  assign capsule_event_seen = |capsule_event_count | property_fail_valid | capsule_frozen;
  assign recorder_overflow_seen = capsule_overflow;
  assign recorder_status_xor = ^recorder_status_mix;
endmodule
