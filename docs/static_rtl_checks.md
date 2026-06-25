# Static RTL Checks

`scripts/static_rtl_checks.py` is a lightweight, Python-only guard for the
ReplayCapsule-RV RTL contract. It does not invoke Verilator, Yosys, or any other
external HDL tool.

## What It Checks

- Required SystemVerilog source files are present under `rtl/`.
- The `replaycapsule_event_pkg` package is declared in `rtl/event_pkg.sv`.
- Required modules from the architecture contract are declared once in their
  expected files.
- Required `EV_*` event names are defined in `rtl/event_pkg.sv` with the v1
  numeric values `0` through `11`.
- RTL references to `EV_*` names use the known v1 event vocabulary.
- RTL text does not contain basic placeholder markers such as `TODO`, `FIXME`,
  `TBD`, `XXX`, `placeholder`, `stub`, `dummy`, `fake`, `not implemented`, or
  `unimplemented`.

The module and event lists intentionally mirror the current v1 hardware contract
in `docs/architecture.md` and `docs/event_interface.md`.

## Usage

Readable stdout report:

```powershell
python scripts/static_rtl_checks.py
```

CSV report:

```powershell
python scripts/static_rtl_checks.py --format csv
```

The process exits with status `0` when all checks pass and status `1` when any
row has `FAIL`.

## CSV Columns

The CSV output has these columns:

- `check`: check family, such as `required_module` or `required_event`.
- `status`: `PASS` or `FAIL`.
- `path`: repository-relative file path, when applicable.
- `line`: one-based line number, when applicable.
- `detail`: concise explanation of the result.

This script is intentionally standalone so it can be integrated into the broader
test runner without making RTL simulation or synthesis a local prerequisite.
