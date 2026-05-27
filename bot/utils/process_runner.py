import os
import subprocess
from pathlib import Path

from bot.utils.logger import get_logger, log_exception


logger = get_logger("process_runner")
ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"


def run_command(
    command: list[str],
    cwd: str | Path | None = None,
    log_name: str = "bot.log",
    wait: bool = True,
) -> str:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / log_name
    working_dir = Path(cwd) if cwd else ROOT_DIR

    logger.info("Running command: %s cwd=%s wait=%s", " ".join(command), working_dir, wait)

    try:
        if wait:
            completed = subprocess.run(
                command,
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
            )
            output = "\n".join(
                part for part in [completed.stdout.strip(), completed.stderr.strip()] if part
            )
            if not output:
                output = f"Command finished with exit code {completed.returncode}."

            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(f"\n$ {' '.join(command)}\n{output}\n")

            if completed.returncode != 0:
                raise RuntimeError(output)

            return output

        log_file = log_path.open("a", encoding="utf-8")
        process = subprocess.Popen(
            command,
            cwd=str(working_dir),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            shell=False,
        )
        return f"Started process PID={process.pid}: {' '.join(command)}"

    except Exception as exc:
        log_exception(logger, "Process command failed", exc)
        raise


def run_powershell(
    command: str,
    cwd: str | Path | None = None,
    log_name: str = "bot.log",
    wait: bool = True,
) -> str:
    powershell = os.getenv("POWERSHELL_EXE", "powershell")
    return run_command(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=cwd,
        log_name=log_name,
        wait=wait,
    )
