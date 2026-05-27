import os
import sys
from pathlib import Path

from bot.utils.process_runner import run_command


def run_comfy_test() -> str:
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        # fall back to repository root
        project_root = str(Path(__file__).resolve().parents[2])

    script_path = Path(project_root) / "scripts" / "comfy" / "run_minimal_comfy_test.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Comfy test script not found: {script_path}")

    return run_command(
        [sys.executable, str(script_path)],
        cwd=project_root,
        log_name="comfy_test.log",
        wait=True,
    )
