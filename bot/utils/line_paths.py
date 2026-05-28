"""SPA_MODEL manufacturing-line script paths (repo root relative)."""
from __future__ import annotations

import os
from pathlib import Path

LINE_CAREER = "01_career-card"
LINE_GAME = "02_game-object"
LINE_MANGA = "03_manga-content"
LINE_AI = "04_AI-manager"
LINE_DISCORD = "05_Discord-logistics"
LINE_FC = "06_FC-system"
LINE_WORLD = "07_world-IP"


def project_root() -> Path:
    configured = os.getenv("PROJECT_ROOT", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2]


def spa_model_dir() -> Path:
    return project_root() / "SPA_MODEL"


def line_dir(line_id: str) -> Path:
    return spa_model_dir() / line_id


def line_scripts(line_id: str) -> Path:
    return line_dir(line_id) / "scripts"


def script_path(line_id: str, *parts: str) -> Path:
    return line_scripts(line_id).joinpath(*parts)


def game_blender_dir() -> Path:
    return line_dir(LINE_GAME) / "blender"


def game_blender_input_dir() -> Path:
    return game_blender_dir() / "input_assets"


def game_blender_output_dir() -> Path:
    return game_blender_dir() / "output_assets"


def game_unity_project_dir() -> Path:
    return line_dir(LINE_GAME) / "unity" / "kaido-walk"


def game_generated_assets_dir() -> Path:
    return game_unity_project_dir() / "Assets" / "Generated"


def manga_line_dir() -> Path:
    return line_dir(LINE_MANGA)


def manga_outputs_dir() -> Path:
    return manga_line_dir() / "outputs" / "manga"


def manga_pipeline_yaml() -> Path:
    primary = manga_line_dir() / "pipelines" / "manga.yaml"
    if primary.exists():
        return primary
    return project_root() / "pipelines" / "manga.yaml"


def career_line_dir() -> Path:
    return line_dir(LINE_CAREER)


def career_gas_dir() -> Path:
    primary = career_line_dir() / "gas"
    if primary.exists():
        return primary
    return project_root() / "integrations" / "gas" / "career-card"


def career_pipeline_yaml() -> Path:
    primary = career_line_dir() / "pipelines" / "career-card.yaml"
    if primary.exists():
        return primary
    return project_root() / "pipelines" / "career-card.yaml"


def world_ip_dir() -> Path:
    return line_dir(LINE_WORLD)


def world_request_json() -> Path:
    canonical = world_ip_dir() / "world-settings" / "world_request.json"
    if canonical.exists():
        return canonical
    return project_root() / "world_request.json"


def world_request_write_path() -> Path:
    """Canonical location for new writes."""
    path = world_ip_dir() / "world-settings" / "world_request.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
