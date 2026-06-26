`include "event_pkg.sv"

module event_classifier (
  input  logic       event_valid,
  input  logic [3:0] event_type,
  input  logic [3:0] capture_mode,
  input  logic       property_window_active,
  input  logic       overflow_guard,
  output logic       keep_event,
  output logic       event_is_nondeterministic,
  output logic       event_is_property_relevant
);
  `include "event_defs.svh"

  always_comb begin
    event_is_nondeterministic = 1'b0;
    event_is_property_relevant = 1'b0;

    unique case (event_type)
      EV_MMIO_READ,
      EV_INTERRUPT_ENTER,
      EV_INTERRUPT_EXIT,
      EV_EXTERNAL_INPUT: begin
        event_is_nondeterministic = 1'b1;
        event_is_property_relevant = 1'b1;
      end
      EV_MMIO_WRITE,
      EV_STORE,
      EV_BRANCH,
      EV_JUMP,
      EV_PROPERTY_FAIL,
      EV_CHECKPOINT_HASH: begin
        event_is_property_relevant = 1'b1;
      end
      default: begin
        event_is_nondeterministic = 1'b0;
        event_is_property_relevant = 1'b0;
      end
    endcase
  end

  always_comb begin
    keep_event = 1'b0;
    unique case (capture_mode)
      CAPTURE_ALL: begin
        keep_event = event_valid;
      end
      CAPTURE_MMIO_INTERRUPT: begin
        keep_event = event_valid && (
          event_type == EV_MMIO_READ ||
          event_type == EV_MMIO_WRITE ||
          event_type == EV_INTERRUPT_ENTER ||
          event_type == EV_INTERRUPT_EXIT ||
          event_type == EV_EXTERNAL_INPUT ||
          event_type == EV_PROPERTY_FAIL
        );
      end
      CAPTURE_PROPERTY_AWARE: begin
        keep_event = event_valid && (event_is_nondeterministic || property_window_active || event_type == EV_PROPERTY_FAIL);
      end
      CAPTURE_REPLAYCAPSULE_RV: begin
        keep_event = event_valid && (event_is_nondeterministic || event_is_property_relevant || overflow_guard);
      end
      default: begin
        keep_event = event_valid;
      end
    endcase
  end
endmodule
