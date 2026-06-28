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
  integer bit_index;
  integer fold_bit;

  always_comb begin
    folded = 32'h0;
    for (bit_index = 0; bit_index < EVENT_WIDTH; bit_index = bit_index + 32) begin
      for (fold_bit = 0; fold_bit < 32; fold_bit = fold_bit + 1) begin
        if (bit_index + fold_bit < EVENT_WIDTH) begin
          folded[fold_bit] = folded[fold_bit] ^ event_packet[bit_index + fold_bit];
        end
      end
    end
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
