module rcv2_payload_hasher (
  input  logic        enable,
  input  logic        event_valid,
  input  logic [3:0]  event_type,
  input  logic [31:0] commit_index,
  input  logic [31:0] addr,
  input  logic [31:0] data,
  output logic        hash_valid,
  output logic [31:0] payload_hash
);
  logic [31:0] mixed;

  always_comb begin
    mixed = data ^ {event_type, event_type, event_type, event_type, event_type, event_type, event_type, event_type};
    mixed = mixed ^ {commit_index[15:0], commit_index[31:16]};
    mixed = mixed ^ {addr[7:0], addr[31:8]};
    mixed = (mixed << 5) ^ (mixed >> 2) ^ 32'h9e37_79b9;
    payload_hash = enable ? mixed : data;
    hash_valid = event_valid;
  end
endmodule
