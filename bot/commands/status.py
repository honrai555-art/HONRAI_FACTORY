import subprocess
from pathlib import Path

import psutil


ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"


def _gpu_usage() -> str:
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            first_gpu = completed.stdout.strip().splitlines()[0].strip()
            return f"{first_gpu}%"
    except Exception:
        pass
    return "N/A"


def _is_process_running(keyword: str) -> bool:
    keyword_lower = keyword.lower()
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            name = (proc.info.get("name") or "").lower()
            if keyword_lower in cmdline or keyword_lower in name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def _last_error(log_name: str) -> str:
    path = LOG_DIR / log_name
    if not path.exists():
        return "no log yet"

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in reversed(lines):
            if "[ERROR]" in line or "error:" in line.lower() or "ERROR:" in line:
                return line.strip()[:160]
        return "no errors logged"
    except Exception:
        return "error reading log"


def _last_unity_status() -> str:
    path = LOG_DIR / "unity.log"
    if not path.exists():
        return "no log yet"

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in reversed(lines):
            lower = line.lower()
            if "completed" in lower or "failed" in lower or "successful" in lower:
                return line.strip()[:160]
        return "build status unknown"
    except Exception:
        return "error reading log"


def get_status() -> str:
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    gpu = _gpu_usage()

    manga_status = "RUNNING" if _is_process_running("watch_manga_output.py") else "STOPPED"
    unity_status = "RUNNING" if _is_process_running("unity") else "STOPPED"

    return "\n".join(
        [
            "HONRAI_FACTORY STATUS",
            "=====================",
            "",
            f"CPU: {cpu:.0f}% | RAM: {ram:.0f}% | GPU: {gpu}",
            "",
            "Manga Line",
            "----------",
            f"Status: {manga_status}",
            f"Error: {_last_error('manga.log')}",
            "",
            "Unity Line",
            "----------",
            f"Status: {unity_status}",
            f"Build: {_last_unity_status()}",
            f"Error: {_last_error('unity.log')}",
        ]
    )
