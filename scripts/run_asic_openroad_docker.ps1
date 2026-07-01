param(
    [string]$Image = "openroad/orfs:latest"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    $dockerDesktopCli = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"
    if (Test-Path $dockerDesktopCli) {
        $env:PATH = "$(Split-Path $dockerDesktopCli);$env:PATH"
    } else {
        throw "Docker is not installed or is not on PATH. Install Docker Desktop or run .github/workflows/asic-openroad.yml on GitHub Actions."
    }
}

$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$inner = @'
set -euo pipefail
if ! command -v openroad >/dev/null 2>&1; then
    mkdir -p results/raw/asic_openpdk
    find / -type f -name openroad -perm /111 2>/dev/null | sort > results/raw/asic_openpdk/openroad_candidates.txt
    OPENROAD_BIN="$(head -n 1 results/raw/asic_openpdk/openroad_candidates.txt || true)"
    if [ -n "$OPENROAD_BIN" ]; then
        export PATH="$(dirname "$OPENROAD_BIN"):$PATH"
    fi
fi
which openroad
openroad -version
python3 scripts/materialize_nangate45_from_orfs.py
python3 scripts/probe_asic_physical_tools.py
python3 scripts/run_asic_openpdk.py
python3 scripts/audit_aspdac_submission.py
python3 scripts/update_chat_context.py
python3 scripts/summarize_artifact_manifest.py
'@

docker pull $Image
$inner | docker run --rm -i `
    -v "${repo}:/work" `
    -w /work `
    -e PDK_ROOT=/work/.tools/openpdk/nangate45 `
    -e ASIC_OPENPDK_PLATFORM=nangate45 `
    -e ASIC_OPENPDK_LIBERTY=/work/.tools/openpdk/nangate45/NangateOpenCellLibrary_typical.lib `
    -e ASIC_OPENPDK_LEF=/work/.tools/openpdk/nangate45/NangateOpenCellLibrary.combined.lef `
    -e ASIC_OPENPDK_ROUTE_STAGE=global `
    -e ASIC_OPENPDK_OPENROAD_TIMEOUT=900 `
    $Image `
    bash -s
