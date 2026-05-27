#!/usr/bin/env python3
"""HONRAI_FACTORY pipeline orchestrator."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_env(root: Path) -> None:
    """Load bot/.env so pipeline steps can use OPENAI_API_KEY and DISCORD_WEBHOOK_URL."""
    env_path = root / "bot" / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except ImportError:
        print("Note: python-dotenv is not installed; using existing environment variables only.")


def load_pipeline(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print(
            "PyYAML is not installed.\n"
            "Install it with:\n"
            "  python -m pip install pyyaml",
            file=sys.stderr,
        )
        sys.exit(1)

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid pipeline file: {path}")
    if "steps" not in data or not isinstance(data["steps"], list):
        raise ValueError(f"Pipeline must define a steps list: {path}")

    return data


def resolve_output_file(output_path: Path) -> Path:
    if output_path.suffix:
        return output_path
    return output_path / "prompts_for_comfy.json"


def build_python_command(step: dict, root: Path) -> list[str]:
    command_path = step.get("command")
    if not command_path:
        raise ValueError(f"Step {step.get('id', '?')} is missing command")

    script_path = root / command_path
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    cmd = [sys.executable, str(script_path), "--repo-root", str(root)]
    script_name = script_path.name

    if step.get("input"):
        input_path = root / step["input"]
        if script_name == "extract_image_prompts.py":
            cmd.extend(["--source-dir", str(input_path)])
        elif script_name == "notify_discord.py":
            cmd.extend(["--input-dir", str(input_path)])

    if step.get("output"):
        output_path = root / step["output"]
        if script_name == "extract_image_prompts.py":
            cmd.extend(["--output-file", str(resolve_output_file(output_path))])

    if script_name == "gpt_manga_generate.py":
        manga_type = os.environ.get("MANGA_PIPELINE_TYPE", "4koma")
        instruction = os.environ.get(
            "MANGA_PIPELINE_INSTRUCTION",
            "HONRAI_FACTORY pipeline test manga",
        )
        cmd.extend(["--type", manga_type, "--instruction", instruction])

    extra_args = step.get("args") or []
    if extra_args:
        cmd.extend(str(arg) for arg in extra_args)

    return cmd


def run_step(step: dict, root: Path) -> subprocess.CompletedProcess[str]:
    step_id = step.get("id", "unknown")
    step_type = step.get("type", "python")

    if step_type != "python":
        raise ValueError(f"Unsupported step type '{step_type}' in step '{step_id}'")

    cmd = build_python_command(step, root)
    print(f"[START] {step_id}")
    print(f"  command: {' '.join(cmd)}")

    completed = subprocess.run(
        cmd,
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )

    if completed.stdout.strip():
        print(completed.stdout.strip())
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)

    if completed.returncode == 0:
        print(f"[DONE] {step_id}")
    else:
        print(f"[FAILED] {step_id} (exit code {completed.returncode})", file=sys.stderr)

    return completed


def run_pipeline(pipeline_path: Path) -> None:
    root = repo_root()
    load_env(root)
    pipeline = load_pipeline(pipeline_path)

    print(f"HONRAI_FACTORY orchestrator")
    print(f"Pipeline: {pipeline.get('name', pipeline_path.name)}")
    if pipeline.get("description"):
        print(f"Description: {pipeline['description']}")
    print(f"Root: {root}")
    print("")

    for step in pipeline["steps"]:
        completed = run_step(step, root)
        if completed.returncode != 0:
            detail = "\n".join(
                part for part in [completed.stdout.strip(), completed.stderr.strip()] if part
            )
            raise RuntimeError(
                f"Pipeline stopped at step '{step.get('id', 'unknown')}'.\n{detail}"
            )

    print("")
    print("Pipeline completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a HONRAI_FACTORY pipeline")
    parser.add_argument(
        "pipeline",
        nargs="?",
        default="pipelines/manga.yaml",
        help="Path to pipeline YAML (default: pipelines/manga.yaml)",
    )
    args = parser.parse_args()

    root = repo_root()
    pipeline_path = Path(args.pipeline)
    if not pipeline_path.is_absolute():
        pipeline_path = root / pipeline_path

    if not pipeline_path.exists():
        print(f"Pipeline file not found: {pipeline_path}", file=sys.stderr)
        sys.exit(1)

    try:
        run_pipeline(pipeline_path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
