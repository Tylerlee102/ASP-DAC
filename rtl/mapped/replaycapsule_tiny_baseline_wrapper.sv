module replaycapsule_tiny_baseline_wrapper (
  input  logic        clk,
  input  logic        rst_n,
  output logic        capsule_frozen,
  output logic        capsule_overflow,
  output logic [7:0]  property_id,
  output logic [31:0] running_signature
);
  logic [31:0] cycle_count;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      cycle_count <= 32'h0;
    end else begin
      cycle_count <= cycle_count + 32'h1;
    end
  end

  assign capsule_frozen = 1'b0;
  assign capsule_overflow = 1'b0;
  assign property_id = 8'h0;
  assign running_signature = cycle_count ^ 32'h5243_5256;
endmodule
