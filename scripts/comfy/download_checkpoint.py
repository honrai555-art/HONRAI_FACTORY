#!/usr/bin/env python3
"""Download Stable Diffusion 1.5 checkpoint as model.safetensors for ComfyUI."""
import argparse
import shutil
import sys
from pathlib import Path

REPO_ID = "runwayml/stable-diffusion-v1-5"
FILENAME = "v1-5-pruned-emaonly.safetensors"
TARGET_NAME = "model.safetensors"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[2],
        type=Path,
        help="Repository root",
    )
    args = parser.parse_args()

    checkpoint_dir = (
        args.repo_root / "tools" / "comfyui" / "ComfyUI-master" / "models" / "checkpoints"
    )
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    target_path = checkpoint_dir / TARGET_NAME

    if target_path.exists() and target_path.stat().st_size > 0:
        print(f"Checkpoint already exists: {target_path}")
        return 0

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("Install huggingface_hub first: pip install huggingface_hub")
        return 2

    print(f"Downloading {REPO_ID}/{FILENAME} ...")
    downloaded = Path(
        hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
        )
    )
    if target_path.exists():
        target_path.unlink()
    shutil.copy2(downloaded, target_path)
    print(f"Saved checkpoint to {target_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
