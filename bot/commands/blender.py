import os
from pathlib import Path

from bot.utils.process_runner import run_powershell
from bot.utils.logger import get_logger

logger = get_logger("blender")


def run_blender_build(*, wait: bool = False) -> str:
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise RuntimeError("PROJECT_ROOT is not configured in bot/.env")

    root = Path(project_root)
    ps1_path = root / "scripts" / "blender_build.ps1"
    import_ps1_path = root / "scripts" / "import_generated_assets.ps1"
    if not ps1_path.exists():
        raise FileNotFoundError(f"Blender build script not found: {ps1_path}")

    input_dir = root / "blender" / "input_assets"
    output_dir = root / "blender" / "output_assets"
    generated_dir = root / "unityprojects" / "kaido-walk" / "Assets" / "Generated"
    fbx_count = len(list(input_dir.glob("*.fbx"))) if input_dir.exists() else 0

    config_info = "Blender asset pipeline configuration:\n"
    config_info += f"  Script: {ps1_path.name}\n"
    config_info += f"  Import: {import_ps1_path.name} (auto after build)\n"
    config_info += f"  Input: {input_dir}\n"
    config_info += f"  Output: {output_dir}\n"
    config_info += f"  Unity target: {generated_dir}\n"
    config_info += f"  FBX files: {fbx_count}\n"

    blender_exe = os.getenv("BLENDER_EXE", "").strip()
    if blender_exe:
        config_info += f"  BLENDER_EXE: {blender_exe}\n"
    else:
        config_info += "  BLENDER_EXE: (auto-detect)\n"

    if fbx_count == 0:
        config_info += "\nWarning: blender/input_assets に FBX がありません。"

    logger.info(config_info)

    return run_powershell(
        f"& '{ps1_path}'",
        cwd=project_root,
        log_name="blender_build.log",
        wait=wait,
    )


def run_blender() -> str:
    return run_blender_build(wait=False)
