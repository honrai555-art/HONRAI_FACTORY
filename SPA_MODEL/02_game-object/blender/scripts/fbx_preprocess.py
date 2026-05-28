"""Ensure FBX input is binary before Blender 5.x import."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pipeline_utils import append_log, parse_script_args, resolve_project_root

FBX_BINARY_SIGNATURE = b"Kaydara FBX Binary  \x00\x1a\x00"


def parse_args(argv: list[str]) -> argparse.Namespace:
    project_root = resolve_project_root()
    parser = argparse.ArgumentParser(description="Convert ASCII FBX to binary FBX when needed.")
    parser.add_argument("--input", required=True, help="Input FBX path")
    parser.add_argument(
        "--output",
        default="",
        help="Output binary FBX path (default: workspace/temp/<name>_binary.fbx)",
    )
    parser.add_argument(
        "--log",
        default=str(project_root / "logs" / "blender_build.log"),
        help="Log file path",
    )
    return parser.parse_args(argv)


def is_binary_fbx(path: Path) -> bool:
    with path.open("rb") as handle:
        header = handle.read(len(FBX_BINARY_SIGNATURE))
    return header == FBX_BINARY_SIGNATURE


def is_ascii_fbx(path: Path) -> bool:
    with path.open("rb") as handle:
        header = handle.read(64)
    return header.lstrip().startswith(b"; FBX") or header.lstrip().startswith(b";")


def default_output_path(input_path: Path, project_root: Path) -> Path:
    temp_dir = project_root / "workspace" / "temp" / "fbx_binary"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir / f"{input_path.stem}_binary.fbx"


def find_fbx_format_converter() -> Path | None:
    env_path = os.getenv("FBX_FORMAT_CONVERTER_EXE", "").strip()
    if env_path and Path(env_path).exists():
        return Path(env_path)

    project_root = resolve_project_root()
    candidates = [
        project_root / "tools" / "fbx" / "FbxFormatConverter.exe",
        Path(r"C:\Program Files\Autodesk\FBX\FBX Converter\FBXConverter.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def convert_with_fbx_format_converter(input_path: Path, output_path: Path, log_path: Path) -> bool:
    converter = find_fbx_format_converter()
    if converter is None:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(converter),
        "-c",
        str(input_path),
        "-o",
        str(output_path),
        "-binary",
    ]
    append_log(log_path, f"Converting ASCII FBX via FbxFormatConverter: {converter.name}")
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.stdout.strip():
        append_log(log_path, completed.stdout.strip())
    if completed.stderr.strip():
        append_log(log_path, completed.stderr.strip(), level="WARN")
    return completed.returncode == 0 and output_path.exists()


def convert_with_assimp(input_path: Path, output_path: Path, log_path: Path) -> bool:
    try:
        import assimp_py
    except ImportError:
        append_log(log_path, "assimp-py is not installed. Skipping assimp conversion.", level="WARN")
        return False

    flags = (
        assimp_py.Process_Triangulate
        | assimp_py.Process_GenNormals
        | assimp_py.Process_JoinIdenticalVertices
    )
    append_log(log_path, f"Converting ASCII FBX via assimp-py: {input_path.name}")
    try:
        scene = assimp_py.import_file(str(input_path), flags)
    except Exception as exc:
        append_log(log_path, f"assimp import failed: {exc}", level="WARN")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        assimp_py.export_scene(scene, str(output_path), "fbx")
    except Exception as exc:
        append_log(log_path, f"assimp export failed: {exc}", level="WARN")
        return False

    return output_path.exists() and is_binary_fbx(output_path)


def convert_with_blender_legacy(input_path: Path, output_path: Path, log_path: Path) -> bool:
    configured = os.getenv("BLENDER_LEGACY_EXE", "").strip()
    hub_root = Path(r"C:\Program Files\Blender Foundation")
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured))
    if hub_root.exists():
        for version_dir in sorted(hub_root.iterdir(), reverse=True):
            if not version_dir.is_dir():
                continue
            version_name = version_dir.name
            if version_name.startswith("Blender 5"):
                continue
            candidate = version_dir / "blender.exe"
            if candidate.exists():
                candidates.append(candidate)

    convert_script = SCRIPT_DIR / "convert_fbx_in_blender.py"
    if not convert_script.exists():
        return False

    for blender_exe in candidates:
        append_log(log_path, f"Trying legacy Blender conversion: {blender_exe}")
        command = [
            str(blender_exe),
            "--background",
            "--python",
            str(convert_script),
            "--",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--log",
            str(log_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if completed.returncode == 0 and output_path.exists() and is_binary_fbx(output_path):
            return True
        if completed.stderr.strip():
            append_log(log_path, completed.stderr.strip(), level="WARN")
    return False


def convert_ascii_to_binary(input_path: Path, output_path: Path, log_path: Path) -> Path:
    converters = (
        convert_with_fbx_format_converter,
        convert_with_assimp,
        convert_with_blender_legacy,
    )
    for converter in converters:
        if converter(input_path, output_path, log_path) and is_binary_fbx(output_path):
            append_log(log_path, f"ASCII FBX converted to binary: {output_path}")
            return output_path

    raise RuntimeError(
        f"Failed to convert ASCII FBX to binary: {input_path.name}. "
        "Re-export as FBX Binary, or install FbxFormatConverter / assimp-py."
    )


def ensure_binary_fbx(input_path: Path, output_path: Path | None, log_path: Path) -> Path:
    input_path = input_path.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input FBX not found: {input_path}")

    if is_binary_fbx(input_path):
        append_log(log_path, f"FBX already binary: {input_path.name}")
        return input_path

    if not is_ascii_fbx(input_path):
        append_log(
            log_path,
            f"Unknown FBX format for {input_path.name}. Attempting conversion.",
            level="WARN",
        )

    project_root = resolve_project_root()
    target_path = output_path.resolve() if output_path else default_output_path(input_path, project_root)
    append_log(log_path, f"ASCII FBX detected: {input_path.name}")
    return convert_ascii_to_binary(input_path, target_path, log_path)


def parse_cli_args() -> list[str]:
    argv = parse_script_args()
    if argv:
        return argv
    return sys.argv[1:]


def main() -> int:
    args = parse_args(parse_cli_args())
    log_path = Path(args.log)
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    try:
        result_path = ensure_binary_fbx(input_path, output_path, log_path)
        print(f"OUTPUT_FBX={result_path}")
        return 0
    except Exception as exc:
        append_log(log_path, f"FBX preprocess failed: {exc}", level="ERROR")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
