@echo off
setlocal enabledelayedexpansion
if "%~1"=="" (
  if "%DISCORD_WEBHOOK_URL%"=="" (
    echo Usage: %~n0 ^<preview-image-path^> [webhook-url]
    echo   or set DISCORD_WEBHOOK_URL environment variable.
    exit /b 1
  )
  set "PREVIEW=%~1"
  set "WEBHOOK_URL=%DISCORD_WEBHOOK_URL%"
) else if "%~2"=="" (
  set "PREVIEW=%~1"
  set "WEBHOOK_URL=%DISCORD_WEBHOOK_URL%"
) else (
  set "PREVIEW=%~1"
  set "WEBHOOK_URL=%~2"
)
if not defined PREVIEW set "PREVIEW=..\output\manga\preview.png"
if not defined WEBHOOK_URL (
  echo ERROR: Discord webhook URL not provided.
  exit /b 1
)
python "%~dp0discord_webhook_notify.py" --webhook-url "%WEBHOOK_URL%" --preview "%PREVIEW%"
endlocal
