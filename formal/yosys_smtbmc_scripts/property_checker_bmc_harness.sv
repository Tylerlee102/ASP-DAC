`default_nettype none

module property_checker_bmc_harness (
  input logic clk
);
  `include "../../rtl/event_defs.svh"

  localparam logic [31:0] SENSOR_ADDR = 32'h4000_0000;
  localparam logic [31:0] ACTUATOR_ADDR = 32'h4000_0004;
  localparam logic [31:0] CONFIG_ADDR = 32'h4000_0008;
  localparam logic [31:0] COMMAND_ADDR = 32'h4000_000c;
  localparam logic [31:0] STACK_LOW_ADDR = 32'h0000_1000;
  localparam logic [31:0] STACK_HIGH_ADDR = 32'h0000_1400;
  localparam logic [31:0] SENSOR_THRESHOLD = 32'd700;
  localparam logic [31:0] ACTUATOR_MAX_SAFE = 32'd100;
  localparam logic [31:0] CONFIG_SAFE_MAGIC = 32'h0000_cafe;
  localparam logic [31:0] WATCHDOG_HEARTBEAT = 32'h0000_feed;
  localparam logic [7:0] RESPONSE_DEADLINE = 8'd2;
  localparam logic [7:0] WATCHDOG_TIMEOUT = 8'd2;

  localparam logic [7:0] PROP_ACTUATOR_LIMIT = 8'd1;
  localparam logic [7:0] PROP_INTERRUPT_CRIT = 8'd2;
  localparam logic [7:0] PROP_SENSOR_DEADLINE = 8'd3;
  localparam logic [7:0] PROP_STACK_PROTECT = 8'd4;
  localparam logic [7:0] PROP_MMIO_ORDERING = 8'd5;
  localparam logic [7:0] PROP_WATCHDOG_TIMEOUT = 8'd6;

  logic rst_n = 1'b0;
  always_ff @(posedge clk) begin
    rst_n <= 1'b1;
  end

  (* anyseq *) logic clear_any;
  (* anyseq *) logic event_valid;
  (* anyseq *) logic [3:0] event_type;
  (* anyseq *) logic [31:0] event_commit_index;
  (* anyseq *) logic [31:0] event_pc;
  (* anyseq *) logic [31:0] event_addr;
  (* anyseq *) logic [31:0] event_data;

  logic clear;
  logic property_fail_valid;
  logic [7:0] property_id;
  logic [31:0] property_signature;
  logic sensor_deadline_active;
  logic critical_section_active;
  logic past_valid = 1'b0;
  logic prev_rst_n;
  logic prev_clear;
  logic prev_event_valid;
  logic [3:0] prev_event_type;
  logic [31:0] prev_event_commit_index;
  logic [31:0] prev_event_pc;
  logic [31:0] prev_event_addr;
  logic [31:0] prev_event_data;
  logic shadow_sensor_deadline_active;
  logic shadow_critical_section_active;
  logic shadow_safe_config_seen;
  logic shadow_watchdog_active;
  logic [7:0] shadow_deadline_count;
  logic [7:0] shadow_watchdog_count;
  logic prev_shadow_sensor_deadline_active;
  logic prev_shadow_critical_section_active;
  logic prev_shadow_safe_config_seen;
  logic prev_shadow_watchdog_active;
  logic [7:0] prev_shadow_deadline_count;
  logic [7:0] prev_shadow_watchdog_count;

  logic past_actuator_limit;
  logic past_stack_violation;
  logic past_mmio_ordering_violation;
  logic past_interrupt_critical_violation;
  logic past_watchdog_violation;
  logic past_sensor_deadline_violation;
  logic past_command_enter;
  logic past_config_write;
  logic past_sensor_high_read;
  logic past_safe_actuator_write;

  assign clear = rst_n && clear_any;
  assign past_actuator_limit =
    prev_event_valid &&
    prev_event_type == EV_MMIO_WRITE &&
    prev_event_addr == ACTUATOR_ADDR &&
    prev_event_data > ACTUATOR_MAX_SAFE;
  assign past_stack_violation =
    prev_event_valid &&
    prev_event_type == EV_STORE &&
    prev_event_addr >= STACK_LOW_ADDR &&
    prev_event_addr < STACK_HIGH_ADDR;
  assign past_mmio_ordering_violation =
    prev_event_valid &&
    prev_event_type == EV_MMIO_WRITE &&
    prev_event_addr == ACTUATOR_ADDR &&
    prev_event_data != 32'h0 &&
    prev_event_data <= ACTUATOR_MAX_SAFE &&
    !prev_shadow_safe_config_seen;
  assign past_interrupt_critical_violation =
    prev_event_valid &&
    prev_event_type == EV_INTERRUPT_ENTER &&
    prev_shadow_critical_section_active;
  assign past_watchdog_violation =
    prev_event_valid &&
    prev_event_type == EV_COMMIT &&
    prev_shadow_watchdog_active &&
    prev_shadow_watchdog_count == 8'h0;
  assign past_sensor_deadline_violation =
    prev_event_valid &&
    prev_event_type == EV_COMMIT &&
    prev_shadow_sensor_deadline_active &&
    prev_shadow_deadline_count == 8'h0 &&
    !(prev_shadow_watchdog_active && prev_shadow_watchdog_count == 8'h0);
  assign past_command_enter =
    prev_event_valid &&
    prev_event_type == EV_MMIO_WRITE &&
    prev_event_addr == COMMAND_ADDR &&
    prev_event_data[0] &&
    prev_event_data != WATCHDOG_HEARTBEAT;
  assign past_config_write =
    prev_event_valid &&
    prev_event_type == EV_MMIO_WRITE &&
    prev_event_addr == CONFIG_ADDR;
  assign past_sensor_high_read =
    prev_event_valid &&
    prev_event_type == EV_MMIO_READ &&
    prev_event_addr == SENSOR_ADDR &&
    prev_event_data > SENSOR_THRESHOLD;
  assign past_safe_actuator_write =
    prev_event_valid &&
    prev_event_type == EV_MMIO_WRITE &&
    prev_event_addr == ACTUATOR_ADDR &&
    prev_event_data <= ACTUATOR_MAX_SAFE;

  property_checker #(
    .SENSOR_ADDR(SENSOR_ADDR),
    .ACTUATOR_ADDR(ACTUATOR_ADDR),
    .CONFIG_ADDR(CONFIG_ADDR),
    .COMMAND_ADDR(COMMAND_ADDR),
    .STACK_LOW_ADDR(STACK_LOW_ADDR),
    .STACK_HIGH_ADDR(STACK_HIGH_ADDR),
    .SENSOR_THRESHOLD(SENSOR_THRESHOLD),
    .ACTUATOR_MAX_SAFE(ACTUATOR_MAX_SAFE),
    .CONFIG_SAFE_MAGIC(CONFIG_SAFE_MAGIC),
    .ENABLE_WATCHDOG(1'b1),
    .WATCHDOG_HEARTBEAT(WATCHDOG_HEARTBEAT),
    .RESPONSE_DEADLINE(RESPONSE_DEADLINE),
    .WATCHDOG_TIMEOUT(WATCHDOG_TIMEOUT)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .watchdog_enable(1'b0),
    .event_valid(event_valid),
    .event_type(event_type),
    .event_commit_index(event_commit_index),
    .event_pc(event_pc),
    .event_addr(event_addr),
    .event_data(event_data),
    .property_fail_valid(property_fail_valid),
    .property_id(property_id),
    .property_signature(property_signature),
    .sensor_deadline_active(sensor_deadline_active),
    .critical_section_active(critical_section_active)
  );

  always_ff @(posedge clk) begin
    past_valid <= 1'b1;
    prev_rst_n <= rst_n;
    prev_clear <= clear;
    prev_event_valid <= event_valid;
    prev_event_type <= event_type;
    prev_event_commit_index <= event_commit_index;
    prev_event_pc <= event_pc;
    prev_event_addr <= event_addr;
    prev_event_data <= event_data;
    prev_shadow_sensor_deadline_active <= shadow_sensor_deadline_active;
    prev_shadow_critical_section_active <= shadow_critical_section_active;
    prev_shadow_safe_config_seen <= shadow_safe_config_seen;
    prev_shadow_watchdog_active <= shadow_watchdog_active;
    prev_shadow_deadline_count <= shadow_deadline_count;
    prev_shadow_watchdog_count <= shadow_watchdog_count;

    if (!rst_n || clear) begin
      shadow_sensor_deadline_active <= 1'b0;
      shadow_critical_section_active <= 1'b0;
      shadow_safe_config_seen <= 1'b0;
      shadow_watchdog_active <= 1'b0;
      shadow_deadline_count <= 8'h0;
      shadow_watchdog_count <= 8'h0;
    end else if (event_valid) begin
      if (event_type == EV_MMIO_WRITE && event_addr == COMMAND_ADDR && event_data[0] && event_data != WATCHDOG_HEARTBEAT) begin
        shadow_critical_section_active <= 1'b1;
      end else if (event_type == EV_MMIO_WRITE && event_addr == CONFIG_ADDR) begin
        shadow_critical_section_active <= 1'b0;
      end

      if (event_type == EV_MMIO_WRITE && event_addr == CONFIG_ADDR && event_data == CONFIG_SAFE_MAGIC) begin
        shadow_safe_config_seen <= 1'b1;
      end

      if (event_type == EV_MMIO_READ && event_addr == SENSOR_ADDR && event_data > SENSOR_THRESHOLD) begin
        shadow_sensor_deadline_active <= 1'b1;
        shadow_deadline_count <= RESPONSE_DEADLINE;
        shadow_watchdog_active <= 1'b1;
        shadow_watchdog_count <= WATCHDOG_TIMEOUT;
      end else if (event_type == EV_MMIO_WRITE && event_addr == COMMAND_ADDR && event_data == WATCHDOG_HEARTBEAT) begin
        shadow_watchdog_active <= 1'b0;
        shadow_watchdog_count <= 8'h0;
      end else if (event_type == EV_COMMIT && shadow_watchdog_active && shadow_watchdog_count != 8'h0) begin
        shadow_watchdog_count <= shadow_watchdog_count - 8'h1;
      end

      if (event_type == EV_MMIO_WRITE && event_addr == ACTUATOR_ADDR && event_data <= ACTUATOR_MAX_SAFE) begin
        shadow_sensor_deadline_active <= 1'b0;
        shadow_deadline_count <= 8'h0;
      end else if (event_type == EV_COMMIT && shadow_sensor_deadline_active && shadow_deadline_count != 8'h0) begin
        shadow_deadline_count <= shadow_deadline_count - 8'h1;
      end
    end

    if (past_valid) begin
      if (!prev_rst_n || prev_clear) begin
        assert(!property_fail_valid);
        assert(property_id == 8'h0);
        assert(property_signature == 32'h0);
        assert(!sensor_deadline_active);
        assert(!critical_section_active);
      end else begin
        if (!prev_event_valid) begin
          assert(!property_fail_valid);
        end

        if (past_actuator_limit) begin
          assert(property_fail_valid);
          assert(property_id == PROP_ACTUATOR_LIMIT);
          assert(property_signature == (prev_event_data ^ prev_event_commit_index ^ 32'hac70_0001));
        end

        if (past_stack_violation) begin
          assert(property_fail_valid);
          assert(property_id == PROP_STACK_PROTECT);
          assert(property_signature == (prev_event_addr ^ prev_event_data ^ 32'h57ac_0004));
        end

        if (past_mmio_ordering_violation) begin
          assert(property_fail_valid);
          assert(property_id == PROP_MMIO_ORDERING);
          assert(property_signature == (prev_event_data ^ prev_event_commit_index ^ 32'h0d0e_0005));
        end

        if (past_interrupt_critical_violation) begin
          assert(property_fail_valid);
          assert(property_id == PROP_INTERRUPT_CRIT);
          assert(property_signature == (prev_event_pc ^ prev_event_commit_index ^ 32'h1a1e_0002));
        end

        if (past_watchdog_violation) begin
          assert(property_fail_valid);
          assert(property_id == PROP_WATCHDOG_TIMEOUT);
          assert(property_signature == (prev_event_pc ^ prev_event_commit_index ^ 32'hfeed_0006));
        end

        if (past_sensor_deadline_violation) begin
          assert(property_fail_valid);
          assert(property_id == PROP_SENSOR_DEADLINE);
          assert(property_signature == (prev_event_pc ^ prev_event_commit_index ^ 32'h5e05_0003));
        end

        if (past_command_enter) begin
          assert(critical_section_active);
        end

        if (past_config_write) begin
          assert(!critical_section_active);
        end

        if (past_sensor_high_read) begin
          assert(sensor_deadline_active);
        end

        if (past_safe_actuator_write) begin
          assert(!sensor_deadline_active);
        end
      end

      cover(past_actuator_limit && property_fail_valid && property_id == PROP_ACTUATOR_LIMIT);
      cover(past_stack_violation && property_fail_valid && property_id == PROP_STACK_PROTECT);
      cover(past_mmio_ordering_violation && property_fail_valid && property_id == PROP_MMIO_ORDERING);
      cover(past_interrupt_critical_violation && property_fail_valid && property_id == PROP_INTERRUPT_CRIT);
      cover(past_watchdog_violation && property_fail_valid && property_id == PROP_WATCHDOG_TIMEOUT);
      cover(past_sensor_deadline_violation && property_fail_valid && property_id == PROP_SENSOR_DEADLINE);
    end
  end
endmodule

`default_nettype wire
