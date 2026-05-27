#!/usr/bin/env python3
"""Send Discord webhook notification after Blender / Unity import pipeline completion."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def read_log_tail(log_path: Path, lines: int) -> str:
    if not log_path.exists():
        return f"(log not found: {log_path})"

    try:
        content = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return f"(failed to read log: {exc})"

    if not content:
        return "(log is empty)"

    return "\n".join(content[-lines:])


def send_webhook(webhook_url: str, content: str) -> None:
    payload = json.dumps({"content": content, "username": "HONRAI_FACTORY"}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "HONRAI_FACTORY/1.0",
        },
    )
    with urllib.request.urlopen(request) as response:
        if response.getcode() >= 400:
            body = response.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Discord webhook failed ({response.getcode()}): {body}")


def build_message(
    *,
    status: str,
    repo_root: Path,
    output_files: list[str],
    error: str,
    log_file: Path | None,
    log_lines: int,
) -> str:
    if status == "pipeline_success":
        if output_files:
            file_lines = "\n".join(
                f"- {Path(path).resolve().relative_to(repo_root)}"
                for path in output_files
            )
            body = (
                "HONRAI_FACTORY: Blender build + Unity import complete.\n\n"
                f"Generated glb ({len(output_files)}):\n{file_lines}\n\n"
                "Unity path: unityprojects/kaido-walk/Assets/Generated/"
            )
        else:
            body = "HONRAI_FACTORY: Blender build + Unity import complete."
        return body

    if status == "import_failed":
        tail = read_log_tail(log_file, log_lines) if log_file else error
        return (
            "HONRAI_FACTORY: Blender build succeeded, Unity import failed.\n\n"
            f"```\n{tail[:1500]}\n```"
        )

    if status == "success":
        if output_files:
            file_lines = "\n".join(
                f"- {Path(path).resolve().relative_to(repo_root)}"
                for path in output_files
            )
            return (
                "HONRAI_FACTORY: Blender 軽量化ラインが完了しました。\n\n"
                f"出力 ({len(output_files)} 件):\n{file_lines}"
            )
        return "HONRAI_FACTORY: Blender 軽量化ラインが完了しました。（出力ファイルなし）"

    tail = read_log_tail(log_file, log_lines) if log_file else error.strip() or "Unknown error"
    return f"HONRAI_FACTORY: Blender build failed.\n\n```\n{tail[:1500]}\n```"


def main() -> None:
    parser = argparse.ArgumentParser(description="Notify Discord about Blender pipeline output")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--webhook-url", default=os.environ.get("DISCORD_WEBHOOK_URL", ""), help="Discord webhook URL")
    parser.add_argument(
        "--status",
        choices=("success", "failed", "import_failed", "pipeline_success"),
        required=True,
        help="Pipeline result",
    )
    parser.add_argument("--output-file", action="append", default=[], help="Exported glTF path (repeatable)")
    parser.add_argument("--error", default="", help="Error message")
    parser.add_argument("--log-file", default="", help="Log file path for tail output")
    parser.add_argument("--log-lines", type=int, default=20, help="Number of log lines to include")
    args = parser.parse_args()

    repo_root = Path(args.repo_root or Path(__file__).resolve().parent.parent)
    log_path = Path(args.log_file) if args.log_file else None

    if not args.webhook_url:
        print("ERROR: DISCORD_WEBHOOK_URL is required.", file=sys.stderr)
        sys.exit(1)

    content = build_message(
        status=args.status,
        repo_root=repo_root,
        output_files=args.output_file,
        error=args.error,
        log_file=log_path,
        log_lines=args.log_lines,
    )
    send_webhook(args.webhook_url, content[:2000])
    print("Discord notification sent.")


if __name__ == "__main__":
    main()
