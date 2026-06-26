`default_nettype none

module mmio_interrupt_loggers_bmc_harness (
  input logic clk
);
  `include "../../rtl/event_defs.svh"

  localparam logic [31:0] MMIO_BASE = 32'h4000_0000;
  localparam logic [31:0] MMIO_MASK = 32'hffff_0000;

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic clear_any;
  (* anyseq *) logic bus_valid;
  (* anyseq *) logic bus_write;
  (* anyseq *) logic [31:0] bus_addr;
  (* anyseq *) logic [31:0] bus_wdata;
  (* anyseq *) logic [31:0] bus_rdata;
  (* anyseq *) logic [31:0] mmio_commit_index;
  (* anyseq *) logic [31:0] mmio_pc;
  (* anyseq *) logic trap_enter;
  (* anyseq *) logic trap_exit;
  (* anyseq *) logic [31:0] irq_commit_index;
  (* anyseq *) logic [31:0] irq_pc;

  logic clear;
  logic is_mmio;
  logic mmio_event_valid;
  logic [3:0] mmio_event_type;
  logic [31:0] mmio_event_commit_index;
  logic [31:0] mmio_event_pc;
  logic [31:0] mmio_event_addr;
  logic [31:0] mmio_event_data;
  logic irq_event_valid;
  logic [3:0] irq_event_type;
  logic [31:0] irq_event_commit_index;
  logic [31:0] irq_event_pc;
  logic [31:0] irq_event_data;
  logic unpaired_exit;
  logic [7:0] active_depth;

  logic past_valid = 1'b0;
  logic prev_rst_n;
  logic prev_clear;
  logic prev_trap_enter;
  logic prev_trap_exit;
  logic prev_unpaired_exit;
  logic [7:0] prev_active_depth;

  assign clear = rst_n && clear_any;
  assign is_mmio = (bus_addr & MMIO_MASK) == (MMIO_BASE & MMIO_MASK);

  mmio_logger #(
    .MMIO_BASE(MMIO_BASE),
    .MMIO_MASK(MMIO_MASK)
  ) u_mmio_logger (
    .bus_valid(bus_valid),
    .bus_write(bus_write),
    .bus_addr(bus_addr),
    .bus_wdata(bus_wdata),
    .bus_rdata(bus_rdata),
    .commit_index(mmio_commit_index),
    .pc(mmio_pc),
    .event_valid(mmio_event_valid),
    .event_type(mmio_event_type),
    .event_commit_index(mmio_event_commit_index),
    .event_pc(mmio_event_pc),
    .event_addr(mmio_event_addr),
    .event_data(mmio_event_data)
  );

  interrupt_logger u_interrupt_logger (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .trap_enter(trap_enter),
    .trap_exit(trap_exit),
    .commit_index(irq_commit_index),
    .pc(irq_pc),
    .event_valid(irq_event_valid),
    .event_type(irq_event_type),
    .event_commit_index(irq_event_commit_index),
    .event_pc(irq_event_pc),
    .event_data(irq_event_data),
    .unpaired_exit(unpaired_exit),
    .active_depth(active_depth)
  );

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;
    prev_rst_n <= rst_n;
    prev_clear <= clear;
    prev_trap_enter <= trap_enter;
    prev_trap_exit <= trap_exit;
    prev_unpaired_exit <= unpaired_exit;
    prev_active_depth <= active_depth;

    assert(mmio_event_valid == (bus_valid && is_mmio));
    assert(mmio_event_type == (bus_write ? EV_MMIO_WRITE : EV_MMIO_READ));
    assert(mmio_event_commit_index == mmio_commit_index);
    assert(mmio_event_pc == mmio_pc);
    assert(mmio_event_addr == bus_addr);
    assert(mmio_event_data == (bus_write ? bus_wdata : bus_rdata));

    assert(irq_event_valid == (trap_enter || trap_exit));
    assert(irq_event_type == (trap_enter ? EV_INTERRUPT_ENTER : EV_INTERRUPT_EXIT));
    assert(irq_event_commit_index == irq_commit_index);
    assert(irq_event_pc == irq_pc);
    assert(irq_event_data == {24'h0, active_depth});

    if (past_valid) begin
      if (!prev_rst_n || prev_clear) begin
        assert(active_depth == 8'h0);
        assert(!unpaired_exit);
      end else if (prev_trap_enter && !prev_trap_exit) begin
        assert(active_depth == prev_active_depth + 8'h1);
      end else if (prev_trap_exit && !prev_trap_enter && prev_active_depth == 8'h0) begin
        assert(active_depth == 8'h0);
        assert(unpaired_exit);
      end else if (prev_trap_exit && !prev_trap_enter && prev_active_depth != 8'h0) begin
        assert(active_depth == prev_active_depth - 8'h1);
      end else begin
        assert(active_depth == prev_active_depth);
      end

      if (prev_unpaired_exit && prev_rst_n && !prev_clear) begin
        assert(unpaired_exit);
      end

      cover(bus_valid && !bus_write && is_mmio && mmio_event_valid && mmio_event_type == EV_MMIO_READ);
      cover(bus_valid && bus_write && is_mmio && mmio_event_valid && mmio_event_type == EV_MMIO_WRITE);
      cover(prev_trap_enter && !prev_trap_exit && active_depth == prev_active_depth + 8'h1);
      cover(prev_trap_exit && !prev_trap_enter && prev_active_depth != 8'h0 && active_depth == prev_active_depth - 8'h1);
      cover(prev_trap_exit && !prev_trap_enter && prev_active_depth == 8'h0 && unpaired_exit);
    end
  end
endmodule

`default_nettype wire
