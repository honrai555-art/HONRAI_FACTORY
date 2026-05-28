$ErrorActionPreference = "Stop"

$projectRoot = [System.Environment]::GetEnvironmentVariable("PROJECT_ROOT")
if (-not $projectRoot -or $projectRoot -eq "") {
    $projectRoot = "C:\Users\honra\HONRAI_FACTORY"
}
. (Join-Path $projectRoot "SPA_MODEL\02_game-object\_lib\paths.ps1")
$gp = Get-GameObjectLinePaths -ProjectRoot $projectRoot
$logsDir = Join-Path $projectRoot "logs"
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
$logPath = Join-Path $logsDir "unity.log"
$editorLogPath = Join-Path $logsDir "unity_editor.log"
$errorLogPath = Join-Path $logsDir "errors.log"

function Log-Message {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "$timestamp [$Level] $Message"
    Add-Content -Path $logPath -Value $logLine -Force
    Write-Host $logLine
}

function Log-Error {
    param([string]$Message)
    Log-Message -Message $Message -Level "ERROR"
    Add-Content -Path $errorLogPath -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [ERROR] $Message" -Force
}

try {
    Log-Message "Unity build started."
    
    # Load environment variables from bot/.env if available
    $botEnvPath = Join-Path $projectRoot "bot\.env"
    $unityExe = [System.Environment]::GetEnvironmentVariable("UNITY_EXE")
    $unityProjectPath = [System.Environment]::GetEnvironmentVariable("UNITY_PROJECT_PATH")
    $unityBuildMethod = [System.Environment]::GetEnvironmentVariable("UNITY_BUILD_METHOD")
    $unityBuildTarget = [System.Environment]::GetEnvironmentVariable("UNITY_BUILD_TARGET")

    # If env vars not set, try to load from .env file
    if (Test-Path $botEnvPath) {
        Log-Message "Loading settings from $botEnvPath"
        $envContent = Get-Content $botEnvPath -Raw
        
        if ($envContent -match 'UNITY_EXE=(.+)') {
            $unityExe = $Matches[1].Trim()
        }
        if ($envContent -match 'UNITY_PROJECT_PATH=(.+)') {
            $unityProjectPath = $Matches[1].Trim()
        }
        if ($envContent -match 'UNITY_BUILD_METHOD=(.+)') {
            $unityBuildMethod = $Matches[1].Trim()
        }
        if ($envContent -match 'UNITY_BUILD_TARGET=(.+)') {
            $unityBuildTarget = $Matches[1].Trim()
        }
    }

    # Auto-detect project path if not set
    if (-not $unityProjectPath -or $unityProjectPath -eq "") {
        Log-Message "UNITY_PROJECT_PATH not set. Auto-detecting Unity projects..."
        if (Test-Path $gp.UnityProject) {
            $unityProjectPath = $gp.UnityProject
            Log-Message "Auto-detected project: $unityProjectPath"
        }
    }

    # Check if project path is valid
    if (-not $unityProjectPath -or -not (Test-Path $unityProjectPath)) {
        Log-Error "UNITY_PROJECT_PATH is not set or invalid: $unityProjectPath"
        Write-Error "Unity project path not found. Please set UNITY_PROJECT_PATH in bot/.env"
        exit 1
    }

    # Verify Assets folder exists (sign of valid Unity project)
    if (-not (Test-Path (Join-Path $unityProjectPath "Assets"))) {
        Log-Error "Unity project at $unityProjectPath does not contain Assets folder"
        Write-Error "Invalid Unity project. Assets folder not found."
        exit 1
    }

    # Auto-detect Unity.exe if not set
    if (-not $unityExe -or $unityExe -eq "") {
        Log-Message "UNITY_EXE not set. Searching for Unity installation..."
        
        # Common Unity Hub paths
        $unityHubPaths = @(
            "C:\Program Files\Unity\Hub\Editor",
            "C:\Program Files (x86)\Unity\Hub\Editor"
        )
        
        $foundExe = $null
        foreach ($hubPath in $unityHubPaths) {
            if (Test-Path $hubPath) {
                $versions = @(Get-ChildItem -Path $hubPath -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending)
                if ($versions.Count -gt 0) {
                    $editorPath = Join-Path $versions[0].FullName "Editor\Unity.exe"
                    if (Test-Path $editorPath) {
                        $foundExe = $editorPath
                        Log-Message "Auto-detected Unity.exe: $foundExe"
                        break
                    }
                }
            }
        }
        
        if (-not $foundExe) {
            Log-Error "Could not find Unity.exe. Please set UNITY_EXE in bot/.env"
            Write-Error "Unity.exe not found. Please install Unity and set UNITY_EXE in bot/.env"
            exit 1
        }
        $unityExe = $foundExe
    }

    # Verify Unity.exe exists
    if (-not (Test-Path $unityExe)) {
        Log-Error "Unity.exe not found at: $unityExe"
        Write-Error "Unity.exe not found at specified path"
        exit 1
    }

    # Set default build parameters if not configured
    if (-not $unityBuildMethod -or $unityBuildMethod -eq "") {
        $unityBuildMethod = "BuildPipeline.BuildPlayer"
        Log-Message "UNITY_BUILD_METHOD not set. Using default: $unityBuildMethod"
    }

    if (-not $unityBuildTarget -or $unityBuildTarget -eq "") {
        $unityBuildTarget = "Win64"
        Log-Message "UNITY_BUILD_TARGET not set. Using default: $unityBuildTarget"
    }

    # Execute Unity batch build
    Log-Message "Starting Unity batchmode build..."
    Log-Message "Project: $unityProjectPath"
    Log-Message "Build Method: $unityBuildMethod"
    Log-Message "Build Target: $unityBuildTarget"

    $unityArgs = @(
        "-batchmode",
        "-quit",
        "-projectPath", "`"$unityProjectPath`"",
        "-executeMethod", $unityBuildMethod,
        "-logFile", "`"$editorLogPath`""
    )

    Write-Host "Executing: & `"$unityExe`" $($unityArgs -join ' ')"
    & $unityExe @unityArgs

    $exitCode = $LASTEXITCODE
    Log-Message "Unity build completed with exit code: $exitCode"

    if ($exitCode -eq 0) {
        Log-Message "Build successful."
        Write-Host "Build completed successfully."
    } else {
        Log-Error "Build failed with exit code: $exitCode. Check $editorLogPath for details."
        Write-Error "Build failed. Check logs for details."
        exit $exitCode
    }

} catch {
    $errorMsg = $_.Exception.Message
    Log-Error $errorMsg
    Write-Error $errorMsg
    exit 1
}

