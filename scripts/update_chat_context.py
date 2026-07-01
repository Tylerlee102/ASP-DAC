#!/usr/bin/env python3
"""Generate the new-chat handoff file for ReplayCapsule-RV.

The output is intentionally compact and evidence-oriented. It gives future
chats one place to understand what exists, what has been proven, and what is
still only partially integrated.
"""

from __future__ import annotations

import csv
import datetime as _dt
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "CHAT_CONTEXT.md"

SKIP_WALK_DIRS = {".git", ".tools", "__pycache__", ".pytest_cache"}


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_context(), encoding="utf-8")
    print(f"WROTE {repo_rel(OUTPUT)}")
    return 0


def render_context() -> str:
    generated_at = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    lines: list[str] = []

    lines.extend(
        [
            "# ReplayCapsule-RV Chat Context",
            "",
            "> Generated file. Refresh after code, paper, evidence, or artifact changes with `make chat-context` or by running `scripts/update_chat_context.py` with a real Python 3 executable.",
            "",
            f"- Generated at: `{generated_at}`",
            f"- Repository root: `{REPO_ROOT}`",
            f"- Python used for this snapshot: `{sys.executable}`",
            "",
        ]
    )
    lines.extend(section_git_state())
    lines.extend(section_quick_read())
    lines.extend(section_repository_inventory())
    lines.extend(section_implemented_components())
    lines.extend(section_evidence_status())
    lines.extend(section_paper_artifacts())
    lines.extend(section_claim_boundaries())
    lines.extend(section_autonomous_replay_status())
    lines.extend(section_next_priorities())
    lines.extend(section_file_map())
    lines.extend(section_update_rules())
    return "\n".join(lines).rstrip() + "\n"


def section_git_state() -> list[str]:
    branch = git_text(["branch", "--show-current"]) or "unknown"
    commit = git_text(["rev-parse", "--short", "HEAD"]) or "unknown"
    status = git_text(["status", "--short"])
    status_lines = status.splitlines() if status else []

    lines = [
        "## Current Git State",
        "",
        f"- Branch: `{branch}`",
        f"- Commit: `{commit}`",
        f"- Working tree status: `{len(status_lines)} changed paths`",
    ]
    if status_lines:
        lines.append("- Changed paths:")
        for item in status_lines[:40]:
            lines.append(f"  - `{item}`")
        if len(status_lines) > 40:
            lines.append(f"  - `... {len(status_lines) - 40} more`")
    else:
        lines.append("- Changed paths: none")
    lines.append("")
    return lines


def section_quick_read() -> list[str]:
    return [
        "## Read This First",
        "",
        "- This repo is a ReplayCapsule-RV research artifact for scoped single-hart RV32I interrupt/MMIO failure replay.",
        "- The project already contains RTL, firmware benchmarks, Verilator replay harnesses, v2 compressed recorder logic, a v2 replay-consume checker, FPGA mapping evidence, generated paper assets, artifact packages, a second-core wrapper/replay-smoke breadth gate, a focused Hazard3 true-ISR firmware smoke, and a seeded Hazard3 v2 MMIO+IRQ replay benchmark matrix.",
        "- The current strongest claim is event-sufficient replay for scoped embedded interrupt/MMIO failures with compiler-backed full RTL replay evidence.",
        "- The v2 full RTL replay path now preloads capsule words into an RTL replay source, then uses the RTL replay consumer to drive replay MMIO/IRQ inputs into the core-facing paths; evidence rows should show `replay_stimulus_source=rtl_capsule_source_mmio_irq`.",
        "- For conference-review questions, check `docs/conference_readiness_dashboard.md`, `docs/final_reviewer_report.md`, `docs/main_track_submission_review.md`, and `docs/novelty_audit.md`.",
        "",
    ]


def section_repository_inventory() -> list[str]:
    rows = directory_inventory()
    total_files = sum(row["files"] for row in rows)
    total_bytes = sum(row["bytes"] for row in rows)

    lines = [
        "## Repository Inventory",
        "",
        f"- Counted files: `{total_files}`",
        f"- Counted size: `{format_bytes(total_bytes)}`",
        "- `.git` and `.tools` are skipped as repository metadata/local toolchain cache.",
        "",
        "| Path | Files | Size | Notes |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['path']}` | {row['files']} | {format_bytes(row['bytes'])} | {row['notes']} |"
        )
    lines.append("")
    return lines


def section_implemented_components() -> list[str]:
    rtl_files = sorted(p.name for p in (REPO_ROOT / "rtl").glob("*.sv"))
    v2_files = sorted(p.name for p in (REPO_ROOT / "rtl" / "replaycapsule_v2").glob("*.sv"))
    integration_files = sorted(p.name for p in (REPO_ROOT / "rtl" / "rv32i_integration").glob("*.sv"))
    mapped_files = sorted(p.name for p in (REPO_ROOT / "rtl" / "mapped").glob("*.sv"))
    third_party_cores = sorted(p.name for p in (REPO_ROOT / "third_party").iterdir() if p.is_dir())
    firmware_benchmarks = sorted(
        {row.get("benchmark", "") for row in read_csv("results/processed/firmware_build.csv") if row.get("benchmark")}
    )
    expanded_benchmarks = sorted(
        {
            row.get("benchmark", "")
            for row in read_csv("results/processed/expanded_benchmark_replay_measured.csv")
            if row.get("benchmark")
        }
    )

    lines = [
        "## Implemented Components",
        "",
        "### RTL",
        "",
        f"- Core ReplayCapsule modules: {inline_list(rtl_files)}",
        f"- v2 modules: {inline_list(v2_files)}",
        f"- RV32I/PicoRV32 integration modules: {inline_list(integration_files)}",
        f"- Mapped board/wrapper modules: {inline_list(mapped_files)}",
        f"- Vendored core sources: {inline_list(third_party_cores)}",
        "",
        "### Firmware And Harnesses",
        "",
        f"- Compiler-backed firmware benchmarks in current firmware evidence: {inline_list(firmware_benchmarks)}",
        f"- Expanded v2 benchmark families in measured replay evidence: {inline_list(expanded_benchmarks)}",
        "- Verilator harness files live under `tb/verilator/` and include record/replay execution, capsule JSON I/O, runtime comparisons, and hardware-driven v2 replay stimulus checks.",
        "- Directed replay-consumer tests live under `tb/replay_consumer/`; system tests and HDL checks live under `tb/system/`.",
        "",
        "### Paper And Packaging",
        "",
        "- Paper source is under `paper/` with generated figures, tables, and ACM/ASP-DAC-style `paper/main.pdf`.",
        "- Artifact packages are under `dist/`.",
        "- Submission/readiness docs are under `docs/`.",
        "",
    ]
    return lines


