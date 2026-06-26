`default_nettype none

module event_classifier_slicer_bmc_harness (
  input logic clk
);
  `include "../../rtl/event_defs.svh"

  localparam int LAST_K = 3;
  localparam int COUNT_W = 2;
  localparam logic [COUNT_W-1:0] LAST_K_VALUE = COUNT_W'(LAST_K);

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic clear_any;
  (* anyseq *) logic event_valid;
  (* anyseq *) logic [3:0] event_type;
  (* anyseq *) logic [3:0] capture_mode;
  (* anyseq *) logic property_fail_valid;
  (* anyseq *) logic overflow_guard;

  logic clear;
  logic keep_event;
  logic event_is_nondeterministic;
  logic event_is_property_relevant;
  logic property_window_active;
  logic keep_context_event;

  logic expected_nondeterministic;
  logic expected_property_relevant;
  logic expected_keep_event;
  logic expected_keep_context_event;
  logic [COUNT_W-1:0] shadow_context_count;
  logic [COUNT_W-1:0] prev_shadow_context_count;
  logic prev_rst_n;
  logic prev_clear;
  logic prev_event_valid;
  logic prev_property_fail_valid;
  logic past_valid = 1'b0;

  assign clear = rst_n && clear_any;

  always_comb begin
    expected_nondeterministic = 1'b0;
    expected_property_relevant = 1'b0;

    case (event_type)
      EV_MMIO_READ,
      EV_INTERRUPT_ENTER,
      EV_INTERRUPT_EXIT,
      EV_EXTERNAL_INPUT: begin
        expected_nondeterministic = 1'b1;
        expected_property_relevant = 1'b1;
      end
      EV_MMIO_WRITE,
      EV_STORE,
      EV_BRANCH,
      EV_JUMP,
      EV_PROPERTY_FAIL,
      EV_CHECKPOINT_HASH: begin
        expected_property_relevant = 1'b1;
      end
      default: begin
        expected_nondeterministic = 1'b0;
        expected_property_relevant = 1'b0;
      end
    endcase
  end

  always_comb begin
    expected_keep_event = 1'b0;
    case (capture_mode)
      CAPTURE_ALL: begin
        expected_keep_event = event_valid;
      end
      CAPTURE_MMIO_INTERRUPT: begin
        expected_keep_event = event_valid && (
          event_type == EV_MMIO_READ ||
          event_type == EV_MMIO_WRITE ||
          event_type == EV_INTERRUPT_ENTER ||
          event_type == EV_INTERRUPT_EXIT ||
          event_type == EV_EXTERNAL_INPUT ||
          event_type == EV_PROPERTY_FAIL
        );
      end
      CAPTURE_PROPERTY_AWARE: begin
        expected_keep_event =
          event_valid &&
          (expected_nondeterministic || property_window_active || event_type == EV_PROPERTY_FAIL);
      end
      CAPTURE_REPLAYCAPSULE_RV: begin
        expected_keep_event =
          event_valid &&
          (expected_nondeterministic || expected_property_relevant || overflow_guard);
      end
      default: begin
        expected_keep_event = event_valid;
      end
    endcase
  end

  assign expected_keep_context_event =
    event_valid &&
    (
      capture_mode == CAPTURE_ALL ||
      event_type == EV_PROPERTY_FAIL ||
      event_type == EV_MMIO_READ ||
      event_type == EV_MMIO_WRITE ||
      event_type == EV_INTERRUPT_ENTER ||
      event_type == EV_INTERRUPT_EXIT ||
      event_type == EV_EXTERNAL_INPUT ||
      property_window_active
    );

  event_classifier u_event_classifier (
    .event_valid(event_valid),
    .event_type(event_type),
    .capture_mode(capture_mode),
    .property_window_active(property_window_active),
    .overflow_guard(overflow_guard),
    .keep_event(keep_event),
    .event_is_nondeterministic(event_is_nondeterministic),
    .event_is_property_relevant(event_is_property_relevant)
  );

  event_slicer #(
    .LAST_K(LAST_K)
  ) u_event_slicer (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(event_valid),
    .event_type(event_type),
    .property_fail_valid(property_fail_valid),
    .capture_mode(capture_mode),
    .property_window_active(property_window_active),
    .keep_context_event(keep_context_event)
  );

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;
    prev_rst_n <= rst_n;
    prev_clear <= clear;
    prev_event_valid <= event_valid;
    prev_property_fail_valid <= property_fail_valid;
    prev_shadow_context_count <= shadow_context_count;

    if (!rst_n || clear) begin
      shadow_context_count <= '0;
    end else if (property_fail_valid) begin
      shadow_context_count <= LAST_K_VALUE;
    end else if (event_valid && shadow_context_count != '0) begin
      shadow_context_count <= shadow_context_count - 1'b1;
    end

    assert(event_is_nondeterministic == expected_nondeterministic);
    assert(event_is_property_relevant == expected_property_relevant);
    assert(keep_event == expected_keep_event);
    assert(keep_context_event == expected_keep_context_event);

    if (past_valid) begin
      if (!prev_rst_n || prev_clear) begin
        assert(!property_window_active);
      end else if (prev_property_fail_valid) begin
        assert(property_window_active);
      end else if (prev_event_valid && prev_shadow_context_count == 1) begin
        assert(!property_window_active);
      end else if (prev_shadow_context_count != '0) begin
        assert(property_window_active);
      end

      cover(event_valid && capture_mode == CAPTURE_ALL && keep_event);
      cover(event_valid && event_type == EV_MMIO_READ && event_is_nondeterministic && keep_event);
      cover(event_valid && capture_mode == CAPTURE_REPLAYCAPSULE_RV && overflow_guard && keep_event);
      cover(prev_property_fail_valid && property_window_active);
      cover(prev_event_valid && prev_shadow_context_count == 1 && !property_window_active);
    end
  end
endmodule

`default_nettype wire
