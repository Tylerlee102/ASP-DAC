#!/usr/bin/env python3
"""Audit ASP-DAC 2027 review-submission formatting constraints."""

from __future__ import annotations

import csv
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUT_CSV = REPO_ROOT / "results/processed/aspdac_submission_audit.csv"

FIELDNAMES = ["check", "status", "file", "detail", "source"]

ASPDAC_PAPER_GUIDE = "https://www.aspdac.com/aspdac2027/author/technical_paper/"
ASPDAC_CFP = "https://www.aspdac.com/aspdac2027/cfp/"


def main() -> int:
    rows: list[dict[str, str]] = []
    main_tex = PAPER_DIR / "main.tex"
    text = main_tex.read_text(encoding="utf-8") if main_tex.exists() else ""

    rows.append(_source_check(
        "acm_primary_template",
        "\\documentclass" in text and "acmart" in _documentclass_line(text) and "sigconf" in _documentclass_line(text),
        "paper/main.tex",
        "initial manuscript must use the ACM Primary Article Template, sample-sigconf/acmart format",
        ASPDAC_PAPER_GUIDE,
    ))
    rows.append(_source_check(
        "not_ieee_format",
        "IEEEtran" not in text and "IEEEauthorblock" not in text,
        "paper/main.tex",
        "ASP-DAC 2027 requires ACM format, not IEEEtran",
        ASPDAC_PAPER_GUIDE,
    ))
    rows.append(_source_check(
        "anonymous_review_mode",
        "anonymous" in _documentclass_line(text),
        "paper/main.tex",
        "initial manuscripts must be double-blind and omit author-identifying information",
        ASPDAC_PAPER_GUIDE,
    ))
    rows.append(_source_check(
        "abstract_before_maketitle",
        _index(text, "\\input{sections/abstract}") < _index(text, "\\maketitle"),
        "paper/main.tex",
        "acmart expects the abstract before maketitle",
        "ACM Primary Article Template",
    ))
    rows.append(_source_check(
        "acm_bibliography_style",
        "\\bibliographystyle{ACM-Reference-Format}" in text,
        "paper/main.tex",
        "bibliography should use ACM reference formatting for ACM proceedings",
        "ACM Primary Article Template",
    ))
    rows.append(_source_check(
        "references_flushed_after_content",
        "\\clearpage" in text and "\\label{aspdac:references-start}" in text,
        "paper/main.tex",
        "all figures and tables must count in the six-page body before references",
        ASPDAC_CFP,
    ))
    rows.extend(_private_marker_rows())
    rows.extend(_build_artifact_rows(text))
    rows.extend(_v2_evidence_rows())

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    failures = [row for row in rows if row["status"] == "FAIL"]
    print(f"WROTE {OUT_CSV}; FAIL rows={len(failures)}")
    return 1 if failures else 0