def section_evidence_status() -> list[str]:
    firmware = read_csv("results/processed/firmware_build.csv")
    full_rtl = read_csv("results/processed/full_rtl_replay.csv")
    full_rtl_v2 = read_csv("results/processed/full_rtl_replay_v2.csv")
    self_replay = read_csv("results/processed/self_replay_handoff_v2.csv")
    standalone_self = read_csv("results/processed/standalone_self_replay_smokes.csv")
    negative = read_csv("results/processed/full_rtl_replay_negative.csv")
    workload_v2 = read_csv("results/processed/workload_scaling_v2_measured_summary.csv")
    expanded = read_csv("results/processed/expanded_benchmark_replay_measured.csv")
    mapped_v2 = read_csv("results/processed/mapped_scaling_overhead_v2_measured.csv")
    asic_summary = read_csv("results/processed/asic_openpdk_summary.csv")
    asic_rows = read_csv("results/processed/asic_openpdk.csv")
    asic_overhead = read_csv("results/processed/asic_openpdk_overhead.csv")
    asic_area = read_csv("results/processed/asic_openpdk_yosys_area.csv")
    asic_area_overhead = read_csv("results/processed/asic_openpdk_yosys_area_overhead.csv")
    asic_tool_probe = read_csv("results/processed/asic_physical_tool_probe.csv")
    hdl = read_csv("results/processed/hdl_checks.csv")
    formal = read_csv("results/processed/formal_checks.csv")
    zero_fail = read_csv("results/processed/v2_zero_fail_bug_inventory.csv")
    second_core = read_csv("results/processed/second_core_breadth.csv")
    second_core_irq = read_csv("results/processed/second_core_irq_candidate.csv")
    hazard3_irq_smoke = read_csv("results/processed/hazard3_irq_smoke.csv")
    hazard3_v2_replay = read_csv("results/processed/hazard3_v2_replay_smoke.csv")
    second_core_replay = read_csv("results/processed/second_core_replay_smokes.csv")
    second_core_v2 = read_csv("results/processed/second_core_v2_smokes.csv")
    second_core_profiles = sorted({row.get("capture_profile", "") for row in second_core_replay if row.get("capture_profile")})
    second_core_v2_configs = sorted({row.get("recorder_config", "") for row in second_core_v2 if row.get("status") == "PASS"})
    second_core_v2_benchmarks = sorted({row.get("benchmark", "") for row in second_core_v2 if row.get("status") == "PASS"})
    second_core_v2_seeds = sorted({row.get("seed", "") for row in second_core_v2 if row.get("status") == "PASS"})
    standalone_irq_rows = [
        row for row in standalone_self
        if row.get("status") == "PASS"
        and row.get("irq_after_command") == "1"
        and row.get("record_irq_entry_count") not in {"", "0", "NA", None}
        and row.get("record_irq_entry_count") == row.get("replay_irq_entry_count")
    ]

    fw_pass = count_rows(firmware, lambda r: r.get("build_status") == "PASS" and r.get("firmware_source") == "compiler_c")
    rtl_pass = count_rows(
        full_rtl,
        lambda r: r.get("rtl_record_status") == "PASS"
        and r.get("replay_status") == "PASS"
        and r.get("final_signature_match") == "PASS",
    )
    v2_pass = count_rows(
        full_rtl_v2,
        lambda r: r.get("rtl_record_status") == "PASS"
        and r.get("replay_status") == "PASS"
        and r.get("final_signature_match") == "PASS"
        and r.get("replay_consumer_status") == "PASS",
    )
    negative_reject = count_rows(negative, lambda r: r.get("expected_result") == "REJECT" and r.get("actual_result") == "REJECT")
    negative_unexpected = count_rows(
        negative,
        lambda r: r.get("expected_result") == "REJECT" and r.get("actual_result") not in {"REJECT", ""},
    )
    workload_pass = sum(int_float(row.get("pass_count")) for row in workload_v2)
    workload_total = sum(
        int_float(row.get("pass_count"))
        + int_float(row.get("fail_count"))
        + int_float(row.get("timeout_count"))
        + int_float(row.get("blocked_count"))
        for row in workload_v2
    )
    expanded_pass = count_rows(
        expanded,
        lambda r: r.get("rtl_record_status") == "PASS"
        and r.get("replay_status") == "PASS"
        and r.get("final_signature_match") == "PASS",
    )
    self_replay_pass = count_rows(
        self_replay,
        lambda r: r.get("self_replay_status") == "PASS"
        and r.get("replay_consumer_status") == "PASS"
        and r.get("replay_stimulus_source") == "rtl_replay_mode_controller_capture_store_mmio_irq",
    )
    standalone_self_pass = count_rows(standalone_self, lambda r: r.get("status") == "PASS")
    hdl_pass = count_rows(hdl, lambda r: r.get("status") == "PASS")
    formal_pass = count_rows(formal, lambda r: r.get("status") == "PASS")
    second_core_pass = count_rows(second_core, lambda r: r.get("status") == "PASS")
    second_core_info = count_rows(second_core, lambda r: r.get("status") == "INFO")
    second_core_irq_pass = count_rows(second_core_irq, lambda r: r.get("status") == "PASS")
    second_core_irq_info = count_rows(second_core_irq, lambda r: r.get("status") == "INFO")
    hazard3_irq_smoke_pass = count_rows(
        hazard3_irq_smoke,
        lambda r: r.get("status") == "PASS"
        and r.get("request_writes") == "1"
        and r.get("isr_writes") == "1"
        and r.get("ack_writes") == "1"
        and r.get("done_value") == "1"
        and r.get("irq_final") == "0",
    )
    hazard3_v2_replay_pass = count_rows(
        hazard3_v2_replay,
        lambda r: r.get("status") == "PASS"
        and r.get("property") == r.get("expected_property", r.get("property"))
        and r.get("words") == r.get("consumed")
        and r.get("signature_match") == "1"
        and r.get("changed_sensor") == "PASS"
        and int_float(r.get("record_irq_entries")) > 0
        and int_float(r.get("replay_irq_entries")) > 0
        and int_float(r.get("record_mmio_reads")) > 0
        and int_float(r.get("replay_mmio_reads")) > 0
        and int_float(r.get("replay_mmio_drives")) > 0
        and int_float(r.get("replay_irq_drives")) > 0
        and r.get("external_irq_replay") == "0",
    )
    hazard3_v2_benchmarks = sorted({row.get("benchmark", "") for row in hazard3_v2_replay if row.get("benchmark")})
    hazard3_v2_configs = sorted({row.get("config", "") for row in hazard3_v2_replay if row.get("config")})
    hazard3_v2_seeds = sorted({row.get("seed", "") for row in hazard3_v2_replay if row.get("seed")})
    hazard3_v2_properties = sorted({row.get("property", "") for row in hazard3_v2_replay if row.get("property") not in {"", "NA"}})
    second_core_replay_pass = count_rows(second_core_replay, lambda r: r.get("status") == "PASS")
    second_core_v2_pass = count_rows(
        second_core_v2,
        lambda r: r.get("status") == "PASS" and r.get("signature_match") == "PASS" and r.get("changed_input") == "PASS",
    )

    mapped_claims = [
        f"{row.get('metric')} {row.get('percent_overhead')}%"
        for row in mapped_v2
        if row.get("recorder_config") == "minimal" and row.get("claim_allowed") == "yes"
    ]
    asic_area_pass = count_rows(asic_area, lambda r: r.get("status") == "PASS")
    asic_physical_pass = count_rows(asic_rows, lambda r: r.get("status") == "PASS")
    asic_area_claims = [
        f"{row.get('recorder_config')} {row.get('percent_overhead')}%"
        for row in asic_area_overhead
        if row.get("status") == "PASS" and row.get("metric") == "area_um2"
    ]
    asic_physical_area_claims = [
        f"{row.get('recorder_config')} {row.get('percent_overhead')}%"
        for row in asic_overhead
        if row.get("status") == "PASS" and row.get("metric") == "area_um2"
    ]
    asic_physical_power_claims = [
        f"{row.get('recorder_config')} {row.get('percent_overhead')}%"
        for row in asic_overhead
        if row.get("status") == "PASS" and row.get("metric") == "power_mw"
    ]
    asic_summary_row = asic_summary[0] if asic_summary else {}
    openroad_probe = next((row for row in asic_tool_probe if row.get("check") == "openroad_binary"), {})
    docker_probe = next((row for row in asic_tool_probe if row.get("check") == "docker_binary"), {})
    docker_image_probe = next((row for row in asic_tool_probe if row.get("check") == "openroad_orfs_docker_image"), {})
    wsl_probe = next((row for row in asic_tool_probe if row.get("check") == "wsl_status"), {})

    lines = [
        "## Evidence Status",
        "",
        "| Area | Current generated evidence |",
        "| --- | --- |",
        f"| Compiler firmware | `{fw_pass}/{len(firmware)}` compiler-backed rows PASS in `results/processed/firmware_build.csv` |",
        f"| Full RTL replay v1 | `{rtl_pass}/{len(full_rtl)}` rows PASS in `results/processed/full_rtl_replay.csv` |",
        f"| Full RTL replay v2 | `{v2_pass}/{len(full_rtl_v2)}` rows PASS with RTL-driven MMIO/IRQ replay-consumer checks in `results/processed/full_rtl_replay_v2.csv` |",
        f"| v2 self-replay handoff | `{self_replay_pass}/{len(self_replay)}` rows PASS from captured RTL store in `results/processed/self_replay_handoff_v2.csv` |",
        f"| Standalone self-replay smokes | `{standalone_self_pass}/{len(standalone_self)}` rows PASS through the reusable RTL self-replay SoC shell across base and expanded MMIO/interrupt/watchdog/profile2 families and 3 v2 recorder configs, including `{len(standalone_irq_rows)}` IRQ rows with matching nonzero PicoRV32 record/replay interrupt-handler entry counts, in `results/processed/standalone_self_replay_smokes.csv` |",
        f"| Negative replay | `{negative_reject}` replay-critical corruptions rejected; `{negative_unexpected}` unexpected accepts in `results/processed/full_rtl_replay_negative.csv` |",
        f"| v2 measured workload scaling | `{workload_pass}/{workload_total}` rows PASS from `results/processed/workload_scaling_v2_measured_summary.csv` |",
        f"| Expanded benchmark replay | `{expanded_pass}/{len(expanded)}` rows PASS in `results/processed/expanded_benchmark_replay_measured.csv` |",
        f"| v2 zero-fail inventory | `{len(zero_fail)}` open bug rows in `results/processed/v2_zero_fail_bug_inventory.csv` |",
        f"| HDL checks | `{hdl_pass}/{len(hdl)}` PASS in `results/processed/hdl_checks.csv` |",
        f"| Formal checks | `{formal_pass}/{len(formal)}` PASS in `results/processed/formal_checks.csv` |",
        f"| Second-core breadth | `{second_core_pass}` PASS checks and `{second_core_info}` scope-boundary row in `results/processed/second_core_breadth.csv`; `{second_core_replay_pass}/{len(second_core_replay)}` focused FemtoRV32 replay rows across `{len(second_core_profiles)}` v1 capture profiles in `results/processed/second_core_replay_smokes.csv`; `{second_core_v2_pass}/{len(second_core_v2)}` scoped seeded v2 MMIO replay-consumer rows across `{len(second_core_v2_benchmarks)}` benchmark families, `{len(second_core_v2_configs)}` recorder configs, and `{len(second_core_v2_seeds)}` seeds in `results/processed/second_core_v2_smokes.csv` |",
        f"| Interrupt-capable second-core candidate | `{second_core_irq_pass}` PASS checks and `{second_core_irq_info}` scope-boundary row in `results/processed/second_core_irq_candidate.csv`; Hazard3 is vendored/pinned with IRQ/CSR/MRET markers and Verilator frontend lint |",
        f"| Hazard3 true ISR smoke | `{hazard3_irq_smoke_pass}/{len(hazard3_irq_smoke)}` focused firmware row PASS in `results/processed/hazard3_irq_smoke.csv`; RV32I+Zicsr firmware takes a machine external interrupt, writes an ISR marker, acknowledges the IRQ, returns with `mret`, and writes done |",
        f"| Hazard3 v2 MMIO+IRQ replay benchmark matrix | `{hazard3_v2_replay_pass}/{len(hazard3_v2_replay)}` seeded rows PASS in `results/processed/hazard3_v2_replay_smoke.csv`; benchmarks={len(hazard3_v2_benchmarks)} configs={','.join(hazard3_v2_configs) if hazard3_v2_configs else 'NA'} seeds={len(hazard3_v2_seeds)} properties={','.join(hazard3_v2_properties) if hazard3_v2_properties else 'NA'}; ReplayCapsule wraps Hazard3, records MMIO plus true ISR marker/ack evidence, replays with host sensor/IRQ perturbed, and consumes the selected v2 recorder capsule stream |",
        f"| v2 selected mapped overhead | `{'; '.join(mapped_claims) if mapped_claims else 'no claim-allowed minimal rows found'}` in `results/processed/mapped_scaling_overhead_v2_measured.csv` |",
        f"| ASIC/open-PDK | `{asic_summary_row.get('status', 'MISSING')}`; `{asic_physical_pass}/{len(asic_rows)}` OpenROAD placed/global-routed Nangate45 rows PASS with area/timing/power; `{asic_area_pass}/{len(asic_area)}` Yosys+ABC synthesis-only rows PASS; OpenROAD probe `{openroad_probe.get('status', 'MISSING')}`; local Docker `{docker_probe.get('status', 'MISSING')}`; OpenROAD Docker image `{docker_image_probe.get('status', 'MISSING')}`; WSL probe `{wsl_probe.get('status', 'MISSING')}`; physical area overheads: `{'; '.join(asic_physical_area_claims) if asic_physical_area_claims else 'NA'}`; physical power overheads: `{'; '.join(asic_physical_power_claims) if asic_physical_power_claims else 'NA'}`; synthesis-only area overheads: `{'; '.join(asic_area_claims) if asic_area_claims else 'NA'}` |",
        "",
    ]
    return lines


