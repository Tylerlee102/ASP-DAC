module rcv2_event_stream_fifo #(
  parameter int WORD_WIDTH = 64,
  parameter int DEPTH = 16,
  parameter int ADDR_W = (DEPTH <= 2) ? 1 : $clog2(DEPTH)
) (
  input  logic                  clk,
  input  logic                  rst_n,
  input  logic                  clear,

  input  logic                  push_valid,
  output logic                  push_ready,
  input  logic [WORD_WIDTH-1:0] push_data,
  input  logic                  freeze,

  input  logic [ADDR_W-1:0]     read_addr,
  output logic [WORD_WIDTH-1:0] read_data,

  output logic                  stream_valid,
  input  logic                  stream_ready,
  output logic [WORD_WIDTH-1:0] stream_data,

  output logic                  frozen,
  output logic                  overflow,
  output logic [ADDR_W:0]       used_words
);
  (* ram_style = "block" *) logic [WORD_WIDTH-1:0] mem [0:DEPTH-1];
  logic [ADDR_W-1:0] write_ptr;
  logic [ADDR_W-1:0] read_ptr;
  logic push_fire;
  logic pop_fire;

  localparam logic [ADDR_W:0] DEPTH_COUNT = (ADDR_W + 1)'(DEPTH);

  assign push_ready = !frozen && (used_words < DEPTH_COUNT);
  assign stream_valid = used_words != '0;
  assign stream_data = mem[read_ptr];
  assign read_data = mem[read_addr];
  assign push_fire = push_valid && push_ready;
  assign pop_fire = stream_valid && stream_ready;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      write_ptr <= '0;
      read_ptr <= '0;
      used_words <= '0;
      frozen <= 1'b0;
      overflow <= 1'b0;
    end else if (clear) begin
      write_ptr <= '0;
      read_ptr <= '0;
      used_words <= '0;
      frozen <= 1'b0;
      overflow <= 1'b0;
    end else begin
      if (push_fire) begin
        mem[write_ptr] <= push_data;
        write_ptr <= write_ptr + 1'b1;
      end else if (push_valid) begin
        overflow <= 1'b1;
      end

      if (pop_fire) begin
        read_ptr <= read_ptr + 1'b1;
      end

      unique case ({push_fire, pop_fire})
        2'b10: used_words <= used_words + 1'b1;
        2'b01: used_words <= used_words - 1'b1;
        default: used_words <= used_words;
      endcase

      if (freeze) begin
        frozen <= 1'b1;
      end
    end
  end
endmodule
