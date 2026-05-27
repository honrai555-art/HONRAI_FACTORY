@echo off
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\.."
set "COMFYUI_ROOT=%SCRIPT_DIR%ComfyUI-master"
set "PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"
if not exist "%COMFYUI_ROOT%\main.py" (
  echo ERROR: ComfyUI not found at "%COMFYUI_ROOT%"
  exit /b 1
)
if not exist "%PYTHON%" (
  echo ERROR: .venv python not found at "%PYTHON%"
  exit /b 1
)
cd /d "%COMFYUI_ROOT%"
echo Launching ComfyUI from %COMFYUI_ROOT%
echo API: http://127.0.0.1:8188
"%PYTHON%" main.py --listen 127.0.0.1 --port 8188
endlocal