def section_paper_artifacts() -> list[str]:
    paper_status = read_csv("results/processed/paper_build_status.csv")
    aspdac = read_csv("results/processed/aspdac_submission_audit.csv")
    number_audit = read_csv("results/processed/paper_number_audit.csv")
    private_scan = read_csv("results/processed/private_marker_scan.csv")
    dist_files = sorted(p.name for p in (REPO_ROOT / "dist").glob("*") if p.is_file())

    aspdac_checks = {row.get("check", ""): row for row in aspdac}
    pdf_pages = aspdac_checks.get("pdf_total_pages", {}).get("detail", "NA")
    body_pages = aspdac_checks.get("body_page_limit", {}).get("detail", "NA")
    references = aspdac_checks.get("reference_start_page", {}).get("detail", "NA")
    paper_pass = any(row.get("status") == "PASS" for row in paper_status)
    number_pass = any(row.get("status") == "PASS" for row in number_audit)
    private_pass = any(row.get("status") == "PASS" for row in private_scan)

    return [
        "## Paper And Artifacts",
        "",
        f"- Paper build: `{'PASS' if paper_pass else 'not passing or not generated'}` from `results/processed/paper_build_status.csv`.",
        f"- ASP-DAC page audit: `{pdf_pages}`; `{body_pages}`; `{references}`.",
        f"- Numeric claim audit: `{'PASS' if number_pass else 'check results/processed/paper_number_audit.csv'}`.",
        f"- Private marker scan: `{'PASS' if private_pass else 'check results/processed/private_marker_scan.csv'}`.",
        f"- Dist artifacts: {inline_list(dist_files)}",
        "",
    ]


