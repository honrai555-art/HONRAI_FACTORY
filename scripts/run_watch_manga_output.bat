@echo off
setlocal enabledelayedexpansion
if not defined DISCORD_WEBHOOK_URL (
  echo Usage: %~n0
  echo.
  echo Set DISCORD_WEBHOOK_URL environment variable first.
  exit /b 1
)
python "%~dp0..\watch_manga_output.py" --webhook-url "%DISCORD_WEBHOOK_URL%"
endlocal
