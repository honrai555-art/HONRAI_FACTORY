"""Procedural Blender FBX catalog for auto / hourly generation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetPart:
    primitive: str
    scale: tuple[float, float, float]
    location: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class AssetSpec:
    slug: str
    parts: tuple[AssetPart, ...]


ASSET_SPECS: dict[str, AssetSpec] = {
    "torii": AssetSpec("torii", (AssetPart("cube", (2.0, 0.4, 3.0), (0.0, 0.0, 1.5)),)),
    "bridge": AssetSpec("bridge", (AssetPart("cube", (3.0, 0.3, 12.0), (0.0, 0.0, 0.15)),)),
    "lava_rock": AssetSpec("lava_rock", (AssetPart("uv_sphere", (1.6, 1.2, 0.8), (0.0, 0.0, 0.6)),)),
    "post_town": AssetSpec(
        "post_town",
        (
            AssetPart("cube", (4.0, 3.0, 2.5), (0.0, 0.0, 1.25)),
            AssetPart("cube", (1.2, 1.2, 1.8), (-1.2, 1.0, 0.9)),
        ),
    ),
    "shrine": AssetSpec(
        "shrine",
        (
            AssetPart("cube", (2.5, 2.5, 1.2), (0.0, 0.0, 0.6)),
            AssetPart("cone", (1.8, 1.8, 2.0), (0.0, 0.0, 2.4)),
        ),
    ),
    "forest": AssetSpec(
        "forest",
        (
            AssetPart("cylinder", (0.35, 0.35, 2.5), (0.0, 0.0, 1.25)),
            AssetPart("cone", (1.4, 1.4, 1.8), (0.0, 0.0, 3.0)),
        ),
    ),
    "volcano": AssetSpec("volcano", (AssetPart("cone", (3.5, 3.5, 4.0), (0.0, 0.0, 2.0)),)),
    "mountain": AssetSpec("mountain", (AssetPart("cone", (4.5, 4.5, 5.0), (0.0, 0.0, 2.5)),)),
    "river": AssetSpec("river", (AssetPart("cube", (6.0, 0.2, 14.0), (0.0, 0.0, 0.1)),)),
    "lantern": AssetSpec(
        "lantern",
        (
            AssetPart("cylinder", (0.25, 0.25, 1.6), (0.0, 0.0, 0.8)),
            AssetPart("cube", (0.6, 0.6, 0.8), (0.0, 0.0, 1.8)),
        ),
    ),
    "gate": AssetSpec(
        "gate",
        (
            AssetPart("cube", (0.5, 0.5, 2.8), (-1.2, 0.0, 1.4)),
            AssetPart("cube", (0.5, 0.5, 2.8), (1.2, 0.0, 1.4)),
            AssetPart("cube", (3.0, 0.35, 0.5), (0.0, 0.0, 2.6)),
        ),
    ),
    "tower": AssetSpec("tower", (AssetPart("cylinder", (1.2, 1.2, 6.0), (0.0, 0.0, 3.0)),)),
    "pagoda": AssetSpec(
        "pagoda",
        (
            AssetPart("cube", (2.0, 2.0, 1.0), (0.0, 0.0, 0.5)),
            AssetPart("cube", (1.6, 1.6, 1.0), (0.0, 0.0, 1.6)),
            AssetPart("cube", (1.2, 1.2, 1.0), (0.0, 0.0, 2.7)),
        ),
    ),
    "crystal": AssetSpec("crystal", (AssetPart("cone", (0.8, 0.8, 2.5), (0.0, 0.0, 1.25)),)),
    "cave": AssetSpec("cave", (AssetPart("cube", (3.0, 2.5, 2.0), (0.0, 0.0, 1.0)),)),
    "hot_spring": AssetSpec(
        "hot_spring",
        (
            AssetPart("cylinder", (2.5, 2.5, 0.3), (0.0, 0.0, 0.15)),
            AssetPart("uv_sphere", (0.5, 0.5, 0.5), (0.0, 0.0, 0.6)),
        ),
    ),
    "watchtower": AssetSpec(
        "watchtower",
        (
            AssetPart("cylinder", (1.0, 1.0, 4.5), (0.0, 0.0, 2.25)),
            AssetPart("cube", (2.0, 2.0, 1.0), (0.0, 0.0, 5.0)),
        ),
    ),
    "camp": AssetSpec(
        "camp",
        (
            AssetPart("cone", (2.0, 2.0, 1.8), (0.0, 0.0, 0.9)),
            AssetPart("cube", (0.8, 0.8, 0.6), (1.2, 0.0, 0.3)),
        ),
    ),
    "waterfall": AssetSpec("waterfall", (AssetPart("cube", (2.0, 0.3, 5.0), (0.0, 0.0, 2.5)),)),
    "statue": AssetSpec("statue", (AssetPart("cylinder", (0.8, 0.8, 2.2), (0.0, 0.0, 1.1)),)),
}

ALL_HOURLY_SLUGS: tuple[str, ...] = tuple(ASSET_SPECS.keys())

DEFAULT_HOURLY_INTERVAL_SEC = 7200
DEFAULT_HOURLY_OBJECT_COUNT = 5
DEFAULT_HOURLY_OBJECT_COUNT_MIN = 3
DEFAULT_HOURLY_OBJECT_COUNT_MAX = 7
DEFAULT_HOURLY_ROUTE_LENGTH = 900
HOURLY_ROUTE_LENGTH_PER_OBJECT = 120
HOURLY_ROUTE_LENGTH_MIN = 700
