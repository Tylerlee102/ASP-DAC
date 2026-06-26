`include "event_pkg.sv"

module mmio_logger #(
  parameter logic [31:0] MMIO_BASE = 32'h4000_0000,
  parameter logic [31:0] MMIO_MASK = 32'hffff_0000
) (
  input  logic        bus_valid,
  input  logic        bus_write,
  input  logic [31:0] bus_addr,
  input  logic [31:0] bus_wdata,
  input  logic [31:0] bus_rdata,
  input  logic [31:0] commit_index,
  input  logic [31:0] pc,

  output logic        event_valid,
  output logic [3:0]  event_type,
  output logic [31:0] event_commit_index,
  output logic [31:0] event_pc,
  output logic [31:0] event_addr,
  output logic [31:0] event_data
);
  `include "event_defs.svh"

  logic is_mmio;
  assign is_mmio = (bus_addr & MMIO_MASK) == (MMIO_BASE & MMIO_MASK);

  always_comb begin
    event_valid = bus_valid && is_mmio;
    event_type = bus_write ? EV_MMIO_WRITE : EV_MMIO_READ;
    event_commit_index = commit_index;
    event_pc = pc;
    event_addr = bus_addr;
    event_data = bus_write ? bus_wdata : bus_rdata;
  end
endmodule
