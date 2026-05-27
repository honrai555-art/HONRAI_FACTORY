import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Watch output/manga and send Discord webhook notifications for new files.")
    parser.add_argument("--webhook-url", default=os.environ.get("DISCORD_WEBHOOK_URL", ""), help="Discord webhook URL")
    parser.add_argument("--watch-dir", default=None, help="Directory to watch for new manga files")
    parser.add_argument("--file-types", default=".json,.md,.png,.jpg,.jpeg", help="Comma-separated file extensions to watch")
    parser.add_argument("--poll-interval", type=float, default=3.0, help="Polling interval in seconds")
    parser.add_argument("--log-file", default=None, help="Path to the discord log file")
    parser.add_argument("--error-log-file", default=None, help="Path to the error log file")
    parser.add_argument("--notification-script", default=None, help="Path to the discord notification script")
    parser.add_argument("--message", default="HONRAI_FACTORY: 漫画生成が完了しました。", help="Discord notification message")
    parser.add_argument("--username", default="HONRAI_FACTORY", help="Discord webhook username")
    parser.add_argument("--avatar-url", default="", help="Discord webhook avatar URL")
    return parser.parse_args()


def setup_loggers(log_file: Path, error_log_file: Path):
    log_file.parent.mkdir(parents=True, exist_ok=True)
    error_log_file.parent.mkdir(parents=True, exist_ok=True)

    discord_logger = logging.getLogger("discord_watcher")
    discord_logger.setLevel(logging.INFO)
    if not discord_logger.handlers:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s [INFO] %(message)s", "%Y-%m-%d %H:%M:%S"))
        discord_logger.addHandler(fh)

    error_logger = logging.getLogger("discord_watcher_error")
    error_logger.setLevel(logging.ERROR)
    if not error_logger.handlers:
        eh = logging.FileHandler(error_log_file, encoding="utf-8")
        eh.setLevel(logging.ERROR)
        eh.setFormatter(logging.Formatter("%(asctime)s [ERROR] %(message)s", "%Y-%m-%d %H:%M:%S"))
        error_logger.addHandler(eh)

    return discord_logger, error_logger


def is_supported_file(path: Path, file_types: set):
    return path.suffix.lower() in file_types


def wait_for_stable_file(path: Path, timeout: float = 10.0, interval: float = 1.0):
    start = time.time()
    last_size = -1
    while time.time() - start < timeout:
        try:
            current_size = path.stat().st_size
        except OSError:
            return False
        if current_size == last_size:
            return True
        last_size = current_size
        time.sleep(interval)
    return False


def send_notification(script_path: Path, webhook_url: str, file_path: Path, message: str, username: str, avatar_url: str):
    command = [sys.executable, str(script_path), "--webhook-url", webhook_url, "--preview", str(file_path), "--content", message, "--username", username]
    if avatar_url:
        command += ["--avatar-url", avatar_url]
    result = subprocess.run(command, capture_output=True, text=True)
    return result


def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    watch_dir = Path(args.watch_dir or repo_root / "output" / "manga")
    log_file = Path(args.log_file or repo_root / "logs" / "discord.log")
    error_log_file = Path(args.error_log_file or repo_root / "logs" / "error.log")
    notification_script = Path(args.notification_script or repo_root / "scripts" / "discord_webhook_notify.py")
    
    file_types = {f".{ft.strip()}" if not ft.strip().startswith(".") else ft.strip() for ft in args.file_types.split(",")}

    if not args.webhook_url:
        print("ERROR: Discord webhook URL is required. Set --webhook-url or DISCORD_WEBHOOK_URL.")
        sys.exit(1)

    if not notification_script.exists():
        print(f"ERROR: Notification script not found: {notification_script}")
        sys.exit(1)

    watch_dir.mkdir(parents=True, exist_ok=True)

    discord_logger, error_logger = setup_loggers(log_file, error_log_file)
    discord_logger.info(f"Starting watcher for {watch_dir} (file types: {file_types})")

    known_files = {p for p in watch_dir.glob("**/*") if p.is_file() and is_supported_file(p, file_types)}

    try:
        while True:
            current_files = {p for p in watch_dir.glob("**/*") if p.is_file() and is_supported_file(p, file_types)}
            new_files = sorted(current_files - known_files, key=lambda p: p.stat().st_mtime)
            for file_path in new_files:
                if not wait_for_stable_file(file_path):
                    error_logger.error(f"File not stable or unreadable: {file_path}")
                    continue
                discord_logger.info(f"Detected new file: {file_path}")
                result = send_notification(notification_script, args.webhook_url, file_path, args.message, args.username, args.avatar_url)
                if result.returncode == 0:
                    discord_logger.info(f"Notification sent for {file_path}. stdout={result.stdout.strip()}")
                    known_files.add(file_path)
                else:
                    error_logger.error(f"Notification failed for {file_path}. returncode={result.returncode} stderr={result.stderr.strip()} stdout={result.stdout.strip()}")
            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        discord_logger.info("Watcher stopped by user")
        print("Watcher stopped.")


if __name__ == "__main__":
    main()
