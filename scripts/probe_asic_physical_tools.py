#!/usr/bin/env python3
"""Probe local tool availability for ASIC physical-flow evidence."""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = REPO_ROOT / "results/processed/asic_physical_tool_probe.csv"
DOC_PATH = REPO_ROOT / "docs/asic_physical_tool_probe.md"
OPENROAD_RELEASE_API = "https://vaultlink.precisioninno.com/api/releases/latest"
OPENROAD_CONDA_API = "https://api.anaconda.org/package/litex-hub/openroad"
OPENROAD_DOCKER_TAG_API = "https://hub.docker.com/v2/repositories/openroad/orfs/tags/latest"

FIELDS = [
    "check",
    "status",
    "tool",
    "path",
    "detail",
    "action_needed",
    "notes",
]


def main() -> int:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = _probe_rows()
    _write_csv(rows)
    _write_doc(rows)
    print(f"WROTE {rel(OUT_CSV)}")
    print(f"WROTE {rel(DOC_PATH)}")
    return 0


def _probe_rows() -> list[dict[str, str]]:
    rows = [
        _tool_row(
            "openroad_binary",
            "openroad",
            required_for_physical_flow=True,
            action_needed="Install OpenROAD in PATH or set up a runnable Linux/Docker/WSL OpenROAD flow.",
            notes="Required for placed/routed ASIC area, timing, and power evidence.",
        ),
        _tool_row(
            "opensta_binary",
            "sta",
            alternate_names=("opensta",),
            required_for_physical_flow=False,
            action_needed="Optional if timing is reported through OpenROAD; otherwise install OpenSTA.",
            notes="Useful for independent static timing checks.",
        ),
        _tool_row(
            "docker_binary",
            "docker",
            required_for_physical_flow=False,
            action_needed="Install Docker Desktop or provide another runnable OpenROAD environment.",
            notes="Common way to run Linux-only EDA flows from Windows.",
        ),
        _docker_openroad_image_row(),
        _wsl_row(),
        _dism_wsl_feature_row(),
        _winget_openroad_row(),
        _conda_openroad_row(),
        *_openroad_release_rows(),
        _tool_row(
            "yosys_binary",
            "yosys",
            required_for_physical_flow=False,
            action_needed="Install OSS CAD Suite if synthesis-only area rows need regeneration.",
            notes="Already sufficient for the current Nangate45 synthesis-only rows.",
        ),
        _file_row(
            "nangate45_liberty",
            REPO_ROOT / ".tools/openpdk/nangate45/NangateOpenCellLibrary_typical.lib",
            action_needed="Provide a Liberty file for the selected open PDK.",
            notes="Required for synthesis and timing.",
        ),
        _file_row(
            "nangate45_lef",
            REPO_ROOT / ".tools/openpdk/nangate45/NangateOpenCellLibrary.combined.lef",
            action_needed="Provide a LEF file for the selected open PDK.",
            notes="Required for placement/routing.",
        ),
        _file_row(
            "asic_sdc",
            REPO_ROOT / "constraints/asic_openpdk.sdc",
            action_needed="Provide clock/timing constraints for the ASIC flow.",
            notes="Used by the OpenROAD flow scaffold.",
        ),
    ]
    return rows


def _docker_openroad_image_row() -> dict[str, str]:
    try:
        with urllib.request.urlopen(
            urllib.request.Request(OPENROAD_DOCKER_TAG_API, headers={"User-Agent": "replaycapsule-asic-probe"}),
            timeout=20,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "check": "openroad_orfs_docker_image",
            "status": "BLOCKED",
            "tool": "dockerhub",
            "path": OPENROAD_DOCKER_TAG_API,
            "detail": _single_line(str(exc)),
            "action_needed": "Retry Docker Hub metadata check or use another OpenROAD install route.",
            "notes": "Checks whether the public OpenROAD-flow-scripts container image can be used by Docker/GitHub Actions.",
        }
    images = payload.get("images") or []
    amd64 = [image for image in images if image.get("architecture") == "amd64" and image.get("os") == "linux"]
    detail = f"tag={payload.get('name', 'latest')} size={payload.get('full_size', 'NA')} images={len(images)} amd64_linux={len(amd64)}"
    return {
        "check": "openroad_orfs_docker_image",
        "status": "PASS" if amd64 else "BLOCKED",
        "tool": "dockerhub",
        "path": "openroad/orfs:latest",
        "detail": detail,
        "action_needed": "none" if amd64 else "Find a current OpenROAD Docker image or use WSL/Linux.",
        "notes": "The repo includes scripts/run_asic_openroad_docker.ps1 and .github/workflows/asic-openroad.yml for this image.",
    }


