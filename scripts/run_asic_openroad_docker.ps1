param(
    [string]$Image = "openroad/orfs:latest"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or is not on PATH. Install Docker Desktop or run .github/workflows/asic-openroad.yml on GitHub Actions."
}

$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

docker pull $Image
docker run --rm `
    -v "${repo}:/work" `
    -w /work `
    -e PDK_ROOT=/work/.tools/openpdk/nangate45 `
    -e ASIC_OPENPDK_PLATFORM=nangate45 `
    -e ASIC_OPENPDK_LIBERTY=/work/.tools/openpdk/nangate45/NangateOpenCellLibrary_typical.lib `
    -e ASIC_OPENPDK_LEF=/work/.tools/openpdk/nangate45/NangateOpenCellLibrary.combined.lef `
    $Image `
    bash -lc "set -euo pipefail; python3 scripts/materialize_nangate45_from_orfs.py; python3 scripts/probe_asic_physical_tools.py; python3 scripts/run_asic_openpdk.py; python3 scripts/audit_aspdac_submission.py; python3 scripts/update_chat_context.py; python3 scripts/summarize_artifact_manifest.py"
