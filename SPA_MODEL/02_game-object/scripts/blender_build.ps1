$ErrorActionPreference = "Stop"

$projectRoot = [System.Environment]::GetEnvironmentVariable("PROJECT_ROOT")
if (-not $projectRoot -or $projectRoot -eq "") {
    $projectRoot = "C:\Users\honra\HONRAI_FACTORY"
}

. (Join-Path $projectRoot "SPA_MODEL\02_game-object\_lib\paths.ps1")
$gp = Get-GameObjectLinePaths -ProjectRoot $projectRoot

$blenderDir = $gp.BlenderDir
$inputDir = $gp.InputAssets
$outputDir = $gp.OutputAssets
$scriptsDir = $gp.BlenderScripts
$logsDir = $gp.RepoLogs
$logPath = Join-Path $logsDir "blender_build.log"
$optimizeScript = Join-Path $scriptsDir "optimize_fbx.py"
$exportScript = Join-Path $scriptsDir "export_gltf.py"
$preprocessScript = Join-Path $scriptsDir "fbx_preprocess.py"
$lineScripts = $gp.LineScripts
$notifyScript = Join-Path $lineScripts "notify_blender_build.py"
$importScript = Join-Path $lineScripts "import_generated_assets.ps1"
$unityImportLog = Join-Path $logsDir "unity_import.log"

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputDir -Force | Out-Null
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

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

function Write-BuildLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp [$Level] $Message"
    Add-Content -Path $logPath -Value $line -Force
    Write-Host $line
}

function Get-LogTail {
    param(
        [string]$Path,
        [int]$Lines = 20
    )

    if (-not (Test-Path $Path)) {
        return "(log file not found: $Path)"
    }

    return ((Get-Content -Path $Path -Tail $Lines -ErrorAction SilentlyContinue) -join "`n")
}

function Send-DiscordNotification {
    param(
        [string]$Status,
        [string[]]$OutputFiles,
        [string]$ErrorMessage = "",
        [string]$LogFile = "",
        [int]$LogLines = 20
    )

    $webhookUrl = Load-EnvValue -Name "DISCORD_WEBHOOK_URL"
    if (-not $webhookUrl) {
        Write-BuildLog "DISCORD_WEBHOOK_URL is not set. Skipping Discord notification." "WARN"
        return
    }

    $pythonExe = $env:PYTHON_EXE
    if (-not $pythonExe -or $pythonExe -eq "") {
        $pythonExe = "python"
    }

    if (-not (Test-Path $notifyScript)) {
        Write-BuildLog "Discord notify script not found: $notifyScript" "WARN"
        return
    }

    $notifyArgs = @(
        $notifyScript,
        "--repo-root", $projectRoot,
        "--webhook-url", $webhookUrl,
        "--status", $Status,
        "--log-lines", $LogLines
    )

    if ($LogFile) {
        $notifyArgs += @("--log-file", $LogFile)
    }

    if ($ErrorMessage) {
        $notifyArgs += @("--error", $ErrorMessage)
    }

    foreach ($file in $OutputFiles) {
        $notifyArgs += @("--output-file", $file)
    }

    & $pythonExe @notifyArgs
}

