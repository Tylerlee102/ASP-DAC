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
  input  logic [31:0] replay_critical_event_count,
  input  logic [31:0] stream_stall_count,
  input  logic [31:0] dropped_diagnostic_count,
  input  logic [31:0] replay_critical_overflow_count,

  output logic [3:0]  capture_mode,
  output logic        capsule_clear,
  output logic        replay_enable
);
  localparam logic [31:0] REG_CONTROL = BASE_ADDR + 32'h00;
  localparam logic [31:0] REG_STATUS  = BASE_ADDR + 32'h04;
  localparam logic [31:0] REG_COUNT   = BASE_ADDR + 32'h08;
  localparam logic [31:0] REG_SIG     = BASE_ADDR + 32'h0c;
  localparam logic [31:0] REG_STREAM_STATUS = BASE_ADDR + 32'h10;
  localparam logic [31:0] REG_CRITICAL_COUNT = BASE_ADDR + 32'h14;
  localparam logic [31:0] REG_STREAM_STALLS = BASE_ADDR + 32'h18;
  localparam logic [31:0] REG_DIAG_DROPS = BASE_ADDR + 32'h1c;
  localparam logic [31:0] REG_CRITICAL_OVERFLOW = BASE_ADDR + 32'h20;

  logic selected;
  always_comb begin
    selected = 1'b0;
    if (bus_valid) begin
      unique case (bus_addr)
        REG_CONTROL,
        REG_STATUS,
        REG_COUNT,
        REG_SIG,
        REG_STREAM_STATUS,
        REG_CRITICAL_COUNT,
        REG_STREAM_STALLS,
        REG_DIAG_DROPS,
        REG_CRITICAL_OVERFLOW: selected = 1'b1;
        default: selected = 1'b0;
      endcase
    end
  end
  assign bus_ready = selected;

  always_comb begin
    bus_rdata = 32'h0;
    if (selected && !bus_write) begin
      unique case (bus_addr)
        REG_CONTROL: bus_rdata = {27'h0, replay_enable, capture_mode};
        REG_STATUS:  bus_rdata = {30'h0, capsule_overflow, capsule_frozen};
        REG_COUNT:   bus_rdata = event_count;
        REG_SIG:     bus_rdata = failure_signature;
        REG_STREAM_STATUS: bus_rdata = {
          29'h0,
          replay_critical_overflow_count != 32'h0,
          dropped_diagnostic_count != 32'h0,
          stream_stall_count != 32'h0
        };
        REG_CRITICAL_COUNT: bus_rdata = replay_critical_event_count;
        REG_STREAM_STALLS: bus_rdata = stream_stall_count;
        REG_DIAG_DROPS: bus_rdata = dropped_diagnostic_count;
        REG_CRITICAL_OVERFLOW: bus_rdata = replay_critical_overflow_count;
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
