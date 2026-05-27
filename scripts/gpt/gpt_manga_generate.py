#!/usr/bin/env python3
"""
GPT Manga Generator
OpenAI API を使用して、4コマ漫画または普通の漫画を生成します。
"""
import argparse
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


def setup_loggers(repo_root: Path):
    """Set up logging to discord.log and error.log"""
    log_dir = repo_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    gpt_logger = logging.getLogger("gpt_manga")
    gpt_logger.setLevel(logging.INFO)
    if not gpt_logger.handlers:
        fh = logging.FileHandler(log_dir / "gpt.log", encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s [INFO] %(message)s", "%Y-%m-%d %H:%M:%S"))
        gpt_logger.addHandler(fh)

    error_logger = logging.getLogger("gpt_manga_error")
    error_logger.setLevel(logging.ERROR)
    if not error_logger.handlers:
        eh = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
        eh.setLevel(logging.ERROR)
        eh.setFormatter(logging.Formatter("%(asctime)s [ERROR] %(message)s", "%Y-%m-%d %H:%M:%S"))
        error_logger.addHandler(eh)

    return gpt_logger, error_logger


def build_4koma_prompt(instruction: str, repo_root: Path) -> str:
    """Build the system prompt for 4koma manga generation"""
    prompt = """You are an expert 4-panel manga creator. Generate a 4-panel manga based on the instruction provided.
Output ONLY valid JSON, no markdown code blocks or extra text.

The JSON structure must be exactly:
{
  "title": "manga title",
  "theme": "theme of the manga",
  "type": "type (e.g., comedy, drama, action)",
  "mold": "mold/template type",
  "panels": [
    {
      "panel_number": 1,
      "scene": "description of the scene",
      "dialogue": "character dialogue or empty string",
      "narration": "narration text or empty string",
      "image_prompt": "detailed image prompt for image generation"
    },
    ...
  ],
  "post_text": "post-generation text or afterword"
}

Instruction: """ + instruction
    return prompt


def build_normal_manga_prompt(instruction: str, repo_root: Path) -> str:
    """Build the system prompt for normal manga generation"""
    prompt = """You are an expert manga creator. Generate a manga episode based on the instruction provided.
Output ONLY valid JSON, no markdown code blocks or extra text.

The JSON structure must be exactly:
{
  "title": "episode title",
  "theme": "theme of the episode",
  "episode_summary": "brief summary of the episode",
  "pages": [
    {
      "page_number": 1,
      "page_goal": "what this page should accomplish",
      "panels": [
        {
          "panel_number": 1,
          "scene": "description of the scene",
          "dialogue": "character dialogue or empty string",
          "narration": "narration text or empty string",
          "image_prompt": "detailed image prompt for image generation"
        },
        ...
      ]
    },
    ...
  ],
  "next_episode_hook": "hook/cliffhanger for next episode"
}

Instruction: """ + instruction
    return prompt


def call_openai_api(api_key: str, system_prompt: str, instruction: str) -> dict:
    """Call OpenAI API and return JSON response"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": instruction
            }
        ],
        "temperature": 0.7,
        "max_tokens": 3000,
    }
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected API response: {data}")
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")


def parse_json_response(response_text: str) -> dict:
    """Parse JSON from OpenAI response"""
    response_text = response_text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
    return json.loads(response_text)


def generate_markdown(manga_data: dict, manga_type: str) -> str:
    """Generate Markdown representation of the manga"""
    md = []
    md.append(f"# {manga_data.get('title', 'Untitled')}")
    md.append("")
    md.append(f"**Theme:** {manga_data.get('theme', '')}")
    md.append("")

    if manga_type == "4koma":
        md.append(f"**Type:** {manga_data.get('type', '')}")
        md.append(f"**Mold:** {manga_data.get('mold', '')}")
        md.append("")
        md.append("## Panels")
        md.append("")
        for panel in manga_data.get("panels", []):
            md.append(f"### Panel {panel['panel_number']}")
            md.append(f"**Scene:** {panel.get('scene', '')}")
            if panel.get("dialogue"):
                md.append(f"**Dialogue:** {panel['dialogue']}")
            if panel.get("narration"):
                md.append(f"**Narration:** {panel['narration']}")
            md.append(f"**Image Prompt:** {panel.get('image_prompt', '')}")
            md.append("")
        if manga_data.get("post_text"):
            md.append(f"## Post Text\n{manga_data['post_text']}")
    else:
        md.append(f"**Episode Summary:** {manga_data.get('episode_summary', '')}")
        md.append("")
        for page in manga_data.get("pages", []):
            md.append(f"## Page {page['page_number']}")
            md.append(f"**Goal:** {page.get('page_goal', '')}")
            md.append("")
            for panel in page.get("panels", []):
                md.append(f"### Panel {panel['panel_number']}")
                md.append(f"**Scene:** {panel.get('scene', '')}")
                if panel.get("dialogue"):
                    md.append(f"**Dialogue:** {panel['dialogue']}")
                if panel.get("narration"):
                    md.append(f"**Narration:** {panel['narration']}")
                md.append(f"**Image Prompt:** {panel.get('image_prompt', '')}")
                md.append("")
        if manga_data.get("next_episode_hook"):
            md.append(f"## Next Episode Hook\n{manga_data['next_episode_hook']}")

    return "\n".join(md)


def save_outputs(manga_data: dict, manga_type: str, repo_root: Path):
    """Save JSON and Markdown outputs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title_slug = manga_data.get("title", "untitled").replace(" ", "_").lower()
    filename_base = f"{timestamp}_{title_slug}"

    if manga_type == "4koma":
        output_dir = repo_root / "output" / "manga" / "4koma"
    else:
        output_dir = repo_root / "output" / "manga" / "normal"

    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{filename_base}.json"
    md_path = output_dir / f"{filename_base}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manga_data, f, ensure_ascii=False, indent=2)

    md_content = generate_markdown(manga_data, manga_type)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return json_path, md_path


def main():
    parser = argparse.ArgumentParser(description="Generate manga using GPT")
    parser.add_argument("--type", choices=["4koma", "normal"], required=True, help="Manga type")
    parser.add_argument("--instruction", required=True, help="Instruction for manga generation")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"), help="OpenAI API key")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root or Path(__file__).resolve().parent.parent.parent)
    gpt_logger, error_logger = setup_loggers(repo_root)

    if not args.api_key:
        error_msg = "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass --api-key"
        error_logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    try:
        gpt_logger.info(f"Starting manga generation: type={args.type} instruction={args.instruction}")

        if args.type == "4koma":
            system_prompt = build_4koma_prompt(args.instruction, repo_root)
        else:
            system_prompt = build_normal_manga_prompt(args.instruction, repo_root)

        gpt_logger.info("Calling OpenAI API...")
        response_text = call_openai_api(args.api_key, system_prompt, args.instruction)

        gpt_logger.info("Parsing API response...")
        manga_data = parse_json_response(response_text)

        gpt_logger.info("Saving outputs...")
        json_path, md_path = save_outputs(manga_data, args.type, repo_root)

        gpt_logger.info(f"Manga generated successfully: JSON={json_path} Markdown={md_path}")
        print(f"JSON: {json_path}")
        print(f"Markdown: {md_path}")

    except Exception as e:
        error_logger.error(f"Manga generation failed: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
