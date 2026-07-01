`timescale 1ns/1ps

module tb_hazard3_irq_smoke;
  localparam integer MEM_WORDS = 8192;
  localparam [31:0] MMIO_IRQ_REQUEST = 32'h4000_0000;
  localparam [31:0] MMIO_IRQ_ACK     = 32'h4000_0004;
  localparam [31:0] MMIO_DONE        = 32'h4000_0008;
  localparam [31:0] MMIO_ISR_MARK    = 32'h4000_0010;
  localparam [31:0] NOP              = 32'h0000_0013;

  reg clk;
  reg rst_n;
  reg [31:0] mem [0:MEM_WORDS-1];
  reg [31:0] cycle_count;
  reg [31:0] max_cycles;
  reg [1023:0] memfile;
  reg trace_writes;
  integer init_i;

  wire pwrup_req;
  wire clk_en;
  wire unblock_out;
  wire [31:0] haddr;
  wire hwrite;
  wire [1:0] htrans;
  wire [2:0] hsize;
  wire [2:0] hburst;
  wire [3:0] hprot;
  wire hmastlock;
  wire [7:0] hmaster;
  wire hexcl;
  wire [31:0] hwdata;
  reg [31:0] hrdata;
  wire hready;
  wire hresp;
  wire hexokay;
  wire fence_i_vld;
  wire fence_d_vld;
  wire dbg_halted;
  wire dbg_running;
  wire [31:0] dbg_data0_wdata;
  wire dbg_data0_wen;
  wire dbg_instr_data_rdy;
  wire dbg_instr_caught_exception;
  wire dbg_instr_caught_ebreak;
  wire dbg_sbus_rdy;
  wire dbg_sbus_err;
  wire [31:0] dbg_sbus_rdata;

  reg dph_valid;
  reg dph_write;
  reg [2:0] dph_size;
  reg [31:0] dph_addr;
  reg irq_ext;
  reg done;
  reg [31:0] done_value;
  reg [31:0] irq_request_writes;
  reg [31:0] irq_ack_writes;
  reg [31:0] isr_marker_writes;
  reg [31:0] isr_marker_value;

  assign hready = 1'b1;
  assign hresp = 1'b0;
  assign hexokay = 1'b1;

  hazard3_cpu_1port #(
    .RESET_VECTOR(32'h0000_0080),
    .MTVEC_INIT(32'h0000_0010),
    .EXTENSION_A(0),
    .EXTENSION_C(0),
    .EXTENSION_M(0),
    .CSR_COUNTER(0),
    .DEBUG_SUPPORT(0),
    .RESET_REGFILE(1)
  ) u_core (
    .clk(clk),
    .clk_always_on(clk),
    .rst_n(rst_n),
    .pwrup_req(pwrup_req),
    .pwrup_ack(1'b1),
    .clk_en(clk_en),
    .unblock_out(unblock_out),
    .unblock_in(1'b0),
    .haddr(haddr),
    .hwrite(hwrite),
    .htrans(htrans),
    .hsize(hsize),
    .hburst(hburst),
    .hprot(hprot),
    .hmastlock(hmastlock),
    .hmaster(hmaster),
    .hexcl(hexcl),
    .hready(hready),
    .hresp(hresp),
    .hexokay(hexokay),
    .hwdata(hwdata),
    .hrdata(hrdata),
    .fence_i_vld(fence_i_vld),
    .fence_d_vld(fence_d_vld),
    .fence_rdy(1'b1),
    .dbg_req_halt(1'b0),
    .dbg_req_halt_on_reset(1'b0),
    .dbg_req_resume(1'b0),
    .dbg_halted(dbg_halted),
    .dbg_running(dbg_running),
    .dbg_data0_rdata(32'h0),
    .dbg_data0_wdata(dbg_data0_wdata),
    .dbg_data0_wen(dbg_data0_wen),
    .dbg_instr_data(32'h0),
    .dbg_instr_data_vld(1'b0),
    .dbg_instr_data_rdy(dbg_instr_data_rdy),
    .dbg_instr_caught_exception(dbg_instr_caught_exception),
    .dbg_instr_caught_ebreak(dbg_instr_caught_ebreak),
    .dbg_sbus_addr(32'h0),
    .dbg_sbus_write(1'b0),
    .dbg_sbus_size(2'b00),
    .dbg_sbus_vld(1'b0),
    .dbg_sbus_rdy(dbg_sbus_rdy),
    .dbg_sbus_err(dbg_sbus_err),
    .dbg_sbus_wdata(32'h0),
    .dbg_sbus_rdata(dbg_sbus_rdata),
    .mhartid_val(32'h0),
    .eco_version(4'h0),
    .irq(irq_ext),
    .soft_irq(1'b0),
    .timer_irq(1'b0)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  function [31:0] read_word;
    input [31:0] addr;
    begin
      if (addr[31:16] == 16'h4000) begin
        read_word = 32'h0;
      end else if (addr[31:2] < MEM_WORDS) begin
        read_word = mem[addr[31:2]];
      end else begin
        read_word = NOP;
      end
    end
  endfunction

  always @* begin
    hrdata = read_word(dph_addr);
  end

  task write_mem;
    input [31:0] addr;
    input [2:0] size;
    input [31:0] data;
    reg [31:0] current;
    integer lane;
    begin
      if (addr[31:2] < MEM_WORDS) begin
        current = mem[addr[31:2]];
        if (size == 3'b010) begin
          mem[addr[31:2]] = data;
        end else if (size == 3'b001) begin
          if (addr[1]) begin
            current[31:16] = data[15:0];
          end else begin
            current[15:0] = data[15:0];
          end
          mem[addr[31:2]] = current;
        end else begin
          lane = addr[1:0];
          current[lane * 8 +: 8] = data[7:0];
          mem[addr[31:2]] = current;
        end
      end
    end
  endtask

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      dph_valid <= 1'b0;
      dph_write <= 1'b0;
      dph_size <= 3'b000;
      dph_addr <= 32'h0;
      irq_ext <= 1'b0;
      done <= 1'b0;
      done_value <= 32'h0;
      irq_request_writes <= 32'h0;
      irq_ack_writes <= 32'h0;
      isr_marker_writes <= 32'h0;
      isr_marker_value <= 32'h0;
    end else begin
      dph_valid <= htrans[1] && hready;
      dph_write <= hwrite;
      dph_size <= hsize;
      dph_addr <= haddr;
      if (dph_valid && dph_write) begin
        if (trace_writes) begin
          $display("HAZARD3_IRQ_TRACE cycle=%0d addr=%08x data=%08x size=%0d haddr_now=%08x hwrite_now=%0b htrans_now=%0d", cycle_count, dph_addr, hwdata, dph_size, haddr, hwrite, htrans);
        end
        if (dph_addr == MMIO_IRQ_REQUEST) begin
          irq_ext <= 1'b1;
          irq_request_writes <= irq_request_writes + 32'h1;
        end else if (dph_addr == MMIO_IRQ_ACK) begin
          irq_ext <= 1'b0;
          irq_ack_writes <= irq_ack_writes + 32'h1;
        end else if (dph_addr == MMIO_ISR_MARK) begin
          isr_marker_writes <= isr_marker_writes + 32'h1;
          isr_marker_value <= hwdata;
        end else if (dph_addr == MMIO_DONE) begin
          done <= 1'b1;
          done_value <= hwdata;
        end else if (dph_addr[31:16] != 16'h4000) begin
          write_mem(dph_addr, dph_size, hwdata);
        end
      end
    end
  end

  initial begin
    memfile = "build/hazard3_irq_smoke/hazard3_irq_smoke.mem";
    max_cycles = 2000;
    trace_writes = 1'b0;
    if (!$value$plusargs("MEMFILE=%s", memfile)) begin end
    if (!$value$plusargs("MAX_CYCLES=%d", max_cycles)) begin end
    if ($test$plusargs("TRACE_WRITES")) begin
      trace_writes = 1'b1;
    end
    for (init_i = 0; init_i < MEM_WORDS; init_i = init_i + 1) begin
      mem[init_i] = NOP;
    end
    $readmemh(memfile, mem);
    rst_n = 1'b0;
    repeat (10) @(posedge clk);
    rst_n = 1'b1;
    cycle_count = 0;
    while (cycle_count < max_cycles && !done) begin
      @(posedge clk);
      cycle_count = cycle_count + 1;
    end
    if (!done) begin
      $fatal(1, "Hazard3 IRQ smoke timed out request=%0d isr=%0d ack=%0d irq=%0b haddr=%08x htrans=%0d", irq_request_writes, isr_marker_writes, irq_ack_writes, irq_ext, haddr, htrans);
    end
    repeat (4) @(posedge clk);
    if (irq_request_writes != 32'd1 || isr_marker_writes != 32'd1 || irq_ack_writes != 32'd1 || done_value != 32'd1 || irq_ext != 1'b0) begin
      $fatal(1, "Hazard3 IRQ smoke mismatch request=%0d isr_writes=%0d isr_value=%0d ack=%0d done=%0d irq=%0b", irq_request_writes, isr_marker_writes, isr_marker_value, irq_ack_writes, done_value, irq_ext);
    end
    $display(
      "HAZARD3_IRQ_SMOKE_PASS cycles=%0d request_writes=%0d isr_writes=%0d isr_value=%0d ack_writes=%0d done_value=%0d irq_final=%0d",
      cycle_count,
      irq_request_writes,
      isr_marker_writes,
      isr_marker_value,
      irq_ack_writes,
      done_value,
      irq_ext
    );
    $finish;
  end

  wire unused_outputs = pwrup_req ^ clk_en ^ unblock_out ^ fence_i_vld ^ fence_d_vld ^ dbg_halted ^ dbg_running ^
                        dbg_data0_wen ^ dbg_instr_data_rdy ^ dbg_instr_caught_exception ^ dbg_instr_caught_ebreak ^
                        dbg_sbus_rdy ^ dbg_sbus_err ^ hmastlock ^ hexcl ^ ^hburst ^ ^hprot ^ ^hmaster ^
                        ^dbg_data0_wdata ^ ^dbg_sbus_rdata;
endmodule
