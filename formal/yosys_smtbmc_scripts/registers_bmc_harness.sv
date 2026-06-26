`default_nettype none

module registers_bmc_harness (
  input logic clk
);
  localparam logic [31:0] BASE_ADDR = 32'h4001_0000;
  localparam logic [31:0] REG_CONTROL = BASE_ADDR + 32'h00;
  localparam logic [31:0] REG_STATUS = BASE_ADDR + 32'h04;
  localparam logic [31:0] REG_COUNT = BASE_ADDR + 32'h08;
  localparam logic [31:0] REG_SIG = BASE_ADDR + 32'h0c;

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic clear_any;
  (* anyseq *) logic bus_valid;
  (* anyseq *) logic bus_write;
  (* anyseq *) logic [31:0] bus_addr;
  (* anyseq *) logic [31:0] bus_wdata;
  (* anyseq *) logic capsule_frozen;
  (* anyseq *) logic capsule_overflow;
  (* anyseq *) logic [31:0] event_count;
  (* anyseq *) logic [31:0] failure_signature;

  logic clear;
  logic bus_ready;
  logic [31:0] bus_rdata;
  logic [3:0] capture_mode;
  logic capsule_clear;
  logic replay_enable;
  logic selected;
  logic [31:0] expected_rdata;

  logic past_valid = 1'b0;
  logic prev_rst_n;
  logic prev_clear;
  logic prev_selected;
  logic prev_bus_write;
  logic [31:0] prev_bus_addr;
  logic [31:0] prev_bus_wdata;
  logic [3:0] prev_capture_mode;
  logic prev_capsule_clear;
  logic prev_replay_enable;

  assign clear = rst_n && clear_any;
  assign selected = bus_valid && bus_addr[31:4] == BASE_ADDR[31:4];

  always_comb begin
    expected_rdata = 32'h0;
    if (selected && !bus_write) begin
      unique case (bus_addr)
        REG_CONTROL: expected_rdata = {27'h0, replay_enable, capture_mode};
        REG_STATUS: expected_rdata = {30'h0, capsule_overflow, capsule_frozen};
        REG_COUNT: expected_rdata = event_count;
        REG_SIG: expected_rdata = failure_signature;
        default: expected_rdata = 32'h0;
      endcase
    end
  end

  registers #(
    .BASE_ADDR(BASE_ADDR)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .bus_valid(bus_valid),
    .bus_write(bus_write),
    .bus_addr(bus_addr),
    .bus_wdata(bus_wdata),
    .bus_ready(bus_ready),
    .bus_rdata(bus_rdata),
    .capsule_frozen(capsule_frozen),
    .capsule_overflow(capsule_overflow),
    .event_count(event_count),
    .failure_signature(failure_signature),
    .capture_mode(capture_mode),
    .capsule_clear(capsule_clear),
    .replay_enable(replay_enable)
  );

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;
    prev_rst_n <= rst_n;
    prev_clear <= clear;
    prev_selected <= selected;
    prev_bus_write <= bus_write;
    prev_bus_addr <= bus_addr;
    prev_bus_wdata <= bus_wdata;
    prev_capture_mode <= capture_mode;
    prev_capsule_clear <= capsule_clear;
    prev_replay_enable <= replay_enable;

    assert(bus_ready == selected);
    assert(bus_rdata == expected_rdata);

    if (past_valid) begin
      if (!prev_rst_n) begin
        assert(capture_mode == 4'h3);
        assert(!replay_enable);
        assert(!capsule_clear);
      end else if (prev_clear) begin
        assert(capture_mode == 4'h3);
        assert(!replay_enable);
        assert(capsule_clear);
      end else if (prev_selected && prev_bus_write && prev_bus_addr == REG_CONTROL) begin
        assert(capture_mode == prev_bus_wdata[3:0]);
        assert(replay_enable == prev_bus_wdata[4]);
        assert(capsule_clear == prev_bus_wdata[8]);
      end else begin
        assert(capture_mode == prev_capture_mode);
        assert(replay_enable == prev_replay_enable);
        assert(!capsule_clear);
      end

      if (prev_capsule_clear && prev_rst_n && !prev_clear) begin
        assert(!capsule_clear || (prev_selected && prev_bus_write && prev_bus_addr == REG_CONTROL && prev_bus_wdata[8]));
      end

      cover(selected && !bus_write && bus_addr == REG_STATUS && bus_ready);
      cover(selected && !bus_write && bus_addr == REG_COUNT && bus_rdata == event_count);
      cover(prev_selected && prev_bus_write && prev_bus_addr == REG_CONTROL && replay_enable == prev_bus_wdata[4]);
      cover(prev_clear && capsule_clear && capture_mode == 4'h3);
    end
  end
endmodule

`default_nettype wire
