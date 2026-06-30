#!/usr/bin/env python3
"""Generate ASIC/open-PDK evidence rows when an OpenROAD PDK flow is configured."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "results/raw/asic_openpdk"
OUT_CSV = REPO_ROOT / "results/processed/asic_openpdk.csv"
OVERHEAD_CSV = REPO_ROOT / "results/processed/asic_openpdk_overhead.csv"
AREA_CSV = REPO_ROOT / "results/processed/asic_openpdk_yosys_area.csv"
AREA_OVERHEAD_CSV = REPO_ROOT / "results/processed/asic_openpdk_yosys_area_overhead.csv"
SUMMARY_CSV = REPO_ROOT / "results/processed/asic_openpdk_summary.csv"
DOC_PATH = REPO_ROOT / "docs/asic_openpdk_evidence.md"
SDC = REPO_ROOT / "constraints/asic_openpdk.sdc"
DEFAULT_PDK_ROOT = REPO_ROOT / ".tools/openpdk/nangate45"
DEFAULT_LIBERTY = DEFAULT_PDK_ROOT / "NangateOpenCellLibrary_typical.lib"
DEFAULT_LEF = DEFAULT_PDK_ROOT / "NangateOpenCellLibrary.combined.lef"

FIELDS = [
    "architecture",
    "recorder_config",
    "target",
    "flow",
    "design",
    "top",
    "memory_words",
    "buffer_depth",
    "clock_period_ns",
    "area_um2",
    "cell_area_um2",
    "die_area_um2",
    "wns_ns",
    "tns_ns",
    "power_mw",
    "status",
    "report_path",
    "notes",
]

OVERHEAD_FIELDS = [
    "recorder_config",
    "target",
    "flow",
    "metric",
    "baseline",
    "with_replaycapsule",
    "delta",
    "percent_overhead",
    "status",
    "notes",
]

SUMMARY_FIELDS = ["gate", "status", "pass_rows", "area_only_rows", "blocked_rows", "fail_rows", "notes"]

YOSYS_AREA_TIMEOUT_SECONDS = 240
OPENROAD_TIMEOUT_SECONDS = int(os.environ.get("ASIC_OPENPDK_OPENROAD_TIMEOUT", "900"))
NANGATE45_SITE = "FreePDK45_38x28_10R_NP_162NW_34O"
TARGET_UTILIZATION = 0.55
CORE_MARGIN_UM = 20.0


@dataclass(frozen=True)
class Design:
    architecture: str
    recorder_config: str
    design: str
    top: str
    memory_words: int
    buffer_depth: int | str
    chparams: tuple[tuple[str, str], ...]
    sources: tuple[str, ...]


COMMON_V2_SOURCES = (
    "third_party/picorv32/picorv32.v",
    "rtl/event_pkg.sv",
    "rtl/event_tap.sv",
    "rtl/event_classifier.sv",
    "rtl/capsule_buffer.sv",
    "rtl/property_checker.sv",
    "rtl/event_slicer.sv",
    "rtl/hash_signature.sv",
    "rtl/replaycapsule_v2/rcv2_payload_hasher.sv",
    "rtl/replaycapsule_v2/rcv2_address_dictionary.sv",
    "rtl/replaycapsule_v2/rcv2_adaptive_window.sv",
    "rtl/replaycapsule_v2/rcv2_event_packer.sv",
    "rtl/replaycapsule_v2/rcv2_event_fifo_bram.sv",
    "rtl/replaycapsule_v2/rcv2_event_stream_fifo.sv",
    "rtl/replaycapsule_v2/rcv2_recorder.sv",
    "rtl/mapped/mapped_memory.sv",
    "rtl/mapped/full_core_replaycapsule_v2_board_top.sv",
)

DESIGNS = (
    Design(
        "baseline",
        "baseline",
        "full_core_baseline_board",
        "full_core_baseline_board_top",
        128,
        "NA",
        (("MEM_WORDS", "128"),),
        (
            "third_party/picorv32/picorv32.v",
            "rtl/mapped/mapped_memory.sv",
            "rtl/mapped/full_core_baseline_board_top.sv",
        ),
    ),
    Design("v2", "minimal", "full_core_v2_minimal_board", "full_core_replaycapsule_v2_board_top", 128, 8, (("MEM_WORDS", "128"), ("CAPSULE_DEPTH", "8"), ("REPLAYCAPSULE_CONFIG", "0")), COMMON_V2_SOURCES),
    Design("v2", "core", "full_core_v2_core_board", "full_core_replaycapsule_v2_board_top", 128, 8, (("MEM_WORDS", "128"), ("CAPSULE_DEPTH", "8"), ("REPLAYCAPSULE_CONFIG", "1")), COMMON_V2_SOURCES),
    Design("v2", "hashed", "full_core_v2_hashed_board", "full_core_replaycapsule_v2_board_top", 128, 8, (("MEM_WORDS", "128"), ("CAPSULE_DEPTH", "8"), ("REPLAYCAPSULE_CONFIG", "2")), COMMON_V2_SOURCES),
    Design("v2", "full", "full_core_v2_full_board", "full_core_replaycapsule_v2_board_top", 128, 8, (("MEM_WORDS", "128"), ("CAPSULE_DEPTH", "8"), ("REPLAYCAPSULE_CONFIG", "4")), COMMON_V2_SOURCES),
)


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    blocker = _flow_blocker()
    area_rows = _yosys_area_rows()
    if blocker:
        rows = [_blocked_row(design, blocker) for design in DESIGNS]
    else:
        rows = _openroad_rows(area_rows)
    overhead = _overhead_rows(rows)
    area_overhead = _area_overhead_rows(area_rows)
    summary = _summary_rows(rows, area_rows, blocker)
    _write_csv(OUT_CSV, FIELDS, rows)
    _write_csv(OVERHEAD_CSV, OVERHEAD_FIELDS, overhead)
    _write_csv(AREA_CSV, FIELDS, area_rows)
    _write_csv(AREA_OVERHEAD_CSV, OVERHEAD_FIELDS, area_overhead)
    _write_csv(SUMMARY_CSV, SUMMARY_FIELDS, summary)
    _write_flow_scaffold()
    _write_doc(rows, area_rows, summary[0])
    print("WROTE results/processed/asic_openpdk.csv")
    print("WROTE results/processed/asic_openpdk_overhead.csv")
    print("WROTE results/processed/asic_openpdk_yosys_area.csv")
    print("WROTE results/processed/asic_openpdk_yosys_area_overhead.csv")
    print("WROTE results/processed/asic_openpdk_summary.csv")
    print("WROTE docs/asic_openpdk_evidence.md")
    return 0


def _flow_blocker() -> str:
    missing = []
    if _find_tool("openroad") is None:
        missing.append("openroad")
    if _find_tool("yosys") is None:
        missing.append("yosys")
    if _pdk_root() is None:
        missing.append("PDK_ROOT")
    if _liberty_path() is None:
        missing.append("ASIC_OPENPDK_LIBERTY")
    if _lef_path() is None:
        missing.append("ASIC_OPENPDK_LEF")
    if missing:
        return "missing " + ", ".join(missing)
    return ""


def _blocked_row(design: Design, blocker: str) -> dict[str, object]:
    return {
        "architecture": design.architecture,
        "recorder_config": design.recorder_config,
        "target": _target_name(),
        "flow": "yosys+openroad-openpdk",
        "design": design.design,
        "top": design.top,
        "memory_words": design.memory_words,
        "buffer_depth": design.buffer_depth,
        "clock_period_ns": "20.000",
        "area_um2": "NA",
        "cell_area_um2": "NA",
        "die_area_um2": "NA",
        "wns_ns": "NA",
        "tns_ns": "NA",
        "power_mw": "NA",
        "status": "BLOCKED",
        "report_path": rel(RAW_DIR / f"{design.design}_flow.tcl"),
        "notes": blocker,
    }


def _overhead_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    baseline = next((row for row in rows if row["architecture"] == "baseline"), {})
    out: list[dict[str, object]] = []
    for row in rows:
        if row["architecture"] != "v2":
            continue
        for metric in ("area_um2", "wns_ns", "power_mw"):
            out.append(
                {
                    "recorder_config": row["recorder_config"],
                    "target": row["target"],
                    "flow": row["flow"],
                    "metric": metric,
                    "baseline": baseline.get(metric, "NA"),
                    "with_replaycapsule": row.get(metric, "NA"),
                    "delta": "NA",
                    "percent_overhead": "NA",
                    "status": "BLOCKED",
                    "notes": "ASIC/open-PDK measurement unavailable until design rows are PASS",
                }
            )
    return out


def _yosys_area_rows() -> list[dict[str, object]]:
    yosys = _find_tool("yosys")
    liberty = _liberty_path()
    if not yosys or not liberty:
        blocker = "missing " + ", ".join(item for item, present in (("yosys", yosys), ("Liberty", liberty)) if not present)
        return [_area_blocked_row(design, blocker) for design in DESIGNS]
    return [_run_yosys_area(design, yosys, liberty) for design in DESIGNS]


def _area_blocked_row(design: Design, blocker: str) -> dict[str, object]:
    row = _blocked_row(design, blocker)
    row["flow"] = "yosys+abc-nangate45-area-only"
    row["report_path"] = rel(RAW_DIR / f"{design.design}_yosys_area.txt")
    return row


def _run_yosys_area(design: Design, yosys: str, liberty: Path) -> dict[str, object]:
    log_path = RAW_DIR / f"{design.design}_yosys_area.txt"
    mapped_path = RAW_DIR / f"{design.design}_yosys_area_mapped.v"
    script = _yosys_area_script(design, liberty, mapped_path)
    completed = subprocess.run(
        [yosys, "-p", script],
        cwd=REPO_ROOT,
        env=_yosys_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=YOSYS_AREA_TIMEOUT_SECONDS,
        check=False,
    )
    log_path.write_text(_clean_log(completed.stdout), encoding="utf-8")
    area = _last_float(r"Chip area for top module .*?:\s+([0-9.]+)", completed.stdout)
    if completed.returncode != 0 or area is None:
        row = _area_blocked_row(design, "Yosys Nangate45 area synthesis failed")
        row["status"] = "FAIL"
        return row
    return {
        "architecture": design.architecture,
        "recorder_config": design.recorder_config,
        "target": _target_name(),
        "flow": "yosys+abc-nangate45-area-only",
        "design": design.design,
        "top": design.top,
        "memory_words": design.memory_words,
        "buffer_depth": design.buffer_depth,
        "clock_period_ns": "20.000",
        "area_um2": f"{area:.3f}",
        "cell_area_um2": f"{area:.3f}",
        "die_area_um2": "NA",
        "wns_ns": "NA",
        "tns_ns": "NA",
        "power_mw": "NA",
        "status": "PASS",
        "report_path": rel(log_path),
        "notes": "Yosys+ABC Nangate45 synthesis-only standard-cell area; no placement, routing, timing, or power",
    }


def _yosys_area_script(design: Design, liberty: Path, mapped_path: Path) -> str:
    source_lines = " ".join(design.sources)
    chparams = "; ".join(f"chparam -set {name} {value} {design.top}" for name, value in design.chparams)
    commands = [
        "read_verilog -sv -Irtl -Irtl/replaycapsule_v2 -Irtl/mapped -Irtl/rv32i_integration -Ithird_party/picorv32 " + source_lines,
    ]
    if chparams:
        commands.append(chparams)
    commands.extend(
        [
            f"synth -top {design.top}",
            f"dfflibmap -liberty {rel(liberty)}",
            f"abc -liberty {rel(liberty)}",
            "clean",
            f"stat -liberty {rel(liberty)}",
            f"write_verilog {rel(mapped_path)}",
        ]
    )
    return "; ".join(commands)


def _area_overhead_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    baseline = next((row for row in rows if row["architecture"] == "baseline" and row["status"] == "PASS"), {})
    out: list[dict[str, object]] = []
    for row in rows:
        if row["architecture"] != "v2":
            continue
        out.append(_area_overhead_row(row, baseline))
    return out


def _openroad_rows(area_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    openroad = _find_tool("openroad")
    if not openroad:
        return [_blocked_row(design, "missing openroad") for design in DESIGNS]
    area_by_design = {str(row.get("design")): row for row in area_rows}
    rows: list[dict[str, object]] = []
    for design in DESIGNS:
        print(f"ASIC_OPENPDK_START design={design.design}", flush=True)
        area_row = area_by_design.get(design.design, {})
        mapped_netlist = RAW_DIR / f"{design.design}_yosys_area_mapped.v"
        if area_row.get("status") != "PASS" or not mapped_netlist.exists():
            rows.append(_blocked_row(design, "missing passing Yosys mapped netlist for OpenROAD physical flow"))
            print(f"ASIC_OPENPDK_DONE design={design.design} status=BLOCKED", flush=True)
            continue
        rows.append(_run_openroad_physical(design, area_row, openroad, mapped_netlist))
        print(f"ASIC_OPENPDK_DONE design={design.design} status={rows[-1]['status']}", flush=True)
    return rows


def _run_openroad_physical(
    design: Design,
    area_row: dict[str, object],
    openroad: str,
    mapped_netlist: Path,
) -> dict[str, object]:
    flow_tcl = _write_openroad_flow_tcl(design, area_row, mapped_netlist)
    log_path = RAW_DIR / f"{design.design}_openroad_physical.txt"
    try:
        completed = subprocess.run(
            [openroad, rel(flow_tcl)],
            cwd=REPO_ROOT,
            env=dict(os.environ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=OPENROAD_TIMEOUT_SECONDS,
            check=False,
        )
    except OSError as exc:
        log_path.write_text(str(exc) + "\n", encoding="utf-8")
        row = _blocked_row(design, "OpenROAD invocation failed")
        row["status"] = "FAIL"
        row["report_path"] = rel(log_path)
        row["notes"] = _single_line(str(exc))
        return row
    except subprocess.TimeoutExpired as exc:
        partial = ""
        if exc.stdout:
            partial += exc.stdout if isinstance(exc.stdout, str) else exc.stdout.decode("utf-8", errors="replace")
        if exc.stderr:
            partial += exc.stderr if isinstance(exc.stderr, str) else exc.stderr.decode("utf-8", errors="replace")
        partial += f"\nRC_OPENROAD_TIMEOUT after {OPENROAD_TIMEOUT_SECONDS}s\n"
        log_path.write_text(_clean_log(partial), encoding="utf-8")
        row = _blocked_row(design, "OpenROAD invocation timed out")
        row["status"] = "FAIL"
        row["report_path"] = rel(log_path)
        row["notes"] = f"OpenROAD timeout after {OPENROAD_TIMEOUT_SECONDS}s; see partial log"
        return row

    log_text = _clean_log(completed.stdout)
    log_path.write_text(log_text, encoding="utf-8")
    metrics = _parse_openroad_metrics(log_text, area_row)
    flow_pass = completed.returncode == 0 and "RC_OPENROAD_STATUS PASS" in log_text
    metrics_present = metrics["cell_area_um2"] != "NA" and metrics["wns_ns"] != "NA" and metrics["power_mw"] != "NA"
    status = "PASS" if flow_pass and metrics_present else "FAIL"
    notes = (
        f"OpenROAD placed/{_route_stage_label()} Nangate45 physical-flow row with parsed area/timing/power"
        if status == "PASS"
        else _openroad_failure_note(completed.returncode, log_text, metrics_present)
    )
    return {
        "architecture": design.architecture,
        "recorder_config": design.recorder_config,
        "target": _target_name(),
        "flow": f"yosys+openroad-openpdk-{_route_stage_label()}",
        "design": design.design,
        "top": design.top,
        "memory_words": design.memory_words,
        "buffer_depth": design.buffer_depth,
        "clock_period_ns": "20.000",
        "area_um2": metrics["area_um2"],
        "cell_area_um2": metrics["cell_area_um2"],
        "die_area_um2": metrics["die_area_um2"],
        "wns_ns": metrics["wns_ns"],
        "tns_ns": metrics["tns_ns"],
        "power_mw": metrics["power_mw"],
        "status": status,
        "report_path": rel(log_path),
        "notes": notes,
    }


def _write_openroad_flow_tcl(design: Design, area_row: dict[str, object], mapped_netlist: Path) -> Path:
    liberty = _liberty_path()
    lef = _lef_path()
    if liberty is None or lef is None:
        raise RuntimeError("OpenROAD flow requested without Liberty/LEF")
    cell_area = _float_value(area_row.get("cell_area_um2")) or 1000.0
    core_side = max(120.0, (cell_area / TARGET_UTILIZATION) ** 0.5)
    die_side = core_side + 2.0 * CORE_MARGIN_UM
    core_hi = CORE_MARGIN_UM + core_side
    def_path = RAW_DIR / f"{design.design}_openroad.def"
    db_path = RAW_DIR / f"{design.design}_openroad.odb"
    flow_tcl = RAW_DIR / f"{design.design}_flow.tcl"
    flow_tcl.write_text(
        "\n".join(
            [
                "set rc_status PASS",
                "proc rc_try {label body} {",
                "  global rc_status",
                "  if {[catch {uplevel 1 $body} err]} {",
                "    puts \"RC_OPENROAD_ERROR $label $err\"",
                "    set rc_status FAIL",
                "  }",
                "}",
                f"read_liberty {rel(liberty)}",
                f"read_lef {rel(lef)}",
                f"read_verilog {rel(mapped_netlist)}",
                f"link_design {design.top}",
                f"read_sdc {rel(SDC)}",
                f"initialize_floorplan -site {NANGATE45_SITE} -die_area {{0 0 {die_side:.3f} {die_side:.3f}}} -core_area {{{CORE_MARGIN_UM:.3f} {CORE_MARGIN_UM:.3f} {core_hi:.3f} {core_hi:.3f}}}",
                "rc_try place_pins {place_pins -hor_layer metal3 -ver_layer metal2}",
                f"rc_try global_placement {{global_placement -density {TARGET_UTILIZATION:.2f}}}",
                "rc_try detailed_placement {detailed_placement}",
                "rc_try estimate_parasitics_placement {estimate_parasitics -placement}",
                "rc_try repair_design {repair_design}",
                "if {[llength [info commands clock_tree_synthesis]] != 0} {",
                "  rc_try clock_tree_synthesis {clock_tree_synthesis -root_buf CLKBUF_X3 -buf_list {CLKBUF_X1 CLKBUF_X2 CLKBUF_X3}}",
                "  rc_try detailed_placement_after_cts {detailed_placement}",
                "} else {",
                "  puts \"RC_OPENROAD_WARN clock_tree_synthesis command unavailable\"",
                "}",
                "rc_try global_route {global_route}",
                *(
                    ["rc_try detailed_route {detailed_route}"]
                    if _detailed_route_enabled()
                    else ["puts \"RC_OPENROAD_WARN detailed_route disabled; using global-routed timing/power evidence\""]
                ),
                "if {[catch {estimate_parasitics -global_routing} err]} {",
                "  puts \"RC_OPENROAD_WARN estimate_parasitics_global $err\"",
                "  rc_try estimate_parasitics_placement_final {estimate_parasitics -placement}",
                "}",
                "puts \"RC_OPENROAD_METRIC_BEGIN\"",
                "report_design_area",
                "report_wns",
                "report_tns",
                "report_checks -path_delay max",
                "report_power",
                "puts \"RC_OPENROAD_METRIC_END\"",
                f"rc_try write_def {{write_def {rel(def_path)}}}",
                f"if {{[llength [info commands write_db]] != 0}} {{ rc_try write_db {{write_db {rel(db_path)}}} }}",
                "puts \"RC_OPENROAD_STATUS $rc_status\"",
                "if {$rc_status ne \"PASS\"} { exit 2 }",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_tcl


def _parse_openroad_metrics(log_text: str, area_row: dict[str, object]) -> dict[str, str]:
    cell_area = _first_float(
        (
            r"Design area\s+([-+0-9.eE]+)",
            r"design area\s+([-+0-9.eE]+)",
            r"Cell area:\s+([-+0-9.eE]+)",
        ),
        log_text,
    )
    die_area = _first_float((r"Die area:\s+([-+0-9.eE]+)",), log_text)
    wns = _first_float((r"\bwns\b\s+([-+0-9.eE]+)", r"worst slack\s+([-+0-9.eE]+)"), log_text, last=True)
    tns = _first_float((r"\btns\b\s+([-+0-9.eE]+)", r"total negative slack\s+([-+0-9.eE]+)"), log_text, last=True)
    power_w = _parse_total_power_w(log_text)
    area_fallback = _float_value(area_row.get("cell_area_um2"))
    cell_area = cell_area if cell_area is not None else area_fallback
    area = cell_area
    return {
        "area_um2": f"{area:.3f}" if area is not None else "NA",
        "cell_area_um2": f"{cell_area:.3f}" if cell_area is not None else "NA",
        "die_area_um2": f"{die_area:.3f}" if die_area is not None else "NA",
        "wns_ns": f"{wns:.3f}" if wns is not None else "NA",
        "tns_ns": f"{tns:.3f}" if tns is not None else "NA",
        "power_mw": f"{power_w * 1000.0:.6f}" if power_w is not None else "NA",
    }


def _parse_total_power_w(log_text: str) -> float | None:
    total_lines = [line for line in log_text.splitlines() if re.match(r"\s*Total\b", line)]
    for line in reversed(total_lines):
        numbers = [float(value) for value in re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", line)]
        if numbers:
            return numbers[-1]
    return None


def _detailed_route_enabled() -> bool:
    return os.environ.get("ASIC_OPENPDK_ROUTE_STAGE", "detailed").lower() in {"detailed", "detail", "droute"}


def _route_stage_label() -> str:
    return "detailed-routed" if _detailed_route_enabled() else "global-routed"


def _first_float(patterns: tuple[str, ...], text: str, *, last: bool = False) -> float | None:
    values: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            try:
                values.append(float(match.group(1)))
            except ValueError:
                pass
    if not values:
        return None
    return values[-1] if last else values[0]


def _openroad_failure_note(returncode: int, log_text: str, metrics_present: bool) -> str:
    errors = [line.strip() for line in log_text.splitlines() if "RC_OPENROAD_ERROR" in line]
    if errors:
        return errors[-1][:240]
    if "RC_OPENROAD_STATUS PASS" not in log_text:
        return f"OpenROAD flow did not report PASS; exit_code={returncode}"
    if not metrics_present:
        return "OpenROAD flow completed but area/timing/power metrics were not all parsed"
    return f"OpenROAD flow failed; exit_code={returncode}"


def _area_overhead_row(row: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    metric = "area_um2"
    base = _float_value(baseline.get(metric))
    replay = _float_value(row.get(metric))
    if row.get("status") != "PASS" or base is None or replay is None:
        return {
            "recorder_config": row["recorder_config"],
            "target": row["target"],
            "flow": row["flow"],
            "metric": metric,
            "baseline": baseline.get(metric, "NA"),
            "with_replaycapsule": row.get(metric, "NA"),
            "delta": "NA",
            "percent_overhead": "NA",
            "status": "BLOCKED",
            "notes": "area-only overhead unavailable until baseline and ReplayCapsule rows pass",
        }
    delta = replay - base
    return {
        "recorder_config": row["recorder_config"],
        "target": row["target"],
        "flow": row["flow"],
        "metric": metric,
        "baseline": f"{base:.3f}",
        "with_replaycapsule": f"{replay:.3f}",
        "delta": f"{delta:.3f}",
        "percent_overhead": f"{(delta / base) * 100:.2f}" if base else "NA",
        "status": "PASS",
        "notes": "synthesis-only Nangate45 cell-area overhead; no placement, routing, timing, or power",
    }


def _summary_rows(rows: list[dict[str, object]], area_rows: list[dict[str, object]], blocker: str) -> list[dict[str, object]]:
    pass_rows = sum(1 for row in rows if row["status"] == "PASS")
    area_only_rows = sum(1 for row in area_rows if row["status"] == "PASS")
    blocked_rows = sum(1 for row in rows if row["status"] == "BLOCKED")
    fail_rows = sum(1 for row in rows if row["status"] == "FAIL")
    status = "PASS" if pass_rows == len(rows) else "PARTIAL" if area_only_rows == len(DESIGNS) else "BLOCKED" if blocked_rows else "FAIL"
    notes = blocker
    if status == "PARTIAL":
        notes = f"{blocker}; Yosys+ABC Nangate45 synthesis-only area rows available"
    return [
        {
            "gate": "asic_openpdk",
            "status": status,
            "pass_rows": pass_rows,
            "area_only_rows": area_only_rows,
            "blocked_rows": blocked_rows,
            "fail_rows": fail_rows,
            "notes": notes,
        }
    ]


def _write_flow_scaffold() -> None:
    liberty = _liberty_path()
    lef = _lef_path()
    for design in DESIGNS:
        source_lines = " \\\n  ".join(design.sources)
        chparams = "\n".join(f"chparam -set {name} {value} {design.top}" for name, value in design.chparams)
        (RAW_DIR / f"{design.design}_synth.ys").write_text(
            "\n".join(
                [
                    "read_verilog -sv -Irtl -Irtl/replaycapsule_v2 -Irtl/mapped -Ithird_party/picorv32 \\",
                    f"  {source_lines}",
                    chparams,
                    f"synth -top {design.top}",
                    f"abc -liberty {rel(liberty) if liberty else '$::env(ASIC_OPENPDK_LIBERTY)'}",
                    f"write_verilog {rel(RAW_DIR / (design.design + '_yosys_area_mapped.v'))}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (RAW_DIR / f"{design.design}_flow.tcl").write_text(
            "\n".join(
                [
                    f"read_liberty {rel(liberty) if liberty else '$::env(ASIC_OPENPDK_LIBERTY)'}",
                    f"read_lef {rel(lef) if lef else '$::env(ASIC_OPENPDK_LEF)'}",
                    f"read_verilog {rel(RAW_DIR / (design.design + '_yosys_area_mapped.v'))}",
                    f"link_design {design.top}",
                    f"read_sdc {rel(SDC)}",
                    "report_checks -path_delay max",
                    "report_tns",
                    "report_wns",
                    "report_power",
                    "",
                ]
            ),
            encoding="utf-8",
        )


def _write_doc(rows: list[dict[str, object]], area_rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    lines = [
        "# ASIC/Open-PDK Evidence",
        "",
        "Generated by `scripts/run_asic_openpdk.py`.",
        "",
        f"- Status: `{summary['status']}`",
        f"- PASS rows: `{summary['pass_rows']}`",
        f"- Synthesis-only area rows: `{summary['area_only_rows']}`",
        f"- BLOCKED rows: `{summary['blocked_rows']}`",
        f"- Notes: {summary['notes']}",
        "",
        "Allowed from the area-only rows: Nangate45 Yosys+ABC standard-cell synthesis area estimates.",
        "Do not claim placed/routed ASIC area, timing, power, or energy unless the OpenROAD rows contain PASS results with real numeric area/timing/power fields.",
        "To generate those rows without a native Windows OpenROAD install, use `scripts/run_asic_openroad_docker.ps1` with Docker Desktop or run `.github/workflows/asic-openroad.yml` on GitHub Actions.",
        "",
        f"- Effective PDK root: `{rel(_pdk_root()) if _pdk_root() else 'not found'}`",
        f"- Effective Liberty: `{rel(_liberty_path()) if _liberty_path() else 'not found'}`",
        f"- Effective LEF: `{rel(_lef_path()) if _lef_path() else 'not found'}`",
        "- Local default platform files are the Nangate45 examples from OpenROAD-flow-scripts when present under `.tools/openpdk/nangate45/`.",
        "",
        "| Design | Config | Status | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['design']}` | `{row['recorder_config']}` | `{row['status']}` | {row['notes']} |")
    lines.extend(
        [
            "",
            "## Synthesis-Only Area Rows",
            "",
            "| Design | Config | Status | Cell area um2 | Notes |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for row in area_rows:
        lines.append(f"| `{row['design']}` | `{row['recorder_config']}` | `{row['status']}` | {row['cell_area_um2']} | {row['notes']} |")
    lines.extend(
        [
            "",
            "Generated outputs:",
            "",
            "- `results/processed/asic_openpdk.csv`",
            "- `results/processed/asic_openpdk_overhead.csv`",
            "- `results/processed/asic_openpdk_yosys_area.csv`",
            "- `results/processed/asic_openpdk_yosys_area_overhead.csv`",
            "- `results/processed/asic_openpdk_summary.csv`",
            "- `results/processed/asic_physical_tool_probe.csv` when `scripts/probe_asic_physical_tools.py` has been run",
            "- `docs/asic_physical_tool_probe.md` when `scripts/probe_asic_physical_tools.py` has been run",
            "- `results/raw/asic_openpdk/*_synth.ys` and `*_flow.tcl` scaffolds",
            "",
        ]
    )
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def _find_tool(name: str) -> str | None:
    for candidate in (name, f"{name}.exe"):
        found = shutil.which(candidate)
        if found:
            return found
    oss = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite/bin"
    for candidate in (oss / name, oss / f"{name}.exe"):
        if candidate.exists():
            return str(candidate)
    return None


def _yosys_env() -> dict[str, str]:
    env = dict(os.environ)
    suite = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite"
    env["PATH"] = os.pathsep.join([str(suite / "bin"), str(suite / "lib"), env.get("PATH", "")])
    return env


def _target_name() -> str:
    if os.environ.get("ASIC_OPENPDK_PLATFORM"):
        return os.environ["ASIC_OPENPDK_PLATFORM"]
    if _pdk_root() == DEFAULT_PDK_ROOT:
        return "nangate45"
    return "openpdk"


def _pdk_root() -> Path | None:
    env_root = os.environ.get("PDK_ROOT")
    if env_root:
        path = Path(env_root)
        return path if path.exists() else None
    return DEFAULT_PDK_ROOT if DEFAULT_PDK_ROOT.exists() else None


def _liberty_path() -> Path | None:
    env_lib = os.environ.get("ASIC_OPENPDK_LIBERTY")
    if env_lib:
        path = Path(env_lib)
        return path if path.exists() else None
    return DEFAULT_LIBERTY if DEFAULT_LIBERTY.exists() else None


def _lef_path() -> Path | None:
    env_lef = os.environ.get("ASIC_OPENPDK_LEF")
    if env_lef:
        path = Path(env_lef)
        return path if path.exists() else None
    return DEFAULT_LEF if DEFAULT_LEF.exists() else None


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _clean_log(text: str) -> str:
    text = re.sub(
        r"End of script\. Logfile hash: ([0-9a-f]+), time: [^,]+, user: [^,]+, system: [^\n]+",
        r"End of script. Logfile hash: \1, time: <time>, user: <time>, system: <time>",
        text,
    )
    text = re.sub(r"Time spent: .+", "Time spent: <normalized>", text)
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def _single_line(text: str) -> str:
    return " / ".join(line.strip() for line in str(text).splitlines() if line.strip())[:240] or "no output"


def _last_float(pattern: str, text: str) -> float | None:
    matches = [float(match.group(1)) for match in re.finditer(pattern, text)]
    return matches[-1] if matches else None


def _float_value(value: object) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
