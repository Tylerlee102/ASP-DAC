# ReplayCapsule-RV Replay Testbench

This directory holds a lightweight deterministic replay engine skeleton for embedded RV32I interrupt/MMIO capsules. It is intentionally small and runnable without project-specific simulators so that capsule fixtures can be checked early.

## Success Criteria

`replay_driver.py` returns success only when all of these match:

- `property_id`
- `failure_signature`
- at least one relevant PC evidence event
- at least one relevant MMIO evidence event
- every expected PC/MMIO evidence event at the selected index
- exact consumed input events, with no extra observed inputs
- exact interrupt events and timing, with no extra observed interrupts

PC evidence is treated as checkpoint-style evidence, so extra observed PC events are allowed. MMIO, input, and interrupt evidence are strict.
`scripts/run_replay_negative_tests.py` generates benchmark-derived positive and
negative fixtures that must be caught by these rules. It covers property-ID
mismatch, failure-signature mismatch, missing strict events, duplicate strict
events, payload corruption, cycle-index shifts, commit-index shifts, and
explicit order-tag swaps.

## Run

Built-in passing fixture:

```powershell
python tb/replay_testbench/replay_driver.py --demo
python tb/replay_testbench/replay_driver.py --demo --mode commit-index --json
```

Compare two fixtures:

```powershell
python tb/replay_testbench/replay_driver.py expected.txt observed.txt --mode cycle-index
python tb/replay_testbench/replay_driver.py expected.json observed.json --mode commit-index
```

Exit codes:

- `0`: replay evidence matched
- `1`: replay evidence mismatched
- `2`: fixture or configuration error

## Text Fixture Format

```text
property_id rv32i.irq.mmio
failure_signature irq_store_mismatch
pc cycle=10 commit=3 pc=0x80000018
mmio cycle=12 commit=4 direction=write addr=0x40000010 value=0x1
input cycle=13 commit=4 input_id=gpio0 value=0x1
interrupt cycle=16 commit=5 irq=timer0 state=taken
```

`@10` can be used instead of `cycle=10`, and `#3` can be used instead of `commit=3`.
Repository-style event names are accepted too, including `EVT_SYNC`, `EVT_MMIO_READ`,
`EVT_MMIO_WRITE`, `EVT_IRQ_LEVEL`, `EVT_IRQ_TAKEN`, `interrupt_line`,
`interrupt_delivery`, `external_input`, and `mmio_write_observed`.

Example with hardware-facing names:

```text
property_id rv32i.irq.mmio
failure_signature irq_store_mismatch
EVT_SYNC cycle=10 commit=3 pc=0x80000018
EVT_MMIO_WRITE cycle=12 commit=4 addr=0x40000010 wdata=0x1 byte_en=0xf resp=0
external_input cycle=13 commit=4 input_id=gpio0 value=0x1
EVT_IRQ_LEVEL cycle=16 commit=5 source_id=0 irq_value=0x1 state=asserted
```

## JSON Fixture Format

```json
{
  "property_id": "rv32i.irq.mmio",
  "failure_signature": "irq_store_mismatch",
  "events": [
    {"kind": "pc", "cycle": 10, "commit": 3, "pc": "0x80000018"},
    {"kind": "mmio", "cycle": 12, "commit": 4, "direction": "write", "addr": "0x40000010", "value": "0x1"},
    {"kind": "input", "cycle": 13, "commit": 4, "input_id": "gpio0", "value": "0x1"},
    {"kind": "interrupt", "cycle": 16, "commit": 5, "irq": "timer0", "state": "taken"}
  ]
}
```

Grouped JSON keys are also accepted: `pc_evidence`, `mmio_evidence`, `inputs`, and `interrupts`.
MMIO fixtures can use either generic `value` or hardware names `rdata`/`wdata`.
Event kind may be named `kind`, `type`, `event`, or `event_type`.

## Notes

This is a skeleton, not a simulator. It compares declared replay evidence emitted by a simulator or trace extractor. The next integration step is to point the observed fixture input at the real RV32I replay trace producer.
