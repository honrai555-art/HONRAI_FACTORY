"""Convert ASCII FBX to binary FBX using a legacy Blender build (< 5.0)."""
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

from pipeline_utils import append_log, parse_script_args


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert ASCII FBX to binary FBX in Blender.")
    parser.add_argument("--input", required=True, help="Input FBX path")
    parser.add_argument("--output", required=True, help="Output binary FBX path")
    parser.add_argument("--log", default="", help="Optional log path")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(parse_script_args())
    log_path = Path(args.log) if args.log else None
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path:
        append_log(log_path, f"Legacy Blender converting FBX: {input_path} -> {output_path}")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(input_path))
    bpy.ops.export_scene.fbx(
        filepath=str(output_path),
        use_selection=False,
        object_types={"MESH", "ARMATURE", "EMPTY"},
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
        embed_textures=False,
    )
    if log_path:
        append_log(log_path, f"Legacy Blender conversion complete: {output_path}")
    print(f"OUTPUT_FBX={output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
