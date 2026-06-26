#!/usr/bin/env python3
"""Run negative replay-comparator fixtures over generated benchmark capsules."""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from replaycapsule_model import BENCHMARKS, capsule_fixture, run_benchmark  # noqa: E402
sys.path.insert(0, str(REPO_ROOT / "tb" / "replay_testbench"))
from capsule_parser import parse_capsule  # noqa: E402
from replay_compare import compare_capsules  # noqa: E402


OUT_CSV = REPO_ROOT / "results/processed/replay_negative_tests.csv"
EVENT_PREFIXES = ("pc ", "mmio ", "input ", "interrupt ", "store ", "branch ", "checkpoint ")
STRICT_EVENT_PREFIXES = ("mmio ", "input ", "interrupt ", "store ", "branch ", "checkpoint ")


@dataclass(frozen=True)
class NegativeCase:
    name: str
    expected_success: bool
    mutate_expected: Callable[[str], str]
    mutate_observed: Callable[[str], str]


def main() -> int:
    rows: list[dict[str, str]] = []
    failures: list[str] = []
    for benchmark in BENCHMARKS:
        base_text = capsule_fixture(run_benchmark(benchmark, failing=True))
        for case in _cases():
            expected_text = case.mutate_expected(base_text)
            observed_text = case.mutate_observed(base_text)
            compare = compare_capsules(
                parse_capsule(expected_text, source=f"{benchmark}:{case.name}:expected"),
                parse_capsule(observed_text, source=f"{benchmark}:{case.name}:observed"),
                mode="commit-index",
            )
            status = "PASS" if compare.success == case.expected_success else "FAIL"
            if status == "FAIL":
                failures.append(f"{benchmark}:{case.name} expected success={case.expected_success}, got {compare.success}")
            rows.append(
                {
                    "test": case.name,
                    "benchmark": benchmark,
                    "status": status,
                    "expected_comparator_success": str(case.expected_success),
                    "actual_comparator_success": str(compare.success),
                    "evidence_level": "model",
                    "mode": "commit-index",
                    "notes": "; ".join(compare.errors[:3]) if compare.errors else "comparator accepted fixture",
                }
            )
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "test",
                "benchmark",
                "status",
                "expected_comparator_success",
                "actual_comparator_success",
                "evidence_level",
                "mode",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"WROTE {OUT_CSV}")
    return 1 if failures else 0


def _cases() -> tuple[NegativeCase, ...]:
    identity = lambda text: text
    return (
        NegativeCase("positive_identity_control", True, identity, identity),
        NegativeCase("property_id_mismatch", False, identity, _mutate_property_id),
        NegativeCase("failure_signature_mismatch", False, identity, _mutate_failure_signature),
        NegativeCase("missing_first_replay_event", False, identity, _drop_first_strict_event),
        NegativeCase("duplicate_first_replay_event", False, identity, _duplicate_first_strict_event),
        NegativeCase("corrupt_first_payload", False, identity, _corrupt_first_value),
        NegativeCase("shift_first_commit_index", False, identity, _shift_first_strict_commit),
        NegativeCase("swap_strict_event_order_tags", False, _add_order_tags, _swap_first_two_strict_order_tags),
    )


def _mutate_property_id(text: str) -> str:
    return _replace_line_prefix(text, "property_id ", "property_id CORRUPTED_PROPERTY")


def _mutate_failure_signature(text: str) -> str:
    return _replace_line_prefix(text, "failure_signature ", "failure_signature 0xffffffff")


def _drop_first_strict_event(text: str) -> str:
    lines = text.splitlines()
    index = _first_line_index(lines, STRICT_EVENT_PREFIXES)
    return "\n".join(lines[:index] + lines[index + 1 :]) + "\n"


def _duplicate_first_strict_event(text: str) -> str:
    lines = text.splitlines()
    index = _first_line_index(lines, STRICT_EVENT_PREFIXES)
    return "\n".join(lines[: index + 1] + [lines[index]] + lines[index + 1 :]) + "\n"


def _corrupt_first_value(text: str) -> str:
    lines = text.splitlines()
    index = _first_line_with_token(lines, STRICT_EVENT_PREFIXES, "value")
    lines[index] = _replace_token(lines[index], "value", _increment_hex_token(_get_token(lines[index], "value")))
    return "\n".join(lines) + "\n"


def _shift_first_strict_commit(text: str) -> str:
    lines = text.splitlines()
    index = _first_line_with_token(lines, STRICT_EVENT_PREFIXES, "commit")
    lines[index] = _replace_token(lines[index], "commit", str(int(_get_token(lines[index], "commit"), 0) + 1))
    return "\n".join(lines) + "\n"


def _add_order_tags(text: str) -> str:
    lines = text.splitlines()
    order = 0
    tagged: list[str] = []
    for line in lines:
        if line.startswith(EVENT_PREFIXES):
            tagged.append(_replace_token(line, "order", str(order)))
            order += 1
        else:
            tagged.append(line)
    return "\n".join(tagged) + "\n"


def _swap_first_two_strict_order_tags(text: str) -> str:
    lines = _add_order_tags(text).splitlines()
    strict_indices = [index for index, line in enumerate(lines) if line.startswith(STRICT_EVENT_PREFIXES)]
    if len(strict_indices) < 2:
        raise ValueError("need at least two strict replay events for order-swap test")
    first, second = strict_indices[0], strict_indices[1]
    first_order = _get_token(lines[first], "order")
    second_order = _get_token(lines[second], "order")
    lines[first] = _replace_token(lines[first], "order", second_order)
    lines[second] = _replace_token(lines[second], "order", first_order)
    return "\n".join(lines) + "\n"


def _replace_line_prefix(text: str, prefix: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise ValueError(f"missing line prefix {prefix!r}")


def _first_line_index(lines: list[str], prefixes: tuple[str, ...]) -> int:
    for index, line in enumerate(lines):
        if line.startswith(prefixes):
            return index
    raise ValueError(f"missing event line with prefixes {prefixes!r}")


def _first_line_with_token(lines: list[str], prefixes: tuple[str, ...], key: str) -> int:
    for index, line in enumerate(lines):
        if line.startswith(prefixes) and _has_token(line, key):
            return index
    raise ValueError(f"missing {key} token on event line")


def _has_token(line: str, key: str) -> bool:
    prefix = f"{key}="
    return any(token.startswith(prefix) for token in line.split())


def _get_token(line: str, key: str) -> str:
    prefix = f"{key}="
    for token in line.split():
        if token.startswith(prefix):
            return token[len(prefix) :]
    raise ValueError(f"missing {key} token in {line!r}")


def _replace_token(line: str, key: str, value: str) -> str:
    prefix = f"{key}="
    tokens = line.split()
    for index, token in enumerate(tokens):
        if token.startswith(prefix):
            tokens[index] = f"{key}={value}"
            return " ".join(tokens)
    return " ".join([*tokens, f"{key}={value}"])


def _increment_hex_token(value: str) -> str:
    return f"0x{(int(value, 0) + 1) & 0xffff_ffff:08x}"


if __name__ == "__main__":
    raise SystemExit(main())
