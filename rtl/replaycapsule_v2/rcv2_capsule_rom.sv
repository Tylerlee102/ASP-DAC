module rcv2_capsule_rom #(
  parameter int WORD_WIDTH = 64,
  parameter int WORDS = 16,
  parameter int ADDR_W = (WORDS <= 2) ? 1 : $clog2(WORDS),
  parameter string INIT_FILE = ""
) (
  input  logic                  clk,
  input  logic [ADDR_W-1:0]     read_addr,
  output logic [WORD_WIDTH-1:0] read_data
);
  (* rom_style = "block" *) logic [WORD_WIDTH-1:0] rom [0:WORDS-1];

  initial begin
    if (INIT_FILE != "") begin
      $readmemh(INIT_FILE, rom);
    end
  end

  always_ff @(posedge clk) begin
    read_data <= rom[read_addr];
  end
endmodule
