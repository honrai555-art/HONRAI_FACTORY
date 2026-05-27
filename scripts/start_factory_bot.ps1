$ErrorActionPreference = "Stop"

$projectRoot = [System.Environment]::GetEnvironmentVariable("PROJECT_ROOT")
if (-not $projectRoot -or $projectRoot -eq "") {
    $projectRoot = "C:\Users\honra\HONRAI_FACTORY"
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$botScript = Join-Path $projectRoot "bot\factory_bot.py"
$envPath = Join-Path $projectRoot "bot\.env"
$logsDir = Join-Path $projectRoot "logs"
$logPath = Join-Path $logsDir "bot.log"
$restartDelaySec = 5
$restartExitCode = 10

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

function Write-WatchdogLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [$Level] watchdog: $Message"
    Add-Content -Path $logPath -Value $line -Encoding UTF8
    Write-Host $line
}

function Load-EnvValue {
    param(
        [string]$Name,
        [string]$Default = ""
    )

    $value = [System.Environment]::GetEnvironmentVariable($Name)
    if ($value) {
        return $value.Trim()
    }

    if (Test-Path $envPath) {
        $match = Select-String -Path $envPath -Pattern "^$Name=(.+)$" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($match) {
            return $match.Matches[0].Groups[1].Value.Trim()
        }
    }

    return $Default
}

function Test-BotEnvironment {
    $missing = @()
    $recommended = @("DISCORD_WEBHOOK_URL", "PROJECT_ROOT", "UNITY_EXE")

    $token = Load-EnvValue -Name "DISCORD_TOKEN"
    if (-not $token) {
        $missing += "DISCORD_TOKEN"
    }

    foreach ($key in $recommended) {
        if (-not (Load-EnvValue -Name $key)) {
            Write-WatchdogLog "Recommended env key is missing: $key" "WARN"
        }
    }

    if ($missing.Count -gt 0) {
        Write-WatchdogLog ("Missing required env keys: " + ($missing -join ", ")) "ERROR"
        return $false
    }

    return $true
}

if (-not (Test-Path $pythonExe)) {
    Write-WatchdogLog "Python venv not found: $pythonExe" "ERROR"
    Write-Error "Create venv first: python -m venv .venv && .\.venv\Scripts\pip install -r bot\requirements.txt"
    exit 1
}

if (-not (Test-Path $botScript)) {
    Write-WatchdogLog "Bot script not found: $botScript" "ERROR"
    Write-Error "Bot script not found: $botScript"
    exit 1
}

if (-not (Test-Path $envPath)) {
    Write-WatchdogLog "bot/.env not found: $envPath" "ERROR"
    Write-Error "Create bot/.env from bot/.env.example and set DISCORD_TOKEN."
    exit 1
}

if (-not (Test-BotEnvironment)) {
    Write-Error "Bot environment check failed. Fix bot/.env and retry."
    exit 1
}

$env:PROJECT_ROOT = Load-EnvValue -Name "PROJECT_ROOT" -Default $projectRoot
if (-not $env:PROJECT_ROOT) {
    $env:PROJECT_ROOT = $projectRoot
}
$env:HONRAI_WATCHDOG = "1"

Write-WatchdogLog "Factory bot watchdog started."
Write-WatchdogLog "Project root: $($env:PROJECT_ROOT)"
Write-WatchdogLog "Python: $pythonExe"
Write-WatchdogLog "Press Ctrl+C to stop."

while ($true) {
    Write-WatchdogLog "Starting factory_bot.py..."

    try {
        & $pythonExe $botScript
        $exitCode = $LASTEXITCODE
    }
    catch {
        $exitCode = 1
        Write-WatchdogLog "Process launch failed: $($_.Exception.Message)" "ERROR"
    }

    if ($exitCode -eq $restartExitCode) {
        Write-WatchdogLog "!restart received. Restarting in ${restartDelaySec}s..."
    }
    elseif ($exitCode -eq 0) {
        Write-WatchdogLog "Bot exited cleanly (code 0). Restarting in ${restartDelaySec}s..."
    }
    else {
        Write-WatchdogLog "Bot crashed or failed (code $exitCode). Restarting in ${restartDelaySec}s..." "ERROR"
    }

    Start-Sleep -Seconds $restartDelaySec
}
