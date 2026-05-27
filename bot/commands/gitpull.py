import os
from pathlib import Path

from bot.utils.process_runner import run_command


def run_gitpull() -> str:
    git_pull_dir = os.getenv("GIT_PULL_DIR") or os.getenv("PROJECT_ROOT")
    if not git_pull_dir:
        raise RuntimeError("GIT_PULL_DIR or PROJECT_ROOT is not configured in bot/.env")

    repo_dir = Path(git_pull_dir)
    if not (repo_dir / ".git").exists():
        candidates = [
            str(path.parent)
            for path in repo_dir.rglob(".git")
            if path.is_dir()
        ][:10]
        hint = "\n".join(candidates) if candidates else "No .git directories found under this path."
        raise RuntimeError(
            f"Git repository not found: {repo_dir}\n"
            f"Set GIT_PULL_DIR in bot/.env to a folder that contains .git.\n\n"
            f"Candidates:\n{hint}"
        )

    return run_command(["git", "pull"], cwd=repo_dir, log_name="bot.log", wait=True)
