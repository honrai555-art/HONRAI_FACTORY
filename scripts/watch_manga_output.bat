@echo off
setlocal enabledelayedexpansion
set "WEBHOOK_URL=%DISCORD_WEBHOOK_URL%"
if not "%~1"=="" set "WEBHOOK_URL=%~1"
if not defined WEBHOOK_URL (
  echo Usage: %~n0 [webhook-url]
  echo Or set DISCORD_WEBHOOK_URL environment variable.
  exit /b 1
)
python "%~dp0watch_manga_output.py" --webhook-url "%WEBHOOK_URL%"
endlocal
