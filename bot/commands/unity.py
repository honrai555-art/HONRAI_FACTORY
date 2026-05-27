import os
from pathlib import Path

from bot.utils.process_runner import run_powershell
from bot.utils.logger import get_logger

logger = get_logger("unity")


def run_unity() -> str:
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise RuntimeError("PROJECT_ROOT is not configured in bot/.env")

    ps1_path = Path(project_root) / "scripts" / "unity_build.ps1"
    if not ps1_path.exists():
        raise FileNotFoundError(f"Unity build script not found: {ps1_path}")

    # Check Unity configuration
    unity_exe = os.getenv("UNITY_EXE", "").strip()
    unity_project_path = os.getenv("UNITY_PROJECT_PATH", "").strip()
    
    config_info = "Unity build configuration:\n"
    if unity_exe:
        config_info += f"  UNITY_EXE: {unity_exe}\n"
    else:
        config_info += f"  UNITY_EXE: (auto-detect)\n"
    
    if unity_project_path:
        config_info += f"  UNITY_PROJECT_PATH: {unity_project_path}\n"
    else:
        config_info += f"  UNITY_PROJECT_PATH: (auto-detect from unityprojects/)\n"
    
    logger.info(config_info)

    return run_powershell(
        f"& '{ps1_path}'",
        cwd=project_root,
        log_name="unity.log",
        wait=False,
    )
