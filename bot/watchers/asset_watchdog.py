#!/usr/bin/env python3
"""Watch blender/input_assets for new FBX files and run the full asset pipeline."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from bot.commands.world import build_auto_world_request, write_world_request

DEFAULT_POLL_INTERVAL_SEC = 3
RETRY_COOLDOWN_SEC = 120
LOG_NAME = "asset_watchdog.log"
STATE_NAME = "asset_watchdog_state.json"


@dataclass(frozen=True)
class FileSignature:
    mtime: float
    size: int
    digest: str

    def to_dict(self) -> dict:
        return {"mtime": self.mtime, "size": self.size, "digest": self.digest}

    @classmethod
    def from_dict(cls, data: dict) -> FileSignature:
        return cls(
            mtime=float(data["mtime"]),
            size=int(data["size"]),
            digest=str(data["digest"]),
        )


class AssetWatchdog:
    def __init__(self, project_root: Path, poll_interval: int = DEFAULT_POLL_INTERVAL_SEC) -> None:
        self.project_root = project_root
        self.poll_interval = poll_interval
        self.input_dir = project_root / "blender" / "input_assets"
        self.logs_dir = project_root / "logs"
        self.log_path = self.logs_dir / LOG_NAME
        self.state_path = self.logs_dir / STATE_NAME
        self.preview_path = project_root / "BuildPreviews" / "preview.png"
        self.powershell = os.getenv("POWERSHELL_EXE", "powershell")
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
        self._busy = False
        self._queue: list[list[Path]] = []
        self._failed_at: dict[str, float] = {}
        self._stable_signatures: dict[str, FileSignature] = {}

        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def append_log(self, message: str, level: str = "INFO") -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} [{level}] {message}"
        print(line, flush=True)
        with self.log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(line + "\n")

    def send_discord(self, message: str) -> None:
        if not self.webhook_url:
            self.append_log("DISCORD_WEBHOOK_URL is not set. Notification skipped.", "WARN")
            return

        payload = json.dumps(
            {"content": f"HONRAI_FACTORY: {message}", "username": "HONRAI_FACTORY"},
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            self.webhook_url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "HONRAI_FACTORY/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.getcode() >= 400:
                    body = response.read().decode("utf-8", errors="replace")
                    raise RuntimeError(f"Discord webhook failed ({response.getcode()}): {body}")
            self.append_log(f"Discord notification sent: {message[:120]}")
        except Exception as exc:
            self.append_log(f"Discord notification failed: {exc}", "ERROR")

    def load_state(self) -> dict:
        if not self.state_path.exists():
            return {"processed": {}}

        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.append_log("State file corrupted. Resetting processed map.", "WARN")
            return {"processed": {}}

    def save_state(self, state: dict) -> None:
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def compute_signature(self, path: Path) -> FileSignature:
        data = path.read_bytes()
        stat = path.stat()
        digest = hashlib.sha256(data).hexdigest()
        return FileSignature(mtime=stat.st_mtime, size=stat.st_size, digest=digest)

    def is_pending(self, path: Path, signature: FileSignature, processed: dict) -> bool:
        key = path.name
        previous = processed.get(key)
        if previous and FileSignature.from_dict(previous) == signature:
            return False

        failed_key = f"{key}:{signature.digest}"
        last_failed = self._failed_at.get(failed_key)
        if last_failed and (time.time() - last_failed) < RETRY_COOLDOWN_SEC:
            return False

        return True

    def scan_pending_files(self) -> list[Path]:
        state = self.load_state()
        processed = state.get("processed", {})
        pending: list[Path] = []
        next_stable: dict[str, FileSignature] = {}

        for path in sorted(self.input_dir.glob("*.fbx")):
            if not path.is_file():
                continue

            try:
                signature = self.compute_signature(path)
            except OSError as exc:
                self.append_log(f"Failed to inspect {path.name}: {exc}", "ERROR")
                continue

            key = path.name
            if self._stable_signatures.get(key) != signature:
                next_stable[key] = signature
                continue

            next_stable[key] = signature
            if self.is_pending(path, signature, processed):
                pending.append(path)

        self._stable_signatures = next_stable
        return pending

    def run_ps1(self, script_name: str) -> None:
        script_path = self.project_root / "scripts" / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        self.append_log(f"Running {script_name}")
        completed = subprocess.run(
            [
                self.powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
            ],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if completed.stdout.strip():
            self.append_log(completed.stdout.strip())
        if completed.stderr.strip():
            self.append_log(completed.stderr.strip(), "WARN")

        if completed.returncode != 0:
            raise RuntimeError(f"{script_name} failed with exit code {completed.returncode}")

    def mark_processed(self, paths: list[Path]) -> None:
        state = self.load_state()
        processed = state.setdefault("processed", {})

        for path in paths:
            signature = self.compute_signature(path)
            processed[path.name] = signature.to_dict()

        state["last_success_at"] = datetime.now().isoformat(timespec="seconds")
        self.save_state(state)

    def mark_failed(self, paths: list[Path]) -> None:
        now = time.time()
        for path in paths:
            try:
                signature = self.compute_signature(path)
            except OSError:
                continue
            self._failed_at[f"{path.name}:{signature.digest}"] = now

    def process_batch(self, trigger_files: list[Path]) -> None:
        all_fbx = sorted(self.input_dir.glob("*.fbx"))
        names = ", ".join(path.name for path in trigger_files)
        self.append_log(f"FBX detected: {names}")
        self.send_discord(f"FBX detected\n- {names}")

        request = build_auto_world_request(self.input_dir)
        json_path = write_world_request(request)
        self.append_log(f"Updated world_request.json: {json_path}")
        self.append_log(f"objects={request['objects']} characters={request['characters']}")

        try:
            self.send_discord("Blender build started")
            self.run_ps1("blender_build.ps1")

            self.send_discord("Unity import started")
            self.run_ps1("import_generated_assets.ps1")

            self.send_discord("World build started")
            self.run_ps1("unity_world_build.ps1")

            if self.preview_path.exists():
                self.send_discord(
                    "Preview complete\n"
                    f"preview: {self.preview_path}\n"
                    f"world_name: {request['world_name']}\n"
                    f"objects: {', '.join(request['objects'])}"
                )
            else:
                self.send_discord(
                    "World build finished, preview.png was not found.\n"
                    f"world_name: {request['world_name']}"
                )

            self.mark_processed(all_fbx)
            self.append_log("Auto pipeline complete.")
        except Exception as exc:
            self.append_log(f"Auto pipeline failed: {exc}", "ERROR")
            self.mark_failed(trigger_files)
            self.send_discord(f"Auto pipeline failed\n```\n{exc}\n```")
            raise

    def enqueue(self, files: list[Path]) -> None:
        if not files:
            return
        self._queue.append(files)
        self.append_log(f"Queued batch ({len(files)} file(s)).")

    def drain_queue(self) -> None:
        if self._busy or not self._queue:
            return

        self._busy = True
        batch = self._queue.pop(0)
        try:
            self.process_batch(batch)
        except Exception:
            pass
        finally:
            self._busy = False

    def run_forever(self) -> None:
        self.append_log("Asset watchdog started.")
        self.append_log(f"Watching: {self.input_dir}")
        self.append_log(f"Poll interval: {self.poll_interval}s")

        while True:
            try:
                pending = self.scan_pending_files()
                if pending and not self._busy:
                    self.enqueue(pending)
                self.drain_queue()
            except Exception as exc:
                self.append_log(f"Watch loop error: {exc}", "ERROR")

            time.sleep(self.poll_interval)


def resolve_project_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()

    env_root = os.getenv("PROJECT_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()

    return PROJECT_DIR


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch FBX drops and run the auto asset pipeline.")
    parser.add_argument("--project-root", default=None, help="HONRAI_FACTORY root path")
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL_SEC, help="Poll interval seconds")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    load_dotenv(project_root / "bot" / ".env", encoding="utf-8-sig")
    os.environ.setdefault("PROJECT_ROOT", str(project_root))

    watchdog = AssetWatchdog(project_root=project_root, poll_interval=max(1, args.poll_interval))

    try:
        watchdog.run_forever()
    except KeyboardInterrupt:
        watchdog.append_log("Asset watchdog stopped by user.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
