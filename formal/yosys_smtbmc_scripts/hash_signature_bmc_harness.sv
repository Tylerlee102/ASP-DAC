`default_nettype none

module hash_signature_bmc_harness (
  input logic clk
);
  localparam int EVENT_WIDTH = 168;
  localparam logic [31:0] RESET_SEED = 32'h5243_5256;
  localparam logic [31:0] MIX_CONST = 32'h9e37_79b9;

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic clear_any;
  (* anyseq *) logic event_valid;
  (* anyseq *) logic [EVENT_WIDTH-1:0] event_packet;

  logic clear;
  logic [31:0] signature;
  logic past_valid = 1'b0;
  logic prev_rst_n;
  logic prev_clear;
  logic prev_event_valid;
  logic [EVENT_WIDTH-1:0] prev_event_packet;
  logic [31:0] prev_signature;

  assign clear = rst_n && clear_any;

  hash_signature #(
    .EVENT_WIDTH(EVENT_WIDTH),
    .RESET_SEED(RESET_SEED)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(event_valid),
    .event_packet(event_packet),
    .signature(signature)
  );

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;
    prev_rst_n <= rst_n;
    prev_clear <= clear;
    prev_event_valid <= event_valid;
    prev_event_packet <= event_packet;
    prev_signature <= signature;

    if (past_valid) begin
      if (!prev_rst_n || prev_clear) begin
        assert(signature == RESET_SEED);
      end else if (prev_event_valid) begin
        assert(signature == _next_signature(prev_signature, prev_event_packet));
      end else begin
        assert(signature == prev_signature);
      end

      cover(!prev_rst_n && signature == RESET_SEED);
      cover(prev_clear && signature == RESET_SEED);
      cover(!prev_event_valid && signature == prev_signature);
      cover(prev_event_valid && signature == _next_signature(prev_signature, prev_event_packet));
    end
  end

  function automatic logic [31:0] _next_signature(
    input logic [31:0] old_signature,
    input logic [EVENT_WIDTH-1:0] packet
  );
    _next_signature = {old_signature[26:0], old_signature[31:27]} ^ _fold_packet(packet) ^ MIX_CONST;
  endfunction

  function automatic logic [31:0] _fold_packet(input logic [EVENT_WIDTH-1:0] packet);
    _fold_packet =
      packet[31:0] ^
      packet[63:32] ^
      packet[95:64] ^
      packet[127:96] ^
      packet[159:128] ^
      {24'h0, packet[167:160]};
  endfunction
endmodule

`default_nettype wire
