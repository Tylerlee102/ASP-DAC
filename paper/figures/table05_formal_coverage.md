# Table 5. Bounded Formal Coverage

Generated from `../../results/processed/formal_coverage.csv`.

Each row is a bounded local RTL contract check, not an end-to-end processor/replay proof.

| RTL contract family | Depth | Status | Checked obligations | Explicit limit |
| --- | ---: | --- | --- | --- |
| event_tap | 2 | PASS (formal-bmc) | priority ordering, event field routing, multievent-pending flag | local event-source harness; not a full CPU proof |
| event_classifier_slicer | 8 | PASS (formal-bmc) | capture-policy classification, required-event retention, LAST_K context-window behavior | bounded policy proof; workload-scale event coverage comes from simulation rows |
| property_checker | 8 | PASS (formal-bmc) | six failure-family IDs/signatures, reset/clear behavior, state exposure | synthetic checker stimuli with reduced deadline constants |
| hash_signature | 4 | PASS (formal-bmc) | reset seed, clear seed, no-event stability, exact rotate/XOR update | integrity accumulator behavior only; no cryptographic-strength claim |
| mmio_interrupt_loggers | 6 | PASS (formal-bmc) | MMIO read/write packet fields, interrupt enter/exit fields, depth tracking, unpaired-exit sticky flag | local logger interfaces; not a complete bus-protocol proof |
| registers | 6 | PASS (formal-bmc) | address decode, readback muxing, reset defaults, global clear, control writes, one-cycle clear pulse | register-block contract only; no external bus timing proof |
| replay_control | 8 | PASS (formal-bmc) | event consume/inject rules, time mismatch handling, non-injectable event handling, sticky underflow | local event packets; no firmware-running SoC replay proof |
| replay_mismatch_guards | 14 | PASS (formal-bmc) | wrong-cycle rejection, wrong-commit rejection, wrong-kind rejection, early-EOF underflow, clear recovery, exact payload injection | deterministic mismatch microsequence; no full replay-stream comparator proof |
| capsule_buffer | 12 | PASS (formal-bmc) | count bounds, freeze immutability, frozen-count stability, sticky overflow, first-overflow behavior | small four-entry proof configuration |
| replay_capsule_top | 16 | PASS (formal-bmc) | top-level recorder count bounds, failure-to-freeze behavior, frozen-count stability, overflow reachability | bounded recorder harness; not an end-to-end processor/replay theorem |
