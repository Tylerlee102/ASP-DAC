module rcv2_event_packer #(
  parameter bit ENABLE_DIAGNOSTICS = 1'b0,
  parameter bit ENABLE_PAYLOAD_HASH = 1'b1,
  parameter bit ENABLE_ADDRESS_DICTIONARY = 1'b1
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        event_valid,
  input  logic [3:0]  event_type,
  input  logic [3:0]  event_flags,
  input  logic [31:0] commit_index,
  input  logic [31:0] pc,
  input  logic [31:0] addr,
  input  logic [31:0] data,
  input  logic [7:0]  property_id,
  input  logic        dict_hit,
  input  logic [2:0]  dict_index,
  input  logic [31:0] payload_hash,
  input  logic        diagnostics_enabled_eff,
  output logic        packed_valid,
  output logic [63:0] packed_word,
  output logic        delta_saturated
);
  `include "../event_defs.svh"
  `include "rcv2_config.svh"

  logic [31:0] last_commit_index;
  logic [31:0] commit_delta;
  logic [15:0] commit_delta16;
  logic [7:0] commit_delta8;
  logic [7:0] address_token;
  logic [31:0] replay_payload;
  logic [7:0] debug_context;
  logic [7:0] debug_context_raw;
  logic [3:0] flags;

  assign commit_delta = commit_index - last_commit_index;
  assign delta_saturated = commit_delta > 32'd255;
  assign commit_delta16 = (commit_delta > 32'd65535) ? 16'hffff : commit_delta[15:0];
  assign commit_delta8 = delta_saturated ? commit_delta16[7:0] : commit_delta[7:0];
  assign address_token = (ENABLE_ADDRESS_DICTIONARY && dict_hit) ? {5'h0, dict_index} : addr[7:0];
  assign replay_payload = data;

  always_comb begin
    debug_context_raw = 8'h0;
    if (event_type == EV_PROPERTY_FAIL) begin
      debug_context_raw = property_id;
    end else if (event_type == EV_INTERRUPT_ENTER || event_type == EV_INTERRUPT_EXIT) begin
      debug_context_raw = data[7:0];
    end else if (ENABLE_DIAGNOSTICS && diagnostics_enabled_eff) begin
      debug_context_raw = pc[7:0];
    end
    debug_context = delta_saturated ? commit_delta16[15:8] : debug_context_raw;

    flags = event_flags;
    flags[RCV2_FLAG_DIAGNOSTIC] = ENABLE_DIAGNOSTICS && diagnostics_enabled_eff;
    flags[RCV2_FLAG_HASH] = ENABLE_PAYLOAD_HASH;
    flags[RCV2_FLAG_DICT_HIT] = ENABLE_ADDRESS_DICTIONARY && dict_hit;
    flags[RCV2_FLAG_DELTA_WIDE] = delta_saturated;
    packed_word = {event_type, flags, commit_delta8, address_token, replay_payload, debug_context};
    packed_valid = event_valid;
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      last_commit_index <= 32'h0;
    end else if (clear) begin
      last_commit_index <= 32'h0;
    end else if (event_valid) begin
      last_commit_index <= commit_index;
    end
  end
endmodule
