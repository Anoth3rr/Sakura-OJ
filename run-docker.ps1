$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$dockerCli = if ($env:OJ_DOCKER_CLI) { $env:OJ_DOCKER_CLI } else { $null }
if (-not $dockerCli) {
    $dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
    if ($dockerCommand) {
        $dockerCli = $dockerCommand.Source
    }
}
if (-not $dockerCli) {
    $userDockerCli = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"
    if (Test-Path -LiteralPath $userDockerCli) {
        $dockerCli = $userDockerCli
    }
}
if (-not $dockerCli) {
    throw "未找到 Docker CLI，请安装 Docker Desktop。"
}

& $dockerCli info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker daemon 不可用，请启动 Docker Desktop 后重试。当前 CLI: $dockerCli"
}

$judgeImage = if ($env:OJ_DOCKER_IMAGE) { $env:OJ_DOCKER_IMAGE } else { "sakura-oj-judge:local" }
Write-Host ("Building judge image {0}..." -f $judgeImage)
& $dockerCli build --file (Join-Path $PSScriptRoot "Dockerfile.judge") --tag $judgeImage $PSScriptRoot
if ($LASTEXITCODE -ne 0) {
    throw "Judge 镜像构建失败。"
}

# Pass the resolved CLI path to the API so the background judge uses the same
# user-level Docker installation even when it is not on PATH.
$env:OJ_DOCKER_CLI = $dockerCli

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Creating virtual environment..."
    & python -m venv (Join-Path $PSScriptRoot ".venv")
}

Write-Host "Installing API dependencies..."
& $python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

$env:OJ_JUDGE_MODE = "docker"
$env:OJ_AUTH_REQUIRED = "true"
$hostAddress = if ($env:OJ_HOST) { $env:OJ_HOST } else { "127.0.0.1" }
$port = if ($env:OJ_PORT) { $env:OJ_PORT } else { "8000" }
Write-Host ("Sakura OJ listening on http://{0}:{1} (Docker judge: {2})" -f $hostAddress, $port, $judgeImage)
& $python -m uvicorn app.main:app --host $hostAddress --port $port