def _build_artifact_rows(main_tex: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pdf = PAPER_DIR / "main.pdf"
    log = PAPER_DIR / "main.log"
    aux = PAPER_DIR / "main.aux"

    newest_source = _newest_source_mtime()
    pdf_fresh = pdf.exists() and pdf.stat().st_mtime >= newest_source
    rows.append(_row(
        "fresh_pdf",
        "PASS" if pdf_fresh else "FAIL",
        "paper/main.pdf",
        "PDF must be rebuilt after the latest LaTeX source/table/reference change",
        ASPDAC_PAPER_GUIDE,
    ))
    if not pdf_fresh:
        return rows

    total_pages = _pages_from_log(log)
    if total_pages is None:
        total_pages = _pages_from_pdf_bytes(pdf)
    rows.append(_row(
        "pdf_total_pages",
        "PASS" if total_pages is not None and total_pages <= 7 else "FAIL",
        "paper/main.pdf",
        f"total_pages={total_pages}; ASP-DAC permits six body pages plus one reference page",
        ASPDAC_CFP,
    ))

    reference_page = _reference_start_page(aux)
    rows.append(_row(
        "reference_start_page",
        "PASS" if reference_page is not None else "FAIL",
        "paper/main.aux",
        f"reference_start_page={reference_page}; expected label aspdac:references-start",
        ASPDAC_CFP,
    ))
    if reference_page is not None:
        content_pages = reference_page - 1
        rows.append(_row(
            "body_page_limit",
            "PASS" if content_pages <= 6 else "FAIL",
            "paper/main.pdf",
            f"body_pages_before_references={content_pages}; limit is 6 including figures and tables",
            ASPDAC_CFP,
        ))

    return rows


def _private_marker_rows() -> list[dict[str, str]]:
    forbidden = (
        "C:" + "\\Users\\",
        "One" + "Drive",
        "ty" + "boy",
        "github.com/" + "ty" + "boy",
    )
    rows: list[dict[str, str]] = []
    for path in [PAPER_DIR / "main.tex", *sorted((PAPER_DIR / "sections").glob("*.tex")), PAPER_DIR / "references.bib"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = [marker for marker in forbidden if marker.lower() in text.lower()]
        rows.append(_row(
            "private_marker_scan",
            "FAIL" if matches else "PASS",
            path.relative_to(REPO_ROOT).as_posix(),
            "private/local identity marker(s): " + ", ".join(matches) if matches else "no private/local identity markers",
            ASPDAC_PAPER_GUIDE,
        ))
    return rows


def _v2_evidence_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    full_rtl_v2 = _read_csv(REPO_ROOT / "results/processed/full_rtl_replay_v2.csv")
    if full_rtl_v2:
        checked = [
            row for row in full_rtl_v2
            if row.get("replay_status") == "PASS"
            and row.get("replay_consumer_checked") == "true"
            and row.get("replay_consumer_status") == "PASS"
            and row.get("replay_consumer_consumed") == row.get("replay_consumer_expected")
            and row.get("replay_stimulus_source") == "rtl_capsule_source_mmio_irq"
        ]
        configs = {row.get("recorder_config") for row in checked}
        rows.append(_row(
            "v2_full_rtl_replay_consumer_checked",
            "PASS" if len(checked) == len(full_rtl_v2) and {"core", "hashed", "full"} <= configs else "FAIL",
            "results/processed/full_rtl_replay_v2.csv",
            f"consumer_checked_pass={len(checked)}/{len(full_rtl_v2)} configs={','.join(sorted(configs))} stimulus=rtl_capsule_source_mmio_irq",
            "repository evidence gate",
        ))

    depth8 = _read_csv(REPO_ROOT / "results/processed/full_rtl_replay_v2_depth8_probe.csv")
    if depth8:
        bad_depth8 = [
            row for row in depth8
            if row.get("replay_status") != "PASS"
            or row.get("replay_consumer_status") != "PASS"
            or row.get("overflowed") == "true"
        ]
        configs = {row.get("recorder_config") for row in depth8 if row.get("replay_status") == "PASS"}
        rows.append(_row(
            "v2_depth8_core_hashed_probe_clean",
            "PASS" if not bad_depth8 and {"core", "hashed"} <= configs else "FAIL",
            "results/processed/full_rtl_replay_v2_depth8_probe.csv",
            f"rows={len(depth8)} bad_rows={len(bad_depth8)} configs={','.join(sorted(configs))}",
            "repository evidence gate",
        ))

    measured = _read_csv(REPO_ROOT / "results/processed/workload_scaling_v2_measured_summary.csv")
    if measured:
        total = sum(_int(row.get("n")) for row in measured if row.get("architecture") == "v2")
        passes = sum(_int(row.get("pass_count")) for row in measured if row.get("architecture") == "v2")
        blocked = sum(_int(row.get("blocked_count")) for row in measured if row.get("architecture") == "v2")
        rows.append(_row(
            "v2_measured_workload_zero_fail",
            "PASS" if total > 0 and passes == total and blocked == 0 else "FAIL",
            "results/processed/workload_scaling_v2_measured_summary.csv",
            f"pass_rows={passes}; total_rows={total}; blocked_rows={blocked}",
            "repository evidence gate",
        ))

    expanded = _read_csv(REPO_ROOT / "results/processed/expanded_benchmark_replay_measured.csv")
    if expanded:
        bad = [
            row for row in expanded
            if row.get("replay_status") != "PASS"
            or row.get("rtl_record_status") != "PASS"
            or row.get("capsule_export_status") != "PASS"
            or row.get("compiler_backed") != "true"
            or row.get("replay_consumer_status") != "PASS"
        ]
        configs = {row.get("recorder_config") for row in expanded}
        benchmarks = {row.get("benchmark") for row in expanded}
        seeds = {row.get("seed") for row in expanded}
        rows.append(_row(
            "expanded_benchmark_replay_clean",
            "PASS" if not bad and len(expanded) >= 144 and {"core", "hashed", "full"} <= configs and len(benchmarks) >= 8 and len(seeds) >= 3 else "FAIL",
            "results/processed/expanded_benchmark_replay_measured.csv",
            f"rows={len(expanded)} bad_rows={len(bad)} benchmarks={len(benchmarks)} configs={','.join(sorted(configs))} seeds={','.join(sorted(seeds))}",
            "repository evidence gate",
        ))

    self_replay = _read_csv(REPO_ROOT / "results/processed/self_replay_handoff_v2.csv")
    if self_replay:
        bad = [
            row for row in self_replay
            if row.get("self_replay_status") != "PASS"
            or row.get("compiler_backed") != "true"
            or row.get("capsule_export_status") != "PASS"
            or row.get("event_match") != "PASS"
            or row.get("replay_consumer_status") != "PASS"
            or row.get("replay_stimulus_source") != "rtl_replay_mode_controller_capture_store_mmio_irq"
        ]
        configs = {row.get("recorder_config") for row in self_replay}
        benchmarks = {row.get("benchmark") for row in self_replay}
        seeds = {row.get("seed") for row in self_replay}
        rows.append(_row(
            "v2_self_replay_handoff_clean",
            "PASS" if not bad and len(self_replay) >= 243 and {"core", "hashed", "full"} <= configs and len(benchmarks) >= 12 and len(seeds) >= 3 else "FAIL",
            "results/processed/self_replay_handoff_v2.csv",
            f"rows={len(self_replay)} bad_rows={len(bad)} benchmarks={len(benchmarks)} configs={','.join(sorted(configs))} seeds={','.join(sorted(seeds))} stimulus=rtl_replay_mode_controller_capture_store_mmio_irq",
            "repository evidence gate",
        ))

    standalone_self_replay = _read_csv(REPO_ROOT / "results/processed/standalone_self_replay_smokes.csv")
    if standalone_self_replay:
        bad = [row for row in standalone_self_replay if row.get("status") != "PASS"]
        configs = {row.get("recorder_config") for row in standalone_self_replay}
        benchmarks = {row.get("benchmark") for row in standalone_self_replay}
        shell_bad = [
            row for row in standalone_self_replay
            if row.get("shell") != "rtl_self_replay_soc"
            or row.get("captured_count") in {"", "NA"}
            or row.get("captured_count") != row.get("source_sent_count")
            or row.get("captured_count") != row.get("consumed_count")
            or row.get("controller_done") != "1"
        ]
        irq_rows = [row for row in standalone_self_replay if row.get("irq_after_command") == "1"]
        irq_bad = [
            row for row in irq_rows
            if row.get("record_irq_entry_count") in {"", "0", "NA", None}
            or row.get("replay_irq_entry_count") in {"", "0", "NA", None}
            or row.get("record_irq_entry_count") != row.get("replay_irq_entry_count")
        ]
        rows.append(_row(
            "v2_standalone_self_replay_matrix_clean",
            "PASS" if not bad and not shell_bad and not irq_bad and len(irq_rows) >= 3 and len(standalone_self_replay) >= 42 and {"core", "hashed", "full"} <= configs and len(benchmarks) >= 14 else "FAIL",
            "results/processed/standalone_self_replay_smokes.csv",
            f"rows={len(standalone_self_replay)} bad_rows={len(bad)} shell_bad={len(shell_bad)} irq_rows={len(irq_rows)} irq_bad={len(irq_bad)} benchmarks={len(benchmarks)} configs={','.join(sorted(configs))}; focused base+expanded reusable RTL self-replay SoC shell with PicoRV32 IRQ-entry equality on IRQ rows, not board/silicon replay",
            "repository evidence gate",
        ))

    hdl = _read_csv(REPO_ROOT / "results/processed/hdl_checks.csv")
    if hdl:
        controller_hdl = [
            row for row in hdl
            if row.get("check") == "tb_rcv2_replay_mode_controller" and row.get("status") == "PASS"
        ]
        controller_self = [
            row for row in self_replay
            if row.get("self_replay_status") == "PASS"
            and row.get("replay_stimulus_source") == "rtl_replay_mode_controller_capture_store_mmio_irq"
        ] if self_replay else []
        rows.append(_row(
            "v2_replay_mode_controller_checked",
            "PASS" if controller_hdl and self_replay and len(controller_self) == len(self_replay) else "FAIL",
            "rtl/replaycapsule_v2/rcv2_replay_mode_controller.sv",
            f"hdl_rows={len(controller_hdl)} self_replay_controller_rows={len(controller_self)}/{len(self_replay) if self_replay else 0}",
            "repository evidence gate",
        ))
        standalone_smoke = next(
            (
                row for row in hdl
                if row.get("check") == "tb_picorv32_standalone_self_replay_smoke"
                and row.get("status") == "PASS"
            ),
            {},
        )
        standalone_lint = next(
            (
                row for row in hdl
                if row.get("check") == "verilator_lint_replaycapsule_v2_self_replay_top"
                and row.get("status") == "PASS"
            ),
            {},
        )
        standalone_soc_lint = next(
            (
                row for row in hdl
                if row.get("check") == "verilator_lint_replaycapsule_v2_self_replay_soc"
                and row.get("status") == "PASS"
            ),
            {},
        )
        rows.append(_row(
            "v2_standalone_self_replay_smoke_checked",
            "PASS" if standalone_smoke and standalone_lint and standalone_soc_lint else "FAIL",
            "results/processed/hdl_checks.csv",
            f"standalone_smoke={standalone_smoke.get('status', 'MISSING')} reusable_rtl_lint={standalone_lint.get('status', 'MISSING')} soc_shell_lint={standalone_soc_lint.get('status', 'MISSING')}; focused Icarus shell, not board/silicon replay",
            "repository evidence gate",
        ))

    mapped = _read_csv(REPO_ROOT / "results/processed/mapped_scaling_v2_measured.csv")
    if mapped:
        full_core_pass = [row for row in mapped if row.get("architecture") == "v2" and row.get("status") == "PASS"]
        required_mapped_configs = {"minimal", "core", "hashed"}
        rows.append(_row(
            "v2_full_core_mapped_rows_present",
            "PASS" if required_mapped_configs <= {row.get("recorder_config") for row in full_core_pass} else "FAIL",
            "results/processed/mapped_scaling_v2_measured.csv",
            f"v2_pass_rows={len(full_core_pass)} configs={','.join(sorted({row.get('recorder_config', 'NA') for row in full_core_pass}))}",
            "repository evidence gate",
        ))

    mapped_overhead = _read_csv(REPO_ROOT / "results/processed/mapped_scaling_overhead_v2_measured.csv")
    if mapped_overhead:
        claimable = {
            row.get("recorder_config")
            for row in mapped_overhead
            if row.get("target") == "ecp5-85k" and row.get("claim_allowed") == "yes"
        }
        rows.append(_row(
            "v2_mapped_overhead_selected_minimal_claimable",
            "PASS" if {"minimal"} <= claimable else "FAIL",
            "results/processed/mapped_scaling_overhead_v2_measured.csv",
            f"selected_claim_configs={','.join(sorted(claimable))}",
            "repository evidence gate",
        ))

    asic_area = _read_csv(REPO_ROOT / "results/processed/asic_openpdk_yosys_area.csv")
    asic_area_overhead = _read_csv(REPO_ROOT / "results/processed/asic_openpdk_yosys_area_overhead.csv")
    if asic_area:
        passed = [row for row in asic_area if row.get("status") == "PASS" and row.get("cell_area_um2") not in {"", "NA"}]
        configs = {row.get("recorder_config") for row in passed}
        minimal_overhead = next(
            (
                row
                for row in asic_area_overhead
                if row.get("recorder_config") == "minimal"
                and row.get("metric") == "area_um2"
                and row.get("status") == "PASS"
            ),
            {},
        )
        rows.append(_row(
            "asic_nangate45_area_only_rows_present",
            "PASS" if len(passed) == len(asic_area) and {"baseline", "minimal", "core", "hashed", "full"} <= configs and minimal_overhead else "FAIL",
            "results/processed/asic_openpdk_yosys_area.csv",
            f"area_only_pass_rows={len(passed)}/{len(asic_area)} configs={','.join(sorted(configs))} minimal_area_overhead={minimal_overhead.get('percent_overhead', 'NA')}%; no OpenROAD timing/power claim",
            "repository evidence gate",
        ))

    second_core = _read_csv(REPO_ROOT / "results/processed/second_core_breadth.csv")
    if second_core:
        status_by_check = {row.get("check"): row.get("status") for row in second_core}
        required_checks = {
            "femtorv32_replaycapsule_wrapper_present",
            "femtorv32_replaycapsule_wrapper_lint",
            "femtorv32_replaycapsule_wrapper_synthesis",
            "femtorv32_compiler_firmware_smoke",
            "femtorv32_v1_capsule_replay_checker",
            "femtorv32_v1_mmio_replay_driver",
            "femtorv32_capsule_derived_replay_smoke",
            "femtorv32_v2_mmio_replay_consumer_smoke",
            "femtorv32_v2_mmio_replay_consumer_config_matrix",
            "femtorv32_capsule_derived_replay_matrix",
        }
        passing = {check for check in required_checks if status_by_check.get(check) == "PASS"}
        rows.append(_row(
            "second_core_wrapper_smoke_present",
            "PASS" if passing == required_checks else "FAIL",
            "results/processed/second_core_breadth.csv",
            f"second_core_checks_pass={len(passing)}/{len(required_checks)}; includes v1 RTL replay checker, scoped v1 MMIO replay driver, focused capsule-derived replay matrix, and scoped seeded benchmark/config v2 MMIO replay-consumer signature rows; no true CPU interrupt/full MMIO+IRQ second-core replay claim",
            "repository evidence gate",
        ))

    second_core_irq = _read_csv(REPO_ROOT / "results/processed/second_core_irq_candidate.csv")
    if second_core_irq:
        status_by_check = {row.get("check"): row.get("status") for row in second_core_irq}
        required_checks = {
            "hazard3_source_present",
            "hazard3_filelist_present",
            "hazard3_license_tracked",
            "hazard3_source_pinned",
            "hazard3_declares_rv32i",
            "hazard3_external_irq_ports",
            "hazard3_irq_configurable",
            "hazard3_csr_interrupt_support",
            "hazard3_mret_decode_present",
            "hazard3_irq_controller_present",
            "hazard3_frontend_lint",
        }
        passing = {check for check in required_checks if status_by_check.get(check) == "PASS"}
        rows.append(_row(
            "second_core_irq_candidate_ready",
            "PASS" if passing == required_checks else "FAIL",
            "results/processed/second_core_irq_candidate.csv",
            f"hazard3_irq_candidate_checks_pass={len(passing)}/{len(required_checks)}; vendored pinned interrupt-capable core candidate with external/software/timer IRQ ports, machine CSR/MRET support, and Verilator frontend lint; source/frontend gate only, separate focused Hazard3 v2 replay smoke is tracked in results/processed/hazard3_v2_replay_smoke.csv",
            "repository evidence gate",
        ))

    hazard3_irq_smoke = _read_csv(REPO_ROOT / "results/processed/hazard3_irq_smoke.csv")
    if hazard3_irq_smoke:
        row = hazard3_irq_smoke[0]
        passed = (
            row.get("status") == "PASS"
            and row.get("request_writes") == "1"
            and row.get("isr_writes") == "1"
            and row.get("isr_value") == "1"
            and row.get("ack_writes") == "1"
            and row.get("done_value") == "1"
            and row.get("irq_final") == "0"
            and _int(row.get("cycles")) > 0
        )
        rows.append(_row(
            "hazard3_true_isr_smoke_clean",
            "PASS" if passed else "FAIL",
            "results/processed/hazard3_irq_smoke.csv",
            f"status={row.get('status', 'NA')} cycles={row.get('cycles', 'NA')} request={row.get('request_writes', 'NA')} isr={row.get('isr_writes', 'NA')} ack={row.get('ack_writes', 'NA')} done={row.get('done_value', 'NA')} irq_final={row.get('irq_final', 'NA')}; focused Hazard3 firmware ISR smoke only, not ReplayCapsule wrapper/replay evidence",
            "repository evidence gate",
        ))

    hazard3_v2_replay = _read_csv(REPO_ROOT / "results/processed/hazard3_v2_replay_smoke.csv")
    if hazard3_v2_replay:
        bad = [
            row for row in hazard3_v2_replay
            if row.get("status") != "PASS"
            or row.get("property") != row.get("expected_property", row.get("property"))
            or row.get("words") != row.get("consumed")
            or row.get("signature_match") != "1"
            or row.get("changed_sensor") != "PASS"
            or _int(row.get("record_irq_entries")) <= 0
            or _int(row.get("replay_irq_entries")) <= 0
            or _int(row.get("record_mmio_reads")) <= 0
            or _int(row.get("replay_mmio_reads")) <= 0
            or _int(row.get("replay_mmio_drives")) <= 0
            or _int(row.get("replay_irq_drives")) <= 0
            or row.get("external_irq_replay") != "0"
        ]
        scenarios = {row.get("scenario") for row in hazard3_v2_replay if row.get("scenario")}
        benchmarks = {row.get("benchmark") for row in hazard3_v2_replay if row.get("benchmark")}
        configs = {row.get("config") for row in hazard3_v2_replay if row.get("config")}
        seeds = {row.get("seed") for row in hazard3_v2_replay if row.get("seed")}
        properties = {row.get("property") for row in hazard3_v2_replay if row.get("property") not in {"", "NA", None}}
        required_properties = {"1", "2", "4", "5"}
        rows.append(_row(
            "hazard3_v2_mmio_irq_replay_matrix_clean",
            "PASS"
            if (
                not bad
                and len(hazard3_v2_replay) >= 48
                and len(benchmarks) >= 8
                and len(configs) >= 2
                and len(seeds) >= 3
                and required_properties.issubset(properties)
            )
            else "FAIL",
            "results/processed/hazard3_v2_replay_smoke.csv",
            f"rows={len(hazard3_v2_replay)} bad_rows={len(bad)} benchmarks={len(benchmarks)} scenarios={len(scenarios)} configs={','.join(sorted(configs))} seeds={len(seeds)} properties={','.join(sorted(properties))}; all rows require property=expected_property, words=consumed, signature_match=1, changed replay-side sensor input, nonzero record/replay ISR entries, nonzero MMIO/IRQ replay drives, and external_irq_replay=0; seeded Hazard3 v2 ReplayCapsule MMIO+IRQ replay-consumer benchmark matrix",
            "repository evidence gate",
        ))

    second_core_replay = _read_csv(REPO_ROOT / "results/processed/second_core_replay_smokes.csv")
    if second_core_replay:
        bad = [row for row in second_core_replay if row.get("status") != "PASS"]
        benchmarks = {row.get("benchmark") for row in second_core_replay}
        profiles = {row.get("capture_profile") for row in second_core_replay}
        checker_bad = [row for row in second_core_replay if row.get("checker_consumed") in {"", "NA"} or row.get("checker_consumed") != row.get("capsule_count")]
        mmio_driver_bad = [row for row in second_core_replay if row.get("mmio_driver_hits") in {"", "NA", None}]
        rows.append(_row(
            "second_core_replay_smoke_matrix_clean",
            "PASS" if not bad and not checker_bad and not mmio_driver_bad and len(second_core_replay) >= 56 and len(benchmarks) >= 14 and len(profiles) >= 4 else "FAIL",
            "results/processed/second_core_replay_smokes.csv",
            f"rows={len(second_core_replay)} bad_rows={len(bad)} checker_bad={len(checker_bad)} mmio_driver_bad={len(mmio_driver_bad)} benchmarks={len(benchmarks)} profiles={','.join(sorted(profiles))}; focused FemtoRV32 replay smokes over base and expanded families, scoped v1 MMIO replay reads, no true CPU interrupt/seeded matrix claim",
            "repository evidence gate",
        ))

    second_core_v2 = _read_csv(REPO_ROOT / "results/processed/second_core_v2_smokes.csv")
    if second_core_v2:
        bad = [
            row
            for row in second_core_v2
            if row.get("status") != "PASS"
            or row.get("signature_match") != "PASS"
            or row.get("changed_input") != "PASS"
            or row.get("capsule_words") != row.get("consumed_count")
        ]
        configs = {row.get("recorder_config") for row in second_core_v2 if row.get("status") == "PASS"}
        benchmarks = {row.get("benchmark") for row in second_core_v2 if row.get("status") == "PASS"}
        seeds = {row.get("seed") for row in second_core_v2 if row.get("status") == "PASS"}
        rows.append(_row(
            "second_core_v2_mmio_replay_consumer_matrix_clean",
            "PASS" if not bad and {"core", "hashed", "full"} <= configs and len(second_core_v2) >= 126 and len(benchmarks) >= 14 and len(seeds) >= 3 else "FAIL",
            "results/processed/second_core_v2_smokes.csv",
            f"rows={len(second_core_v2)} bad_rows={len(bad)} benchmarks={len(benchmarks)} configs={','.join(sorted(configs))} seeds={','.join(sorted(seeds))}; scoped seeded FemtoRV32 v2 MMIO replay-consumer rows perturb replay-side host MMIO inputs and match property signatures, no true CPU interrupt/full MMIO+IRQ claim",
            "repository evidence gate",
        ))

    hdl = _read_csv(REPO_ROOT / "results/processed/hdl_checks.csv")
    minimal = next((row for row in hdl if row.get("check") == "tb_rcv2_minimal_recorder"), {})
    rows.append(_row(
        "v2_minimal_recorder_fidelity_checked",
        "PASS" if minimal.get("status") == "PASS" else "FAIL",
        minimal.get("raw_log", "results/processed/hdl_checks.csv"),
        "minimal recorder emits replay-critical boundary events and the v2 consumer accepts the stream",
        "repository evidence gate",
    ))
    source_store = next((row for row in hdl if row.get("check") == "tb_rcv2_capsule_source"), {})
    record_sigs = sorted((REPO_ROOT / "results/raw/rtl_signatures_v2").glob("*_record.json"))
    record_capture_sigs = 0
    for path in record_sigs:
        try:
            if "rtl capture store retained" in path.read_text(encoding="utf-8", errors="replace"):
                record_capture_sigs += 1
        except OSError:
            pass
    rows.append(_row(
        "v2_capture_store_checked",
        "PASS" if source_store.get("status") == "PASS" and record_sigs and record_capture_sigs == len(record_sigs) else "FAIL",
        source_store.get("raw_log", "results/processed/hdl_checks.csv"),
        f"source_store_hdl={source_store.get('status', 'NA')} record_signatures={record_capture_sigs}/{len(record_sigs)}",
        "repository evidence gate",
    ))

    stale_phrases = (
        "No v2 replay PASS is claimed",
        "blocked until full-core v2 runtime harness",
        "Analytic capacity estimates only; no PASS claim",
        "full-core v2 & NA & NA & NA & NA & blocked",
    )
    table_paths = sorted((PAPER_DIR / "tables").glob("table_*_v2.tex")) + [PAPER_DIR / "tables/table_limitations.tex"]
    stale = []
    for path in table_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for phrase in stale_phrases:
            if phrase in text:
                stale.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{phrase}")
    rows.append(_row(
        "v2_generated_tables_not_stale",
        "PASS" if not stale else "FAIL",
        "paper/tables",
        "no stale blocked/no-pass v2 generated table phrases" if not stale else "; ".join(stale),
        "repository evidence gate",
    ))
    return rows


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _int(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _documentclass_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("\\documentclass"):
            return line
    return ""


def _index(text: str, needle: str) -> int:
    found = text.find(needle)
    return found if found >= 0 else 10**9


def _newest_source_mtime() -> float:
    patterns = [
        "main.tex",
        "sections/*.tex",
        "tables/*.tex",
        "references.bib",
    ]
    mtimes: list[float] = []
    for pattern in patterns:
        mtimes.extend(path.stat().st_mtime for path in PAPER_DIR.glob(pattern) if path.exists())
    return max(mtimes) if mtimes else 0.0


def _pages_from_log(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Output written on .+? \((\d+) pages?", text)
    return int(match.group(1)) if match else None


def _pages_from_pdf_bytes(path: Path) -> int | None:
    if not path.exists():
        return None
    data = path.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page\b", data))
    return pages or None


def _reference_start_page(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\newlabel\{aspdac:references-start\}\{\{.*?\}\{(\d+)\}", text)
    return int(match.group(1)) if match else None


def _source_check(check: str, passed: bool, file: str, detail: str, source: str) -> dict[str, str]:
    return _row(check, "PASS" if passed else "FAIL", file, detail, source)


def _row(check: str, status: str, file: str, detail: str, source: str) -> dict[str, str]:
    return {"check": check, "status": status, "file": file, "detail": detail, "source": source}


if __name__ == "__main__":
    raise SystemExit(main())
