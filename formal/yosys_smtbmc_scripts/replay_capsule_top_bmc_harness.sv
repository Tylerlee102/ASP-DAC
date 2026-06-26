`default_nettype none

module replay_capsule_top_bmc_harness (
  input logic clk
);
  `include "../../rtl/event_defs.svh"

  localparam int FORMAL_CAPSULE_DEPTH = 4;
  localparam int FORMAL_ADDR_W = $clog2(FORMAL_CAPSULE_DEPTH);

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic        clear_any;
  (* anyseq *) logic        commit_valid;
  (* anyseq *) logic [31:0] commit_pc;
  (* anyseq *) logic [31:0] commit_instr;
  (* anyseq *) logic [31:0] commit_index;
  (* anyseq *) logic        branch_taken;
  (* anyseq *) logic        jump_taken;
  (* anyseq *) logic        mem_valid;
  (* anyseq *) logic        mem_write;
  (* anyseq *) logic [31:0] mem_addr;
  (* anyseq *) logic [31:0] mem_wdata;
  (* anyseq *) logic [31:0] mem_rdata;
  (* anyseq *) logic        external_input_valid;
  (* anyseq *) logic [31:0] external_input_value;
  (* anyseq *) logic        interrupt_enter;
  (* anyseq *) logic        interrupt_exit;
  (* anyseq *) logic        checkpoint_hash_req;
  (* anyseq *) logic [FORMAL_ADDR_W-1:0] capsule_read_addr;

  logic clear;
  logic [RC_EVENT_WIDTH-1:0] capsule_read_data;
  logic capsule_frozen;
  logic capsule_overflow;
  logic [FORMAL_ADDR_W:0] capsule_event_count;
  logic [31:0] running_signature;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic captured_event_valid;
  logic [3:0] captured_event_type;

  assign clear = rst_n && clear_any;

  replay_capsule_top #(
    .CAPSULE_DEPTH(FORMAL_CAPSULE_DEPTH),
    .ADDR_W(FORMAL_ADDR_W)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .capture_mode(CAPTURE_ALL),
    .commit_valid(commit_valid),
    .commit_pc(commit_pc),
    .commit_instr(commit_instr),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(mem_valid),
    .mem_write(mem_write),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(external_input_valid),
    .external_input_value(external_input_value),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(checkpoint_hash_req),
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
    .captured_event_type(captured_event_type)
  );

  logic past_valid = 1'b0;

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;

    if (past_valid && rst_n && $past(rst_n)) begin
      assert(capsule_event_count <= FORMAL_CAPSULE_DEPTH[FORMAL_ADDR_W:0]);

      if (!clear && !$past(clear)) begin
        if ($past(property_fail_valid)) begin
          assert(capsule_frozen);
        end
        if ($past(capsule_frozen)) begin
          assert(capsule_frozen);
          assert(capsule_event_count == $past(capsule_event_count));
        end
        if ($past(capsule_overflow)) begin
          assert(capsule_overflow);
        end
      end
    end

    cover(rst_n && !clear && captured_event_valid);
    cover(rst_n && !clear && capsule_frozen);
    cover(rst_n && !clear && capsule_overflow);
  end
endmodule

`default_nettype wire