function Find-BlenderExe {
    param(
        [string]$ConfiguredPath
    )

    if ($ConfiguredPath -and (Test-Path $ConfiguredPath)) {
        return $ConfiguredPath
    }

    $hubRoots = @(
        "C:\Program Files\Blender Foundation",
        "C:\Program Files (x86)\Blender Foundation"
    )

    foreach ($hubRoot in $hubRoots) {
        if (-not (Test-Path $hubRoot)) {
            continue
        }

        $versions = Get-ChildItem -Path $hubRoot -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending

        foreach ($version in $versions) {
            $candidate = Join-Path $version.FullName "blender.exe"
            if (Test-Path $candidate) {
                return $candidate
            }
        }
    }

    $fallbackCandidates = @(
        "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
    )

    foreach ($candidate in $fallbackCandidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Resolve-PythonExe {
    param(
        [string]$Root
    )

    $venvPython = Join-Path $Root ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        return $venvPython
    }

    return "python"
}

function Resolve-ProcessedFbx {
    param(
        [string]$PythonExe,
        [string]$PreprocessScript,
        [string]$InputFbx,
        [string]$LogFile
    )

    if (-not (Test-Path $PreprocessScript)) {
        return $InputFbx
    }

    Write-BuildLog "Preprocessing FBX: $InputFbx"
    $outputLines = @(
        & $PythonExe $PreprocessScript --input $InputFbx --log $LogFile 2>&1
    )

    foreach ($line in $outputLines) {
        if ($line) {
            Write-BuildLog $line.ToString()
        }
    }

    if ($LASTEXITCODE -ne 0) {
        throw "fbx_preprocess failed for $InputFbx with exit code $LASTEXITCODE"
    }

    $processedFbx = $InputFbx
    foreach ($line in $outputLines) {
        if ($line -match '^OUTPUT_FBX=(.+)$') {
            $processedFbx = $Matches[1].Trim()
        }
    }

    if (-not (Test-Path $processedFbx)) {
        throw "Processed FBX not found: $processedFbx"
    }

    return $processedFbx
}

$blenderExe = Find-BlenderExe -ConfiguredPath (Load-EnvValue -Name "BLENDER_EXE")
if (-not $blenderExe) {
    $errorMessage = "Blender.exe not found. Set BLENDER_EXE in bot/.env."
    Write-BuildLog $errorMessage "ERROR"
    Send-DiscordNotification -Status "failed" -OutputFiles @() -ErrorMessage $errorMessage -LogFile $logPath
    Write-Error $errorMessage
    exit 1
}

$fbxFiles = @(Get-ChildItem -Path $inputDir -Filter "*.fbx" -File -ErrorAction SilentlyContinue)
if ($fbxFiles.Count -eq 0) {
    $errorMessage = "No FBX files found in input_assets: $inputDir"
    Write-BuildLog $errorMessage "ERROR"
    Send-DiscordNotification -Status "failed" -OutputFiles @() -ErrorMessage $errorMessage -LogFile $logPath
    Write-Error $errorMessage
    exit 1
}

$env:PROJECT_ROOT = $projectRoot
$pythonExe = Resolve-PythonExe -Root $projectRoot
$exportedFiles = @()
$startedAt = Get-Date

Write-BuildLog "Blender asset pipeline started."
Write-BuildLog "Blender: $blenderExe"
Write-BuildLog "Python: $pythonExe"
Write-BuildLog "Input dir: $inputDir"
Write-BuildLog "Output dir: $outputDir"
Write-BuildLog "FBX count: $($fbxFiles.Count)"

try {
    foreach ($fbxFile in $fbxFiles) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($fbxFile.Name)
        $optimizedBlend = Join-Path $outputDir "${stem}_optimized.blend"
        $outputGlb = Join-Path $outputDir "$stem.glb"

        Write-BuildLog "Processing: $($fbxFile.FullName)"

        $processedFbx = Resolve-ProcessedFbx -PythonExe $pythonExe -PreprocessScript $preprocessScript -InputFbx $fbxFile.FullName -LogFile $logPath
        Write-BuildLog "Using FBX input: $processedFbx"

        & $blenderExe `
            --background `
            --python $optimizeScript `
            -- `
            --input $processedFbx `
            --output-blend $optimizedBlend `
            --log $logPath

        if ($LASTEXITCODE -ne 0) {
            throw "optimize_fbx failed for $($fbxFile.Name) with exit code $LASTEXITCODE"
        }

        if (-not (Test-Path $optimizedBlend)) {
            throw "Optimized blend not created: $optimizedBlend"
        }

        & $blenderExe `
            --background `
            --python $exportScript `
            -- `
            --blend $optimizedBlend `
            --output $outputGlb `
            --format GLB `
            --log $logPath

        if ($LASTEXITCODE -ne 0) {
            throw "export_gltf failed for $($fbxFile.Name) with exit code $LASTEXITCODE"
        }

        if (-not (Test-Path $outputGlb)) {
            throw "glTF output not created: $outputGlb"
        }

        $exportedFiles += $outputGlb
        Write-BuildLog "Completed: $outputGlb"
    }

    $elapsed = (Get-Date) - $startedAt
    Write-BuildLog ("Blender asset pipeline complete. Exported {0} file(s) in {1:mm\:ss}." -f $exportedFiles.Count, $elapsed)

    Write-BuildLog "Starting Unity generated asset import..."
    $env:HONRAI_SKIP_IMPORT_DISCORD = "1"
    try {
        & $importScript
        $importExitCode = $LASTEXITCODE
    }
    finally {
        Remove-Item Env:HONRAI_SKIP_IMPORT_DISCORD -ErrorAction SilentlyContinue
    }

    if ($importExitCode -ne 0) {
        $importError = "Unity import failed with exit code $importExitCode"
        Write-BuildLog $importError "ERROR"
        Send-DiscordNotification -Status "import_failed" -OutputFiles $exportedFiles -LogFile $unityImportLog
        Write-Error $importError
        exit $importExitCode
    }

    Write-BuildLog "Unity generated asset import complete."
    Send-DiscordNotification -Status "pipeline_success" -OutputFiles $exportedFiles
    exit 0
}
catch {
    $errorMessage = $_.Exception.Message
    Write-BuildLog $errorMessage "ERROR"
    Send-DiscordNotification -Status "failed" -OutputFiles $exportedFiles -LogFile $logPath
    Write-Error $errorMessage
    exit 1
}