def section_claim_boundaries() -> list[str]:
    return [
        "## Current Claim Boundaries",
        "",
        "Allowed claims:",
        "",
        "- Event-sufficient capsules for scoped single-hart RV32I interrupt/MMIO failures.",
        "- Compiler-backed full RTL record/replay rows for the generated benchmark suite.",
        "- v2 hardware-driven full-core replay-consume checks for measured v2 replay rows.",
        "- v2 RTL capture-store primitive that retains replay-critical capsule words across reset, with HDL and record-signature evidence.",
        "- v2 replay-mode controller primitive that arms the captured store and starts controller-driven same-instance replay without harness-preloaded capsule words.",
        "- v2 same-instance self-replay handoff rows that replay from the captured RTL store without Verilator preloading saved capsule words.",
        "- Reusable v2 RTL self-replay SoC shell plus a focused Icarus standalone self-replay matrix that records, resets, launches captured-store replay, checks captured/source-sent/consumer-consumed handoff for base and expanded MMIO/interrupt/watchdog/profile2 failures, and requires nonzero matching PicoRV32 interrupt-handler entry counts on IRQ-triggered rows.",
        "- Expanded compiler-backed benchmark families, including two alternate-MMIO-profile families, when `expanded_benchmark_replay_measured.csv` is current.",
        "- Corrupted-capsule rejection for replay-critical corruption classes.",
        "- Second open-source RV32I core wrapper/replay-smoke breadth only: FemtoRV32 Quark is vendored, wrapped with ReplayCapsule, linted, generically synthesized, has one compiler-backed capture smoke, has a reusable v1 RTL packet checker for 168-bit capsules, has a scoped v1 MMIO replay driver for replay reads, has focused capsule-derived replay smoke rows over base and expanded benchmark families across v1 capture profiles, including wrapper-level IRQ-boundary and profile2-MMIO evidence, and has scoped seeded v2 MMIO replay-consumer benchmark/config rows that perturb replay-side host MMIO inputs while reproducing the property signature.",
        "- Hazard3 is vendored as a pinned interrupt-capable second-core candidate with Apache-2.0 license metadata, external/software/timer IRQ ports, machine CSR/MRET support markers, Verilator frontend lint, a focused RV32I+Zicsr firmware smoke that takes a machine external interrupt and returns with `mret`, and a seeded v2 ReplayCapsule MMIO+IRQ replay-consumer benchmark matrix across multiple Hazard3 firmware workload families and core/hashed recorder configs.",
        "- Nangate45 OpenROAD placed/global-routed ASIC/open-PDK area, timing, and power rows, explicitly not detailed-route signoff, tapeout, silicon, or energy.",
        "- Same-target ECP5 mapped overhead for the selected v2 minimal recorder profile, with diagnostic core/hashed rows kept separate.",
        "- Reproducible paper/artifact evidence when the generated CSVs and package files are present.",
        "",
        "Do not claim yet:",
        "",
        "- Standalone board/silicon replay flow independent of testbench reset orchestration and the focused reusable memory/MMIO/IRQ/watchdog shell.",
        "- Detailed-route ASIC signoff, tapeout, silicon, or energy.",
        "- True CPU interrupt/ISR replay on FemtoRV32; full v2 MMIO+IRQ replay-consumer stimulus on FemtoRV32; multicore, DMA, cache/coherence, broad platform, or arbitrary peripheral support.",
        "- Hazard3 full-diagnostic `full` recorder-config replay with all-commit IRQ lookahead.",
        "- Do not claim replacement for RISC-V trace/debug standards.",
        "- Do not claim global minimal trace, universal deterministic replay, or first-ever hardware replay.",
        "- Area-optimized overhead claims for diagnostic-rich configurations.",
        "",
    ]


