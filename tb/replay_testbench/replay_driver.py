"""Command-line driver for lightweight deterministic replay checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

try:
    from .capsule_parser import CapsuleParseError, parse_capsule_file
    from .replay_compare import compare_capsules
except ImportError:  # pragma: no cover - script-friendly fallback
    from capsule_parser import CapsuleParseError, parse_capsule_file
    from replay_compare import compare_capsules


DEMO_EXPECTED = """\
property_id rv32i.irq.mmio
failure_signature irq_store_mismatch
pc cycle=10 commit=3 pc=0x80000018
mmio cycle=12 commit=4 direction=write addr=0x40000010 value=0x1
input cycle=13 commit=4 input_id=gpio0 value=0x1
interrupt cycle=16 commit=5 irq=timer0 state=taken
"""

DEMO_OBSERVED = """\
property_id rv32i.irq.mmio
failure_signature irq_store_mismatch
pc cycle=10 commit=3 pc=0x80000018
mmio cycle=12 commit=4 direction=write addr=0x40000010 value=0x1
input cycle=13 commit=4 input_id=gpio0 value=0x1
interrupt cycle=16 commit=5 irq=timer0 state=taken
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare ReplayCapsule-RV expected evidence against an observed replay trace."
    )
    parser.add_argument("expected", nargs="?", help="expected capsule fixture, JSON or text")
    parser.add_argument("observed", nargs="?", help="observed replay trace fixture, JSON or text")
    parser.add_argument(
        "--mode",
        default="cycle",
        choices=("cycle", "cycle-index", "commit", "commit-index"),
        help="index used to align evidence events",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable result JSON")
    parser.add_argument("--demo", action="store_true", help="run the built-in tiny passing fixture")
    args = parser.parse_args(argv)

    try:
        if args.demo:
            return _run_demo(args.mode, args.json)
        if not args.expected or not args.observed:
            parser.error("expected and observed fixture paths are required unless --demo is used")
        result = _run_compare(Path(args.expected), Path(args.observed), args.mode)
    except CapsuleParseError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    _print_result(result, args.json)
    return 0 if result.success else 1


def _run_compare(expected_path: Path, observed_path: Path, mode: str):
    expected = parse_capsule_file(expected_path)
    observed = parse_capsule_file(observed_path)
    return compare_capsules(expected, observed, mode=mode)


def _run_demo(mode: str, as_json: bool) -> int:
    with TemporaryDirectory(prefix="replaycapsule-demo-") as temp_dir:
        root = Path(temp_dir)
        expected = root / "expected.txt"
        observed = root / "observed.txt"
        expected.write_text(DEMO_EXPECTED, encoding="utf-8")
        observed.write_text(DEMO_OBSERVED, encoding="utf-8")
        result = _run_compare(expected, observed, mode)
    _print_result(result, as_json)
    return 0 if result.success else 1


def _print_result(result, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(result.format())


if __name__ == "__main__":
    raise SystemExit(main())
