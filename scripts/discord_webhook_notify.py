import argparse
import json
import mimetypes
import os
import sys
import uuid
import urllib.request


def build_multipart_form_data(fields, files):
    boundary = uuid.uuid4().hex
    lines = []
    for name, value in fields.items():
        lines.append(f"--{boundary}")
        lines.append(f"Content-Disposition: form-data; name=\"{name}\"")
        lines.append("")
        lines.append(value)
    for field_name, file_path in files.items():
        filename = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"
        with open(file_path, "rb") as f:
            file_data = f.read()
        lines.append(f"--{boundary}")
        lines.append(f"Content-Disposition: form-data; name=\"{field_name}\"; filename=\"{filename}\"")
        lines.append(f"Content-Type: {content_type}")
        lines.append("")
        lines.append(file_data)
    lines.append(f"--{boundary}--")
    body = bytearray()
    for item in lines:
        if isinstance(item, str):
            body.extend(item.encode("utf-8"))
            body.extend(b"\r\n")
        else:
            body.extend(item)
            body.extend(b"\r\n")
    content_type = f"multipart/form-data; boundary={boundary}"
    return content_type, bytes(body)


def send_discord_webhook(webhook_url, payload, image_path=None):
    fields = {"payload_json": json.dumps(payload, ensure_ascii=False)}
    files = {}
    if image_path:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Preview image not found: {image_path}")
        files["file"] = image_path
    content_type, body = build_multipart_form_data(fields, files)
    request = urllib.request.Request(webhook_url, data=body, method="POST")
    request.add_header("Content-Type", content_type)
    request.add_header("User-Agent", "HONRAI_FACTORY/1.0")
    with urllib.request.urlopen(request) as response:
        status = response.getcode()
        text = response.read().decode("utf-8", errors="replace")
        return status, text


def parse_args():
    parser = argparse.ArgumentParser(description="Send a Discord webhook notification with a manga preview image.")
    parser.add_argument("--webhook-url", required=True, help="Discord webhook URL")
    parser.add_argument("--preview", required=True, help="Path to the preview image to upload")
    parser.add_argument("--content", default="HONRAI_FACTORY: 漫画生成が完了しました。", help="Webhook content message")
    parser.add_argument("--username", default="HONRAI_FACTORY", help="Webhook username")
    parser.add_argument("--avatar-url", default="", help="Webhook avatar URL")
    parser.add_argument("--thread-name", default="", help="Optional Discord thread name")
    return parser.parse_args()


def main():
    args = parse_args()
    payload = {
        "content": args.content,
        "username": args.username,
    }
    if args.avatar_url:
        payload["avatar_url"] = args.avatar_url
    if args.thread_name:
        payload["thread_name"] = args.thread_name
    try:
        status, response_text = send_discord_webhook(args.webhook_url, payload, args.preview)
        print(f"Discord webhook sent: status={status}")
        print(response_text)
    except Exception as exc:
        print(f"Error sending Discord webhook: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