def section_autonomous_replay_status() -> list[str]:
    wrapper = read_text("rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv")
    hazard3_wrapper = read_text("rtl/rv32i_integration/hazard3_replaycapsule_v2_wrapper.sv")
    harness = read_text("tb/verilator/rtl_harness.cpp")
    source = read_text("rtl/replaycapsule_v2/rcv2_capsule_source.sv")
    controller = read_text("rtl/replaycapsule_v2/rcv2_replay_mode_controller.sv")
    standalone_shell = read_text("rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv")
    standalone_soc_shell = read_text("rtl/rv32i_integration/replaycapsule_v2_self_replay_soc.sv")
    full_rtl_v2 = read_csv("results/processed/full_rtl_replay_v2.csv")
    self_replay = read_csv("results/processed/self_replay_handoff_v2.csv")
    standalone_self = read_csv("results/processed/standalone_self_replay_smokes.csv")
    hazard3_v2_replay = read_csv("results/processed/hazard3_v2_replay_smoke.csv")
    hdl = read_csv("results/processed/hdl_checks.csv")
    consumer_exists = (REPO_ROOT / "rtl/replaycapsule_v2/rcv2_replay_consumer.sv").exists()
    source_exists = (REPO_ROOT / "rtl/replaycapsule_v2/rcv2_capsule_source.sv").exists()
    controller_exists = (REPO_ROOT / "rtl/replaycapsule_v2/rcv2_replay_mode_controller.sv").exists()
    standalone_shell_exists = (REPO_ROOT / "rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv").exists()
    standalone_soc_shell_exists = (REPO_ROOT / "rtl/rv32i_integration/replaycapsule_v2_self_replay_soc.sv").exists()
    consumer_wired = "u_rcv2_replay_consumer" in wrapper
    core_replay_mem = ".mem_rdata(core_mem_rdata)" in wrapper and "replay_consume_mmio_value" in wrapper
    core_replay_irq = ".irq(core_irq)" in wrapper and "replay_consume_irq_valid" in wrapper
    hazard3_consumer_wired = "u_rcv2_replay_consumer" in hazard3_wrapper
    hazard3_replay_mem = "replay_consume_mmio_value" in hazard3_wrapper and "core_hrdata" in hazard3_wrapper
    hazard3_replay_irq = ".irq(replay_drive_active ? replay_irq_level : |irq)" in hazard3_wrapper and "replay_consume_irq_valid" in hazard3_wrapper
    source_capture = "capture_enable" in source and "captured_count" in source and "capture_overflow" in source
    controller_controls = (
        "source_store_clear" in controller
        and "source_capture_enable" in controller
        and "consume_start" in controller
        and "consume_expected_count" in controller
    )
    source_capture_test = next((row for row in hdl if row.get("check") == "tb_rcv2_capsule_source"), {})
    controller_test = next((row for row in hdl if row.get("check") == "tb_rcv2_replay_mode_controller"), {})
    standalone_smoke = next((row for row in hdl if row.get("check") == "tb_picorv32_standalone_self_replay_smoke"), {})
    standalone_lint = next((row for row in hdl if row.get("check") == "verilator_lint_replaycapsule_v2_self_replay_top"), {})
    standalone_soc_lint = next((row for row in hdl if row.get("check") == "verilator_lint_replaycapsule_v2_self_replay_soc"), {})
    harness_mmio = "replay_mmio_value" in harness
    harness_irq = "irq_from_capsule" in harness
    record_sigs = sorted((REPO_ROOT / "results/raw/rtl_signatures_v2").glob("*_record.json"))
    record_capture_sigs = 0
    for path in record_sigs:
        try:
            if "rtl capture store retained" in path.read_text(encoding="utf-8", errors="replace"):
                record_capture_sigs += 1
        except OSError:
            pass
    stimulus_rows = [
        row for row in full_rtl_v2
        if row.get("replay_status") == "PASS"
        and row.get("replay_consumer_checked") == "true"
        and row.get("replay_consumer_status") == "PASS"
        and row.get("replay_consumer_consumed") == row.get("replay_consumer_expected")
        and row.get("replay_stimulus_source") == "rtl_capsule_source_mmio_irq"
    ]
    configs = sorted({row.get("recorder_config", "") for row in stimulus_rows})
    self_replay_rows = [
        row for row in self_replay
        if row.get("self_replay_status") == "PASS"
        and row.get("replay_consumer_status") == "PASS"
        and row.get("replay_stimulus_source") == "rtl_replay_mode_controller_capture_store_mmio_irq"
    ]
    self_configs = sorted({row.get("recorder_config", "") for row in self_replay_rows})
    self_benchmarks = sorted({row.get("benchmark", "") for row in self_replay_rows})
    standalone_self_rows = [row for row in standalone_self if row.get("status") == "PASS"]
    standalone_self_configs = sorted({row.get("recorder_config", "") for row in standalone_self_rows})
    standalone_self_benchmarks = sorted({row.get("benchmark", "") for row in standalone_self_rows})
    standalone_shell_clean = [
        row for row in standalone_self_rows
        if row.get("shell") == "rtl_self_replay_soc"
        and row.get("captured_count") not in {"", "NA"}
        and row.get("captured_count") == row.get("source_sent_count")
        and row.get("captured_count") == row.get("consumed_count")
        and row.get("controller_done") == "1"
    ]
    standalone_irq_rows = [
        row for row in standalone_self_rows
        if row.get("irq_after_command") == "1"
        and row.get("record_irq_entry_count") not in {"", "0", "NA", None}
        and row.get("record_irq_entry_count") == row.get("replay_irq_entry_count")
    ]
    hazard3_v2_rows = [
        row for row in hazard3_v2_replay
        if row.get("status") == "PASS"
        and row.get("property") == row.get("expected_property", row.get("property"))
        and row.get("words") == row.get("consumed")
        and row.get("signature_match") == "1"
        and row.get("changed_sensor") == "PASS"
        and row.get("external_irq_replay") == "0"
    ]
    hazard3_v2_row_benchmarks = sorted({row.get("benchmark", "") for row in hazard3_v2_rows if row.get("benchmark")})
    hazard3_v2_row_configs = sorted({row.get("config", "") for row in hazard3_v2_rows if row.get("config")})
    hazard3_v2_row_seeds = sorted({row.get("seed", "") for row in hazard3_v2_rows if row.get("seed")})

    lines = [
        "## Autonomous Replay Status",
        "",
        "| Item | Status | Evidence |",
        "| --- | --- | --- |",
        f"| v2 RTL replay consumer exists | `{yes_no(consumer_exists)}` | `rtl/replaycapsule_v2/rcv2_replay_consumer.sv` |",
        f"| v2 RTL capsule source exists | `{yes_no(source_exists)}` | `rtl/replaycapsule_v2/rcv2_capsule_source.sv` |",
        f"| v2 RTL replay-mode controller exists | `{yes_no(controller_exists)}` | `rtl/replaycapsule_v2/rcv2_replay_mode_controller.sv` |",
        f"| Reusable v2 self-replay RTL shell exists | `{yes_no(standalone_shell_exists and 'u_replay_mode_controller' in standalone_shell and 'u_replay_source' in standalone_shell)}` | `rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv` |",
        f"| Reusable v2 self-replay SoC shell exists | `{yes_no(standalone_soc_shell_exists and 'replaycapsule_v2_self_replay_top' in standalone_soc_shell and 'imem' in standalone_soc_shell and 'irq_pulse_remaining' in standalone_soc_shell)}` | `rtl/rv32i_integration/replaycapsule_v2_self_replay_soc.sv` |",
        f"| Replay-mode controller sequences source/consumer handoff | `{yes_no(controller_controls)}` | controller drives store clear, capture enable, source select, start, and expected count |",
        f"| Replay-mode controller HDL test | `{controller_test.get('status', 'NA')}` | `tb_rcv2_replay_mode_controller` in `results/processed/hdl_checks.csv` |",
        f"| Standalone self-replay shell lint | `{standalone_lint.get('status', 'NA')}` | `verilator_lint_replaycapsule_v2_self_replay_top` in `results/processed/hdl_checks.csv` |",
        f"| Standalone self-replay SoC shell lint | `{standalone_soc_lint.get('status', 'NA')}` | `verilator_lint_replaycapsule_v2_self_replay_soc` in `results/processed/hdl_checks.csv` |",
        f"| Focused non-Verilator self-replay smoke | `{standalone_smoke.get('status', 'NA')}` | `tb_picorv32_standalone_self_replay_smoke` in `results/processed/hdl_checks.csv` |",
        f"| Focused standalone self-replay matrix | `{len(standalone_self_rows)}/{len(standalone_self) if standalone_self else 0}` | `results/processed/standalone_self_replay_smokes.csv`; shell-clean={len(standalone_shell_clean)}/{len(standalone_self_rows)} irq-entry-clean={len(standalone_irq_rows)} benchmarks={len(standalone_self_benchmarks)} configs={','.join(standalone_self_configs) if standalone_self_configs else 'NA'} |",
        f"| RTL source captures replay-critical words | `{yes_no(source_capture)}` | source contains capture-store controls and counters |",
        f"| Capture store retains across reset | `{source_capture_test.get('status', 'NA')}` | `tb_rcv2_capsule_source` in `results/processed/hdl_checks.csv` |",
        f"| v2 record signatures exercise capture store | `{record_capture_sigs}/{len(record_sigs) if record_sigs else 0}` | `results/raw/rtl_signatures_v2/*_record.json` notes |",
        f"| Consumer wired into PicoRV32 wrapper | `{yes_no(consumer_wired)}` | `rtl/rv32i_integration/picorv32_replaycapsule_wrapper.sv` |",
        f"| Replay consumer drives core-facing MMIO read data | `{yes_no(core_replay_mem)}` | wrapper contains `.mem_rdata(core_mem_rdata)` and `replay_consume_mmio_value` |",
        f"| Replay consumer drives core-facing IRQ input | `{yes_no(core_replay_irq)}` | wrapper contains `.irq(core_irq)` and `replay_consume_irq_valid` |",
        f"| Hazard3 v2 wrapper wires replay consumer | `{yes_no(hazard3_consumer_wired)}` | `rtl/rv32i_integration/hazard3_replaycapsule_v2_wrapper.sv` |",
        f"| Hazard3 replay consumer drives core-facing MMIO/IRQ | `{yes_no(hazard3_replay_mem and hazard3_replay_irq)}` | wrapper drives `core_hrdata` and registered Hazard3 IRQ level from replay-consumer outputs |",
        f"| Harness still injects replay MMIO values | `{yes_no(harness_mmio)}` | `tb/verilator/rtl_harness.cpp` contains `replay_mmio_value` |",
        f"| Harness still injects replay IRQ timing | `{yes_no(harness_irq)}` | `tb/verilator/rtl_harness.cpp` contains `irq_from_capsule` |",
        f"| v2 full RTL rows use RTL MMIO/IRQ replay stimulus | `{len(stimulus_rows)}/{len(full_rtl_v2) if full_rtl_v2 else 0}` | `results/processed/full_rtl_replay_v2.csv`; configs={','.join(configs) if configs else 'NA'} |",
        f"| v2 self-replay uses replay-mode controller and captured RTL store without preload | `{len(self_replay_rows)}/{len(self_replay) if self_replay else 0}` | `results/processed/self_replay_handoff_v2.csv`; configs={','.join(self_configs) if self_configs else 'NA'} benchmarks={len(self_benchmarks)} |",
        f"| Hazard3 v2 MMIO+IRQ replay benchmark matrix | `{len(hazard3_v2_rows)}/{len(hazard3_v2_replay) if hazard3_v2_replay else 0}` | `results/processed/hazard3_v2_replay_smoke.csv`; benchmarks={len(hazard3_v2_row_benchmarks)} configs={','.join(hazard3_v2_row_configs) if hazard3_v2_row_configs else 'NA'} seeds={len(hazard3_v2_row_seeds)} with host IRQ low during replay |",
        "",
    ]

    if (
        consumer_exists
        and consumer_wired
        and core_replay_mem
        and core_replay_irq
        and not harness_mmio
        and not harness_irq
        and full_rtl_v2
        and len(stimulus_rows) == len(full_rtl_v2)
    ):
        lines.extend(
            [
                "Current interpretation: **v2 full-core replay is hardware-driven for MMIO/IRQ replay stimulus in the Verilator evidence path**.",
                "",
                "Additional progress: **the RTL source now has a capture-store path that retains replay-critical capsule words across reset, an RTL replay-mode controller now arms the store and starts captured-store self-replay without Verilator preloading saved capsule words, a reusable RTL self-replay SoC shell now has a focused Icarus standalone matrix covering base and expanded MMIO, interrupt, watchdog, and profile2 failures with captured/source-sent/consumer-consumed count agreement plus matching nonzero PicoRV32 interrupt-handler entry counts on IRQ rows, and Hazard3 now has a seeded v2 MMIO+IRQ replay-consumer matrix with host-side replay IRQ held low.**",
                "",
                "Remaining boundary: the broad replay matrix still uses Verilator orchestration, and the standalone evidence is a focused reusable memory/MMIO/IRQ/watchdog shell rather than a board/silicon replay flow.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Current interpretation: check this section carefully; the static markers no longer match the prior host-driven integration pattern.",
                "",
            ]
        )
    return lines


