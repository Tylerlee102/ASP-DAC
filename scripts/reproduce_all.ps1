param(
    [switch]$CheckPythonOnly
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$candidates = @(
    "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    (Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue)
) | Where-Object { $_ -and (Test-Path $_) }

function Test-PythonCandidate {
    param([string]$Candidate)
    try {
        $version = & $Candidate --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        return ($version -join " ") -match "Python 3\."
    }
    catch {
        return $false
    }
}

$python = $null
foreach ($candidate in $candidates) {
    if (Test-PythonCandidate $candidate) {
        $python = $candidate
        break
    }
}

if (-not $python) {
    throw "No usable Python 3 interpreter found. Install Python 3.9+ or run inside Codex with the bundled runtime."
}

if ($CheckPythonOnly) {
    Write-Output "PYTHON_OK $python"
    exit 0
}

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
