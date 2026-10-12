#Requires -Version 5.1
<#
.SYNOPSIS
启动 Sakura 的 OJ、集训队、录题工作台和评测服务，并保持 WSL 会话。
.EXAMPLE
.\run.ps1
.EXAMPLE
.\run.ps1 -Restart -OpenBrowser
.EXAMPLE
.\run.ps1 -Quiet
#>
[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]*$')]
    [string]$Distro = "Ubuntu-24.04",
    [switch]$Install,
    [switch]$Restart,
    [switch]$OpenBrowser,
    [switch]$Quiet,
    [ValidateRange(10, 300)]
    [int]$StartupTimeoutSeconds = 90
)

$ErrorActionPreference = "Stop"
$wslCommand = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslCommand) { throw "未找到 WSL，请先安装 WSL 和 Ubuntu，参见 README.md。" }
$wslExe = $wslCommand.Source
$keepAlive = $null

function Invoke-SakuraWsl {
    param([string[]]$ArgumentList)
    $result = & $wslExe --distribution $Distro --user root --exec @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "WSL 命令失败（退出码 $LASTEXITCODE）：$($ArgumentList -join ' ')。请检查发行版 $Distro 和上方错误。"
    }
    return ($result | Out-String).Trim()
}

try {
    Write-Host "正在启动 Sakura（WSL: $Distro）..."
    # systemd services alone do not keep a WSL distribution alive. Keep one
    # client attached while waiting for HTTP startup and while the console is open.
    $keepAlive = Start-Process -FilePath $wslExe -WindowStyle Hidden -PassThru -ArgumentList @(
        '--distribution', $Distro, '--user', 'root', '--exec', '/usr/bin/sleep', 'infinity'
    )
    $windowsProjectPath = $PSScriptRoot.Replace('\', '/')
    $linuxProjectPath = Invoke-SakuraWsl @('/usr/bin/wslpath', '-u', $windowsProjectPath)
    if ($Install) {
        & $wslExe --distribution $Distro --user root --exec /usr/bin/python3 "$linuxProjectPath/scripts/install_wsl.py"
        if ($LASTEXITCODE -ne 0) { throw "安装失败，请查看上方错误。" }
    }
    $loadState = Invoke-SakuraWsl @('/bin/systemctl', 'show', 'sakura.service', '--property=LoadState', '--value')
    if ($loadState -ne 'loaded') { throw "服务尚未安装，请按 README.md 安装依赖后执行 .\run.ps1 -Install。" }
    $serviceDirectory = Invoke-SakuraWsl @('/bin/systemctl', 'show', 'sakura.service', '--property=WorkingDirectory', '--value')
    if ($serviceDirectory -ne $linuxProjectPath) {
        throw "已安装服务指向 $serviceDirectory，当前项目为 $linuxProjectPath。请执行 .\run.ps1 -Install 更新服务路径。"
    }
    $operation = if ($Restart) { 'restart' } else { 'start' }
    $null = Invoke-SakuraWsl @('/bin/systemctl', $operation, 'sakura.service')
    $serviceCommand = Invoke-SakuraWsl @('/bin/systemctl', 'show', 'sakura.service', '--property=ExecStart', '--value')
    if ($serviceCommand -notmatch '--port(?:=|\s+)([0-9]+)') {
        throw "无法从 sakura.service 读取监听端口，请检查服务的 ExecStart。"
    }
    $serviceUrl = "http://localhost:$($Matches[1])"
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $health = $null
    do {
        if ($keepAlive.HasExited) { throw "WSL 会话意外退出，请检查发行版 $Distro 是否可以启动。" }
        try {
            $probe = Invoke-RestMethod -Uri "$serviceUrl/health" -TimeoutSec 3
            if ($probe.status -eq 'ok' -and $probe.modules -contains 'oj' -and $probe.modules -contains 'studio') {
                $health = $probe
                break
            }
        } catch {
            # The app and WSL localhost forwarding may need a few seconds.
        }
        Start-Sleep -Seconds 1
    } while ($timer.Elapsed.TotalSeconds -lt $StartupTimeoutSeconds)
    if (-not $health) {
        & $wslExe --distribution $Distro --user root --exec /bin/journalctl --unit sakura.service --no-pager --lines 25
        throw "等待 $StartupTimeoutSeconds 秒后仍无法访问 $serviceUrl/health。请检查上方日志和 WSL 的 localhost 转发。"
    }

    Write-Host "Sakura 已启动" -ForegroundColor Green
    Write-Host "OJ / 题库 / 账号管理：$serviceUrl/"
    Write-Host "录题工作台：          $serviceUrl/studio/"
    Write-Host "集训队管理：          $serviceUrl/team/"
    if ($health.judge.ready) {
        Write-Host "评测机已就绪：$($health.judge.languages -join '、')" -ForegroundColor Green
    } else {
        Write-Warning "网页可访问，但评测机未就绪：$($health.judge.error)"
    }
    if ($OpenBrowser) { Start-Process $serviceUrl }
    Write-Host "请保留此窗口以保持 WSL 运行。Ctrl+C 结束本次会话；关闭后可再次运行脚本。"
    if ($Quiet) {
        while (-not $keepAlive.WaitForExit(1000)) { }
        throw "WSL 会话已结束，请重新运行脚本。"
    } else {
        & $wslExe --distribution $Distro --user root --exec /bin/journalctl --follow --unit sakura.service --no-pager --lines 10
        if ($LASTEXITCODE -ne 0) { throw "服务日志会话已结束（退出码 $LASTEXITCODE）。" }
    }
} finally {
    if ($null -ne $keepAlive -and -not $keepAlive.HasExited) {
        Stop-Process -Id $keepAlive.Id -ErrorAction SilentlyContinue
    }
}
