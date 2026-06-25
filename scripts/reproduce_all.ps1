$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$candidates = @(
    (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    (Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
) | Where-Object { $_ -and (Test-Path $_) }

if (-not $candidates) {
    throw "No usable Python interpreter found. Install Python 3.9+ or run inside Codex with the bundled runtime."
}

$python = $candidates[-1]
$env:PYTHONDONTWRITEBYTECODE = "1"
Push-Location $repoRoot
try {
    & $python scripts/run_all_tests.py
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}

