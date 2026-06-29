module rcv2_replay_consumer_pin_limited_wrapper #(
  parameter int EVENT_COUNT = 8
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        start,
  input  logic        capsule_valid,
  input  logic        stream_done,
  input  logic [63:0] capsule_word,
  input  logic        observed_valid,
  input  logic [3:0]  observed_event_type,
  input  logic [31:0] observed_commit_index,
  input  logic [31:0] observed_addr,
  input  logic [31:0] observed_data,
  input  logic [31:0] observed_payload_hash,
  output logic        capsule_ready,
  output logic        consumed_all_events,
  output logic        replay_error,
  output logic [7:0]  replay_error_code,
  output logic [15:0] consumed_count_low,
  output logic [7:0]  replay_digest
);
  logic        mmio_replay_valid;
  logic [31:0] mmio_replay_addr_token;
  logic [31:0] mmio_replay_value;
  logic        irq_replay_valid;
  logic [7:0]  irq_replay_cause;
  logic [31:0] consumed_count;

  rcv2_replay_consumer #(
    .EVENT_COUNT(EVENT_COUNT)
  ) u_consumer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .start(start),
    .capsule_valid(capsule_valid),
    .capsule_ready(capsule_ready),
    .capsule_word(capsule_word),
    .stream_done(stream_done),
    .observed_valid(observed_valid),
    .observed_event_type(observed_event_type),
    .observed_commit_index(observed_commit_index),
    .observed_addr(observed_addr),
    .observed_data(observed_data),
    .observed_payload_hash(observed_payload_hash),
    .mmio_replay_valid(mmio_replay_valid),
    .mmio_replay_addr_token(mmio_replay_addr_token),
    .mmio_replay_value(mmio_replay_value),
    .irq_replay_valid(irq_replay_valid),
    .irq_replay_cause(irq_replay_cause),
    .consumed_all_events(consumed_all_events),
    .replay_error(replay_error),
    .replay_error_code(replay_error_code),
    .consumed_count(consumed_count)
  );

  assign consumed_count_low = consumed_count[15:0];
  assign replay_digest = {
    ^mmio_replay_addr_token,
    ^mmio_replay_value,
    ^irq_replay_cause,
    mmio_replay_valid,
    irq_replay_valid,
    consumed_all_events,
    replay_error,
    capsule_ready
  };
endmodule
