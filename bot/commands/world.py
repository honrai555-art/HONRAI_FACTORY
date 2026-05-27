import json
import os
import re
from datetime import datetime
from pathlib import Path

from bot.commands.unity import run_import_generated_assets, run_unity_world_build
from bot.utils.logger import get_logger

logger = get_logger("world")

OBJECT_SLUG_MAP = {
    "鳥居": "torii",
    "torii": "torii",
    "橋": "bridge",
    "bridge": "bridge",
    "溶岩": "lava_rock",
    "lava": "lava_rock",
    "lava_rock": "lava_rock",
    "宿場町": "post_town",
    "posttown": "post_town",
    "post_town": "post_town",
    "森": "forest",
    "forest": "forest",
    "川": "river",
    "river": "river",
    "山": "mountain",
    "mountain": "mountain",
    "神社": "shrine",
    "shrine": "shrine",
    "火山": "volcano",
    "volcano": "volcano",
}

CHARACTER_SLUG_MAP = {
    "ホンライくん": "honrai_kun",
    "honrai_kun": "honrai_kun",
    "たぬき": "tanuki",
    "tanuki": "tanuki",
    "鹿": "deer",
    "deer": "deer",
    "モグラ": "mole",
    "mole": "mole",
}

KNOWN_OBJECTS = list(OBJECT_SLUG_MAP.keys())
KNOWN_CHARACTERS = list(CHARACTER_SLUG_MAP.keys())

DEFAULT_ROUTE_LENGTH = 500
DEFAULT_TARGET = "Spatial軽量版"
DEFAULT_MOOD = "探索"
LOG_TAIL_LINES = 40


def _project_root() -> Path:
    project_root = os.getenv("PROJECT_ROOT", "").strip()
    if not project_root:
        raise RuntimeError("PROJECT_ROOT is not configured in bot/.env")
    return Path(project_root)


def _world_request_path() -> Path:
    return _project_root() / "world_request.json"


def _unity_world_log_path() -> Path:
    return _project_root() / "logs" / "unity_world_build.log"


def _normalize_slug(name: str, slug_map: dict[str, str]) -> str:
    if name in slug_map:
        return slug_map[name]

    if re.fullmatch(r"[a-z0-9_]+", name):
        return name

    return re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_") or name


def _normalize_object_slug(name: str) -> str:
    return _normalize_slug(name, OBJECT_SLUG_MAP)


def _normalize_character_slug(name: str) -> str:
    return _normalize_slug(name, CHARACTER_SLUG_MAP)


def extract_terms_in_order(text: str, known_terms: list[str]) -> list[str]:
    ordered = sorted(known_terms, key=len, reverse=True)
    found: list[str] = []
    index = 0

    while index < len(text):
        matched = None
        for term in ordered:
            if text.startswith(term, index):
                matched = term
                break

        if matched:
            found.append(matched)
            index += len(matched)
            continue

        index += 1

    return found


def _split_known_from_token(
    token: str,
    known_terms: list[str],
) -> tuple[list[str], str]:
    if token in known_terms:
        return [token], ""

    found = extract_terms_in_order(token, known_terms)
    if not found:
        return [], token

    remainder = token
    for term in found:
        remainder = remainder.replace(term, "", 1)
    remainder = remainder.strip()

    if len(remainder) >= 2:
        return [], token

    return found, remainder


def _parse_route_length(text: str) -> int:
    route_match = re.search(r"(?:route|length|距離)[:：\s-]*(\d+)", text, re.IGNORECASE)
    if route_match:
        return int(route_match.group(1))

    meter_match = re.search(r"(\d+)\s*m\b", text, re.IGNORECASE)
    if meter_match:
        return int(meter_match.group(1))

    for token in text.split():
        if token.isdigit():
            value = int(token)
            if 50 <= value <= 10000:
                return value

    return DEFAULT_ROUTE_LENGTH


def _build_theme(theme_parts: list[str], fallback_text: str) -> str:
    theme_text = " ".join(part for part in theme_parts if part).strip()
    theme_text = re.sub(
        r"(?:route|length|距離)[:：\s-]*\d+\s*m?\b",
        " ",
        theme_text,
        flags=re.IGNORECASE,
    )
    theme_text = re.sub(r"\b\d+\s*m\b", " ", theme_text, flags=re.IGNORECASE)
    theme_text = re.sub(r"\s+", " ", theme_text).strip()

    if theme_text:
        return theme_text

    compact = re.sub(r"\s+", "", fallback_text)
    if compact:
        return compact

    return "HONRAI探索ルート"


