`include "event_pkg.sv"

module capsule_buffer #(
  parameter int EVENT_WIDTH = replaycapsule_event_pkg::RC_EVENT_WIDTH,
  parameter int DEPTH = 256,
  parameter int ADDR_W = $clog2(DEPTH)
) (
  input  logic                   clk,
  input  logic                   rst_n,
  input  logic                   clear,

  input  logic                   event_valid,
  input  logic [EVENT_WIDTH-1:0] event_packet,
  input  logic                   fail_freeze,

  input  logic [ADDR_W-1:0]      read_addr,
  output logic [EVENT_WIDTH-1:0] read_data,

  output logic                   frozen,
  output logic                   overflow,
  output logic [ADDR_W:0]        write_count
);
  logic [EVENT_WIDTH-1:0] mem [0:DEPTH-1];
  logic [ADDR_W-1:0] write_ptr;
  localparam logic [ADDR_W:0] DEPTH_COUNT = DEPTH;

  assign read_data = mem[read_addr];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      write_ptr   <= '0;
      write_count <= '0;
      frozen      <= 1'b0;
      overflow    <= 1'b0;
    end else if (clear) begin
      write_ptr   <= '0;
      write_count <= '0;
      frozen      <= 1'b0;
      overflow    <= 1'b0;
    end else begin
      if (event_valid && !frozen) begin
        if (write_count < DEPTH_COUNT) begin
          mem[write_ptr] <= event_packet;
          write_ptr <= write_ptr + 1'b1;
          write_count <= write_count + 1'b1;
        end else begin
          overflow <= 1'b1;
        end
      end

      if (fail_freeze) begin
        frozen <= 1'b1;
      end
    end
  end
endmodule
