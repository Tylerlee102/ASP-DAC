# ReplayCapsule-RV Top-Conference V2 Baseline

This folder freezes the evidence before the v2 improvement pass.

## Starting Evidence

- Firmware build: 15/15 PASS.
- Full RTL replay: 45/45 PASS.
- Negative replay: 10 rejected, 0 unexpected accepts, 2 NA.
- Workload scaling: 225 PASS / 150 FAIL.
- Buffer sensitivity: depths 4-128 overflow heavily; depth 256 reaches only partial replay success.
- Mapped overhead: high LUT/FF overhead and reduced Fmax on ECP5 evidence.
- Replay consume path: host-driven; no synthesizable replay-consume datapath in the baseline.
- Readiness status: borderline submission-ready, with top-conference risks around scaling, overhead, benchmark diversity, target diversity, and replay consumption scope.

