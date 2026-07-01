module rcv2_replay_consumer #(
  parameter int EVENT_COUNT = 0,
  parameter bit ENABLE_PAYLOAD_HASH = 1'b1,
  parameter bit STRICT_ORDER = 1'b1,
  parameter int IRQ_REPLAY_LEAD = 0
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        start,
  input  logic [31:0] expected_event_count,

  input  logic        capsule_valid,
  output logic        capsule_ready,
  input  logic [63:0] capsule_word,
  input  logic        stream_done,

  input  logic [31:0] current_commit_index,
  input  logic        observed_valid,
  input  logic [3:0]  observed_event_type,
  input  logic [31:0] observed_commit_index,
  input  logic [31:0] observed_addr,
  input  logic [31:0] observed_data,
  input  logic [31:0] observed_payload_hash,

  output logic        mmio_replay_valid,
  output logic [31:0] mmio_replay_addr_token,
  output logic [31:0] mmio_replay_value,
  output logic        irq_replay_valid,
  output logic [7:0]  irq_replay_cause,
  output logic        consumed_all_events,
  output logic        replay_error,
  output logic [7:0]  replay_error_code,
  output logic [31:0] consumed_count
);
  `include "../event_defs.svh"
  `include "rcv2_config.svh"

  logic active;
  logic [31:0] expected_commit_index;
  logic [31:0] active_event_count;
  logic pending_valid;
  logic [63:0] pending_word;
  logic active_word_valid;
  logic [63:0] active_word;
  logic [3:0] expected_type;
  logic [3:0] expected_flags;
  logic [31:0] expected_payload;
  logic [31:0] next_commit_index;
  logic [31:0] expected_payload_hash;
  logic event_commit_armed;
  logic irq_event_commit_armed;
  logic [31:0] direct_next_commit_index;
  logic [31:0] direct_payload;
  logic direct_event_commit_armed;
  logic direct_irq_event_commit_armed;
  logic direct_irq_replay_valid;
  logic [7:0] direct_irq_replay_cause;
  logic active_irq_replay_valid;
  logic [7:0] active_irq_replay_cause;
  logic accept_direct_word;
  logic accept_pending_word;
  logic pending_consumes_this_cycle;
  logic consume_active_word;
  logic mmio_mismatch;
  logic irq_mismatch;

  localparam logic [31:0] IRQ_REPLAY_LEAD_VALUE = IRQ_REPLAY_LEAD;

  function automatic logic [31:0] rcv2_hash_addr_for_event(
    input logic [3:0] event_type,
    input logic [RCV2_WORD_WIDTH-1:0] word,
    input logic [31:0] observed_addr
  );
    begin
      if (event_type == EV_PROPERTY_FAIL) begin
        rcv2_hash_addr_for_event = {24'h0, rcv2_word_addr_token(word)};
      end else begin
        rcv2_hash_addr_for_event = observed_addr;
      end
    end
  endfunction

  function automatic logic [31:0] rcv2_commit_delta_for_word(
    input logic [RCV2_WORD_WIDTH-1:0] word
  );
    logic [3:0] word_flags;
    begin
      word_flags = rcv2_word_flags(word);
      if (word_flags[RCV2_FLAG_DELTA_WIDE]) begin
        rcv2_commit_delta_for_word = {16'h0, rcv2_word_debug(word), rcv2_word_delta(word)};
      end else begin
        rcv2_commit_delta_for_word = {24'h0, rcv2_word_delta(word)};
      end
    end
  endfunction

  function automatic logic [31:0] rcv2_expected_payload_hash(
    input logic [3:0] event_type,
    input logic [31:0] commit_index,
    input logic [31:0] addr,
    input logic [31:0] data
  );
    logic [31:0] mixed;
    begin
      mixed = data ^ {event_type, event_type, event_type, event_type, event_type, event_type, event_type, event_type};
      mixed = mixed ^ {commit_index[15:0], commit_index[31:16]};
      mixed = mixed ^ {addr[7:0], addr[31:8]};
      rcv2_expected_payload_hash = (mixed << 5) ^ (mixed >> 2) ^ 32'h9e37_79b9;
    end
  endfunction

  assign active_word_valid = pending_valid || (capsule_valid && capsule_ready);
  assign active_word = pending_valid ? pending_word : capsule_word;
  assign expected_type = rcv2_word_type(active_word);
  assign expected_flags = rcv2_word_flags(active_word);
  assign expected_payload = rcv2_word_payload(active_word);
  assign next_commit_index = expected_commit_index + rcv2_commit_delta_for_word(active_word);
  assign expected_payload_hash = rcv2_expected_payload_hash(
    expected_type,
    next_commit_index,
    rcv2_hash_addr_for_event(expected_type, active_word, observed_addr),
    expected_payload
  );
  assign event_commit_armed = (current_commit_index + 32'h1) >= next_commit_index;
  assign irq_event_commit_armed = (current_commit_index + 32'h1 + IRQ_REPLAY_LEAD_VALUE) >= next_commit_index;
  assign direct_payload = rcv2_word_payload(capsule_word);
  assign direct_next_commit_index = next_commit_index + rcv2_commit_delta_for_word(capsule_word);
  assign direct_event_commit_armed = (current_commit_index + 32'h1) >= direct_next_commit_index;
  assign direct_irq_event_commit_armed = (current_commit_index + 32'h1 + IRQ_REPLAY_LEAD_VALUE) >= direct_next_commit_index;
  assign pending_consumes_this_cycle = active && pending_valid && observed_valid && !replay_error && !consumed_all_events;
  assign capsule_ready = active && !replay_error && !consumed_all_events && (!pending_valid || pending_consumes_this_cycle);
  assign accept_direct_word = capsule_valid && capsule_ready;
  assign accept_pending_word = pending_valid;
  assign consume_active_word = active && active_word_valid && observed_valid && !replay_error && !consumed_all_events;

  rcv2_mmio_replay_driver u_mmio_replay_driver (
    .event_valid(active_word_valid),
    .event_word(active_word),
    .observed_valid(observed_valid),
    .observed_addr(observed_addr),
    .observed_data(observed_data),
    .mmio_replay_valid(mmio_replay_valid),
    .mmio_replay_addr_token(mmio_replay_addr_token),
    .mmio_replay_value(mmio_replay_value),
    .mmio_mismatch(mmio_mismatch)
  );

  rcv2_irq_replay_driver u_irq_replay_driver (
    .event_valid(active_word_valid && irq_event_commit_armed),
    .event_word(active_word),
    .observed_valid(observed_valid),
    .observed_cause(observed_data),
    .irq_replay_valid(active_irq_replay_valid),
    .irq_replay_cause(active_irq_replay_cause),
    .irq_mismatch(irq_mismatch)
  );

  assign direct_irq_replay_valid =
    accept_direct_word &&
    accept_pending_word &&
    direct_irq_event_commit_armed &&
    (rcv2_word_type(capsule_word) == EV_INTERRUPT_ENTER || rcv2_word_type(capsule_word) == EV_INTERRUPT_EXIT);
  assign direct_irq_replay_cause = direct_payload[7:0];
  assign irq_replay_valid = active_irq_replay_valid || direct_irq_replay_valid;
  assign irq_replay_cause = active_irq_replay_valid ? active_irq_replay_cause : direct_irq_replay_cause;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active <= 1'b0;
      expected_commit_index <= 32'h0;
      active_event_count <= EVENT_COUNT[31:0];
      pending_valid <= 1'b0;
      pending_word <= 64'h0;
      consumed_all_events <= 1'b0;
      replay_error <= 1'b0;
      replay_error_code <= RCV2_ERR_NONE;
      consumed_count <= 32'h0;
    end else if (clear) begin
      active <= 1'b0;
      expected_commit_index <= 32'h0;
      active_event_count <= EVENT_COUNT[31:0];
      pending_valid <= 1'b0;
      pending_word <= 64'h0;
      consumed_all_events <= 1'b0;
      replay_error <= 1'b0;
      replay_error_code <= RCV2_ERR_NONE;
      consumed_count <= 32'h0;
    end else begin
      if (start) begin
        active <= 1'b1;
        expected_commit_index <= 32'h0;
        active_event_count <= (expected_event_count != 32'h0) ? expected_event_count : EVENT_COUNT[31:0];
        consumed_all_events <= ((expected_event_count != 32'h0) ? expected_event_count : EVENT_COUNT[31:0]) == 32'h0;
        pending_valid <= 1'b0;
        pending_word <= 64'h0;
        replay_error <= 1'b0;
        replay_error_code <= RCV2_ERR_NONE;
        consumed_count <= 32'h0;
      end

      if (active && accept_direct_word && !observed_valid) begin
        pending_valid <= 1'b1;
        pending_word <= capsule_word;
      end

      if (active && stream_done && !consumed_all_events && !pending_valid && !replay_error) begin
        replay_error <= 1'b1;
        replay_error_code <= RCV2_ERR_TRUNCATED_CAPSULE;
      end

      if (active && capsule_valid && consumed_all_events && !replay_error) begin
        replay_error <= 1'b1;
        replay_error_code <= RCV2_ERR_DUPLICATE_EVENT;
      end else if (active && observed_valid && !active_word_valid && !replay_error && !consumed_all_events) begin
        replay_error <= 1'b1;
        replay_error_code <= RCV2_ERR_MISSING_EVENT;
      end else if (consume_active_word) begin
        if (!event_commit_armed && (expected_type == EV_INTERRUPT_ENTER || expected_type == EV_INTERRUPT_EXIT)) begin
          replay_error <= 1'b1;
          replay_error_code <= RCV2_ERR_REORDERED_EVENT;
        end else if (STRICT_ORDER && (observed_event_type != expected_type || observed_commit_index != next_commit_index)) begin
          replay_error <= 1'b1;
          replay_error_code <= RCV2_ERR_REORDERED_EVENT;
        end else if (mmio_mismatch) begin
          replay_error <= 1'b1;
          replay_error_code <= RCV2_ERR_WRONG_MMIO_VALUE;
        end else if (irq_mismatch) begin
          replay_error <= 1'b1;
          replay_error_code <= RCV2_ERR_WRONG_IRQ_CAUSE;
        end else if (ENABLE_PAYLOAD_HASH && expected_flags[RCV2_FLAG_HASH] && observed_payload_hash != expected_payload_hash) begin
          replay_error <= 1'b1;
          replay_error_code <= RCV2_ERR_WRONG_PAYLOAD_HASH;
        end else begin
          expected_commit_index <= next_commit_index;
          consumed_count <= consumed_count + 32'h1;
          pending_valid <= accept_direct_word && accept_pending_word;
          if (accept_direct_word && accept_pending_word) begin
            pending_word <= capsule_word;
          end
          if (consumed_count + 32'h1 >= active_event_count) begin
            consumed_all_events <= 1'b1;
          end
        end
      end
    end
  end
endmodule
