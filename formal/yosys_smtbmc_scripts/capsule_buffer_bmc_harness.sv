`default_nettype none

module capsule_buffer_bmc_harness (
  input logic clk
);
  localparam int FORMAL_DEPTH = 4;
  localparam int FORMAL_ADDR_W = $clog2(FORMAL_DEPTH);
  localparam int FORMAL_EVENT_WIDTH = 168;
  localparam logic [FORMAL_ADDR_W:0] DEPTH_COUNT = (FORMAL_ADDR_W + 1)'(FORMAL_DEPTH);

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic clear_any;
  (* anyseq *) logic event_valid;
  (* anyseq *) logic [FORMAL_EVENT_WIDTH-1:0] event_packet;
  (* anyseq *) logic fail_freeze;
  (* anyseq *) logic [FORMAL_ADDR_W-1:0] read_addr;

  logic clear;
  logic [FORMAL_EVENT_WIDTH-1:0] read_data;
  logic frozen;
  logic overflow;
  logic [FORMAL_ADDR_W:0] write_count;
  logic past_valid = 1'b0;

  assign clear = rst_n && clear_any;

  capsule_buffer #(
    .EVENT_WIDTH(FORMAL_EVENT_WIDTH),
    .DEPTH(FORMAL_DEPTH),
    .ADDR_W(FORMAL_ADDR_W)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .event_valid(event_valid),
    .event_packet(event_packet),
    .fail_freeze(fail_freeze),
    .read_addr(read_addr),
    .read_data(read_data),
    .frozen(frozen),
    .overflow(overflow),
    .write_count(write_count)
  );

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;

    if (past_valid && rst_n && $past(rst_n)) begin
      assert(write_count <= DEPTH_COUNT);

      if (!clear && !$past(clear)) begin
        if ($past(fail_freeze)) begin
          assert(frozen);
        end

        if ($past(frozen)) begin
          assert(frozen);
          assert(write_count == $past(write_count));
        end

        if ($past(overflow)) begin
          assert(overflow);
        end

        if ($past(event_valid) && !$past(frozen) && $past(write_count) < DEPTH_COUNT) begin
          assert(write_count == $past(write_count) + 1'b1);
        end

        if ($past(event_valid) && !$past(frozen) && $past(write_count) == DEPTH_COUNT) begin
          assert(overflow);
          assert(write_count == DEPTH_COUNT);
        end
      end
    end

    cover(rst_n && !clear && event_valid && write_count == 1);
    cover(rst_n && !clear && frozen);
    cover(rst_n && !clear && overflow);
  end

  logic [FORMAL_EVENT_WIDTH-1:0] unused_read_data;
  assign unused_read_data = read_data;
endmodule

`default_nettype wire
