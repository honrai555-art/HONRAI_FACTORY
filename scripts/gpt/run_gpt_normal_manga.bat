@echo off
setlocal enabledelayedexpansion
if "%~1"=="" (
  echo Usage: %~n0 "instruction text"
  echo.
  echo Example: %~n0 "KAIDO WALKの普通の漫画。主人公が街道で歴史AIに出会う回を作る"
  exit /b 1
)
if not defined OPENAI_API_KEY (
  echo ERROR: OPENAI_API_KEY environment variable is not set.
  exit /b 1
)
python "%~dp0gpt_manga_generate.py" --type normal --instruction "%~1"
endlocal