def parse_world_instruction(instruction: str) -> dict:
    text = instruction.strip()
    if not text:
        raise ValueError("world 指示が空です。例: !world 火山の街道 鳥居 溶岩 ホンライくん")

    objects: list[str] = []
    characters: list[str] = []
    theme_parts: list[str] = []

    for token in text.split():
        if token.isdigit():
            continue

        if token in KNOWN_OBJECTS:
            objects.append(_normalize_object_slug(token))
            continue

        if token in KNOWN_CHARACTERS:
            characters.append(_normalize_character_slug(token))
            continue

        token_objects, object_remainder = _split_known_from_token(token, KNOWN_OBJECTS)
        token_characters, character_remainder = _split_known_from_token(token, KNOWN_CHARACTERS)

        if token_objects or token_characters:
            objects.extend(_normalize_object_slug(name) for name in token_objects)
            characters.extend(_normalize_character_slug(name) for name in token_characters)
            remainder = object_remainder
            for term in token_characters:
                remainder = remainder.replace(term, "", 1)
            if remainder.strip():
                theme_parts.append(remainder.strip())
            continue

        theme_parts.append(token)

    theme = _build_theme(theme_parts, text)
    route_length = _parse_route_length(text)
    world_name = f"KAIDO_{datetime.now():%Y%m%d_%H%M%S}"

    if not objects:
        objects = ["torii", "bridge"]

    if not characters:
        characters = ["honrai_kun"]

    objects = [_normalize_object_slug(name) for name in objects]
    characters = [_normalize_character_slug(name) for name in characters]

    request = {
        "world_name": world_name,
        "theme": theme,
        "route_length": route_length,
        "objects": objects,
        "characters": characters,
        "mood": DEFAULT_MOOD,
        "target": DEFAULT_TARGET,
    }

    logger.info("Parsed world request: %s", request)
    return request


def build_auto_world_request(input_dir: Path) -> dict:
    character_slugs = set(CHARACTER_SLUG_MAP.values())
    objects: list[str] = []
    characters: list[str] = []

    for fbx_path in sorted(input_dir.glob("*.fbx")):
        slug = _normalize_object_slug(fbx_path.stem)
        if slug in character_slugs:
            characters.append(_normalize_character_slug(slug))
        else:
            objects.append(slug)

    if not objects:
        objects = ["torii", "bridge"]

    if not characters:
        characters = ["honrai_kun"]

    return {
        "world_name": f"AUTO_{datetime.now():%Y%m%d_%H%M%S}",
        "theme": "auto detected assets",
        "route_length": DEFAULT_ROUTE_LENGTH,
        "objects": objects,
        "characters": characters,
        "mood": DEFAULT_MOOD,
        "target": DEFAULT_TARGET,
    }


def write_world_request(request: dict) -> Path:
    json_path = _world_request_path()
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(request, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")

    logger.info("Updated world_request.json: %s", json_path)
    return json_path


def get_unity_import_log_tail(lines: int = LOG_TAIL_LINES) -> str:
    log_path = _project_root() / "logs" / "unity_import.log"
    if not log_path.exists():
        return "logs/unity_import.log が見つかりません。"

    try:
        content = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return f"ログ読み取りに失敗しました: {exc}"

    if not content:
        return "logs/unity_import.log は空です。"

    return "\n".join(content[-lines:])


def get_unity_world_log_tail(lines: int = LOG_TAIL_LINES) -> str:
    log_path = _unity_world_log_path()
    if not log_path.exists():
        return "logs/unity_world_build.log が見つかりません。"

    try:
        content = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return f"ログ読み取りに失敗しました: {exc}"

    if not content:
        return "logs/unity_world_build.log は空です。"

    tail = content[-lines:]
    return "\n".join(tail)


def run_world_request(request: dict) -> dict:
    json_path = write_world_request(request)

    try:
        run_import_generated_assets(wait=True)
    except Exception:
        tail = get_unity_import_log_tail()
        raise RuntimeError(f"Generated asset import failed.\n{tail}") from None

    try:
        run_unity_world_build(wait=True, import_assets=False)
    except Exception:
        tail = get_unity_world_log_tail()
        raise RuntimeError(tail) from None

    return {
        "json_path": str(json_path),
        "request": request,
    }


def run_world_pipeline(instruction: str) -> dict:
    request = parse_world_instruction(instruction)
    return run_world_request(request)


def format_world_summary(request: dict) -> str:
    objects = ", ".join(request["objects"])
    characters = ", ".join(request["characters"])
    return (
        f"world_name: {request['world_name']}\n"
        f"theme: {request['theme']}\n"
        f"objects: {objects}\n"
        f"characters: {characters}\n"
        f"route_length: {request['route_length']}\n"
        f"target: {request['target']}"
    )
