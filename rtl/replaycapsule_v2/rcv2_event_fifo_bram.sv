module rcv2_event_fifo_bram #(
  parameter int WORD_WIDTH = 64,
  parameter int MEMORY_WORDS = 512,
  parameter int ADDR_W = (MEMORY_WORDS <= 2) ? 1 : $clog2(MEMORY_WORDS)
) (
  input  logic                    clk,
  input  logic                    rst_n,
  input  logic                    clear,
  input  logic                    write_valid,
  input  logic [WORD_WIDTH-1:0]   write_data,
  input  logic                    freeze,
  input  logic [ADDR_W-1:0]       read_addr,
  output logic [WORD_WIDTH-1:0]   read_data,
  output logic                    frozen,
  output logic                    overflow,
  output logic [ADDR_W:0]         used_words
);
  (* ram_style = "block" *) logic [WORD_WIDTH-1:0] mem [0:MEMORY_WORDS-1];
  logic [ADDR_W-1:0] write_ptr;
  localparam logic [ADDR_W:0] MEMORY_COUNT = (ADDR_W + 1)'(MEMORY_WORDS);

  assign read_data = mem[read_addr];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      write_ptr <= '0;
      used_words <= '0;
      frozen <= 1'b0;
      overflow <= 1'b0;
    end else if (clear) begin
      write_ptr <= '0;
      used_words <= '0;
      frozen <= 1'b0;
      overflow <= 1'b0;
    end else begin
      if (write_valid && !frozen) begin
        if (used_words < MEMORY_COUNT) begin
          mem[write_ptr] <= write_data;
          write_ptr <= write_ptr + 1'b1;
          used_words <= used_words + 1'b1;
        end else begin
          overflow <= 1'b1;
        end
      end

      if (freeze) begin
        frozen <= 1'b1;
      end
    end
  end
endmodule
