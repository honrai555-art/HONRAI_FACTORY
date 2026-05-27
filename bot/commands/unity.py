import os
from pathlib import Path

from bot.utils.process_runner import run_powershell
from bot.utils.logger import get_logger

logger = get_logger("unity")


def run_import_generated_assets(*, wait: bool = False) -> str:
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise RuntimeError("PROJECT_ROOT is not configured in bot/.env")

    ps1_path = Path(project_root) / "scripts" / "import_generated_assets.ps1"
    if not ps1_path.exists():
        raise FileNotFoundError(f"Import script not found: {ps1_path}")

    source_dir = Path(project_root) / "blender" / "output_assets"
    target_dir = Path(project_root) / "unityprojects" / "kaido-walk" / "Assets" / "Generated"
    glb_count = len(list(source_dir.glob("*.glb"))) if source_dir.exists() else 0
    gltf_count = len(list(source_dir.glob("*.gltf"))) if source_dir.exists() else 0

    config_info = "Unity generated asset import configuration:\n"
    config_info += f"  Script: {ps1_path.name}\n"
    config_info += f"  Source: {source_dir}\n"
    config_info += f"  Target: {target_dir}\n"
    config_info += f"  glb files: {glb_count}\n"
    config_info += f"  gltf files: {gltf_count}\n"

    logger.info(config_info)

    return run_powershell(
        f"& '{ps1_path}'",
        cwd=project_root,
        log_name="unity_import.log",
        wait=wait,
    )


def run_unity_world_build(*, wait: bool = False, import_assets: bool = True) -> str:
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise RuntimeError("PROJECT_ROOT is not configured in bot/.env")

    ps1_path = Path(project_root) / "scripts" / "unity_world_build.ps1"
    import_ps1_path = Path(project_root) / "scripts" / "import_generated_assets.ps1"
    if not ps1_path.exists():
        raise FileNotFoundError(f"Unity world build script not found: {ps1_path}")

    json_path = Path(project_root) / "world_request.json"
    config_info = "Unity world build configuration:\n"
    config_info += f"  Script: {ps1_path.name}\n"
    config_info += f"  Import: {import_ps1_path.name if import_assets else '(skipped)'}\n"
    config_info += f"  JSON: {json_path}\n"
    config_info += f"  Preview: {Path(project_root) / 'BuildPreviews' / 'preview.png'}\n"

    unity_exe = os.getenv("UNITY_EXE", "").strip()
    if unity_exe:
        config_info += f"  UNITY_EXE: {unity_exe}\n"
    else:
        config_info += "  UNITY_EXE: (auto-detect)\n"

    logger.info(config_info)

    if import_assets and import_ps1_path.exists():
        command = (
            f"& '{import_ps1_path}'; "
            f"if ($LASTEXITCODE -ne 0) {{ exit $LASTEXITCODE }}; "
            f"& '{ps1_path}'"
        )
    else:
        command = f"& '{ps1_path}'"

    return run_powershell(
        command,
        cwd=project_root,
        log_name="unity_world_build.log",
        wait=wait,
    )


def run_unity() -> str:
    return run_unity_world_build(wait=False, import_assets=True)
