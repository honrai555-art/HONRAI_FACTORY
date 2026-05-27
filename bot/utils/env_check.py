"""Validate bot/.env configuration at startup."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnvCheckResult:
    missing_required: list[str]
    missing_recommended: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.missing_required


REQUIRED_KEYS = ("DISCORD_TOKEN",)
RECOMMENDED_KEYS = (
    "DISCORD_WEBHOOK_URL",
    "PROJECT_ROOT",
    "UNITY_EXE",
    "ALLOWED_CHANNEL_ID",
)


def _is_set(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def validate_env(*, project_dir: Path) -> EnvCheckResult:
    missing_required = [key for key in REQUIRED_KEYS if not _is_set(key)]
    missing_recommended = [key for key in RECOMMENDED_KEYS if not _is_set(key)]
    warnings: list[str] = []

    project_root = os.getenv("PROJECT_ROOT", "").strip()
    if not project_root:
        inferred = str(project_dir)
        os.environ.setdefault("PROJECT_ROOT", inferred)
        warnings.append(f"PROJECT_ROOT is not set. Using default: {inferred}")
    elif not Path(project_root).exists():
        warnings.append(f"PROJECT_ROOT does not exist: {project_root}")

    if not _is_set("ALLOWED_CHANNEL_ID"):
        warnings.append("ALLOWED_CHANNEL_ID is not set. Commands are allowed in all channels.")

    return EnvCheckResult(
        missing_required=missing_required,
        missing_recommended=missing_recommended,
        warnings=warnings,
    )


def format_env_report(result: EnvCheckResult) -> str:
    lines: list[str] = []

    if result.missing_required:
        lines.append("Missing required keys:")
        lines.extend(f"  - {key}" for key in result.missing_required)

    if result.missing_recommended:
        lines.append("Missing recommended keys:")
        lines.extend(f"  - {key}" for key in result.missing_recommended)

    if result.warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in result.warnings)

    return "\n".join(lines)
