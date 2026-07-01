module rcv2_replay_mode_controller (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,
  input  logic        enable,
  input  logic        arm_record,
  input  logic        start_replay,
  input  logic [31:0] captured_count,
  input  logic        capture_overflow,
  input  logic        source_underflow,
  input  logic        consume_all_events,
  input  logic        consume_error,

  output logic        source_store_clear,
  output logic        source_capture_enable,
  output logic        consume_use_source,
  output logic        consume_start,
  output logic [31:0] consume_expected_count,
  output logic        busy,
  output logic        record_active,
  output logic        replay_active,
  output logic        done,
  output logic        error,
  output logic [7:0]  state,
  output logic [7:0]  error_code
);
  localparam logic [7:0] STATE_IDLE   = 8'd0;
  localparam logic [7:0] STATE_RECORD = 8'd1;
  localparam logic [7:0] STATE_REPLAY = 8'd2;
  localparam logic [7:0] STATE_DONE   = 8'd3;
  localparam logic [7:0] STATE_ERROR  = 8'd4;

  localparam logic [7:0] ERR_NONE     = 8'd0;
  localparam logic [7:0] ERR_OVERFLOW = 8'd1;
  localparam logic [7:0] ERR_CONSUMER = 8'd3;
  localparam logic [7:0] ERR_SOURCE   = 8'd4;

  logic [31:0] replay_count;
  logic can_start_replay;
  logic start_replay_pulse;
  logic arm_record_active;

  assign arm_record_active = enable && arm_record && state != STATE_REPLAY;
  assign can_start_replay = enable && start_replay && !capture_overflow;
  assign start_replay_pulse =
    can_start_replay && (state == STATE_IDLE || state == STATE_RECORD || state == STATE_DONE);

  assign source_store_clear = arm_record_active;
  assign source_capture_enable =
    enable && !start_replay && !error &&
    (state == STATE_RECORD || arm_record_active);
  assign consume_use_source = enable && (state == STATE_REPLAY || start_replay_pulse);
  assign consume_start = start_replay_pulse;
  assign consume_expected_count = start_replay_pulse ? captured_count : replay_count;
  assign busy = enable && (state == STATE_RECORD || state == STATE_REPLAY);
  assign record_active = enable && state == STATE_RECORD;
  assign replay_active = enable && state == STATE_REPLAY;
  assign done = enable && state == STATE_DONE;
  assign error = enable && state == STATE_ERROR;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state <= STATE_IDLE;
      error_code <= ERR_NONE;
      replay_count <= 32'h0;
    end else if (clear || !enable) begin
      state <= STATE_IDLE;
      error_code <= ERR_NONE;
      replay_count <= 32'h0;
    end else begin
      unique case (state)
        STATE_IDLE: begin
          error_code <= ERR_NONE;
          if (arm_record) begin
            state <= STATE_RECORD;
            replay_count <= 32'h0;
          end else if (start_replay) begin
            if (capture_overflow) begin
              state <= STATE_ERROR;
              error_code <= ERR_OVERFLOW;
            end else begin
              state <= STATE_REPLAY;
              replay_count <= captured_count;
            end
          end
        end

        STATE_RECORD: begin
          if (capture_overflow) begin
            state <= STATE_ERROR;
            error_code <= ERR_OVERFLOW;
          end else if (start_replay) begin
            state <= STATE_REPLAY;
            replay_count <= captured_count;
          end
        end

        STATE_REPLAY: begin
          if (consume_error) begin
            state <= STATE_ERROR;
            error_code <= ERR_CONSUMER;
          end else if (source_underflow) begin
            state <= STATE_ERROR;
            error_code <= ERR_SOURCE;
          end else if (consume_all_events) begin
            state <= STATE_DONE;
          end
        end

        STATE_DONE: begin
          if (arm_record) begin
            state <= STATE_RECORD;
            error_code <= ERR_NONE;
            replay_count <= 32'h0;
          end else if (start_replay) begin
            if (capture_overflow) begin
              state <= STATE_ERROR;
              error_code <= ERR_OVERFLOW;
            end else begin
              state <= STATE_REPLAY;
              error_code <= ERR_NONE;
              replay_count <= captured_count;
            end
          end
        end

        STATE_ERROR: begin
          if (arm_record) begin
            state <= STATE_RECORD;
            error_code <= ERR_NONE;
            replay_count <= 32'h0;
          end
        end

        default: begin
          state <= STATE_ERROR;
          error_code <= ERR_CONSUMER;
        end
      endcase
    end
  end
endmodule
