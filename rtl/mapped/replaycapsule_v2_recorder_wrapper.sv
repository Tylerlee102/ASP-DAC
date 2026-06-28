module replaycapsule_v2_recorder_wrapper #(
  parameter int MEMORY_WORDS = 1024,
  parameter int BUFFER_DEPTH = 256,
  parameter int MEMORY_ADDR_W = (MEMORY_WORDS <= 2) ? 1 : $clog2(MEMORY_WORDS),
  parameter int REPLAYCAPSULE_CONFIG = 1
) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic [3:0] gpio_in,
  output logic [7:0] gpio_out,
  output logic       recorder_status_xor
);
  logic [31:0] counter;
  logic [MEMORY_ADDR_W-1:0] capsule_read_addr;
  logic [63:0] capsule_read_data;
  logic capsule_frozen;
  logic capsule_overflow;
  logic [MEMORY_ADDR_W:0] capsule_event_count;
  logic [31:0] running_signature;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic captured_event_valid;
  logic [3:0] captured_event_type;
  logic [31:0] dropped_diagnostic_count;
  logic mem_valid;
  logic mem_write;
  logic [31:0] mem_addr;
  logic [31:0] mem_wdata;
  logic [31:0] mem_rdata;
  logic interrupt_enter;
  logic interrupt_exit;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      counter <= 32'h0;
    end else begin
      counter <= counter + 32'h1;
    end
  end

  assign capsule_read_addr = counter[MEMORY_ADDR_W-1:0];
  assign mem_valid = counter[0] | counter[3];
  assign mem_write = counter[2];
  assign mem_addr = 32'h4000_0000 + {24'h0, counter[7:0]};
  assign mem_wdata = counter ^ 32'ha5a5_5a5a;
  assign mem_rdata = {24'h0, gpio_in, counter[3:0]};
  assign interrupt_enter = counter[5:0] == 6'h11;
  assign interrupt_exit = counter[5:0] == 6'h12;

  (* keep_hierarchy = "yes" *) rcv2_recorder #(
    .REPLAYCAPSULE_CONFIG(REPLAYCAPSULE_CONFIG),
    .BUFFER_DEPTH(BUFFER_DEPTH),
    .MEMORY_WORDS(MEMORY_WORDS),
    .MEMORY_ADDR_W(MEMORY_ADDR_W),
    .ENABLE_DIAGNOSTICS(1'b1),
    .ENABLE_PAYLOAD_HASH(1'b1),
    .ENABLE_ADDRESS_DICTIONARY(1'b1),
    .ENABLE_BRam_FIFO(1'b1),
    .ENABLE_ADAPTIVE_WINDOW(1'b1),
    .ENABLE_WATCHDOG(1'b0)
  ) u_rcv2_recorder (
    .clk(clk),
    .rst_n(rst_n),
    .clear(1'b0),
    .watchdog_enable(1'b0),
    .commit_valid(1'b1),
    .commit_pc(counter),
    .commit_instr(32'h0000_0013),
    .commit_index(counter),
    .branch_taken(counter[4]),
    .jump_taken(1'b0),
    .mem_valid(mem_valid),
    .mem_write(mem_write),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(counter[6]),
    .external_input_value(counter ^ {28'h0, gpio_in}),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(counter[7:0] == 8'h7f),
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
    .dropped_diagnostic_count(dropped_diagnostic_count)
  );

  assign gpio_out =
    capsule_read_data[7:0] ^
    running_signature[7:0] ^
    property_signature[7:0] ^
    property_id ^
    {4'h0, captured_event_type};
  assign recorder_status_xor =
    ^capsule_read_data ^
    ^running_signature ^
    capsule_frozen ^
    capsule_overflow ^
    property_fail_valid ^
    captured_event_valid ^
    ^capsule_event_count ^
    ^dropped_diagnostic_count;
endmodule
