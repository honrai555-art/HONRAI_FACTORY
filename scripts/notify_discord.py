#!/usr/bin/env python3
"""Send Discord webhook notification after manga pipeline completion."""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def collect_recent_files(input_dir: Path, limit: int = 10) -> list[Path]:
    patterns = ("*.json", "*.md", "*.png", "*.jpg", "*.jpeg")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(input_dir.glob(f"**/{pattern}"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


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
            raise RuntimeError(f"Discord webhook failed ({response.getcode}): {body}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Notify Discord about manga pipeline output")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--input-dir", default=None, help="Input directory (default: output/manga)")
    parser.add_argument("--webhook-url", default=os.environ.get("DISCORD_WEBHOOK_URL", ""), help="Discord webhook URL")
    args = parser.parse_args()

    repo_root = Path(args.repo_root or Path(__file__).resolve().parent.parent)
    input_dir = Path(args.input_dir or repo_root / "output" / "manga")

    if not args.webhook_url:
        print("ERROR: DISCORD_WEBHOOK_URL is required.", file=sys.stderr)
        sys.exit(1)

    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    recent_files = collect_recent_files(input_dir)
    if recent_files:
        file_lines = "\n".join(f"- {path.relative_to(repo_root)}" for path in recent_files)
        content = f"HONRAI_FACTORY: 漫画パイプラインが完了しました。\n\n最新ファイル:\n{file_lines}"
    else:
        content = "HONRAI_FACTORY: 漫画パイプラインが完了しました。（output/manga にファイルがありません）"

    send_webhook(args.webhook_url, content[:2000])
    print("Discord notification sent.")


if __name__ == "__main__":
    main()
