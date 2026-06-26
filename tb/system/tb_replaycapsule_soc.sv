`timescale 1ns/1ps

module tb_replaycapsule_soc;
  logic clk;
  logic rst_n;
  logic clean_start;
  logic bug_start;
  logic [31:0] sensor_value;
  logic timer_irq;

  logic clean_done;
  logic clean_failure_seen;
  logic [31:0] clean_failure_signature;
  logic [31:0] clean_running_signature;
  logic [15:0] clean_capsule_event_count;

  logic bug_done;
  logic bug_failure_seen;
  logic [31:0] bug_failure_signature;
  logic [31:0] bug_running_signature;
  logic [15:0] bug_capsule_event_count;

  logic clean_failure_latched;
  logic bug_failure_latched;
  logic [31:0] bug_signature_latched;

  replaycapsule_soc #(
    .BUG_MODE(1'b0)
  ) u_clean_soc (
    .clk(clk),
    .rst_n(rst_n),
    .start(clean_start),
    .sensor_value(sensor_value),
    .timer_irq(timer_irq),
    .done(clean_done),
    .failure_seen(clean_failure_seen),
    .failure_signature(clean_failure_signature),
    .running_signature(clean_running_signature),
    .capsule_event_count(clean_capsule_event_count)
  );

  replaycapsule_soc #(
    .BUG_MODE(1'b1)
  ) u_bug_soc (
    .clk(clk),
    .rst_n(rst_n),
    .start(bug_start),
    .sensor_value(sensor_value),
    .timer_irq(timer_irq),
    .done(bug_done),
    .failure_seen(bug_failure_seen),
    .failure_signature(bug_failure_signature),
    .running_signature(bug_running_signature),
    .capsule_event_count(bug_capsule_event_count)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      clean_failure_latched <= 1'b0;
      bug_failure_latched <= 1'b0;
      bug_signature_latched <= 32'h0;
    end else begin
      if (clean_failure_seen) begin
        clean_failure_latched <= 1'b1;
      end
      if (bug_failure_seen) begin
        bug_failure_latched <= 1'b1;
        bug_signature_latched <= bug_failure_signature;
      end
    end
  end

  initial begin
    int cycles;

    rst_n = 1'b0;
    clean_start = 1'b0;
    bug_start = 1'b0;
    sensor_value = 32'd850;
    timer_irq = 1'b0;

    repeat (3) @(posedge clk);
    rst_n = 1'b1;

    @(negedge clk);
    clean_start = 1'b1;
    bug_start = 1'b1;
    @(negedge clk);
    clean_start = 1'b0;
    bug_start = 1'b0;

    cycles = 0;
    while (!clean_done && cycles < 100) begin
      @(posedge clk);
      cycles++;
    end
    #1;
    if (!clean_done) begin
      $fatal(1, "clean SoC did not finish");
    end
    if (clean_failure_latched) begin
      $fatal(1, "clean SoC path unexpectedly reported a property failure");
    end
    if (clean_capsule_event_count == 16'h0 || clean_running_signature == 32'h5243_5256) begin
      $fatal(1, "clean SoC path did not record visible events");
    end

    cycles = 0;
    while (!bug_done && cycles < 100) begin
      @(posedge clk);
      cycles++;
    end
    #1;
    if (!bug_done) begin
      $fatal(1, "bug-mode SoC did not finish");
    end
    if (!bug_failure_latched || bug_signature_latched == 32'h0) begin
      $fatal(1, "bug-mode SoC did not report a latched property failure signature");
    end
    if (bug_capsule_event_count == 16'h0 || bug_running_signature == 32'h5243_5256) begin
      $fatal(1, "bug-mode SoC path did not record visible events");
    end

    $finish;
  end
endmodule
