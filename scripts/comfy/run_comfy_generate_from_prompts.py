#!/usr/bin/env python3
"""
Generate images from prompts_for_comfy.json using ComfyUI API
"""
import argparse
import json
import logging
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path


def setup_logger(repo_root: Path):
    """Set up logging"""
    log_dir = repo_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("comfy_generator")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(log_dir / "comfy.log", encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s [INFO] %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(fh)

    error_logger = logging.getLogger("comfy_generator_error")
    error_logger.setLevel(logging.ERROR)
    if not error_logger.handlers:
        eh = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
        eh.setLevel(logging.ERROR)
        eh.setFormatter(logging.Formatter("%(asctime)s [ERROR] %(message)s", "%Y-%m-%d %H:%M:%S"))
        error_logger.addHandler(eh)

    return logger, error_logger


def check_comfyui_connection(api_url: str) -> bool:
    """Check if ComfyUI is running"""
    try:
        request = urllib.request.Request(f"{api_url}/queue", method="GET")
        with urllib.request.urlopen(request, timeout=3) as response:
            response.read()
        return True
    except Exception:
        return False


def load_prompts(prompts_file: Path) -> list:
    """Load prompts from JSON"""
    try:
        with open(prompts_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load prompts: {e}")


def build_workflow(image_prompt: str) -> dict:
    """Build a minimal ComfyUI workflow for text-to-image generation"""
    workflow = {
        "1": {
            "inputs": {
                "text": image_prompt,
                "clip": ["7", 0]
            },
            "class_type": "CLIPTextEncode (Prompt)"
        },
        "2": {
            "inputs": {
                "text": "",
                "clip": ["7", 0]
            },
            "class_type": "CLIPTextEncode (Prompt)"
        },
        "3": {
            "inputs": {
                "seed": 12345,
                "steps": 20,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["1", 0],
                "negative": ["2", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "model.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["7", 2]
            },
            "class_type": "VAEDecode"
        },
        "7": {
            "inputs": {
                "ckpt_name": "model.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "8": {
            "inputs": {
                "filename_prefix": "generated",
                "images": ["6", 0]
            },
            "class_type": "SaveImage"
        }
    }
    return workflow


def submit_workflow(api_url: str, workflow: dict) -> str:
    """Submit workflow to ComfyUI and return prompt_id"""
    try:
        payload = json.dumps(workflow).encode("utf-8")
        request = urllib.request.Request(f"{api_url}/prompt", data=payload, method="POST")
        request.add_header("Content-Type", "application/json")
        
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
            prompt_id = result.get("prompt_id")
            if not prompt_id:
                raise ValueError("No prompt_id in response")
            return prompt_id
    except Exception as e:
        raise RuntimeError(f"Failed to submit workflow: {e}")


def wait_for_completion(api_url: str, prompt_id: str, timeout: int = 120, poll_interval: int = 2) -> dict:
    """Wait for workflow to complete and return result"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            request = urllib.request.Request(f"{api_url}/history/{prompt_id}", method="GET")
            with urllib.request.urlopen(request) as response:
                history = json.loads(response.read().decode("utf-8"))
                if prompt_id in history:
                    return history[prompt_id]
        except Exception:
            pass
        time.sleep(poll_interval)
    raise RuntimeError(f"Workflow did not complete within {timeout} seconds")


def download_image(api_url: str, filename: str, subfolder: str, output_path: Path) -> None:
    """Download image from ComfyUI"""
    try:
        url = f"{api_url}/view?filename={filename}&subfolder={subfolder}"
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request) as response:
            image_data = response.read()
        
        with open(output_path, "wb") as f:
            f.write(image_data)
    except Exception as e:
        raise RuntimeError(f"Failed to download image: {e}")


def generate_filename(prompt_data: dict) -> str:
    """Generate filename from prompt data"""
    mode = prompt_data.get("type", "unknown")
    title = prompt_data.get("title", "untitled").replace(" ", "_")[:30]
    
    if mode == "4koma":
        panel = prompt_data.get("panel_number", 0)
        return f"{mode}_{title}_panel{panel}.png"
    else:
        page = prompt_data.get("page_number", 0)
        panel = prompt_data.get("panel_number", 0)
        return f"{mode}_{title}_p{page}_panel{panel}.png"


def main():
    parser = argparse.ArgumentParser(description="Generate images from ComfyUI prompts")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--prompts-file", default=None, help="Path to prompts_for_comfy.json")
    parser.add_argument("--api-url", default="http://127.0.0.1:8188", help="ComfyUI API URL")
    parser.add_argument("--limit", type=int, default=1, help="Number of prompts to generate (default: 1)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root or Path(__file__).resolve().parent.parent.parent)
    logger, error_logger = setup_logger(repo_root)

    prompts_file = Path(args.prompts_file or repo_root / "output" / "manga" / "prompts_for_comfy.json")
    output_dir = repo_root / "output" / "manga" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting image generation from {prompts_file}")
    logger.info(f"ComfyUI API: {args.api_url}")

    # Check ComfyUI connection
    logger.info("Checking ComfyUI connection...")
    if not check_comfyui_connection(args.api_url):
        error_msg = f"ComfyUI is not running at {args.api_url}. Please start ComfyUI first."
        error_logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)
    logger.info("ComfyUI connection OK")

    # Load prompts
    try:
        prompts = load_prompts(prompts_file)
    except Exception as e:
        error_logger.error(f"Failed to load prompts: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not prompts:
        error_msg = "No prompts found in prompts_for_comfy.json"
        error_logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    logger.info(f"Loaded {len(prompts)} prompts. Processing {min(args.limit, len(prompts))} image(s)...")

    # Process prompts
    generated_count = 0
    for idx, prompt_data in enumerate(prompts[:args.limit]):
        try:
            image_prompt = prompt_data.get("image_prompt", "")
            if not image_prompt:
                logger.warning(f"Prompt {idx} has no image_prompt, skipping")
                continue

            logger.info(f"Processing prompt {idx+1}: {image_prompt[:80]}...")

            # Build and submit workflow
            workflow = build_workflow(image_prompt)
            prompt_id = submit_workflow(args.api_url, workflow)
            logger.info(f"Workflow submitted with prompt_id: {prompt_id}")

            # Wait for completion
            logger.info("Waiting for image generation to complete...")
            history = wait_for_completion(args.api_url, prompt_id)

            # Extract output filename
            outputs = history.get("outputs", {})
            if not outputs:
                logger.warning(f"No outputs from workflow {prompt_id}")
                continue

            # Get the SaveImage output node
            save_node_output = None
            for node_id, node_output in outputs.items():
                if "images" in node_output:
                    save_node_output = node_output
                    break

            if not save_node_output or not save_node_output.get("images"):
                logger.warning(f"No images in workflow output")
                continue

            # Download image
            image_info = save_node_output["images"][0]
            filename = image_info["filename"]
            subfolder = image_info.get("subfolder", "")
            
            output_filename = generate_filename(prompt_data)
            output_path = output_dir / output_filename
            
            logger.info(f"Downloading image to {output_path}")
            download_image(args.api_url, filename, subfolder, output_path)
            
            logger.info(f"Image generated successfully: {output_path}")
            generated_count += 1
            print(f"Generated: {output_path}")

        except Exception as e:
            error_logger.error(f"Failed to generate image for prompt {idx}: {e}")
            logger.error(f"Prompt: {prompt_data}")
            continue

    logger.info(f"Generation complete. Generated {generated_count} image(s)")
    print(f"Total images generated: {generated_count}")


if __name__ == "__main__":
    main()
