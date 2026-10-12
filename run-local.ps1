$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Creating virtual environment..."
    & python -m venv (Join-Path $PSScriptRoot ".venv")
}

Write-Host "Installing dependencies..."
& $python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

$env:OJ_JUDGE_MODE = "local"
$env:OJ_AUTH_REQUIRED = "false"
$hostAddress = if ($env:OJ_HOST) { $env:OJ_HOST } else { "127.0.0.1" }
$port = if ($env:OJ_PORT) { $env:OJ_PORT } else { "8000" }
Write-Host ("Sakura OJ listening on http://{0}:{1} (judge mode: {2})" -f $hostAddress, $port, $env:OJ_JUDGE_MODE)
& $python -m uvicorn app.main:app --host $hostAddress --port $port
