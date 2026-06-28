module rcv2_irq_replay_driver (
  input  logic        event_valid,
  input  logic [63:0] event_word,
  input  logic        observed_valid,
  input  logic [31:0] observed_cause,
  output logic        irq_replay_valid,
  output logic [7:0]  irq_replay_cause,
  output logic        irq_mismatch
);
  `include "../event_defs.svh"
  `include "rcv2_config.svh"

  logic [3:0] event_type;
  logic [31:0] payload;
  assign event_type = rcv2_word_type(event_word);
  assign payload = rcv2_word_payload(event_word);

  always_comb begin
    irq_replay_valid = event_valid && (event_type == EV_INTERRUPT_ENTER || event_type == EV_INTERRUPT_EXIT);
    irq_replay_cause = payload[7:0];
    irq_mismatch = irq_replay_valid && observed_valid && observed_cause[7:0] != irq_replay_cause;
  end
endmodule
