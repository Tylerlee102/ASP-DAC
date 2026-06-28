module rcv2_address_dictionary #(
  parameter int ENTRIES = 8,
  parameter int INDEX_W = (ENTRIES <= 2) ? 1 : $clog2(ENTRIES)
) (
  input  logic               clk,
  input  logic               rst_n,
  input  logic               clear,
  input  logic               lookup_valid,
  input  logic               allocate,
  input  logic [31:0]        lookup_addr,
  output logic               dict_hit,
  output logic [INDEX_W-1:0] dict_index
);
  logic [31:0] dict_addr [0:ENTRIES-1];
  logic        dict_valid [0:ENTRIES-1];
  logic [INDEX_W-1:0] write_ptr;

  always_comb begin
    dict_hit = 1'b0;
    dict_index = write_ptr;
    for (int i = 0; i < ENTRIES; i = i + 1) begin
      if (lookup_valid && dict_valid[i] && dict_addr[i] == lookup_addr && !dict_hit) begin
        dict_hit = 1'b1;
        dict_index = INDEX_W'(i);
      end
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      write_ptr <= '0;
      for (int i = 0; i < ENTRIES; i = i + 1) begin
        dict_addr[i] <= 32'h0;
        dict_valid[i] <= 1'b0;
      end
    end else if (clear) begin
      write_ptr <= '0;
      for (int i = 0; i < ENTRIES; i = i + 1) begin
        dict_addr[i] <= 32'h0;
        dict_valid[i] <= 1'b0;
      end
    end else if (lookup_valid && allocate && !dict_hit) begin
      dict_addr[write_ptr] <= lookup_addr;
      dict_valid[write_ptr] <= 1'b1;
      if (write_ptr == INDEX_W'(ENTRIES - 1)) begin
        write_ptr <= '0;
      end else begin
        write_ptr <= write_ptr + 1'b1;
      end
    end
  end
endmodule
