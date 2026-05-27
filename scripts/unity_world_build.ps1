$ErrorActionPreference = "Stop"

$projectRoot = "C:\Users\honra\HONRAI_FACTORY"
$unityProjectPath = Join-Path $projectRoot "unityprojects\kaido-walk"
$logsDir = Join-Path $projectRoot "logs"
$logPath = Join-Path $logsDir "unity_world_build.log"

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
    Write-Error "Unity.exe が見つかりません。bot/.env に UNITY_EXE を設定してください。"
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

& $unityExe `
    -batchmode `
    -quit `
    -projectPath $unityProjectPath `
    -executeMethod GenerateWorldFromJson.Run `
    -logFile $logPath

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Error "Unity world build failed with exit code $exitCode. See $logPath"
    exit $exitCode
}

Write-Host "Unity world build complete."
Write-Host "Preview: $(Join-Path $projectRoot 'BuildPreviews\preview.png')"
