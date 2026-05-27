$ErrorActionPreference = "Stop"

$projectRoot = [System.Environment]::GetEnvironmentVariable("PROJECT_ROOT")
if (-not $projectRoot -or $projectRoot -eq "") {
    $projectRoot = "C:\Users\honra\HONRAI_FACTORY"
}

$unityProjectPath = Join-Path $projectRoot "unityprojects\kaido-walk"
$logsDir = Join-Path $projectRoot "logs"
$logPath = Join-Path $logsDir "unity_import.log"
$sourceDir = Join-Path $projectRoot "blender\output_assets"
$targetDir = Join-Path $unityProjectPath "Assets\Generated"

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

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

function Write-ImportLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [$Level] $Message"
    Add-Content -Path $logPath -Value $line -Encoding UTF8
    Write-Host $line
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
    Write-ImportLog "Unity.exe not found. Set UNITY_EXE in bot/.env" "ERROR"
    Write-Error "Unity.exe not found. Set UNITY_EXE in bot/.env"
    exit 1
}

if (-not (Test-Path $unityProjectPath)) {
    Write-ImportLog "Unity project not found: $unityProjectPath" "ERROR"
    Write-Error "Unity project not found: $unityProjectPath"
    exit 1
}

$sourceFiles = @()
if (Test-Path $sourceDir) {
    $sourceFiles = @(
        Get-ChildItem -Path $sourceDir -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in @(".glb", ".gltf") }
    )
}

Write-ImportLog "Unity generated asset import starting..."
Write-ImportLog "Project: $unityProjectPath"
Write-ImportLog "Source: $sourceDir"
Write-ImportLog "Target: $targetDir"
Write-ImportLog "Source files: $($sourceFiles.Count)"

if ($sourceFiles.Count -eq 0) {
    Write-ImportLog "No glb/gltf files found in blender/output_assets. Import step skipped." "WARN"
    exit 0
}

$env:PROJECT_ROOT = $projectRoot

& $unityExe `
    -batchmode `
    -quit `
    -projectPath $unityProjectPath `
    -executeMethod ImportGeneratedAssets.Run `
    -logFile $logPath

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-ImportLog "Unity import failed with exit code $exitCode" "ERROR"
    Write-Error "Unity generated asset import failed with exit code $exitCode. See $logPath"
    exit $exitCode
}

Write-ImportLog "Unity generated asset import complete."
Write-Host "Generated assets imported to $targetDir"
