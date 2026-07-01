module rcv1_capsule_replay_checker #(
  parameter int EVENT_WIDTH = 168
) (
  input  logic                   clk,
  input  logic                   rst_n,
  input  logic                   clear,
  input  logic                   start,
  input  logic [31:0]            expected_event_count,

  input  logic                   check_valid,
  input  logic [EVENT_WIDTH-1:0] expected_packet,
  input  logic [EVENT_WIDTH-1:0] observed_packet,
  input  logic                   finish,

  output logic                   active,
  output logic                   consumed_all_events,
  output logic                   replay_error,
  output logic [7:0]             replay_error_code,
  output logic [31:0]            consumed_count,
  output logic [31:0]            mismatch_index
);
  localparam logic [7:0] RCV1_ERR_NONE = 8'h00;
  localparam logic [7:0] RCV1_ERR_PACKET_MISMATCH = 8'h01;
  localparam logic [7:0] RCV1_ERR_EXTRA_PACKET = 8'h02;
  localparam logic [7:0] RCV1_ERR_COUNT_MISMATCH = 8'h03;

  logic [31:0] active_event_count;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active <= 1'b0;
      active_event_count <= 32'h0;
      consumed_all_events <= 1'b0;
      replay_error <= 1'b0;
      replay_error_code <= RCV1_ERR_NONE;
      consumed_count <= 32'h0;
      mismatch_index <= 32'h0;
    end else if (clear) begin
      active <= 1'b0;
      active_event_count <= 32'h0;
      consumed_all_events <= 1'b0;
      replay_error <= 1'b0;
      replay_error_code <= RCV1_ERR_NONE;
      consumed_count <= 32'h0;
      mismatch_index <= 32'h0;
    end else begin
      if (start) begin
        active <= 1'b1;
        active_event_count <= expected_event_count;
        consumed_all_events <= expected_event_count == 32'h0;
        replay_error <= 1'b0;
        replay_error_code <= RCV1_ERR_NONE;
        consumed_count <= 32'h0;
        mismatch_index <= 32'h0;
      end else if (active && check_valid && !replay_error) begin
        if (consumed_all_events) begin
          replay_error <= 1'b1;
          replay_error_code <= RCV1_ERR_EXTRA_PACKET;
          mismatch_index <= consumed_count;
        end else if (expected_packet !== observed_packet) begin
          replay_error <= 1'b1;
          replay_error_code <= RCV1_ERR_PACKET_MISMATCH;
          mismatch_index <= consumed_count;
        end else begin
          consumed_count <= consumed_count + 32'h1;
          if (consumed_count + 32'h1 >= active_event_count) begin
            consumed_all_events <= 1'b1;
          end
        end
      end

      if (active && finish && !replay_error && !consumed_all_events) begin
        replay_error <= 1'b1;
        replay_error_code <= RCV1_ERR_COUNT_MISMATCH;
        mismatch_index <= consumed_count;
      end
    end
  end
endmodule
