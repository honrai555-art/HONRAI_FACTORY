$ErrorActionPreference = "Stop"

$projectRoot = [System.Environment]::GetEnvironmentVariable("PROJECT_ROOT")
if (-not $projectRoot -or $projectRoot -eq "") {
    $projectRoot = "C:\Users\honra\HONRAI_FACTORY"
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$watchdogScript = Join-Path $projectRoot "bot\watchers\asset_watchdog.py"
$inputDir = Join-Path $projectRoot "blender\input_assets"
$envPath = Join-Path $projectRoot "bot\.env"
$logsDir = Join-Path $projectRoot "logs"
$logPath = Join-Path $logsDir "asset_watchdog.log"
$restartDelaySec = 5

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputDir -Force | Out-Null

function Write-WatchdogLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [$Level] asset-watchdog: $Message"
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

if (-not (Test-Path $pythonExe)) {
    Write-WatchdogLog "Python venv not found: $pythonExe" "ERROR"
    Write-Error "Create venv first: python -m venv .venv && .\.venv\Scripts\pip install -r bot\requirements.txt"
    exit 1
}

if (-not (Test-Path $watchdogScript)) {
    Write-WatchdogLog "Watchdog script not found: $watchdogScript" "ERROR"
    Write-Error "Watchdog script not found: $watchdogScript"
    exit 1
}

$env:PROJECT_ROOT = Load-EnvValue -Name "PROJECT_ROOT" -Default $projectRoot
if (-not $env:PROJECT_ROOT) {
    $env:PROJECT_ROOT = $projectRoot
}

Write-WatchdogLog "Asset watchdog supervisor started."
Write-WatchdogLog "Project root: $($env:PROJECT_ROOT)"
Write-WatchdogLog "Input dir: $inputDir"
Write-WatchdogLog "Python: $pythonExe"
Write-WatchdogLog "Press Ctrl+C to stop."

while ($true) {
    Write-WatchdogLog "Starting asset_watchdog.py..."

    try {
        & $pythonExe $watchdogScript --project-root $env:PROJECT_ROOT
        $exitCode = $LASTEXITCODE
    }
    catch {
        $exitCode = 1
        Write-WatchdogLog "Process launch failed: $($_.Exception.Message)" "ERROR"
    }

    if ($exitCode -eq 0) {
        Write-WatchdogLog "Watchdog exited cleanly. Restarting in ${restartDelaySec}s..."
    }
    else {
        Write-WatchdogLog "Watchdog crashed or failed (code $exitCode). Restarting in ${restartDelaySec}s..." "ERROR"
    }

    Start-Sleep -Seconds $restartDelaySec
}
