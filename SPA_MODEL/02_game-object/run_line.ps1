# 02_game-object 単独起動 — Blender → Unity import → Unity world → Discord 通知
$ErrorActionPreference = "Stop"
$lineRoot = $PSScriptRoot
$repo = if ($env:PROJECT_ROOT) { $env:PROJECT_ROOT } else { Split-Path (Split-Path $lineRoot -Parent) -Parent }
$logDir = Join-Path $lineRoot "logs"
$libRoot = Join-Path (Split-Path $lineRoot -Parent) "_lib"
. (Join-Path $libRoot "Write-LineLog.ps1")
. (Join-Path $libRoot "Read-BotEnv.ps1")
. (Join-Path $lineRoot "_lib\paths.ps1")

$gp = Get-GameObjectLinePaths -ProjectRoot $repo
if (-not $env:PROJECT_ROOT) { $env:PROJECT_ROOT = $repo }

$fbxCount = (Get-ChildItem $gp.InputAssets -Filter "*.fbx" -ErrorAction SilentlyContinue | Measure-Object).Count
Write-LineLog -LogDir $logDir -Level "INFO" -Message "02_game-object pipeline start. FBX=$fbxCount input=$($gp.InputAssets)"

if ($fbxCount -eq 0) {
    Write-LineLog -LogDir $logDir -Level "ERROR" -Message "No FBX in $($gp.InputAssets). Add slug-named .fbx files."
    exit 1
}

$python = if (Test-Path (Join-Path $repo ".venv\Scripts\python.exe")) {
    Join-Path $repo ".venv\Scripts\python.exe"
} else { "python" }

function Invoke-Step {
    param([string]$Name, [scriptblock]$Action)
    try {
        & $Action
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            throw "$Name exit code $LASTEXITCODE"
        }
        Write-LineLog -LogDir $logDir -Level "INFO" -Message "$Name OK"
    }
    catch {
        Write-LineLog -LogDir $logDir -Level "ERROR" -Message "$Name failed: $($_.Exception.Message)"
        throw
    }
}

try {
    Invoke-Step "Blender" { & (Join-Path $gp.LineScripts "blender_build.ps1") }
    Invoke-Step "UnityImport" { & (Join-Path $gp.LineScripts "import_generated_assets.ps1") }
    Invoke-Step "UnityWorld" { & (Join-Path $gp.LineScripts "unity_world_build.ps1") }

    $webhook = $env:DISCORD_WEBHOOK_URL
    if (-not $webhook) { $webhook = Get-BotEnvValue -Name "DISCORD_WEBHOOK_URL" }
    if ($webhook) {
        $glbs = @(Get-ChildItem $gp.OutputAssets -Filter "*.glb" -ErrorAction SilentlyContinue)
        $notifyArgs = @(
            $python,
            (Join-Path $gp.LineScripts "notify_blender_build.py"),
            "--repo-root", $repo,
            "--webhook-url", $webhook,
            "--status", "pipeline_success",
            "--preview", (Join-Path $gp.BuildPreviews "preview.png")
        )
        foreach ($g in $glbs) { $notifyArgs += @("--output-file", $g.FullName) }
        & @notifyArgs
        if ($LASTEXITCODE -ne 0) { throw "Discord notify exit $LASTEXITCODE" }
        Write-LineLog -LogDir $logDir -Level "INFO" -Message "Discord notification sent."
    }
    else {
        Write-LineLog -LogDir $logDir -Level "INFO" -Message "DISCORD_WEBHOOK_URL unset; skipped Discord notify."
    }

    Write-LineLog -LogDir $logDir -Level "INFO" -Message "02_game-object pipeline complete."
}
catch {
    exit 1
}
