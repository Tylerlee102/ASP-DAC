module mapped_memory #(
  parameter int WORDS = 2048,
  parameter int ADDR_W = $clog2(WORDS)
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        mem_valid,
  input  logic        mem_instr,
  output logic        mem_ready,
  input  logic [31:0] mem_addr,
  input  logic [31:0] mem_wdata,
  input  logic [3:0]  mem_wstrb,
  output logic [31:0] mem_rdata,
  input  logic [3:0]  gpio_in,
  output logic [7:0]  gpio_out,
  input  logic        uart_rx,
  output logic        uart_tx,
  output logic [31:0] io_status
);
  (* ram_style = "block" *) logic [31:0] mem [0:WORDS-1];

  logic [ADDR_W-1:0] word_addr;
  logic is_memory_access;
  logic is_io_access;
  logic [31:0] io_read_value;
  logic [31:0] ram_rdata;
  logic [31:0] io_rdata;
  logic last_memory_access;
  logic [31:0] status_counter;

  assign word_addr = mem_addr[ADDR_W+1:2];
  assign is_memory_access = (mem_addr[31:ADDR_W+2] == '0);
  assign is_io_access = (mem_addr[31:8] == 24'h1000_00);

  always_comb begin
    io_read_value = 32'h0;
    if (is_io_access) begin
      unique case (mem_addr[7:0])
        8'h00: io_read_value = {20'h0, gpio_in, gpio_out};
        8'h04: io_read_value = {31'h0, uart_rx};
        8'h08: io_read_value = io_status;
        default: io_read_value = {mem_addr[15:0], gpio_in, uart_rx, 11'h35a};
      endcase
    end else begin
      io_read_value = mem_addr ^ {22'h0, gpio_in, uart_rx, mem_instr, mem_wstrb};
    end
  end

  always_ff @(posedge clk) begin
    if (mem_valid) begin
      last_memory_access <= is_memory_access;
      if (is_memory_access) begin
        ram_rdata <= mem[word_addr];
        if (|mem_wstrb) mem[word_addr] <= mem_wdata;
      end else begin
        io_rdata <= io_read_value;
      end
    end
  end

  assign mem_rdata = last_memory_access ? ram_rdata : io_rdata;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      mem_ready <= 1'b0;
      gpio_out <= 8'h0;
      uart_tx <= 1'b1;
      io_status <= 32'h0;
      status_counter <= 32'h0;
    end else begin
      mem_ready <= mem_valid;
      status_counter <= status_counter + {31'h0, mem_valid};
      io_status <= status_counter ^ mem_addr ^ mem_wdata ^ {22'h0, gpio_in, uart_rx, mem_instr, mem_wstrb};
      if (mem_valid && !is_memory_access && is_io_access && |mem_wstrb) begin
        unique case (mem_addr[7:0])
          8'h00: gpio_out <= mem_wdata[7:0];
          8'h04: uart_tx <= mem_wdata[0];
          default: begin
            gpio_out <= gpio_out ^ mem_wdata[7:0];
            uart_tx <= uart_tx ^ mem_wdata[8];
          end
        endcase
      end
    end
  end
endmodule