def _tool_row(
    check: str,
    primary_name: str,
    *,
    alternate_names: tuple[str, ...] = (),
    required_for_physical_flow: bool,
    action_needed: str,
    notes: str,
) -> dict[str, str]:
    candidates = (
        primary_name,
        f"{primary_name}.exe",
        *alternate_names,
        *(f"{name}.exe" for name in alternate_names),
    )
    found = _find_first_tool(candidates)
    if found:
        return {
            "check": check,
            "status": "PASS",
            "tool": primary_name,
            "path": rel(Path(found)),
            "detail": _version_detail(found),
            "action_needed": "none",
            "notes": notes,
        }
    return {
        "check": check,
        "status": "BLOCKED" if required_for_physical_flow else "MISSING",
        "tool": primary_name,
        "path": "NA",
        "detail": "not found",
        "action_needed": action_needed,
        "notes": notes,
    }


def _wsl_row() -> dict[str, str]:
    launcher = shutil.which("wsl") or shutil.which("wsl.exe")
    if not launcher:
        return {
            "check": "wsl_status",
            "status": "MISSING",
            "tool": "wsl",
            "path": "NA",
            "detail": "wsl.exe not found",
            "action_needed": "Install WSL or use Docker/Linux for OpenROAD.",
            "notes": "Windows launcher is absent.",
        }
    completed = _run([launcher, "--status"], timeout=15)
    detail = _single_line(completed.stdout)
    return {
        "check": "wsl_status",
        "status": "PASS" if completed.returncode == 0 else "BLOCKED",
        "tool": "wsl",
        "path": rel(Path(launcher)),
        "detail": detail or f"exit_code={completed.returncode}",
        "action_needed": "none" if completed.returncode == 0 else "Install and initialize WSL, then install or expose OpenROAD inside the Linux distribution.",
        "notes": "WSL can host Linux OpenROAD flows when a distribution is installed.",
    }


def _dism_wsl_feature_row() -> dict[str, str]:
    completed = _run(
        ["dism.exe", "/online", "/get-featureinfo", "/featurename:Microsoft-Windows-Subsystem-Linux"],
        timeout=20,
    )
    detail = _single_line(completed.stdout) or f"exit_code={completed.returncode}"
    elevated = "Error: 740" in completed.stdout or "Elevated permissions are required" in completed.stdout
    return {
        "check": "wsl_feature_query",
        "status": "BLOCKED" if elevated else ("PASS" if completed.returncode == 0 else "MISSING"),
        "tool": "dism",
        "path": "dism.exe",
        "detail": detail,
        "action_needed": "Run WSL feature installation from an elevated Windows session, then install Ubuntu/OpenROAD." if elevated else "none",
        "notes": "Records whether this Codex session can inspect the Windows WSL feature state without elevation.",
    }


def _winget_openroad_row() -> dict[str, str]:
    winget = shutil.which("winget") or shutil.which("winget.exe")
    if not winget:
        return {
            "check": "winget_openroad_package",
            "status": "MISSING",
            "tool": "winget",
            "path": "NA",
            "detail": "winget not found",
            "action_needed": "Use WSL/Docker/Linux or a manual OpenROAD binary install.",
            "notes": "Winget is only a convenience path, not required by the artifact.",
        }
    completed = _run([winget, "search", "OpenROAD", "--accept-source-agreements"], timeout=40)
    found = completed.returncode == 0 and "No package found" not in completed.stdout
    detail = (
        "No package found matching input criteria."
        if "No package found" in completed.stdout
        else _single_line(completed.stdout)
    )
    return {
        "check": "winget_openroad_package",
        "status": "PASS" if found else "MISSING",
        "tool": "winget",
        "path": rel(Path(winget)),
        "detail": detail or f"exit_code={completed.returncode}",
        "action_needed": "none" if found else "Use WSL/Docker/Linux or a manual OpenROAD binary install.",
        "notes": "Documents whether a native Windows package route is available locally.",
    }


