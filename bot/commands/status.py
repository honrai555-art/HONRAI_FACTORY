import subprocess
from pathlib import Path

import psutil


ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"
BLENDER_INPUT_DIR = ROOT_DIR / "blender" / "input_assets"
BLENDER_OUTPUT_DIR = ROOT_DIR / "blender" / "output_assets"
GENERATED_ASSETS_DIR = ROOT_DIR / "unityprojects" / "kaido-walk" / "Assets" / "Generated"


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


def _count_files(directory: Path, pattern: str) -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


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


def _last_log_timestamp(log_name: str, keywords: tuple[str, ...]) -> str:
    path = LOG_DIR / log_name
    if not path.exists():
        return "no log yet"

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in reversed(lines):
            lower = line.lower()
            if any(keyword in lower for keyword in keywords):
                timestamp = line[:19] if len(line) >= 19 else "unknown time"
                return f"{timestamp} | {line.strip()[:120]}"
        return "status unknown"
    except Exception:
        return "error reading log"


def _last_blender_status() -> str:
    return _last_log_timestamp(
        "blender_build.log",
        ("complete", "failed", "processing:", "import complete"),
    )


def _last_unity_import_status() -> str:
    return _last_log_timestamp(
        "unity_import.log",
        ("import complete", "imported", "failed", "starting"),
    )


def _last_unity_status() -> str:
    path = LOG_DIR / "unity_world_build.log"
    if not path.exists():
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
    blender_status = "RUNNING" if _is_process_running("blender.exe") else "STOPPED"

    blender_input_count = _count_files(BLENDER_INPUT_DIR, "*.fbx")
    blender_output_count = _count_files(BLENDER_OUTPUT_DIR, "*.glb")
    generated_asset_count = _count_files(GENERATED_ASSETS_DIR, "*.glb") + _count_files(
        GENERATED_ASSETS_DIR, "*.gltf"
    )

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
            "Blender Line",
            "------------",
            f"Status: {blender_status}",
            f"Input FBX: {blender_input_count}",
            f"Output glb: {blender_output_count}",
            f"Last build: {_last_blender_status()}",
            f"Error: {_last_error('blender_build.log')}",
            "",
            "Asset Watchdog",
            "--------------",
            f"Status: {'RUNNING' if _is_process_running('asset_watchdog.py') else 'STOPPED'}",
            f"Input FBX: {blender_input_count}",
            f"Last event: {_last_log_timestamp('asset_watchdog.log', ('detected', 'complete', 'failed', 'started'))}",
            f"Error: {_last_error('asset_watchdog.log')}",
            "",
            "Unity Line",
            "----------",
            f"Status: {unity_status}",
            f"Generated assets: {generated_asset_count}",
            f"Last import: {_last_unity_import_status()}",
            f"Import error: {_last_error('unity_import.log')}",
            f"Build: {_last_unity_status()}",
            f"Build error: {_last_error('unity_world_build.log')}",
        ]
    )
