# Verilator Firmware-Running Harness

This directory contains the firmware-running RTL harness for the PicoRV32
ReplayCapsule wrapper.

Build:

```sh
make verilator-harness
```

Record example:

```sh
./build/verilator/replaycapsule_sim \
  --mode record \
  --benchmark sensor_threshold_bug \
  --variant failing \
  --firmware firmware/build/sensor_threshold_bug/failing.hex \
  --capsule results/raw/rtl_capsules/sensor_threshold_bug_failing_seed1.json \
  --signature results/raw/rtl_signatures/sensor_threshold_bug_failing_seed1_record.json \
  --seed 1 \
  --max-cycles 100000
```

Replay example:

```sh
./build/verilator/replaycapsule_sim \
  --mode replay \
  --benchmark sensor_threshold_bug \
  --variant failing \
  --firmware firmware/build/sensor_threshold_bug/failing.hex \
  --capsule results/raw/rtl_capsules/sensor_threshold_bug_failing_seed1.json \
  --signature results/raw/rtl_signatures/sensor_threshold_bug_failing_seed1_replay.json \
  --seed 1 \
  --max-cycles 100000
```

Current limitation:

- The existing RTL exports record-side capsules but does not yet contain a
  standalone hardware replay-consume datapath. Replay mode therefore uses the
  host harness to drive MMIO/IRQ stimulus from the saved capsule and compares
  the newly exported RTL capsule against the record capsule.
- If replay comparison fails, the harness exits nonzero and writes the mismatch
  into the signature JSON.
