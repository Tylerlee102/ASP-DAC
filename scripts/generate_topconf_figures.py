#!/usr/bin/env python3
"""Generate dependency-free PDF figures from top-conference CSVs."""

from __future__ import annotations

from statistics import median

from topconf_eval_common import REPO_ROOT, read_csv, safe_float


FIG_DIR = REPO_ROOT / "paper/figures"


def main() -> int:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    _pdf("fig_replay_success.pdf", "Replay Success By Workload Scale", _replay_lines())
    _pdf("fig_capsule_scaling.pdf", "Capsule Size Scaling", _capsule_lines())
    _pdf("fig_runtime_scaling.pdf", "Runtime Scaling", _runtime_lines())
    _pdf("fig_buffer_sensitivity.pdf", "Buffer Depth Sensitivity", _buffer_lines())
    _pdf("fig_mapped_memory_scaling.pdf", "Mapped Memory Scaling", _mapped_lines("memory_words"))
    _pdf("fig_mapped_buffer_scaling.pdf", "Mapped Buffer Scaling", _mapped_lines("buffer_depth"))
    _pdf("fig_recorder_config_tradeoff.pdf", "Recorder Config Tradeoff", _recorder_lines())
    print("WROTE paper/figures/fig_*.pdf")
    return 0


def _replay_lines() -> list[str]:
    rows = read_csv(REPO_ROOT / "results/processed/workload_scaling.csv")
    lines = []
    for scale in sorted({row.get("workload_scale", "NA") for row in rows}):
        subset = [row for row in rows if row.get("workload_scale") == scale]
        passed = sum(1 for row in subset if row.get("replay_status") == "PASS")
        lines.append(f"{scale}: {passed}/{len(subset)} PASS")
    return lines or ["No workload_scaling.csv rows available."]


def _capsule_lines() -> list[str]:
    rows = read_csv(REPO_ROOT / "results/processed/capsule_baseline_summary.csv")
    lines = []
    for row in rows:
        if row.get("baseline") == "replaycapsule_core":
            lines.append(f"{row.get('workload_scale')}: median {row.get('median_bytes')} bytes, reduction vs full instruction {row.get('median_reduction_vs_full_instruction_pct')}%")
    return lines or ["No capsule baseline summary available."]


def _runtime_lines() -> list[str]:
    rows = read_csv(REPO_ROOT / "results/processed/runtime_scaling_summary.csv")
    lines = []
    for row in rows:
        if row.get("config") == "recorder_enabled":
            lines.append(f"{row.get('workload_scale')}: cycle {row.get('median_cycle_overhead_pct')}%, commit {row.get('median_commit_overhead_pct')}%, simulator wall {row.get('median_sim_wall_time_overhead_pct')}%")
    return lines or ["No runtime scaling summary available."]


def _buffer_lines() -> list[str]:
    rows = read_csv(REPO_ROOT / "results/processed/buffer_sensitivity_summary.csv")
    lines = []
    for depth in sorted({row.get("buffer_depth", "NA") for row in rows}, key=lambda value: int(value) if str(value).isdigit() else 0):
        subset = [row for row in rows if row.get("buffer_depth") == depth]
        overflow_values = [safe_float(row.get("overflow_rate_pct")) for row in subset]
        clean = [value for value in overflow_values if value is not None]
        lines.append(f"depth {depth}: median overflow {median(clean):.2f}%" if clean else f"depth {depth}: NA")
    return lines or ["No buffer sensitivity summary available."]


def _mapped_lines(axis: str) -> list[str]:
    rows = read_csv(REPO_ROOT / "results/processed/mapped_scaling_overhead.csv")
    lines = []
    for key in sorted({row.get(axis, "NA") for row in rows}, key=lambda value: int(value) if str(value).isdigit() else 0):
        subset = [row for row in rows if row.get(axis) == key and row.get("claim_allowed") == "yes" and row.get("metric") in {"lut", "ff", "bram", "fmax_mhz"}]
        if not subset:
            lines.append(f"{axis} {key}: no same-target PASS overhead row")
            continue
        metrics = ", ".join(f"{row.get('metric')} {row.get('percent_overhead')}%" for row in subset)
        lines.append(f"{axis} {key}: {metrics}")
    return lines or ["No mapped scaling overhead rows available."]


def _recorder_lines() -> list[str]:
    rows = read_csv(REPO_ROOT / "results/processed/recorder_config_replay.csv")
    lines = []
    for config in sorted({row.get("recorder_config", "NA") for row in rows}):
        subset = [row for row in rows if row.get("recorder_config") == config]
        passed = sum(1 for row in subset if row.get("replay_status") == "PASS")
        bytes_values = [safe_float(row.get("capsule_bytes")) for row in subset]
        clean = [value for value in bytes_values if value is not None]
        lines.append(f"{config}: {passed}/{len(subset)} replay PASS, median capsule {median(clean):.0f} bytes" if clean else f"{config}: {passed}/{len(subset)} replay PASS")
    return lines or ["No recorder config replay rows available."]


def _pdf(name: str, title: str, lines: list[str]) -> None:
    content_lines = ["BT", "/F1 15 Tf", "50 770 Td", f"({_escape(title)}) Tj", "/F1 10 Tf"]
    y_step = 16
    for index, line in enumerate(lines[:38]):
        content_lines.append(f"0 -{y_step if index else 24} Td")
        content_lines.append(f"({_escape(line[:110])}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("ascii", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{number} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f\n".encode("ascii"))
    for offset in offsets:
        out.extend(f"{offset:010d} 00000 n\n".encode("ascii"))
    out.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    (FIG_DIR / name).write_bytes(out)


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


if __name__ == "__main__":
    raise SystemExit(main())
