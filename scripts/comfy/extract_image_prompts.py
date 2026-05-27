#!/usr/bin/env python3
"""
Extract image prompts from manga JSON for ComfyUI
"""
import argparse
import json
import logging
import sys
from pathlib import Path


def setup_logger(repo_root: Path):
    """Set up logging"""
    log_dir = repo_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("comfy_extractor")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(log_dir / "gpt.log", encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s [INFO] %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(fh)

    return logger


def extract_prompts_from_4koma(data: dict) -> list:
    """Extract image prompts from 4koma manga JSON"""
    prompts = []
    for panel in data.get("panels", []):
        prompts.append({
            "type": "4koma",
            "title": data.get("title", ""),
            "panel_number": panel.get("panel_number"),
            "scene": panel.get("scene", ""),
            "image_prompt": panel.get("image_prompt", "")
        })
    return prompts


def extract_prompts_from_normal(data: dict) -> list:
    """Extract image prompts from normal manga JSON"""
    prompts = []
    for page in data.get("pages", []):
        for panel in page.get("panels", []):
            prompts.append({
                "type": "normal",
                "title": data.get("title", ""),
                "page_number": page.get("page_number"),
                "panel_number": panel.get("panel_number"),
                "scene": panel.get("scene", ""),
                "image_prompt": panel.get("image_prompt", "")
            })
    return prompts


def load_manga_json(json_file: Path) -> tuple:
    """Load manga JSON and determine type"""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "pages" in data:
            return data, "normal"
        elif "panels" in data:
            return data, "4koma"
        else:
            raise ValueError(f"Unknown manga format in {json_file}")
    except Exception as e:
        raise RuntimeError(f"Failed to load {json_file}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Extract image prompts from manga JSON for ComfyUI")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--source-dir", default=None, help="Source directory (default: output/manga)")
    parser.add_argument("--output-file", default=None, help="Output file (default: output/manga/prompts_for_comfy.json)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root or Path(__file__).resolve().parent.parent.parent)
    logger = setup_logger(repo_root)

    source_dir = Path(args.source_dir or repo_root / "output" / "manga")
    output_file = Path(args.output_file or repo_root / "output" / "manga" / "prompts_for_comfy.json")

    logger.info(f"Starting image prompt extraction from {source_dir}")

    all_prompts = []
    json_files = list(source_dir.glob("*/*.json")) + list(source_dir.glob("*.json"))

    for json_file in json_files:
        try:
            logger.info(f"Processing {json_file}")
            data, manga_type = load_manga_json(json_file)

            if manga_type == "4koma":
                prompts = extract_prompts_from_4koma(data)
            else:
                prompts = extract_prompts_from_normal(data)

            all_prompts.extend(prompts)
            logger.info(f"Extracted {len(prompts)} prompts from {json_file}")

        except Exception as e:
            logger.error(f"Failed to process {json_file}: {e}")
            continue

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_prompts, f, ensure_ascii=False, indent=2)

    logger.info(f"Extracted {len(all_prompts)} total prompts. Saved to {output_file}")
    print(f"Total prompts extracted: {len(all_prompts)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
