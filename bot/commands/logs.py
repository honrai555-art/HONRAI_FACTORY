from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"
LOG_FILES = ["bot.log", "errors.log", "manga.log", "unity.log"]


def _tail(path: Path, lines: int = 30) -> str:
    if not path.exists():
        return "(not created yet)"

    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(content[-lines:]) if content else "(empty)"


def get_latest_logs() -> str:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    sections = []
    for log_file in LOG_FILES:
        sections.append(f"--- {log_file} ---\n{_tail(LOG_DIR / log_file)}")
    return "\n\n".join(sections)
