`include "../event_pkg.sv"

module replaycapsule_soc #(
  parameter bit BUG_MODE = 1'b0
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        start,
  input  logic [31:0] sensor_value,
  input  logic        timer_irq,

  output logic        done,
  output logic        failure_seen,
  output logic [31:0] failure_signature,
  output logic [31:0] running_signature,
  output logic [15:0] capsule_event_count
);
  `include "../event_defs.svh"

  typedef enum logic [3:0] {
    S_IDLE,
    S_COMMIT_BOOT,
    S_READ_SENSOR,
    S_WRITE_CONFIG,
    S_WRITE_ACTUATOR,
    S_BUG_DELAY,
    S_DONE
  } state_e;

  localparam logic [31:0] PC_BOOT     = 32'h0000_0080;
  localparam logic [31:0] PC_SENSOR   = 32'h0000_0090;
  localparam logic [31:0] PC_CONFIG   = 32'h0000_00a0;
  localparam logic [31:0] PC_ACTUATOR = 32'h0000_00b0;
  localparam logic [31:0] PC_DELAY    = 32'h0000_00c0;

  localparam logic [31:0] SENSOR_ADDR   = 32'h4000_0000;
  localparam logic [31:0] ACTUATOR_ADDR = 32'h4000_0004;
  localparam logic [31:0] CONFIG_ADDR   = 32'h4000_0008;
  localparam logic [31:0] CONFIG_MAGIC  = 32'h0000_cafe;

  state_e state;
  logic [7:0] delay_count;
  logic [31:0] commit_index;

  logic commit_valid;
  logic [31:0] commit_pc;
  logic [31:0] commit_instr;
  logic branch_taken;
  logic jump_taken;
  logic mem_valid;
  logic mem_write;
  logic [31:0] mem_addr;
  logic [31:0] mem_wdata;
  logic [31:0] mem_rdata;
  logic interrupt_enter;
  logic interrupt_exit;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic [8:0] capsule_count_wide;

  assign branch_taken = 1'b0;
  assign jump_taken = 1'b0;
  assign commit_instr = 32'h0000_0013;
  assign interrupt_enter = timer_irq && (state == S_BUG_DELAY || state == S_WRITE_CONFIG);
  assign interrupt_exit = 1'b0;
  assign failure_seen = property_fail_valid;
  assign failure_signature = property_signature;

  always_comb begin
    commit_valid = 1'b0;
    commit_pc = PC_BOOT;
    mem_valid = 1'b0;
    mem_write = 1'b0;
    mem_addr = 32'h0;
    mem_wdata = 32'h0;
    mem_rdata = 32'h0;
    done = state == S_DONE;

    unique case (state)
      S_COMMIT_BOOT: begin
        commit_valid = 1'b1;
        commit_pc = PC_BOOT;
      end
      S_READ_SENSOR: begin
        mem_valid = 1'b1;
        mem_write = 1'b0;
        mem_addr = SENSOR_ADDR;
        mem_rdata = sensor_value;
        commit_pc = PC_SENSOR;
      end
      S_WRITE_CONFIG: begin
        mem_valid = 1'b1;
        mem_write = 1'b1;
        mem_addr = CONFIG_ADDR;
        mem_wdata = CONFIG_MAGIC;
        commit_pc = PC_CONFIG;
      end
      S_WRITE_ACTUATOR: begin
        mem_valid = 1'b1;
        mem_write = 1'b1;
        mem_addr = ACTUATOR_ADDR;
        mem_wdata = 32'd0;
        commit_pc = PC_ACTUATOR;
      end
      S_BUG_DELAY: begin
        commit_valid = 1'b1;
        commit_pc = PC_DELAY;
      end
      default: begin
        commit_valid = 1'b0;
      end
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state <= S_IDLE;
      delay_count <= 8'h0;
      commit_index <= 32'h0;
    end else begin
      if (commit_valid) begin
        commit_index <= commit_index + 32'h1;
      end

      unique case (state)
        S_IDLE: begin
          delay_count <= 8'h0;
          if (start) begin
            state <= S_COMMIT_BOOT;
          end
        end
        S_COMMIT_BOOT: state <= S_READ_SENSOR;
        S_READ_SENSOR: begin
          if (BUG_MODE && sensor_value > 32'd700) begin
            state <= S_BUG_DELAY;
            delay_count <= 8'd20;
          end else begin
            state <= S_WRITE_CONFIG;
          end
        end
        S_WRITE_CONFIG: state <= S_WRITE_ACTUATOR;
        S_WRITE_ACTUATOR: state <= S_DONE;
        S_BUG_DELAY: begin
          if (property_fail_valid) begin
            state <= S_DONE;
          end else if (delay_count != 8'h0) begin
            delay_count <= delay_count - 8'h1;
          end else begin
            state <= S_DONE;
          end
        end
        default: state <= S_DONE;
      endcase
    end
  end

  replay_capsule_top #(
    .CAPSULE_DEPTH(256)
  ) u_replay_capsule_top (
    .clk(clk),
    .rst_n(rst_n),
    .clear(1'b0),
    .watchdog_enable(1'b0),
    .capture_mode(CAPTURE_REPLAYCAPSULE_RV),
    .commit_valid(commit_valid),
    .commit_pc(commit_pc),
    .commit_instr(commit_instr),
    .commit_index(commit_index),
    .branch_taken(branch_taken),
    .jump_taken(jump_taken),
    .mem_valid(mem_valid),
    .mem_write(mem_write),
    .mem_addr(mem_addr),
    .mem_wdata(mem_wdata),
    .mem_rdata(mem_rdata),
    .external_input_valid(1'b0),
    .external_input_value(32'h0),
    .interrupt_enter(interrupt_enter),
    .interrupt_exit(interrupt_exit),
    .checkpoint_hash_req(1'b0),
    .capsule_read_addr(8'h0),
    .capsule_read_data(),
    .capsule_frozen(),
    .capsule_overflow(),
    .capsule_event_count(capsule_count_wide),
    .running_signature(running_signature),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .captured_event_valid(),
    .captured_event_type()
  );

  assign capsule_event_count = {7'h0, capsule_count_wide};

  logic [7:0] unused_property_id;
  assign unused_property_id = property_id;
endmodule
