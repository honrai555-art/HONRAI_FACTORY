@echo off
setlocal enabledelayedexpansion
python "%~dp0run_comfy_generate_from_prompts.py" --limit 1
endlocal
