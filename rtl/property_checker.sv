`include "event_pkg.sv"

module property_checker #(
  parameter logic [31:0] SENSOR_ADDR       = 32'h4000_0000,
  parameter logic [31:0] ACTUATOR_ADDR     = 32'h4000_0004,
  parameter logic [31:0] CONFIG_ADDR       = 32'h4000_0008,
  parameter logic [31:0] COMMAND_ADDR      = 32'h4000_000c,
  parameter logic [31:0] STACK_LOW_ADDR    = 32'h0000_1000,
  parameter logic [31:0] STACK_HIGH_ADDR   = 32'h0000_1400,
  parameter logic [31:0] SENSOR_THRESHOLD  = 32'd700,
  parameter logic [31:0] ACTUATOR_MAX_SAFE = 32'd100,
  parameter logic [31:0] CONFIG_SAFE_MAGIC = 32'h0000_cafe,
  parameter int          RESPONSE_DEADLINE = 16
) (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        clear,

  input  logic        event_valid,
  input  logic [3:0]  event_type,
  input  logic [31:0] event_commit_index,
  input  logic [31:0] event_pc,
  input  logic [31:0] event_addr,
  input  logic [31:0] event_data,

  output logic        property_fail_valid,
  output logic [7:0]  property_id,
  output logic [31:0] property_signature,
  output logic        sensor_deadline_active,
  output logic        critical_section_active
);
  import replaycapsule_event_pkg::*;

  localparam logic [7:0] PROP_ACTUATOR_LIMIT = 8'd1;
  localparam logic [7:0] PROP_INTERRUPT_CRIT = 8'd2;
  localparam logic [7:0] PROP_SENSOR_DEADLINE = 8'd3;
  localparam logic [7:0] PROP_STACK_PROTECT = 8'd4;
  localparam logic [7:0] PROP_MMIO_ORDERING = 8'd5;

  logic [7:0] deadline_count;
  logic safe_config_seen;
  logic detected_fail;
  logic [7:0] detected_property_id;
  logic [31:0] detected_signature;
  localparam logic [7:0] RESPONSE_DEADLINE_VALUE = RESPONSE_DEADLINE;

  always_comb begin
    detected_fail = 1'b0;
    detected_property_id = 8'h0;
    detected_signature = 32'h0;

    if (event_valid) begin
      if (event_type == EV_MMIO_WRITE && event_addr == ACTUATOR_ADDR && event_data > ACTUATOR_MAX_SAFE) begin
        detected_fail = 1'b1;
        detected_property_id = PROP_ACTUATOR_LIMIT;
        detected_signature = event_data ^ event_commit_index ^ 32'hac70_0001;
      end else if (event_type == EV_INTERRUPT_ENTER && critical_section_active) begin
        detected_fail = 1'b1;
        detected_property_id = PROP_INTERRUPT_CRIT;
        detected_signature = event_pc ^ event_commit_index ^ 32'h1a1e_0002;
      end else if (event_type == EV_COMMIT && sensor_deadline_active && deadline_count == 8'd0) begin
        detected_fail = 1'b1;
        detected_property_id = PROP_SENSOR_DEADLINE;
        detected_signature = event_pc ^ event_commit_index ^ 32'h5e05_0003;
      end else if (event_type == EV_STORE && event_addr >= STACK_LOW_ADDR && event_addr < STACK_HIGH_ADDR) begin
        detected_fail = 1'b1;
        detected_property_id = PROP_STACK_PROTECT;
        detected_signature = event_addr ^ event_data ^ 32'h57ac_0004;
      end else if (event_type == EV_MMIO_WRITE && event_addr == ACTUATOR_ADDR && event_data != 32'h0 && !safe_config_seen) begin
        detected_fail = 1'b1;
        detected_property_id = PROP_MMIO_ORDERING;
        detected_signature = event_data ^ event_commit_index ^ 32'h0d0e_0005;
      end
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      property_fail_valid <= 1'b0;
      property_id <= 8'h0;
      property_signature <= 32'h0;
      sensor_deadline_active <= 1'b0;
      critical_section_active <= 1'b0;
      deadline_count <= 8'h0;
      safe_config_seen <= 1'b0;
    end else if (clear) begin
      property_fail_valid <= 1'b0;
      property_id <= 8'h0;
      property_signature <= 32'h0;
      sensor_deadline_active <= 1'b0;
      critical_section_active <= 1'b0;
      deadline_count <= 8'h0;
      safe_config_seen <= 1'b0;
    end else begin
      property_fail_valid <= detected_fail;
      property_id <= detected_property_id;
      property_signature <= detected_signature;

      if (event_valid) begin
        if (event_type == EV_MMIO_WRITE && event_addr == COMMAND_ADDR && event_data[0]) begin
          critical_section_active <= 1'b1;
        end else if (event_type == EV_MMIO_WRITE && event_addr == CONFIG_ADDR) begin
          critical_section_active <= 1'b0;
        end

        if (event_type == EV_MMIO_WRITE && event_addr == CONFIG_ADDR && event_data == CONFIG_SAFE_MAGIC) begin
          safe_config_seen <= 1'b1;
        end

        if (event_type == EV_MMIO_READ && event_addr == SENSOR_ADDR && event_data > SENSOR_THRESHOLD) begin
          sensor_deadline_active <= 1'b1;
          deadline_count <= RESPONSE_DEADLINE_VALUE;
        end else if (event_type == EV_MMIO_WRITE && event_addr == ACTUATOR_ADDR && event_data <= ACTUATOR_MAX_SAFE) begin
          sensor_deadline_active <= 1'b0;
          deadline_count <= 8'h0;
        end else if (event_type == EV_COMMIT && sensor_deadline_active && deadline_count != 8'h0) begin
          deadline_count <= deadline_count - 8'h1;
        end
      end
    end
  end
endmodule
