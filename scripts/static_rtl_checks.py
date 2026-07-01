#!/usr/bin/env python3
"""Lightweight static checks for ReplayCapsule-RV SystemVerilog sources."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PACKAGE = ("rtl/event_pkg.sv", "replaycapsule_event_pkg")

REQUIRED_MODULES = [
    ("rtl/replay_capsule_top.sv", "replay_capsule_top"),
    ("rtl/event_tap.sv", "event_tap"),
    ("rtl/event_classifier.sv", "event_classifier"),
    ("rtl/capsule_buffer.sv", "capsule_buffer"),
    ("rtl/property_checker.sv", "property_checker"),
    ("rtl/interrupt_logger.sv", "interrupt_logger"),
    ("rtl/mmio_logger.sv", "mmio_logger"),
    ("rtl/event_slicer.sv", "event_slicer"),
    ("rtl/replay_control.sv", "replay_control"),
    ("rtl/registers.sv", "registers"),
    ("rtl/hash_signature.sv", "hash_signature"),
    ("rtl/rv32i_integration/replaycapsule_soc.sv", "replaycapsule_soc"),
    ("rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv", "picorv32_replaycapsule_wrapper"),
    ("rtl/rv32i_integration/femtorv32_replaycapsule_wrapper.sv", "femtorv32_replaycapsule_wrapper"),
]

REQUIRED_EVENTS = [
    ("EV_COMMIT", 0),
    ("EV_BRANCH", 1),
    ("EV_JUMP", 2),
    ("EV_STORE", 3),
    ("EV_LOAD", 4),
    ("EV_MMIO_READ", 5),
    ("EV_MMIO_WRITE", 6),
    ("EV_INTERRUPT_ENTER", 7),
    ("EV_INTERRUPT_EXIT", 8),
    ("EV_EXTERNAL_INPUT", 9),
    ("EV_PROPERTY_FAIL", 10),
    ("EV_CHECKPOINT_HASH", 11),
]

FORBIDDEN_PLACEHOLDERS = [
    ("TODO", re.compile(r"\bTODO\b", re.IGNORECASE)),
    ("FIXME", re.compile(r"\bFIXME\b", re.IGNORECASE)),
    ("TBD", re.compile(r"\bTBD\b", re.IGNORECASE)),
    ("XXX", re.compile(r"\bXXX\b", re.IGNORECASE)),
    ("placeholder", re.compile(r"\bplaceholder\b", re.IGNORECASE)),
    ("stub", re.compile(r"\bstub(?:bed)?\b", re.IGNORECASE)),
    ("dummy", re.compile(r"\bdummy\b", re.IGNORECASE)),
    ("fake", re.compile(r"\bfake\b", re.IGNORECASE)),
    ("not implemented", re.compile(r"\bnot\s+implemented\b", re.IGNORECASE)),
    ("unimplemented", re.compile(r"\bunimplemented\b", re.IGNORECASE)),
]


@dataclass(frozen=True)
class Finding:
    check: str
    status: str
    path: str = ""
    line: str = ""
    detail: str = ""

    def as_row(self) -> dict[str, str]:
        return {
            "check": self.check,
            "status": self.status,
            "path": self.path,
            "line": self.line,
            "detail": self.detail,
        }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    repo_root = args.repo_root.resolve()

    findings = run_checks(repo_root)

    if args.format == "csv":
        _emit_csv(findings)
    else:
        _emit_text(findings)

    return 1 if any(row.status == "FAIL" for row in findings) else 0


def run_checks(repo_root: Path) -> list[Finding]:
    sv_files = sorted((repo_root / "rtl").rglob("*.sv"))
    findings: list[Finding] = []

    findings.extend(_check_required_files(repo_root))
    findings.extend(_check_required_package(repo_root))
    findings.extend(_check_required_modules(repo_root, sv_files))
    findings.extend(_check_required_events(repo_root, sv_files))
    findings.extend(_check_forbidden_placeholders(repo_root, sv_files))

    return findings


def _check_required_files(repo_root: Path) -> list[Finding]:
    required_paths = [REQUIRED_PACKAGE[0], *[path for path, _module in REQUIRED_MODULES]]
    findings: list[Finding] = []
    for rel_path in required_paths:
        path = repo_root / rel_path
        if path.exists():
            findings.append(Finding("required_file", "PASS", rel_path, "", "present"))
        else:
            findings.append(Finding("required_file", "FAIL", rel_path, "", "missing"))
    return findings


def _check_required_package(repo_root: Path) -> list[Finding]:
    rel_path, package_name = REQUIRED_PACKAGE
    path = repo_root / rel_path
    if not path.exists():
        return [Finding("required_package", "FAIL", rel_path, "", f"missing package {package_name}")]

    text = _strip_sv_comments(_read_text(path))
    pattern = re.compile(rf"\bpackage\s+{re.escape(package_name)}\b")
    match = pattern.search(text)
    if not match:
        return [Finding("required_package", "FAIL", rel_path, "", f"package {package_name} not declared")]

    return [
        Finding(
            "required_package",
            "PASS",
            rel_path,
            str(_line_number(text, match.start())),
            f"package {package_name} declared",
        )
    ]


def _check_required_modules(repo_root: Path, sv_files: Iterable[Path]) -> list[Finding]:
    declarations = _collect_module_declarations(repo_root, sv_files)
    findings: list[Finding] = []

    for rel_path, module_name in REQUIRED_MODULES:
        expected_path = _norm_rel(repo_root / rel_path, repo_root)
        matches = declarations.get(module_name, [])
        expected_matches = [item for item in matches if item[0] == expected_path]

        if len(expected_matches) == 1:
            findings.append(
                Finding(
                    "required_module",
                    "PASS",
                    expected_path,
                    str(expected_matches[0][1]),
                    f"module {module_name} declared",
                )
            )
        elif not matches:
            findings.append(Finding("required_module", "FAIL", expected_path, "", f"module {module_name} missing"))
        elif not expected_matches:
            found_at = ", ".join(f"{path}:{line}" for path, line in matches)
            findings.append(
                Finding(
                    "required_module",
                    "FAIL",
                    expected_path,
                    "",
                    f"module {module_name} not declared in expected file; found at {found_at}",
                )
            )
        else:
            lines = ", ".join(str(line) for _path, line in expected_matches)
            findings.append(
                Finding(
                    "required_module",
                    "FAIL",
                    expected_path,
                    lines,
                    f"module {module_name} declared multiple times in expected file",
                )
            )

    duplicates = {name: locs for name, locs in declarations.items() if len(locs) > 1}
    if duplicates:
        for name, locs in sorted(duplicates.items()):
            detail = ", ".join(f"{path}:{line}" for path, line in locs)
            findings.append(Finding("duplicate_module", "FAIL", "", "", f"module {name} declared at {detail}"))
    else:
        findings.append(Finding("duplicate_module", "PASS", "rtl", "", "no duplicate module declarations"))

    return findings


def _check_required_events(repo_root: Path, sv_files: Iterable[Path]) -> list[Finding]:
    rel_path = REQUIRED_PACKAGE[0]
    path = repo_root / rel_path
    if not path.exists():
        return [Finding("required_event", "FAIL", rel_path, "", "event package file missing")]

    text = _strip_sv_comments(_read_text(path))
    declarations = _collect_event_declarations(text)
    findings: list[Finding] = []

    for event_name, expected_value in REQUIRED_EVENTS:
        event = declarations.get(event_name)
        if event is None:
            findings.append(Finding("required_event", "FAIL", rel_path, "", f"{event_name} missing"))
            continue

        parsed_value, raw_value, line = event
        if parsed_value is None:
            findings.append(
                Finding(
                    "required_event",
                    "FAIL",
                    rel_path,
                    str(line),
                    f"{event_name} value {raw_value!r} could not be parsed; expected {expected_value}",
                )
            )
        elif parsed_value != expected_value:
            findings.append(
                Finding(
                    "required_event",
                    "FAIL",
                    rel_path,
                    str(line),
                    f"{event_name} value {parsed_value} does not match expected {expected_value}",
                )
            )
        else:
            findings.append(
                Finding(
                    "required_event",
                    "PASS",
                    rel_path,
                    str(line),
                    f"{event_name} = {expected_value}",
                )
            )

    findings.extend(_check_unknown_event_references(repo_root, sv_files))
    return findings


def _check_unknown_event_references(repo_root: Path, sv_files: Iterable[Path]) -> list[Finding]:
    known_events = {name for name, _value in REQUIRED_EVENTS}
    unknown: dict[str, list[tuple[str, int]]] = {}

    for path in sv_files:
        text = _strip_sv_comments(_read_text(path))
        rel_path = _norm_rel(path, repo_root)
        for match in re.finditer(r"\bEV_[A-Z0-9_]+\b", text):
            event_name = match.group(0)
            if event_name not in known_events:
                unknown.setdefault(event_name, []).append((rel_path, _line_number(text, match.start())))

    if not unknown:
        return [Finding("unknown_event_reference", "PASS", "rtl", "", "all EV_* references are known")]

    findings: list[Finding] = []
    for event_name, locations in sorted(unknown.items()):
        detail = ", ".join(f"{path}:{line}" for path, line in locations[:5])
        if len(locations) > 5:
            detail += f", ... {len(locations) - 5} more"
        findings.append(Finding("unknown_event_reference", "FAIL", "", "", f"{event_name} at {detail}"))
    return findings


def _check_forbidden_placeholders(repo_root: Path, sv_files: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []

    for path in sv_files:
        rel_path = _norm_rel(path, repo_root)
        for line_no, line in enumerate(_read_text(path).splitlines(), start=1):
            for name, pattern in FORBIDDEN_PLACEHOLDERS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            "forbidden_placeholder",
                            "FAIL",
                            rel_path,
                            str(line_no),
                            f"matched {name}: {line.strip()}",
                        )
                    )

    if findings:
        return findings
    return [Finding("forbidden_placeholder", "PASS", "rtl", "", "no forbidden placeholder markers")]


def _collect_module_declarations(repo_root: Path, sv_files: Iterable[Path]) -> dict[str, list[tuple[str, int]]]:
    declarations: dict[str, list[tuple[str, int]]] = {}
    module_re = re.compile(r"(?m)^\s*module\s+([A-Za-z_][A-Za-z0-9_$]*)\b")

    for path in sv_files:
        text = _strip_sv_comments(_read_text(path))
        rel_path = _norm_rel(path, repo_root)
        for match in module_re.finditer(text):
            module_name = match.group(1)
            declarations.setdefault(module_name, []).append((rel_path, _line_number(text, match.start())))

    return declarations


def _collect_event_declarations(text: str) -> dict[str, tuple[int | None, str, int]]:
    declarations: dict[str, tuple[int | None, str, int]] = {}
    event_re = re.compile(r"\b(EV_[A-Z0-9_]+)\s*=\s*([^,\n}]+)")

    for match in event_re.finditer(text):
        event_name = match.group(1)
        raw_value = match.group(2).strip()
        declarations[event_name] = (_parse_sv_int(raw_value), raw_value, _line_number(text, match.start()))

    return declarations


def _parse_sv_int(value: str) -> int | None:
    clean = value.strip().rstrip(";").replace("_", "")
    literal_re = re.compile(r"(?:(\d+)')?([sS])?([bBoOdDhH])([0-9a-fA-FxXzZ?]+)\Z")
    match = literal_re.fullmatch(clean)

    if match:
        base = match.group(3).lower()
        digits = match.group(4).lower()
        if any(char in digits for char in "xz?"):
            return None
        radix = {"b": 2, "o": 8, "d": 10, "h": 16}[base]
        return int(digits, radix)

    try:
        return int(clean, 0)
    except ValueError:
        return None


def _strip_sv_comments(text: str) -> str:
    chars: list[str] = []
    i = 0
    in_block = False

    while i < len(text):
        if in_block:
            if text.startswith("*/", i):
                chars.extend("  ")
                i += 2
                in_block = False
            else:
                chars.append("\n" if text[i] == "\n" else " ")
                i += 1
            continue

        if text.startswith("//", i):
            while i < len(text) and text[i] != "\n":
                chars.append(" ")
                i += 1
            continue

        if text.startswith("/*", i):
            chars.extend("  ")
            i += 2
            in_block = True
            continue

        chars.append(text[i])
        i += 1

    return "".join(chars)


def _emit_csv(findings: Iterable[Finding]) -> None:
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=["check", "status", "path", "line", "detail"],
        lineterminator="\n",
    )
    writer.writeheader()
    for finding in findings:
        writer.writerow(finding.as_row())


def _emit_text(findings: list[Finding]) -> None:
    for finding in findings:
        location = ""
        if finding.path and finding.line:
            location = f" {finding.path}:{finding.line}"
        elif finding.path:
            location = f" {finding.path}"

        detail = f" - {finding.detail}" if finding.detail else ""
        print(f"{finding.status}: {finding.check}{location}{detail}")

    passed = sum(1 for finding in findings if finding.status == "PASS")
    failed = sum(1 for finding in findings if finding.status == "FAIL")
    print(f"\nSummary: {passed} passed, {failed} failed")


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _norm_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run lightweight ReplayCapsule-RV static RTL contract checks.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="repository root to check (default: inferred from this script)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "csv"),
        default="text",
        help="report format written to stdout",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
