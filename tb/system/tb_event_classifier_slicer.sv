`timescale 1ns/1ps
`include "../../rtl/event_pkg.sv"

module tb_event_classifier_slicer;
  import replaycapsule_event_pkg::*;

  logic clk;
  logic rst_n;
  logic clear;
  logic event_valid;
  logic [3:0] event_type;
  logic [3:0] capture_mode;
  logic property_fail_valid;
  logic overflow_guard;
  logic keep_event;
  logic event_is_nondeterministic;
  logic event_is_property_relevant;
  logic property_window_active;
  logic keep_context_event;

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
    .LAST_K(3)
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

  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    rst_n = 1'b0;
    clear = 1'b0;
    event_valid = 1'b0;
    event_type = EV_COMMIT;
    capture_mode = CAPTURE_ALL;
    property_fail_valid = 1'b0;
    overflow_guard = 1'b0;

    repeat (2) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);

    #1;
    if (keep_event || property_window_active || keep_context_event) begin
      $fatal(1, "inactive classifier/slicer produced an event");
    end

    event_valid = 1'b1;
    event_type = EV_COMMIT;
    capture_mode = CAPTURE_ALL;
    #1;
    if (!keep_event || event_is_nondeterministic || event_is_property_relevant) begin
      $fatal(1, "capture-all commit classification was incorrect");
    end

    capture_mode = CAPTURE_MMIO_INTERRUPT;
    event_type = EV_MMIO_READ;
    #1;
    if (!keep_event || !event_is_nondeterministic || !event_is_property_relevant) begin
      $fatal(1, "MMIO-read classification was not kept as nondeterministic evidence");
    end

    event_type = EV_LOAD;
    #1;
    if (keep_event || event_is_nondeterministic || event_is_property_relevant) begin
      $fatal(1, "ordinary load was incorrectly classified as replay evidence");
    end

    capture_mode = CAPTURE_PROPERTY_AWARE;
    event_type = EV_STORE;
    #1;
    if (keep_event || !event_is_property_relevant) begin
      $fatal(1, "store should be property-relevant but outside the active window");
    end

    capture_mode = CAPTURE_REPLAYCAPSULE_RV;
    overflow_guard = 1'b1;
    event_type = EV_LOAD;
    #1;
    if (!keep_event) begin
      $fatal(1, "overflow guard did not retain an otherwise ordinary event");
    end
    overflow_guard = 1'b0;

    capture_mode = CAPTURE_PROPERTY_AWARE;
    event_type = EV_PROPERTY_FAIL;
    property_fail_valid = 1'b1;
    #1;
    if (!keep_event || !keep_context_event) begin
      $fatal(1, "property failure was not retained by classifier and slicer");
    end

    @(posedge clk);
    #1;
    property_fail_valid = 1'b0;
    event_valid = 1'b0;
    if (!property_window_active) begin
      $fatal(1, "property failure did not open a context window");
    end

    event_valid = 1'b1;
    event_type = EV_STORE;
    #1;
    if (!keep_event || !keep_context_event) begin
      $fatal(1, "active property window did not retain context store");
    end

    repeat (3) @(posedge clk);
    #1;
    event_valid = 1'b0;
    if (property_window_active) begin
      $fatal(1, "context window did not expire after LAST_K accepted events");
    end

    property_fail_valid = 1'b1;
    event_valid = 1'b1;
    event_type = EV_PROPERTY_FAIL;
    @(posedge clk);
    #1;
    clear = 1'b1;
    property_fail_valid = 1'b0;
    event_valid = 1'b0;
    @(posedge clk);
    #1;
    if (property_window_active) begin
      $fatal(1, "clear did not reset the property context window");
    end

    $finish;
  end
endmodule
