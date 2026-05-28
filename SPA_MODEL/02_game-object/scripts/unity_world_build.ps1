$ErrorActionPreference = "Stop"

$projectRoot = [System.Environment]::GetEnvironmentVariable("PROJECT_ROOT")
if (-not $projectRoot -or $projectRoot -eq "") {
    $projectRoot = "C:\Users\honra\HONRAI_FACTORY"
}

. (Join-Path $projectRoot "SPA_MODEL\02_game-object\_lib\paths.ps1")
$gp = Get-GameObjectLinePaths -ProjectRoot $projectRoot

$unityProjectPath = $gp.UnityProject
$logsDir = $gp.RepoLogs
$logPath = Join-Path $logsDir "unity_world_build.log"
$unityBatchLogPath = Join-Path $logsDir "unity_world_build_batch.log"
$previewPath = Join-Path $gp.BuildPreviews "preview.png"

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot "BuildPreviews") -Force | Out-Null

function Load-EnvValue {
    param(
        [string]$Name,
        [string]$Default = ""
    )

    $value = [System.Environment]::GetEnvironmentVariable($Name)
    if ($value) {
        return $value.Trim()
    }

    $botEnvPath = Join-Path $projectRoot "bot\.env"
    if (Test-Path $botEnvPath) {
        $match = Select-String -Path $botEnvPath -Pattern "^$Name=(.+)$" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($match) {
            return $match.Matches[0].Groups[1].Value.Trim()
        }
    }

    return $Default
}

$unityExe = Load-EnvValue -Name "UNITY_EXE"
if (-not $unityExe -or -not (Test-Path $unityExe)) {
    $hubPaths = @(
        "C:\Program Files\Unity\Hub\Editor",
        "C:\Program Files (x86)\Unity\Hub\Editor"
    )

    foreach ($hubPath in $hubPaths) {
        if (-not (Test-Path $hubPath)) { continue }
        $versions = Get-ChildItem -Path $hubPath -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
        foreach ($version in $versions) {
            $candidate = Join-Path $version.FullName "Editor\Unity.exe"
            if (Test-Path $candidate) {
                $unityExe = $candidate
                break
            }
        }
        if ($unityExe) { break }
    }
}

if (-not $unityExe -or -not (Test-Path $unityExe)) {
    Write-Error "Unity.exe not found. Set UNITY_EXE in bot/.env"
    exit 1
}

if (-not (Test-Path $unityProjectPath)) {
    Write-Error "Unity project not found: $unityProjectPath"
    exit 1
}

$env:PROJECT_ROOT = $projectRoot

Write-Host "Unity world build starting..."
Write-Host "Project: $unityProjectPath"
Write-Host "Log: $logPath"

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logPath -Value "$timestamp [INFO] === Unity world build started (PS1) ===" -Encoding UTF8

& $unityExe `
    -batchmode `
    -quit `
    -projectPath $unityProjectPath `
    -executeMethod GenerateWorldFromJson.Run `
    -logFile $unityBatchLogPath

$exitCode = $LASTEXITCODE
if ($null -eq $exitCode -or $exitCode -eq "") {
    $exitCode = 0
}

$logTail = ""
if (Test-Path $logPath) {
    $logTail = (Get-Content $logPath -Tail 40 -Encoding UTF8 -ErrorAction SilentlyContinue) -join "`n"
}
$batchTail = ""
if (Test-Path $unityBatchLogPath) {
    $batchTail = (Get-Content $unityBatchLogPath -Tail 20 -Encoding UTF8 -ErrorAction SilentlyContinue) -join "`n"
}

$buildComplete = $logTail -match "Unity world build complete" -or $logTail -match "=== Unity world build complete ==="
$previewOk = Test-Path $previewPath

if ($exitCode -ne 0 -and ($buildComplete -or $previewOk)) {
    Write-Host "Unity reported exit code $exitCode but build log/preview indicate success. Treating as success."
    $exitCode = 0
}

if ($exitCode -ne 0) {
    $msg = "Unity world build failed with exit code $exitCode. See $logPath and $unityBatchLogPath"
    Add-Content -Path $logPath -Value "$timestamp [ERROR] $msg" -Encoding UTF8
    Write-Error $msg
    exit [int]($exitCode -as [int])
}

Add-Content -Path $logPath -Value "$timestamp [INFO] === Unity world build complete (PS1) ===" -Encoding UTF8
Write-Host "Unity world build complete."
Write-Host "Preview: $previewPath"
