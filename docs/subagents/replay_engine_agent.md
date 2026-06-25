# replay_engine_agent

## Scope

Owned files:

- `tb/replay_testbench/replay_driver.py`
- `tb/replay_testbench/capsule_parser.py`
- `tb/replay_testbench/replay_compare.py`
- `tb/replay_testbench/README.md`
- `docs/subagents/replay_engine_agent.md`

Do not revert edits outside this list.

## Current State

The replay testbench is a lightweight Python skeleton for ReplayCapsule-RV. It parses JSON and line-oriented text capsules, aligns events by cycle index or commit index, and returns a pass only when property ID, failure signature, PC evidence, MMIO evidence, input consumption, and interrupt timing all satisfy the comparison rules.

The parser accepts both friendly names (`pc`, `mmio`, `input`, `interrupt`) and
repository names (`EVT_SYNC`, `EVT_MMIO_READ`, `EVT_MMIO_WRITE`,
`EVT_IRQ_LEVEL`, `EVT_IRQ_TAKEN`, `interrupt_line`, `interrupt_delivery`,
`external_input`, `mmio_write_observed`).
Event kind may be carried in `kind`, `type`, `event`, or `event_type`.

The CLI has a built-in passing fixture:

```powershell
python tb/replay_testbench/replay_driver.py --demo
python tb/replay_testbench/replay_driver.py --demo --mode commit-index --json
```

## Comparison Contract

- `property_id` must be present and equal.
- `failure_signature` must be present and equal.
- The expected capsule must contain at least one PC event and one MMIO event.
- Expected PC evidence must match at the selected cycle or commit index. Extra observed PC events are allowed.
- MMIO evidence must match exactly by selected index, address, value, and direction when those fields are specified. Extra observed MMIO events fail the replay.
- Optional MMIO fields such as `byte_en`, `width`, and `resp` are checked when
  present in the expected fixture.
- Input events must match exactly; missing or extra observed inputs fail the replay.
- Interrupt events must match exactly; missing, extra, or differently timed observed interrupts fail the replay.

## Fixture Formats

Text:

```text
property_id rv32i.irq.mmio
failure_signature irq_store_mismatch
pc cycle=10 commit=3 pc=0x80000018
mmio cycle=12 commit=4 direction=write addr=0x40000010 value=0x1
input cycle=13 commit=4 input_id=gpio0 value=0x1
interrupt cycle=16 commit=5 irq=timer0 state=taken
```

JSON:

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

## Next Work

- Connect observed fixture parsing to the real simulator trace producer.
- Add repository-level tests once the surrounding test runner exists.
- Expand MMIO evidence to include byte enables and read/write response status if the trace format exposes them.
