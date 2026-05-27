#!/usr/bin/env python3
"""Run a minimal ComfyUI API test: check /queue and POST a simple workflow.

This script:
- Loads the first `image_prompt` from `output/manga/prompts_for_comfy.json`.
- GETs `http://127.0.0.1:8188/queue` to verify ComfyUI is reachable.
- POSTs a minimal workflow to `/prompt` and saves the response.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_API_URL = "http://127.0.0.1:8188"
DEFAULT_PROMPT = "A simple test scene, black and white manga style, single character"


def find_image_prompt(data):
    if isinstance(data, dict):
        if "image_prompt" in data and isinstance(data["image_prompt"], str):
            return data["image_prompt"]
        for value in data.values():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "image_prompt" in item:
                        return item["image_prompt"]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "image_prompt" in item:
                return item["image_prompt"]
    return None


def build_minimal_workflow(image_prompt: str) -> dict:
    return {
        "1": {
            "inputs": {"text": image_prompt, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode",
        },
        "2": {
            "inputs": {"text": "", "clip": ["4", 1]},
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {
                "seed": 42,
                "steps": 4,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["1", 0],
                "negative": ["2", 0],
                "latent_image": ["5", 0],
            },
            "class_type": "KSampler",
        },
        "4": {
            "inputs": {"ckpt_name": "model.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        },
        "5": {
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "6": {
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            "class_type": "VAEDecode",
        },
        "7": {
            "inputs": {"filename_prefix": "comfy_test", "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }


def http_get(url: str, timeout: int = 5) -> tuple[int, str]:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def http_post_json(url: str, payload: dict, timeout: int = 30) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="ComfyUI API URL")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    prompts_path = repo_root / "output" / "manga" / "prompts_for_comfy.json"
    image_prompt = DEFAULT_PROMPT

    if prompts_path.exists():
        with prompts_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        found = find_image_prompt(data)
        if found:
            image_prompt = found
        else:
            print("No image_prompt found in", prompts_path, "- using default prompt")
    else:
        print("prompts_for_comfy.json not found at", prompts_path, "- using default prompt")

    queue_url = f"{args.api_url.rstrip('/')}/queue"
    prompt_url = f"{args.api_url.rstrip('/')}/prompt"

    try:
        status, body = http_get(queue_url)
        print("GET", queue_url, "->", status)
    except Exception as exc:
        print("ComfyUI /queue not reachable:", exc)
        sys.exit(2)

    payload = {"prompt": build_minimal_workflow(image_prompt)}

    try:
        status, body = http_post_json(prompt_url, payload)
        print("POST", prompt_url, "->", status)
        out_dir = repo_root / "output" / "manga"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "comfy_test_response.json"
        try:
            parsed = json.loads(body)
            out_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
        except json.JSONDecodeError:
            out_path.write_text(body, encoding="utf-8")
        print("Saved response to", out_path)
        if status >= 400:
            sys.exit(3)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print("POST failed:", exc, error_body)
        sys.exit(3)
    except Exception as exc:
        print("POST failed:", exc)
        sys.exit(3)


if __name__ == "__main__":
    main()
