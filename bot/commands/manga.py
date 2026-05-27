import os
import sys
from pathlib import Path

from bot.utils.process_runner import run_command


def run_manga() -> str:
    project_root = os.getenv("PROJECT_ROOT")
    if not project_root:
        raise RuntimeError("PROJECT_ROOT is not configured in bot/.env")

    script_path = Path(project_root) / "scripts" / "watch_manga_output.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Manga script not found: {script_path}")

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook_url:
        raise RuntimeError(
            "DISCORD_WEBHOOK_URL is not configured in bot/.env.\n"
            "Please set DISCORD_WEBHOOK_URL to your Discord webhook URL to enable manga output notifications."
        )

    return run_command(
        [sys.executable, str(script_path), "--webhook-url", webhook_url],
        cwd=project_root,
        log_name="manga.log",
        wait=False,
    )