def section_next_priorities() -> list[str]:
    return [
        "## Highest-Leverage Next Priorities",
        "",
        "1. 80%-level submission package: closed for the scoped ASP-DAC attempt. ASIC/OpenROAD physical rows, Hazard3 matrix rows, autonomous/captured-store replay wording, artifact packages, and audits are synchronized. Keep future edits claim-disciplined and rerun the audits.",
        "2. Optional above-80 standalone replay: broad board/peripheral integration beyond the focused reusable memory/MMIO/IRQ/watchdog/profile2 shell remains future work only if the paper wants a standalone board/silicon replay claim.",
        "3. Optional above-80 second-core breadth: full-diagnostic all-commit Hazard3 replay remains future work only if the paper wants to claim that specific stronger config.",
        "4. Optional above-80 ASIC strengthening: detailed-route signoff, tapeout, silicon, and energy remain future work only if the paper wants claims beyond the current global-route physical evidence.",
        "",
    ]


def section_file_map() -> list[str]:
    return [
        "## File Map For Future Chats",
        "",
        "- Start here: `docs/CHAT_CONTEXT.md`.",
        "- Project summary: `README.md`.",
        "- Current submission readiness: `docs/conference_readiness_dashboard.md`, `docs/final_reviewer_report.md`, `docs/main_track_submission_review.md`.",
        "- Novelty/scope guardrails: `docs/novelty_audit.md`, `docs/novelty_matrix.md`, `docs/limitations.md`, `docs/related_work_positioning.md`.",
        "- Hardware architecture: `docs/architecture.md`, `docs/core_integration.md`, `rtl/`, `rtl/replaycapsule_v2/`, `rtl/rv32i_integration/`.",
        "- Second-core breadth: `docs/second_core_breadth.md`, `docs/second_core_replay_smokes.md`, `docs/second_core_v2_smokes.md`, `docs/second_core_irq_candidate.md`, `docs/hazard3_irq_smoke.md`, `docs/hazard3_v2_replay_smoke.md`, `results/processed/second_core_breadth.csv`, `results/processed/second_core_replay_smokes.csv`, `results/processed/second_core_v2_smokes.csv`, `results/processed/second_core_irq_candidate.csv`, `results/processed/hazard3_irq_smoke.csv`, `results/processed/hazard3_v2_replay_smoke.csv`, `firmware/hazard3_irq_smoke/`, `firmware/hazard3_replay_smoke/`, `tb/system/tb_hazard3_irq_smoke.v`, `tb/system/tb_hazard3_v2_replay_smoke.sv`, `scripts/run_hazard3_irq_smoke.py`, `scripts/run_hazard3_v2_replay_smoke.py`, `rtl/rv32i_integration/hazard3_replaycapsule_v2_wrapper.sv`, `rtl/rv32i_integration/femtorv32_replaycapsule_v2_wrapper.sv`, `tb/system/tb_femtorv32_v2_replay_smoke.sv`, `third_party/femtorv32/`, and `third_party/hazard3/`.",
        "- Standalone self-replay matrix: `docs/standalone_self_replay_smokes.md`, `results/processed/standalone_self_replay_smokes.csv`, `rtl/rv32i_integration/replaycapsule_v2_self_replay_top.sv`, and `rtl/rv32i_integration/replaycapsule_v2_self_replay_soc.sv`.",
        "- ASIC/open-PDK: `docs/asic_openpdk_evidence.md`, `docs/asic_physical_tool_probe.md`, `results/processed/asic_openpdk.csv`, `results/processed/asic_openpdk_overhead.csv`, `results/processed/asic_openpdk_yosys_area.csv`, `results/processed/asic_openpdk_yosys_area_overhead.csv`, `results/processed/asic_openpdk_summary.csv`, `results/processed/asic_physical_tool_probe.csv`, `results/raw/asic_openpdk/`, `scripts/run_asic_openroad_docker.ps1`, `scripts/materialize_nangate45_from_orfs.py`, and `.github/workflows/asic-openroad.yml`.",
        "- Replay evidence: `results/processed/full_rtl_replay.csv`, `results/processed/full_rtl_replay_v2.csv`, `results/processed/full_rtl_replay_negative.csv`.",
        "- v2 measured evidence: `docs/v2_zero_fail_status.md`, `results/processed/*_v2_measured*.csv`.",
        "- Paper source: `paper/main.tex`, `paper/sections/`, `paper/main.pdf`.",
        "- Build and audit entry points: `Makefile`, especially `make topconf-v2-measured`, `make paper-audit`, and `make chat-context`.",
        "",
    ]


