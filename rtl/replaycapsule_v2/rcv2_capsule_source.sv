module rcv2_capsule_source #(
  parameter int WORDS = 256,
  parameter int ADDR_W = (WORDS <= 2) ? 1 : $clog2(WORDS)
) (
  input  logic              clk,
  input  logic              rst_n,
  input  logic              clear,
  input  logic              store_clear,
  input  logic              capture_enable,
  input  logic              capture_valid,
  input  logic [63:0]       capture_word,
  input  logic              load_valid,
  input  logic [ADDR_W-1:0] load_addr,
  input  logic [63:0]       load_word,
  input  logic              start,
  input  logic [31:0]       expected_count,
  input  logic              capsule_ready,
  output logic              capture_ready,
  output logic              capture_overflow,
  output logic [31:0]       captured_count,
  output logic              capsule_valid,
  output logic [63:0]       capsule_word,
  output logic              stream_done,
  output logic              active,
  output logic              underflow,
  output logic [31:0]       sent_count
);
  logic [63:0] memory [0:WORDS-1];
  logic capture_replay_critical;
  logic capture_accept;
  logic capture_store_fire;
  logic [31:0] capture_commit_index;
  logic [31:0] capture_last_stored_commit;
  logic [31:0] capture_word_delta;
  logic [31:0] capture_next_commit;
  logic [31:0] capture_store_delta;
  logic capture_store_delta_wide;
  logic [63:0] capture_store_word;

  assign capture_replay_critical =
    capture_word[63:60] == 4'h5 ||
    capture_word[63:60] == 4'h6 ||
    capture_word[63:60] == 4'h7 ||
    capture_word[63:60] == 4'h8 ||
    capture_word[63:60] == 4'ha;
  assign capture_ready = captured_count < WORDS;
  assign capture_accept = capture_enable && capture_valid;
  assign capture_store_fire = capture_accept && capture_replay_critical;
  assign capture_word_delta =
    capture_word[59] ? {16'h0, capture_word[7:0], capture_word[55:48]} :
                       {24'h0, capture_word[55:48]};
  assign capture_next_commit = capture_commit_index + capture_word_delta;
  assign capture_store_delta = capture_next_commit - capture_last_stored_commit;
  assign capture_store_delta_wide = capture_store_delta > 32'hff;

  always_comb begin
    capture_store_word = capture_word;
    capture_store_word[59] = capture_store_delta_wide;
    capture_store_word[55:48] = capture_store_delta[7:0];
    if (capture_store_delta_wide) begin
      capture_store_word[7:0] = capture_store_delta[15:8];
    end
  end

  assign capsule_valid = active && !underflow && sent_count < expected_count;
  assign capsule_word = memory[sent_count[ADDR_W-1:0]];

  always_ff @(posedge clk) begin
    if (load_valid) begin
      memory[load_addr] <= load_word;
    end else if (capture_store_fire && capture_ready) begin
      memory[captured_count[ADDR_W-1:0]] <= capture_store_word;
    end
  end

  always_ff @(posedge clk) begin
    if (store_clear || clear) begin
      captured_count <= 32'h0;
      capture_overflow <= 1'b0;
      capture_commit_index <= 32'h0;
      capture_last_stored_commit <= 32'h0;
    end else if (capture_accept) begin
      capture_commit_index <= capture_next_commit;
      if (capture_replay_critical) begin
        if (capture_ready) begin
          captured_count <= captured_count + 32'd1;
          capture_last_stored_commit <= capture_next_commit;
        end else begin
          capture_overflow <= 1'b1;
        end
      end
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active <= 1'b0;
      stream_done <= 1'b0;
      underflow <= 1'b0;
      sent_count <= 32'h0;
    end else begin
      if (clear) begin
        active <= 1'b0;
        stream_done <= 1'b0;
        underflow <= 1'b0;
        sent_count <= 32'h0;
      end else if (start) begin
        sent_count <= 32'h0;
        underflow <= expected_count > WORDS;
        active <= expected_count != 32'h0 && expected_count <= WORDS;
        stream_done <= expected_count == 32'h0;
      end else if (capsule_valid && capsule_ready) begin
        sent_count <= sent_count + 32'd1;
        if (sent_count + 32'd1 >= expected_count) begin
          active <= 1'b0;
          stream_done <= 1'b1;
        end
      end
    end
  end
endmodule
