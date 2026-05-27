import os
import sys
from pathlib import Path

from bot.utils.process_runner import run_command


def run_pipeline_manga() -> str:
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise RuntimeError("PROJECT_ROOT is not configured in bot/.env")

    root = Path(project_root)
    orchestrator = root / "scripts" / "orchestrator.py"
    pipeline = root / "pipelines" / "manga.yaml"

    if not orchestrator.exists():
        raise FileNotFoundError(f"Orchestrator not found: {orchestrator}")
    if not pipeline.exists():
        raise FileNotFoundError(f"Pipeline not found: {pipeline}")

    return run_command(
        [sys.executable, str(orchestrator), str(pipeline)],
        cwd=project_root,
        log_name="pipeline_manga.log",
        wait=True,
    )
