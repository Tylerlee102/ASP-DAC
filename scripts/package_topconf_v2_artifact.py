#!/usr/bin/env python3
"""Package the ReplayCapsule-RV top-conference v2 artifact."""

from __future__ import annotations

import csv
import zipfile
from pathlib import Path

from topconf_eval_common import REPO_ROOT, rel, write_csv


ZIP_PATH = REPO_ROOT / "dist/replaycapsule-rv-topconf-v2-artifact.zip"
MANIFEST_CSV = REPO_ROOT / "dist/topconf_v2_artifact_manifest.csv"
PROCESSED_MANIFEST = REPO_ROOT / "results/processed/topconf_v2_artifact_manifest.csv"
FIELDS = ["path", "bytes", "category", "notes"]


def main() -> int:
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    files = _collect_files()
    rows = []
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, category, notes in files:
            if not path.exists() or not path.is_file():
                continue
            if rel(path) == "results/processed/private_marker_scan.csv":
                continue
            if path.suffix.lower() == ".map":
                continue
            if path.suffix.lower() in {".vvp", ".exe", ".dll", ".json", ".config"} and category == "raw":
                continue
            arcname = rel(path)
            zf.write(path, arcname)
            rows.append({"path": arcname, "bytes": path.stat().st_size, "category": category, "notes": notes})
        manifest_text = _manifest_text(rows)
        zf.writestr("dist/topconf_v2_artifact_manifest.csv", manifest_text)
    _write_manifest_csv(MANIFEST_CSV, rows)
    write_csv(PROCESSED_MANIFEST, FIELDS, rows)
    print(f"WROTE {rel(ZIP_PATH)}")
    print(f"WROTE {rel(MANIFEST_CSV)}")
    print(f"TOPCONF_V2_ARTIFACT files={len(rows) + 1}")
    return 0


def _collect_files() -> list[tuple[Path, str, str]]:
    files: list[tuple[Path, str, str]] = []
    singletons = [
        ("paper/main.pdf", "paper", "locked PDF or locally built PDF"),
        ("paper/main.tex", "paper", "paper source"),
        ("README.md", "docs", "repository README"),
        ("artifact_evaluation.md", "docs", "artifact evaluation instructions"),
        ("docs/novelty_audit.md", "docs", "novelty guardrails"),
        ("docs/related_work_positioning.md", "docs", "related work guardrails"),
        ("docs/conference_readiness_dashboard.md", "docs", "current readiness dashboard"),
    ]
    for rel_path, category, notes in singletons:
        files.append((REPO_ROOT / rel_path, category, notes))

    for pattern, category, notes in [
        ("paper/sections/*.tex", "paper", "paper section source"),
        ("paper/tables/*.tex", "paper", "generated paper table"),
        ("paper/figures/*", "paper", "generated paper figure/source"),
        ("results/processed/*.csv", "results", "processed evidence CSV"),
        ("results/raw/replay_consumer/*", "raw", "replay consumer compile/run log"),
        ("results/raw/replay_consumer_mapping/*", "raw", "replay consumer mapping log"),
        ("results/debug/topconf_v2_before/*", "baseline", "frozen pre-v2 evidence"),
        ("rtl/replaycapsule_v2/*", "rtl", "v2 RTL source"),
        ("rtl/mapped/replaycapsule_v2_recorder_wrapper.sv", "rtl", "v2 synthesis wrapper"),
        ("tb/replay_consumer/*", "tests", "v2 replay consumer testbench"),
        ("scripts/diagnose_workload_failures.py", "scripts", "v2 diagnosis script"),
        ("scripts/run_buffer_sensitivity_v2.py", "scripts", "v2 buffer script"),
        ("scripts/run_workload_scaling_v2.py", "scripts", "v2 workload script"),
        ("scripts/run_capsule_baselines_v2.py", "scripts", "v2 capsule script"),
        ("scripts/run_replay_consumer_tests.py", "scripts", "v2 replay consumer test script"),
        ("scripts/run_replay_consumer_mapping.py", "scripts", "v2 replay consumer mapping script"),
        ("scripts/run_mapped_scaling_v2.py", "scripts", "v2 mapped-status script"),
        ("scripts/run_second_target_mapping.py", "scripts", "v2 second-target script"),
        ("scripts/benchmark_manifest.py", "scripts", "benchmark diversity manifest script"),
        ("scripts/generate_topconf_v2_tables.py", "scripts", "v2 paper table/figure script"),
    ]:
        files.extend((path, category, notes) for path in sorted(REPO_ROOT.glob(pattern)))
    return _dedupe(files)


def _dedupe(files: list[tuple[Path, str, str]]) -> list[tuple[Path, str, str]]:
    seen: set[Path] = set()
    out = []
    for path, category, notes in files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append((path, category, notes))
    return out


def _manifest_text(rows: list[dict[str, object]]) -> str:
    from io import StringIO

    handle = StringIO()
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def _write_manifest_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
