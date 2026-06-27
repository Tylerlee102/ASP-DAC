#!/usr/bin/env python3
"""Check that the mapped full-core ReplayCapsule board keeps recorder logic."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAPPED_CSV = REPO_ROOT / "results/processed/mapped_synthesis.csv"
OUT_CSV = REPO_ROOT / "results/processed/mapped_recorder_presence.csv"
RAW_DIR = REPO_ROOT / "results/raw/mapped_synthesis"

FIELDNAMES = [
    "target",
    "flow",
    "design",
    "mapped_status",
    "recorder_module_seen",
    "capsule_buffer_seen",
    "status_logic_seen",
    "top_outputs_seen",
    "status",
    "report_path",
    "notes",
]

SUFFIX_BY_TARGET = {
    "ecp5-85k": "ecp5_85k",
    "ecp5-45k": "ecp5_45k",
    "ice40-hx8k": "ice40_hx8k",
}

RECORDER_DESIGN = "full_core_replaycapsule_board"


def main() -> int:
    rows = write_presence_csv(REPO_ROOT)
    failed = [row for row in rows if row["mapped_status"] == "PASS" and row["status"] != "PASS"]
    if failed:
        for row in failed:
            print(f"RECORDER PRESENCE FAIL {row['target']}: {row['notes']}")
        return 1
    print(f"WROTE {_rel(OUT_CSV)}")
    return 0


def write_presence_csv(repo_root: Path = REPO_ROOT) -> list[dict[str, str]]:
    mapped_rows = _read_rows(repo_root / "results/processed/mapped_synthesis.csv")
    rows = [_presence_row(repo_root, row) for row in mapped_rows if row.get("design") == RECORDER_DESIGN]
    out = repo_root / "results/processed/mapped_recorder_presence.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _presence_row(repo_root: Path, mapped_row: dict[str, str]) -> dict[str, str]:
    target = mapped_row.get("target", "NA")
    flow = mapped_row.get("flow", "NA")
    suffix = SUFFIX_BY_TARGET.get(target, target.replace("-", "_"))
    json_path = repo_root / "results/raw/mapped_synthesis" / f"{RECORDER_DESIGN}_{suffix}.json"
    yosys_log = repo_root / "results/raw/mapped_synthesis" / f"{RECORDER_DESIGN}_yosys_{suffix}.txt"
    report_paths = [path for path in (json_path, yosys_log) if path.exists()]
    combined = "\n".join(_read_text(path) for path in report_paths)
    json_data = _load_json(json_path)

    recorder_module_seen = _has_any(combined, ("picorv32_replaycapsule_wrapper", "replay_capsule_top", "u_full_core_replaycapsule"))
    capsule_buffer_seen = _has_any(combined, ("capsule_buffer", "u_capsule_buffer", "capsule_event_count"))
    status_logic_seen = _json_has_signal(json_data, "recorder_status_mix") or _has_any(combined, ("recorder_status_mix", "running_signature", "property_signature"))
    top_outputs_seen = all(_json_has_signal(json_data, signal) or signal in combined for signal in ("capsule_event_seen", "recorder_overflow_seen", "recorder_status_xor"))
    mapped_pass = mapped_row.get("status") == "PASS"

    checks = {
        "recorder_module_seen": recorder_module_seen,
        "capsule_buffer_seen": capsule_buffer_seen,
        "status_logic_seen": status_logic_seen,
        "top_outputs_seen": top_outputs_seen,
    }
    missing = [name for name, ok in checks.items() if not ok]
    status = "PASS" if mapped_pass and not missing else "FAIL" if mapped_pass else "NA"
    notes = "recorder hierarchy and status-connected outputs found in mapped artifacts"
    if not mapped_pass:
        notes = "mapped design did not PASS place-and-route; recorder presence not claimable"
    elif missing:
        notes = "missing " + ", ".join(missing)

    return {
        "target": target,
        "flow": flow,
        "design": RECORDER_DESIGN,
        "mapped_status": mapped_row.get("status", "NA"),
        "recorder_module_seen": _yes_no(recorder_module_seen),
        "capsule_buffer_seen": _yes_no(capsule_buffer_seen),
        "status_logic_seen": _yes_no(status_logic_seen),
        "top_outputs_seen": _yes_no(top_outputs_seen),
        "status": status,
        "report_path": _rel(json_path) if json_path.exists() else "NA",
        "notes": notes,
    }


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}


def _json_has_signal(data: dict, needle: str) -> bool:
    if not data:
        return False
    stack = [data]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                if needle in str(key):
                    return True
                stack.append(value)
        elif isinstance(current, list):
            stack.extend(current)
        elif needle in str(current):
            return True
    return False


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
