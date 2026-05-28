"""Shared helpers for Blender batch-mode asset pipeline scripts."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path


def parse_script_args() -> list[str]:
    argv = sys.argv
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return []


def append_log(log_path: Path | None, message: str, level: str = "INFO") -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} [{level}] {message}"
    print(line, flush=True)
    if log_path is None:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(line + "\n")


def resolve_project_root() -> Path:
    env_root = __import__("os").environ.get("PROJECT_ROOT", "").strip()
    if env_root:
        return Path(env_root)
    return Path(__file__).resolve().parents[2]
