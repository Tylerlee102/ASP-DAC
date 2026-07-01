module rcv1_mmio_replay_driver #(
  parameter int DEPTH = 256,
  parameter int ADDR_W = $clog2(DEPTH),
  parameter int EVENT_WIDTH = 168
) (
  input  logic                   clk,
  input  logic                   rst_n,
  input  logic                   store_clear,

  input  logic                   load_valid,
  input  logic [ADDR_W-1:0]      load_addr,
  input  logic [EVENT_WIDTH-1:0] load_packet,

  input  logic                   replay_enable,
  input  logic                   observed_valid,
  input  logic                   observed_mmio_read,
  input  logic [31:0]            observed_addr,

  output logic                   replay_valid,
  output logic [31:0]            replay_value,
  output logic [31:0]            loaded_count,
  output logic [31:0]            hit_count,
  output logic                   replay_miss
);
  localparam logic [3:0] EV_MMIO_READ = 4'h5;

  logic [EVENT_WIDTH-1:0] packet_store [0:DEPTH-1];
  logic [31:0] load_addr_plus_one;
  integer scan_index;

  assign load_addr_plus_one = {{(32-ADDR_W){1'b0}}, load_addr} + 32'h1;

  always_comb begin
    replay_valid = 1'b0;
    replay_value = 32'h0;
    for (scan_index = 0; scan_index < DEPTH; scan_index = scan_index + 1) begin
      if (
        replay_enable &&
        observed_valid &&
        observed_mmio_read &&
        scan_index[31:0] < loaded_count &&
        packet_store[scan_index][167:164] == EV_MMIO_READ &&
        packet_store[scan_index][63:32] == observed_addr &&
        !replay_valid
      ) begin
        replay_valid = 1'b1;
        replay_value = packet_store[scan_index][31:0];
      end
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      loaded_count <= 32'h0;
      hit_count <= 32'h0;
      replay_miss <= 1'b0;
    end else if (store_clear) begin
      loaded_count <= 32'h0;
      hit_count <= 32'h0;
      replay_miss <= 1'b0;
    end else begin
      if (load_valid) begin
        packet_store[load_addr] <= load_packet;
        if (load_addr_plus_one > loaded_count) begin
          loaded_count <= load_addr_plus_one;
        end
      end
      if (replay_enable && observed_valid && observed_mmio_read) begin
        if (replay_valid) begin
          hit_count <= hit_count + 32'h1;
        end else begin
          replay_miss <= 1'b1;
        end
      end
    end
  end
endmodule
