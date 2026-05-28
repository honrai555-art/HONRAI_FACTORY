"""Export optimized Blender scenes to Unity-ready glTF."""
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
    raise SystemExit(
        "This script must run inside Blender. Example:\n"
        '  blender --background --python export_gltf.py -- --blend "output_assets/model_optimized.blend"'
    ) from exc

from pipeline_utils import append_log, parse_script_args, resolve_project_root


def parse_args(argv: list[str]) -> argparse.Namespace:
    project_root = resolve_project_root()
    parser = argparse.ArgumentParser(description="Export a Blender scene to glTF for Unity.")
    parser.add_argument("--blend", required=True, help="Input .blend path")
    parser.add_argument(
        "--output",
        default="",
        help="Output .glb path (default: output_assets/<name>.glb)",
    )
    parser.add_argument(
        "--format",
        choices=("GLB", "GLTF_SEPARATE"),
        default="GLB",
        help="glTF export format (default: GLB)",
    )
    parser.add_argument(
        "--log",
        default=str(project_root / "logs" / "blender_build.log"),
        help="Log file path",
    )
    return parser.parse_args(argv)


def open_blend(blend_path: Path) -> None:
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))


def export_gltf(output_path: Path, export_format: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format=export_format,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_tangents=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
        export_yup=True,
    )


def main() -> int:
    args = parse_args(parse_script_args())
    log_path = Path(args.log)
    blend_path = Path(args.blend).resolve()

    if not blend_path.exists():
        append_log(log_path, f"Blend file not found: {blend_path}", level="ERROR")
        return 1

    project_root = resolve_project_root()
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        stem = blend_path.stem.replace("_optimized", "")
        output_path = (project_root / "blender" / "output_assets" / f"{stem}.glb").resolve()

    append_log(log_path, f"Exporting glTF: {blend_path} -> {output_path}")

    try:
        open_blend(blend_path)
        export_gltf(output_path, args.format)
        append_log(log_path, f"glTF export complete: {output_path}")
        print(f"OUTPUT_GLTF={output_path}")
        return 0
    except Exception as exc:
        append_log(log_path, f"glTF export failed: {exc}", level="ERROR")
        raise


if __name__ == "__main__":
    sys.exit(main())