def _conda_openroad_row() -> dict[str, str]:
    try:
        request = urllib.request.Request(OPENROAD_CONDA_API, headers={"User-Agent": "ReplayCapsule-RV probe"})
        with urllib.request.urlopen(request, timeout=30) as response:
            package = json.loads(response.read().decode("utf-8-sig"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "check": "conda_openroad_package_platforms",
            "status": "MISSING",
            "tool": "conda",
            "path": OPENROAD_CONDA_API,
            "detail": f"metadata unavailable: {_single_line(str(exc))}",
            "action_needed": "Use WSL/Docker/Linux or a current official OpenROAD package.",
            "notes": "Checks whether the litex-hub OpenROAD conda package can supply a native Windows binary.",
        }
    platforms = sorted(
        {
            str(item.get("attrs", {}).get("subdir", "unknown"))
            for item in package.get("files", [])
            if item.get("attrs", {}).get("subdir")
        }
    )
    has_windows = any(platform.startswith("win-") for platform in platforms)
    return {
        "check": "conda_openroad_package_platforms",
        "status": "PASS" if has_windows else "MISSING",
        "tool": "conda",
        "path": OPENROAD_CONDA_API,
        "detail": f"platforms={','.join(platforms) if platforms else 'none'}",
        "action_needed": "none" if has_windows else "Conda route is not native-Windows here; use WSL/Docker/Linux for the Linux package.",
        "notes": "The available litex-hub package metadata is useful only if a runnable platform package exists for this machine.",
    }


def _openroad_release_rows() -> list[dict[str, str]]:
    try:
        request = urllib.request.Request(OPENROAD_RELEASE_API, headers={"User-Agent": "ReplayCapsule-RV probe"})
        with urllib.request.urlopen(request, timeout=30) as response:
            release = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return [
            {
                "check": "openroad_official_release_metadata",
                "status": "MISSING",
                "tool": "openroad-release",
                "path": OPENROAD_RELEASE_API,
                "detail": f"metadata unavailable: {_single_line(str(exc))}",
                "action_needed": "Manually check the official OpenROAD prebuilt release page or use WSL/Docker/Linux.",
                "notes": "Network probe for official prebuilt OpenROAD release metadata.",
            },
            {
                "check": "openroad_official_download_access",
                "status": "MISSING",
                "tool": "openroad-release",
                "path": "NA",
                "detail": "metadata unavailable",
                "action_needed": "Manually download an OpenROAD Linux package after release metadata is available.",
                "notes": "Download access was not tested because metadata could not be fetched.",
            },
        ]

    version = str(release.get("version", "NA"))
    files = release.get("files") or []
    file_names = [str(item.get("name", "")) for item in files if item.get("name")]
    linux_packages = [name for name in file_names if name.endswith(".deb")]
    metadata_detail = f"version={version}; files={'; '.join(file_names) if file_names else 'none'}"
    metadata_status = "PASS" if version != "NA" and linux_packages else "MISSING"
    rows = [
        {
            "check": "openroad_official_release_metadata",
            "status": metadata_status,
            "tool": "openroad-release",
            "path": OPENROAD_RELEASE_API,
            "detail": metadata_detail,
            "action_needed": "none" if metadata_status == "PASS" else "Find a current official OpenROAD prebuilt package.",
            "notes": "Records current official prebuilt OpenROAD release metadata for the ASIC physical-flow blocker.",
        }
    ]

    if not linux_packages:
        rows.append(
            {
                "check": "openroad_official_download_access",
                "status": "MISSING",
                "tool": "openroad-release",
                "path": "NA",
                "detail": "no Linux .deb package listed",
                "action_needed": "Use WSL/Docker/Linux or build OpenROAD locally on a supported Linux distribution.",
                "notes": "No official Linux package was listed in release metadata.",
            }
        )
        return rows

    package = linux_packages[0]
    download_url = f"https://vaultlink.precisioninno.com/api/releases/{version}/{package}/download"
    rows.append(_download_access_row(download_url, package))
    return rows


def _download_access_row(download_url: str, package: str) -> dict[str, str]:
    request = urllib.request.Request(
        download_url,
        headers={"User-Agent": "ReplayCapsule-RV probe", "Range": "bytes=0-0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = getattr(response, "status", 200)
            response.read(1)
        return {
            "check": "openroad_official_download_access",
            "status": "PASS",
            "tool": "openroad-release",
            "path": download_url,
            "detail": f"HTTP {status}; package={package}",
            "action_needed": "Install the Ubuntu .deb inside WSL/Docker/Linux, then rerun the ASIC flow.",
            "notes": "The package endpoint is reachable; Windows still needs a supported Linux execution environment.",
        }
    except urllib.error.HTTPError as exc:
        status = "BLOCKED" if exc.code in {401, 403} else "MISSING"
        action = (
            "Register/authorize download through the official OpenROAD release portal, then install the Ubuntu .deb inside WSL/Docker/Linux."
            if status == "BLOCKED"
            else "Retry the official OpenROAD download or use WSL/Docker/Linux build instructions."
        )
        return {
            "check": "openroad_official_download_access",
            "status": status,
            "tool": "openroad-release",
            "path": download_url,
            "detail": f"HTTP {exc.code}; package={package}",
            "action_needed": action,
            "notes": "The official package endpoint exists, but this local probe is not authorized to download it.",
        }
    except (OSError, urllib.error.URLError) as exc:
        return {
            "check": "openroad_official_download_access",
            "status": "MISSING",
            "tool": "openroad-release",
            "path": download_url,
            "detail": f"download probe failed: {_single_line(str(exc))}",
            "action_needed": "Retry the official OpenROAD download or use WSL/Docker/Linux build instructions.",
            "notes": "The release metadata exists, but package access could not be tested successfully.",
        }


def _file_row(check: str, path: Path, *, action_needed: str, notes: str) -> dict[str, str]:
    exists = path.exists()
    return {
        "check": check,
        "status": "PASS" if exists else "MISSING",
        "tool": "file",
        "path": rel(path),
        "detail": f"bytes={path.stat().st_size}" if exists else "not found",
        "action_needed": "none" if exists else action_needed,
        "notes": notes,
    }


def _find_first_tool(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found
    suite_bin = REPO_ROOT / ".tools/oss-cad-suite/oss-cad-suite/bin"
    for candidate in candidates:
        path = suite_bin / candidate
        if path.exists():
            return str(path)
    return None


def _version_detail(path: str) -> str:
    for flag in ("--version", "-version", "-v"):
        completed = _run([path, flag], timeout=15)
        if completed.returncode == 0 and completed.stdout.strip():
            return _single_line(completed.stdout)
    return "found"


def _run(args: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
            env=dict(os.environ),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(args, 124, stdout=str(exc), stderr="")


def _single_line(text: str) -> str:
    clean = text.replace("\x00", "").replace("|", "/")
    lines = []
    for line in clean.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if " KB / " in stripped or " MB / " in stripped:
            continue
        if stripped in {"-", "\\", "/", "\\"}:
            continue
        lines.append(stripped)
    if not lines:
        return ""
    return " / ".join(lines[:4])[:500]


def _write_csv(rows: list[dict[str, str]]) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_doc(rows: list[dict[str, str]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    native_openroad_ready = next(row for row in rows if row["check"] == "openroad_binary")["status"] == "PASS"
    docker_ready = next(row for row in rows if row["check"] == "docker_binary")["status"] == "PASS"
    docker_image_ready = next(row for row in rows if row["check"] == "openroad_orfs_docker_image")["status"] == "PASS"
    docker_route_ready = docker_ready and docker_image_ready
    physical_ready = native_openroad_ready or docker_route_ready
    count_text = ", ".join(f"{key}={counts[key]}" for key in sorted(counts))
    lines = [
        "# ASIC Physical Tool Probe",
        "",
        "Generated by `scripts/probe_asic_physical_tools.py`.",
        "",
        f"- Physical-flow ready: `{'yes' if physical_ready else 'no'}`",
        f"- Native OpenROAD ready: `{'yes' if native_openroad_ready else 'no'}`",
        f"- Docker/OpenROAD route ready: `{'yes' if docker_route_ready else 'no'}`",
        f"- Status counts: `{count_text}`",
        "",
        "This probe does not create ASIC area, timing, or power evidence. It records whether the local machine can run the physical-flow tools needed to turn the existing OpenROAD scaffolds into measured rows.",
        "",
        "| Check | Status | Detail | Action needed |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['check']}` | `{row['status']}` | {row['detail']} | {row['action_needed']} |"
        )
    lines.extend(
        [
            "",
            "Current reviewer-safe interpretation:",
            "",
            "- If `openroad_binary` is `BLOCKED` locally, use the GitHub Actions/OpenROAD Docker path; the checked evidence rows in `results/processed/asic_openpdk.csv` are the authority for ASIC/open-PDK claims.",
            "- If Docker is available, run `scripts/run_asic_openroad_docker.ps1` to execute the physical flow inside `openroad/orfs:latest`.",
            "- On GitHub, run `.github/workflows/asic-openroad.yml` to generate and upload the same ASIC physical evidence bundle on an Ubuntu runner.",
            "- Claim only OpenROAD PASS rows in `results/processed/asic_openpdk.csv`; detailed-route signoff, tapeout, silicon, and energy remain out of scope.",
            "",
        ]
    )
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
