module rcv2_mmio_replay_driver (
  input  logic        event_valid,
  input  logic [63:0] event_word,
  input  logic        observed_valid,
  input  logic [31:0] observed_addr,
  input  logic [31:0] observed_data,
  output logic        mmio_replay_valid,
  output logic [31:0] mmio_replay_addr_token,
  output logic [31:0] mmio_replay_value,
  output logic        mmio_mismatch
);
  `include "../event_defs.svh"
  `include "rcv2_config.svh"

  logic [3:0] event_type;
  logic [3:0] flags;
  logic [31:0] payload;
  assign event_type = rcv2_word_type(event_word);
  assign flags = rcv2_word_flags(event_word);
  assign payload = rcv2_word_payload(event_word);

  always_comb begin
    mmio_replay_valid = event_valid && (event_type == EV_MMIO_READ || event_type == EV_MMIO_WRITE);
    mmio_replay_addr_token = {24'h0, rcv2_word_addr_token(event_word)};
    mmio_replay_value = payload;
    mmio_mismatch = mmio_replay_valid && observed_valid && observed_data != payload;
    if (mmio_replay_valid && observed_valid && !flags[RCV2_FLAG_DICT_HIT] && observed_addr[7:0] != rcv2_word_addr_token(event_word)) begin
      mmio_mismatch = 1'b1;
    end
  end
endmodule
