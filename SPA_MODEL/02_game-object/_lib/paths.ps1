# 02_game-object ライン基準パス（PROJECT_ROOT = リポジトリルート）
function Get-GameObjectLinePaths {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot
    )
    $lineRoot = Join-Path $ProjectRoot "SPA_MODEL\02_game-object"
    $blenderDir = Join-Path $lineRoot "blender"
    $unityProject = Join-Path $lineRoot "unity\kaido-walk"
    @{
        LineRoot        = $lineRoot
        BlenderDir      = $blenderDir
        InputAssets     = Join-Path $blenderDir "input_assets"
        OutputAssets    = Join-Path $blenderDir "output_assets"
        BlenderScripts  = Join-Path $blenderDir "scripts"
        LineScripts     = Join-Path $lineRoot "scripts"
        UnityProject    = $unityProject
        GeneratedAssets = Join-Path $unityProject "Assets\Generated"
        LineLogs        = Join-Path $lineRoot "logs"
        RepoLogs        = Join-Path $ProjectRoot "logs"
        BuildPreviews   = Join-Path $ProjectRoot "BuildPreviews"
        Exports         = Join-Path $lineRoot "exports"
    }
}
