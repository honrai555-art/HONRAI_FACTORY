"""Optimize FBX assets inside Blender batch mode."""
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
        '  blender --background --python optimize_fbx.py -- --input "input_assets/model.fbx"'
    ) from exc

from pipeline_utils import append_log, parse_script_args, resolve_project_root


DEFAULT_DECIMATE_RATIO = 0.5
MAX_TEXTURE_SIZE = 1024
REMOVABLE_TYPES = {"CAMERA", "LIGHT"}


def parse_args(argv: list[str]) -> argparse.Namespace:
    project_root = resolve_project_root()
    parser = argparse.ArgumentParser(description="Import and optimize an FBX file in Blender.")
    parser.add_argument("--input", required=True, help="Input FBX path")
    parser.add_argument(
        "--output-blend",
        default="",
        help="Optimized .blend output path (default: output_assets/<name>_optimized.blend)",
    )
    parser.add_argument(
        "--decimate-ratio",
        type=float,
        default=DEFAULT_DECIMATE_RATIO,
        help=f"Decimate ratio 0-1 (default: {DEFAULT_DECIMATE_RATIO})",
    )
    parser.add_argument(
        "--max-texture-size",
        type=int,
        default=MAX_TEXTURE_SIZE,
        help=f"Maximum texture edge length (default: {MAX_TEXTURE_SIZE})",
    )
    parser.add_argument(
        "--log",
        default=str(project_root / "logs" / "blender_build.log"),
        help="Log file path",
    )
    return parser.parse_args(argv)


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_fbx(fbx_path: Path) -> None:
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))


def remove_unnecessary_objects(log_path: Path) -> int:
    removed = 0
    objects = list(bpy.data.objects)
    for obj in objects:
        should_remove = False
        if obj.type in REMOVABLE_TYPES:
            should_remove = True
        elif obj.type == "EMPTY" and len(obj.children) == 0 and obj.parent is None:
            should_remove = True

        if should_remove:
            append_log(log_path, f"Removing object: {obj.name} ({obj.type})")
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1
    return removed


def apply_decimate(ratio: float, log_path: Path) -> int:
    processed = 0
    clamped_ratio = max(0.01, min(1.0, ratio))
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.data]

    for obj in mesh_objects:
        face_count = len(obj.data.polygons)
        if face_count < 4:
            continue

        modifier = obj.modifiers.new(name="HONRAI_Decimate", type="DECIMATE")
        modifier.ratio = clamped_ratio

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="HONRAI_Decimate")

        new_face_count = len(obj.data.polygons)
        append_log(
            log_path,
            f"Decimated {obj.name}: {face_count} -> {new_face_count} faces (ratio={clamped_ratio})",
        )
        processed += 1

    return processed


def resize_textures(max_size: int, log_path: Path) -> int:
    resized = 0
    for image in bpy.data.images:
        if image.size[0] == 0 or image.size[1] == 0:
            continue

        width, height = image.size
        longest_edge = max(width, height)
        if longest_edge <= max_size:
            continue

        scale = max_size / float(longest_edge)
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        image.scale(new_width, new_height)
        append_log(log_path, f"Resized texture {image.name}: {width}x{height} -> {new_width}x{new_height}")
        resized += 1

    return resized


def save_blend(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))


def main() -> int:
    args = parse_args(parse_script_args())
    log_path = Path(args.log)
    input_path = Path(args.input).resolve()

    if not input_path.exists():
        append_log(log_path, f"Input FBX not found: {input_path}", level="ERROR")
        return 1

    project_root = resolve_project_root()
    output_blend = Path(args.output_blend) if args.output_blend else (
        project_root / "blender" / "output_assets" / f"{input_path.stem}_optimized.blend"
    )
    output_blend = output_blend.resolve()

    append_log(log_path, f"Optimizing FBX: {input_path}")
    append_log(log_path, f"Output blend: {output_blend}")

    try:
        reset_scene()
        import_fbx(input_path)
        removed = remove_unnecessary_objects(log_path)
        decimated = apply_decimate(args.decimate_ratio, log_path)
        resized = resize_textures(args.max_texture_size, log_path)
        save_blend(output_blend)

        append_log(
            log_path,
            (
                f"Optimization complete: removed={removed}, decimated_meshes={decimated}, "
                f"resized_textures={resized}"
            ),
        )
        print(f"OUTPUT_BLEND={output_blend}")
        return 0
    except Exception as exc:
        append_log(log_path, f"Optimization failed: {exc}", level="ERROR")
        raise


if __name__ == "__main__":
    sys.exit(main())
