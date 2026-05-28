"""Generate binary FBX assets from the procedural catalog."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import bpy
except ImportError as exc:
    raise SystemExit("This script must run inside Blender.") from exc

from asset_catalog import ALL_HOURLY_SLUGS, ASSET_SPECS, AssetPart, AssetSpec
from pipeline_utils import append_log, parse_script_args, resolve_project_root


def parse_args(argv: list[str]) -> argparse.Namespace:
    project_root = resolve_project_root()
    parser = argparse.ArgumentParser(description="Generate binary FBX test assets.")
    parser.add_argument(
        "--output-dir",
        default=str(project_root / "blender" / "input_assets"),
        help="Directory for generated FBX files",
    )
    parser.add_argument(
        "--slugs",
        default="",
        help="Comma-separated slugs to generate (default: all catalog slugs)",
    )
    parser.add_argument(
        "--log",
        default=str(project_root / "logs" / "blender_build.log"),
        help="Log file path",
    )
    return parser.parse_args(argv)


def _add_primitive(part: AssetPart) -> None:
    location = part.location
    scale = part.scale

    if part.primitive == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    elif part.primitive == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=1.0, location=location)
    elif part.primitive == "cone":
        bpy.ops.mesh.primitive_cone_add(radius1=1.0, depth=1.0, location=location)
    elif part.primitive == "uv_sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=location)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)

    obj = bpy.context.active_object
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def export_asset_fbx(output_path: Path, spec: AssetSpec) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for part in spec.parts:
        _add_primitive(part)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=str(output_path),
        use_selection=False,
        object_types={"MESH"},
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
        embed_textures=False,
    )


def resolve_slugs(raw: str) -> list[str]:
    if not raw.strip():
        return list(ALL_HOURLY_SLUGS)

    slugs: list[str] = []
    for item in raw.split(","):
        slug = item.strip()
        if slug and slug in ASSET_SPECS and slug not in slugs:
            slugs.append(slug)
    if not slugs:
        raise ValueError(f"No valid slugs in: {raw}")
    return slugs


def main() -> int:
    args = parse_args(parse_script_args())
    log_path = Path(args.log)
    output_dir = Path(args.output_dir)
    slugs = resolve_slugs(args.slugs)

    for slug in slugs:
        target = output_dir / f"{slug}.fbx"
        append_log(log_path, f"Generating binary FBX: {target} ({slug})")
        export_asset_fbx(target, ASSET_SPECS[slug])
        append_log(log_path, f"Generated binary FBX: {target}")

    print(f"GENERATED_DIR={output_dir}")
    print(f"GENERATED_SLUGS={','.join(slugs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
