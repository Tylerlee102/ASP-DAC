#!/usr/bin/env python3
"""Generate an honest top-conference reviewer simulation audit."""

from __future__ import annotations

from pathlib import Path

from topconf_eval_common import REPO_ROOT, read_csv


OUT = REPO_ROOT / "docs/top_conference_reviewer_audit.md"


ROLES = (
    "Hardware architecture reviewer",
    "EDA/synthesis reviewer",
    "Systems/debug reviewer",
    "Formal/replay-model reviewer",
    "Artifact evaluation reviewer",
    "Skeptical novelty reviewer",
    "Quantitative evaluation reviewer",
)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    status = _status()
    lines = ["# Top-Conference Reviewer Audit", "", f"Overall status: **{status}**", ""]
    for role in ROLES:
        lines.extend(_role_section(role, status))
    while lines and lines[-1] == "":
        lines.pop()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE docs/top_conference_reviewer_audit.md")
    return 0


def _status() -> str:
    workload = read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    mapped = read_csv(REPO_ROOT / "results/processed/mapped_scaling_overhead.csv")
    pass_workload_scales = {row.get("workload_scale") for row in workload if row.get("replay_status") == "PASS"}
    allowed_mapped = [row for row in mapped if row.get("claim_allowed") == "yes"]
    memories = {row.get("memory_words") for row in allowed_mapped}
    depths = {row.get("buffer_depth") for row in allowed_mapped}
    configs = {row.get("recorder_config") for row in allowed_mapped}
    if len(pass_workload_scales) >= 5 and len(memories) >= 3 and len(depths) >= 3 and len(configs) >= 2:
        return "SUBMISSION-READY"
    if len(pass_workload_scales) >= 3 and allowed_mapped:
        return "BORDERLINE SUBMISSION-READY"
    return "WORKSHOP-ONLY"


def _role_section(role: str, status: str) -> list[str]:
    rating = "weak accept" if status == "SUBMISSION-READY" else "borderline" if status == "BORDERLINE SUBMISSION-READY" else "weak reject"
    fatal = "none after scoped wording" if status != "WORKSHOP-ONLY" else "mapped/scaling data remains too thin for top-conference strength"
    return [
        f"## {role}",
        "",
        f"rating: {rating}",
        "",
        "top strengths:",
        "- compiler-backed firmware and full RTL replay evidence are strong",
        "- corrupted-capsule rejection is explicit",
        "- artifact scripts produce traceable CSVs and paper artifacts",
        "",
        "top weaknesses:",
        "- diagnostic mapped LUT/FF overhead is high",
        "- replay consume path remains host-driven",
        "- benchmark and peripheral diversity are limited",
        "",
        f"fatal blockers: {fatal}",
        "",
        "likely reviewer questions:",
        "- How does overhead scale beyond the demonstrated FPGA points?",
        "- Which event classes are replay-critical versus diagnostic-only?",
        "- Why is simulator wall time separated from hardware cycle overhead?",
        "",
        "required paper wording changes:",
        "- state that mapped data is recorder/instrumented-wrapper evidence, not an autonomous replay engine",
        "- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows",
        "- keep ASIC/power and multicore/DMA/cache support out of claims",
        "",
        f"final recommendation: {'submit main-track with scoped claims' if status != 'WORKSHOP-ONLY' else 'submit workshop or gather more mapped/scaling data first'}",
        "",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
