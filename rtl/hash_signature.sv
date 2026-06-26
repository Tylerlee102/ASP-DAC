`include "event_pkg.sv"

module hash_signature #(
  parameter int EVENT_WIDTH = 168,
  parameter logic [31:0] RESET_SEED = 32'h5243_5256
) (
  input  logic                   clk,
  input  logic                   rst_n,
  input  logic                   clear,
  input  logic                   event_valid,
  input  logic [EVENT_WIDTH-1:0] event_packet,
  output logic [31:0]            signature
);
  logic [31:0] folded;

  always_comb begin
    folded = event_packet[31:0] ^
             event_packet[63:32] ^
             event_packet[95:64] ^
             event_packet[127:96] ^
             event_packet[159:128] ^
             {24'h0, event_packet[167:160]};
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      signature <= RESET_SEED;
    end else if (clear) begin
      signature <= RESET_SEED;
    end else if (event_valid) begin
      signature <= {signature[26:0], signature[31:27]} ^ folded ^ 32'h9e37_79b9;
    end
  end
endmodule
