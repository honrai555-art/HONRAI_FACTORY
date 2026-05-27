"""Generate valid binary FBX test assets for E2E pipeline."""
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
        "--log",
        default=str(project_root / "logs" / "blender_build.log"),
        help="Log file path",
    )
    return parser.parse_args(argv)


def export_cube_fbx(output_path: Path, scale: tuple[float, float, float]) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, scale[2] * 0.5))
    cube = bpy.context.active_object
    cube.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

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


def main() -> int:
    args = parse_args(parse_script_args())
    log_path = Path(args.log)
    output_dir = Path(args.output_dir)
    assets = {
        "torii.fbx": (2.0, 0.4, 3.0),
        "bridge.fbx": (3.0, 0.3, 12.0),
    }

    for filename, scale in assets.items():
        target = output_dir / filename
        append_log(log_path, f"Generating binary FBX: {target}")
        export_cube_fbx(target, scale)
        append_log(log_path, f"Generated binary FBX: {target}")

    print(f"GENERATED_DIR={output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
