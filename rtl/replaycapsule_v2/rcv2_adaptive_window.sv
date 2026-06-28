module rcv2_adaptive_window #(
  parameter int COUNT_W = 11,
  parameter int HIGH_WATERMARK_MARGIN = 16
) (
  input  logic                 clk,
  input  logic                 rst_n,
  input  logic                 clear,
  input  logic                 event_valid,
  input  logic                 event_is_replay_critical,
  input  logic                 diagnostics_requested,
  input  logic [COUNT_W-1:0]   used_words,
  input  logic [COUNT_W-1:0]   capacity_words,
  output logic                 capture_event,
  output logic                 diagnostics_enabled_eff,
  output logic                 adaptive_drop,
  output logic [31:0]          dropped_diagnostic_count
);
  logic near_capacity;

  always_comb begin
    near_capacity = used_words + COUNT_W'(HIGH_WATERMARK_MARGIN) >= capacity_words;
    diagnostics_enabled_eff = diagnostics_requested && !near_capacity;
    capture_event = event_valid && (event_is_replay_critical || diagnostics_enabled_eff);
    adaptive_drop = event_valid && diagnostics_requested && !event_is_replay_critical && near_capacity;
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      dropped_diagnostic_count <= 32'h0;
    end else if (clear) begin
      dropped_diagnostic_count <= 32'h0;
    end else if (adaptive_drop) begin
      dropped_diagnostic_count <= dropped_diagnostic_count + 32'h1;
    end
  end
endmodule
