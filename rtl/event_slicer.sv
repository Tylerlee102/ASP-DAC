`include "event_pkg.sv"

module event_slicer #(
  parameter int LAST_K = 16
) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       clear,
  input  logic       event_valid,
  input  logic [3:0] event_type,
  input  logic       property_fail_valid,
  input  logic [3:0] capture_mode,

  output logic       property_window_active,
  output logic       keep_context_event
);
  `include "event_defs.svh"

  localparam int COUNT_W = (LAST_K <= 1) ? 1 : $clog2(LAST_K + 1);
  localparam logic [COUNT_W-1:0] LAST_K_VALUE = COUNT_W'(LAST_K);
  logic [COUNT_W-1:0] context_count;

  always_comb begin
    property_window_active = context_count != '0;
    keep_context_event = event_valid && (
      capture_mode == CAPTURE_ALL ||
      event_type == EV_PROPERTY_FAIL ||
      event_type == EV_MMIO_READ ||
      event_type == EV_MMIO_WRITE ||
      event_type == EV_INTERRUPT_ENTER ||
      event_type == EV_INTERRUPT_EXIT ||
      event_type == EV_EXTERNAL_INPUT ||
      property_window_active
    );
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      context_count <= '0;
    end else if (clear) begin
      context_count <= '0;
    end else if (property_fail_valid) begin
      context_count <= LAST_K_VALUE;
    end else if (event_valid && context_count != '0) begin
      context_count <= context_count - 1'b1;
    end
  end
endmodule