def section_update_rules() -> list[str]:
    return [
        "## Update Rules",
        "",
        "- Run `make chat-context` after adding/removing RTL, firmware, scripts, paper sections, generated evidence, or artifacts.",
        f"- If `python` or `python3` resolves to the Windows Store alias, run `make PYTHON=\"{sys.executable.replace(os.sep, '/')}\" chat-context`.",
        "- Future chats should read this file first and refresh it if it looks stale relative to `git status` or recent work.",
        "- This file is generated, so do not manually edit it for lasting changes. Edit `scripts/update_chat_context.py`, rerun the updater, and commit both files if using git.",
        "",
    ]


def directory_inventory() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for child in sorted(REPO_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if child.name in {".git", ".tools"}:
            rows.append({"path": child.name, "files": 0, "bytes": 0, "notes": "skipped local metadata/toolchain"})
            continue
        if child.is_file():
            rows.append({"path": child.name, "files": 1, "bytes": child.stat().st_size, "notes": "top-level file"})
            continue
        if not child.is_dir():
            continue
        files = 0
        total = 0
        for root, dirs, filenames in os.walk(child):
            dirs[:] = [d for d in dirs if d not in SKIP_WALK_DIRS]
            for filename in filenames:
                path = Path(root) / filename
                try:
                    total += path.stat().st_size
                    files += 1
                except OSError:
                    pass
        rows.append({"path": child.name, "files": files, "bytes": total, "notes": inventory_note(child.name)})
    return rows


def inventory_note(name: str) -> str:
    notes = {
        ".devcontainer": "development container config",
        ".github": "CI workflows",
        "build": "generated build outputs",
        "constraints": "FPGA constraints",
        "dist": "artifact zip packages",
        "docs": "design, review, and readiness docs",
        "firmware": "firmware benchmarks and build outputs",
        "formal": "formal assumptions/proof scripts",
        "paper": "paper source, figures, tables, PDF",
        "results": "raw and processed evidence",
        "rtl": "hardware design source",
        "scripts": "reproduction, analysis, audit, packaging scripts",
        "tb": "testbenches and Verilator harnesses",
        "third_party": "vendored dependencies",
    }
    return notes.get(name, "")


def read_csv(rel_path: str) -> list[dict[str, str]]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return []
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except UnicodeDecodeError:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))


def read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def count_rows(rows: list[dict[str, str]], predicate) -> int:
    return sum(1 for row in rows if predicate(row))


def int_float(value: object) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return 0


def inline_list(items: list[str]) -> str:
    clean = [item for item in items if item]
    if not clean:
        return "`none found`"
    if len(clean) <= 12:
        return ", ".join(f"`{item}`" for item in clean)
    head = ", ".join(f"`{item}`" for item in clean[:12])
    return f"{head}, ... `{len(clean) - 12}` more"


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{size} B"


def git_text(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
