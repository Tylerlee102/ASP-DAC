`default_nettype none

module replay_mismatch_bmc_harness (
  input logic clk
);
  `include "../../rtl/event_defs.svh"

  localparam int FORMAL_EVENT_WIDTH = RC_EVENT_WIDTH;
  localparam logic [31:0] MATCH_CYCLE = 32'h0000_0010;
  localparam logic [31:0] MATCH_COMMIT = 32'h0000_0020;
  localparam logic [31:0] PAYLOAD_A = 32'h1234_abcd;
  localparam logic [31:0] PAYLOAD_B = 32'hfeed_1001;

  logic rst_n = 1'b0;
  logic [3:0] step = 4'h0;

  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
    if (!rst_n) begin
      step <= 4'h0;
    end else if (step != 4'hf) begin
      step <= step + 4'h1;
    end
  end

  logic clear;
  logic replay_enable;
  logic commit_index_mode;
  logic [31:0] current_cycle;
  logic [31:0] current_commit_index;
  logic replay_event_valid;
  logic [FORMAL_EVENT_WIDTH-1:0] replay_event_packet;
  logic replay_event_consume;
  logic inject_mmio_valid;
  logic [31:0] inject_mmio_value;
  logic inject_interrupt_enter;
  logic inject_interrupt_exit;
  logic replay_underflow;

  always_comb begin
    clear = 1'b0;
    replay_enable = rst_n;
    commit_index_mode = 1'b0;
    current_cycle = MATCH_CYCLE;
    current_commit_index = MATCH_COMMIT;
    replay_event_valid = 1'b1;
    replay_event_packet = rc_pack_event(EV_STORE, 4'h0, MATCH_CYCLE, MATCH_COMMIT, 32'h0, 32'h0, PAYLOAD_A);

    unique case (step)
      4'h0: begin
        replay_enable = 1'b0;
        replay_event_valid = 1'b0;
      end
      4'h1: begin
        replay_event_packet = rc_pack_event(EV_MMIO_READ, 4'h0, MATCH_CYCLE + 32'h1, MATCH_COMMIT, 32'h0, 32'h1000, PAYLOAD_A);
      end
      4'h2: begin
        commit_index_mode = 1'b1;
        replay_event_packet = rc_pack_event(EV_MMIO_READ, 4'h0, MATCH_CYCLE, MATCH_COMMIT + 32'h1, 32'h0, 32'h1000, PAYLOAD_A);
      end
      4'h3: begin
        replay_event_packet = rc_pack_event(EV_STORE, 4'h0, MATCH_CYCLE, MATCH_COMMIT, 32'h0, 32'h1000, PAYLOAD_A);
      end
      4'h4: begin
        replay_event_packet = rc_pack_event(EV_MMIO_READ, 4'h0, MATCH_CYCLE, MATCH_COMMIT, 32'h0, 32'h1000, PAYLOAD_A);
      end
      4'h5: begin
        replay_event_packet = rc_pack_event(EV_EXTERNAL_INPUT, 4'h0, MATCH_CYCLE, MATCH_COMMIT, 32'h0, 32'h0, PAYLOAD_B);
      end
      4'h6: begin
        replay_event_packet = rc_pack_event(EV_INTERRUPT_ENTER, 4'h0, MATCH_CYCLE, MATCH_COMMIT, 32'h0, 32'h0, 32'h7);
      end
      4'h7: begin
        replay_event_packet = rc_pack_event(EV_INTERRUPT_EXIT, 4'h0, MATCH_CYCLE, MATCH_COMMIT, 32'h0, 32'h0, 32'h7);
      end
      4'h8: begin
        replay_event_valid = 1'b0;
      end
      4'ha: begin
        clear = 1'b1;
      end
      default: begin
      end
    endcase
  end

  replay_control #(
    .EVENT_WIDTH(FORMAL_EVENT_WIDTH)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .replay_enable(replay_enable),
    .commit_index_mode(commit_index_mode),
    .current_cycle(current_cycle),
    .current_commit_index(current_commit_index),
    .replay_event_valid(replay_event_valid),
    .replay_event_packet(replay_event_packet),
    .replay_event_consume(replay_event_consume),
    .inject_mmio_valid(inject_mmio_valid),
    .inject_mmio_value(inject_mmio_value),
    .inject_interrupt_enter(inject_interrupt_enter),
    .inject_interrupt_exit(inject_interrupt_exit),
    .replay_underflow(replay_underflow)
  );

  logic no_injection;
  assign no_injection = !replay_event_consume && !inject_mmio_valid && !inject_interrupt_enter && !inject_interrupt_exit;

  always_ff @(posedge clk) begin
    if (rst_n) begin
      unique case (step)
        4'h1: assert(no_injection);
        4'h2: assert(no_injection);
        4'h3: assert(no_injection);
        4'h4: begin
          assert(replay_event_consume);
          assert(inject_mmio_valid);
          assert(inject_mmio_value == PAYLOAD_A);
          assert(!inject_interrupt_enter);
          assert(!inject_interrupt_exit);
        end
        4'h5: begin
          assert(replay_event_consume);
          assert(inject_mmio_valid);
          assert(inject_mmio_value == PAYLOAD_B);
          assert(!inject_interrupt_enter);
          assert(!inject_interrupt_exit);
        end
        4'h6: begin
          assert(replay_event_consume);
          assert(!inject_mmio_valid);
          assert(inject_interrupt_enter);
          assert(!inject_interrupt_exit);
        end
        4'h7: begin
          assert(replay_event_consume);
          assert(!inject_mmio_valid);
          assert(!inject_interrupt_enter);
          assert(inject_interrupt_exit);
        end
        4'h8: assert(no_injection);
        4'h9: assert(replay_underflow);
        4'ha: assert(replay_underflow);
        4'hb: assert(!replay_underflow);
        default: begin
        end
      endcase
    end

    cover(rst_n && step == 4'h1 && no_injection);
    cover(rst_n && step == 4'h2 && no_injection);
    cover(rst_n && step == 4'h3 && no_injection);
    cover(rst_n && step == 4'h4 && inject_mmio_valid && inject_mmio_value == PAYLOAD_A);
    cover(rst_n && step == 4'h5 && inject_mmio_valid && inject_mmio_value == PAYLOAD_B);
    cover(rst_n && step == 4'h6 && inject_interrupt_enter);
    cover(rst_n && step == 4'h7 && inject_interrupt_exit);
    cover(rst_n && step == 4'h9 && replay_underflow);
    cover(rst_n && step == 4'hb && !replay_underflow);
  end
endmodule

`default_nettype wire
