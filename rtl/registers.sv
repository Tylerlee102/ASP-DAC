module registers #(
  parameter logic [31:0] BASE_ADDR = 32'h4001_0000
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,

  input  logic        bus_valid,
  input  logic        bus_write,
  input  logic [31:0] bus_addr,
  input  logic [31:0] bus_wdata,
  output logic        bus_ready,
  output logic [31:0] bus_rdata,

  input  logic        capsule_frozen,
  input  logic        capsule_overflow,
  input  logic [31:0] event_count,
  input  logic [31:0] failure_signature,

  output logic [3:0]  capture_mode,
  output logic        capsule_clear,
  output logic        replay_enable
);
  localparam logic [31:0] REG_CONTROL = BASE_ADDR + 32'h00;
  localparam logic [31:0] REG_STATUS  = BASE_ADDR + 32'h04;
  localparam logic [31:0] REG_COUNT   = BASE_ADDR + 32'h08;
  localparam logic [31:0] REG_SIG     = BASE_ADDR + 32'h0c;

  logic selected;
  assign selected = bus_valid && bus_addr[31:4] == BASE_ADDR[31:4];
  assign bus_ready = selected;

  always_comb begin
    bus_rdata = 32'h0;
    if (selected && !bus_write) begin
      unique case (bus_addr)
        REG_CONTROL: bus_rdata = {27'h0, replay_enable, capture_mode};
        REG_STATUS:  bus_rdata = {30'h0, capsule_overflow, capsule_frozen};
        REG_COUNT:   bus_rdata = event_count;
        REG_SIG:     bus_rdata = failure_signature;
        default:     bus_rdata = 32'h0;
      endcase
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      capture_mode <= 4'h3;
      replay_enable <= 1'b0;
      capsule_clear <= 1'b0;
    end else if (clear) begin
      capture_mode <= 4'h3;
      replay_enable <= 1'b0;
      capsule_clear <= 1'b1;
    end else begin
      capsule_clear <= 1'b0;
      if (selected && bus_write && bus_addr == REG_CONTROL) begin
        capture_mode <= bus_wdata[3:0];
        replay_enable <= bus_wdata[4];
        capsule_clear <= bus_wdata[8];
      end
    end
  end
endmodule

