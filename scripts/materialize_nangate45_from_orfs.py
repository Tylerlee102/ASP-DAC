#!/usr/bin/env python3
"""Copy Nangate45 Liberty/LEF files from an OpenROAD-flow-scripts install."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / ".tools/openpdk/nangate45"

LIBERTY_NAME = "NangateOpenCellLibrary_typical.lib"
COMBINED_LEF_NAME = "NangateOpenCellLibrary.combined.lef"
TECH_LEF_NAME = "NangateOpenCellLibrary.tech.lef"
MACRO_LEF_NAME = "NangateOpenCellLibrary.macro.mod.lef"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--search-root", action="append", type=Path, default=[])
    args = parser.parse_args()

    roots = _candidate_roots(args.search_root)
    liberty = _find_first(roots, LIBERTY_NAME)
    combined_lef = _find_first(roots, COMBINED_LEF_NAME)
    tech_lef = _find_first(roots, TECH_LEF_NAME)
    macro_lef = _find_first(roots, MACRO_LEF_NAME)

    if liberty is None:
        raise SystemExit(f"missing {LIBERTY_NAME} under search roots: {', '.join(map(str, roots))}")
    if (tech_lef is None or macro_lef is None) and (
        combined_lef is None or not _lef_has_cell_macros_before_end(combined_lef)
    ):
        raise SystemExit(
            f"missing usable {COMBINED_LEF_NAME}, or {TECH_LEF_NAME}+{MACRO_LEF_NAME}, under search roots: "
            + ", ".join(map(str, roots))
        )

    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    _copy_if_different(liberty, out / LIBERTY_NAME)
    if tech_lef is not None and macro_lef is not None:
        _combine_lefs((tech_lef, macro_lef), out / COMBINED_LEF_NAME)
        _copy_if_different(tech_lef, out / TECH_LEF_NAME)
        _copy_if_different(macro_lef, out / MACRO_LEF_NAME)
    else:
        _copy_if_different(combined_lef, out / COMBINED_LEF_NAME)
    (out / "README.md").write_text(
        "Nangate45 Liberty/LEF files copied from the OpenROAD-flow-scripts container for ReplayCapsule ASIC evidence.\n",
        encoding="utf-8",
    )
    print(f"WROTE {out / LIBERTY_NAME}")
    print(f"WROTE {out / COMBINED_LEF_NAME}")
    return 0


def _candidate_roots(extra: list[Path]) -> list[Path]:
    roots: list[Path] = []
    for value in extra:
        roots.append(value)
    for env_name in ("FLOW_HOME", "OPENROAD_FLOW_HOME", "ORFS_HOME"):
        value = os.environ.get(env_name)
        if value:
            path = Path(value)
            roots.append(path)
            roots.append(path.parent)
    roots.extend(
        [
            Path("/OpenROAD-flow-scripts"),
            Path("/openroad-flow-scripts"),
            Path("/opt/OpenROAD-flow-scripts"),
            Path("/usr/local/share/OpenROAD-flow-scripts"),
            REPO_ROOT / ".tools/openpdk/nangate45",
        ]
    )
    seen: set[Path] = set()
    out: list[Path] = []
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.exists():
            continue
        seen.add(resolved)
        out.append(resolved)
    return out


def _find_first(roots: list[Path], name: str) -> Path | None:
    for root in roots:
        direct = root / name
        if direct.exists():
            return direct
        for match in root.rglob(name):
            if match.is_file():
                return match
    return None


def _combine_lefs(inputs: tuple[Path | None, Path | None], output: Path) -> None:
    with output.open("w", encoding="utf-8") as handle:
        for index, path in enumerate(inputs):
            if path is None:
                continue
            handle.write(f"# ---- {path.name} ----\n")
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                stripped = line.strip()
                upper = stripped.upper()
                if upper == "END LIBRARY":
                    continue
                if index > 0 and upper.startswith(("VERSION ", "BUSBITCHARS ", "DIVIDERCHAR ")):
                    continue
                handle.write(line)
                handle.write("\n")
            handle.write("\n")
        handle.write("END LIBRARY\n")


def _copy_if_different(source: Path, dest: Path) -> None:
    if source.resolve() == dest.resolve():
        return
    shutil.copy2(source, dest)


def _lef_has_cell_macros_before_end(path: Path) -> bool:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.upper() == "END LIBRARY":
            return False
        if stripped in {"MACRO INV_X1", "MACRO NAND2_X1", "MACRO DFF_X1"}:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
