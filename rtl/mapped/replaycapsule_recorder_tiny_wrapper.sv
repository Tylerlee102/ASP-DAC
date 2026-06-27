`include "event_pkg.sv"

module replaycapsule_recorder_tiny_wrapper (
  input  logic        clk,
  input  logic        rst_n,
  output logic        capsule_frozen,
  output logic        capsule_overflow,
  output logic [7:0]  property_id,
  output logic [31:0] running_signature
);
  logic [31:0] cycle_count;
  logic [167:0] capsule_read_data;
  logic [4:0] capsule_event_count;
  logic property_fail_valid;
  logic [31:0] property_signature;
  logic captured_event_valid;
  logic [3:0] captured_event_type;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      cycle_count <= 32'h0;
    end else begin
      cycle_count <= cycle_count + 32'h1;
    end
  end

  replay_capsule_top #(
    .CAPSULE_DEPTH(16),
    .ADDR_W(4),
    .ENABLE_WATCHDOG(1'b0)
  ) u_replay_capsule_top (
    .clk(clk),
    .rst_n(rst_n),
    .clear(1'b0),
    .watchdog_enable(1'b0),
    .capture_mode(4'h3),
    .commit_valid(1'b1),
    .commit_pc(32'h0000_0080 + {cycle_count[27:0], 2'b00}),
    .commit_instr(32'h0000_0013),
    .commit_index(cycle_count),
    .branch_taken(cycle_count[4]),
    .jump_taken(1'b0),
    .mem_valid(cycle_count[1]),
    .mem_write(cycle_count[2]),
    .mem_addr(32'h4000_0000 | {28'h0, cycle_count[5:2]}),
    .mem_wdata(cycle_count ^ 32'h55aa_0001),
    .mem_rdata(cycle_count ^ 32'ha55a_0002),
    .external_input_valid(cycle_count[6]),
    .external_input_value(cycle_count),
    .interrupt_enter(cycle_count == 32'd32),
    .interrupt_exit(cycle_count == 32'd40),
    .checkpoint_hash_req(cycle_count[7]),
    .capsule_read_addr(4'h0),
    .capsule_read_data(capsule_read_data),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .capsule_event_count(capsule_event_count),
    .running_signature(running_signature),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .captured_event_valid(captured_event_valid),
    .captured_event_type(captured_event_type)
  );

  logic unused_outputs;
  assign unused_outputs = ^{
    capsule_read_data,
    capsule_event_count,
    property_fail_valid,
    property_signature,
    captured_event_valid,
    captured_event_type
  };
endmodule
