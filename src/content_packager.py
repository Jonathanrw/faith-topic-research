import json
from pathlib import Path

from src.ctr_rules import (
    build_long_youtube_title,
    build_short_youtube_title,
)


VIDEO_DIR = Path("content/videos")
SCRIPT_DIR = Path("content/scripts")
THUMBNAIL_DIR = Path("content/thumbnails")


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_shorts_json(base_name: str) -> list[dict]:
    shorts_path = SCRIPT_DIR / f"{base_name}_shorts.json"
    return json.loads(shorts_path.read_text(encoding="utf-8"))


def build_long_description(script_text: str, altered_content: bool = True) -> str:
    cta = (
        "\n\nIf this helped you, subscribe for more Bible-based encouragement, "
        "clarity, and peace."
    )

    disclosure = ""
    if altered_content:
        disclosure = "\n\nDisclosure: This video includes AI-generated visuals."

    return (script_text[:4000] + cta + disclosure)[:4900]


def build_short_description(script_text: str, altered_content: bool = True) -> str:
    cta = "\n\nSubscribe for more faith-based shorts and daily encouragement."

    disclosure = ""
    if altered_content:
        disclosure = "\n\nDisclosure: This short includes AI-generated visuals."

    return (script_text[:4000] + cta + disclosure)[:4900]


def get_long_package(base_name: str, altered_content: bool = True) -> dict:
    script_path = SCRIPT_DIR / f"{base_name}_long.txt"
    video_path = VIDEO_DIR / f"{base_name}_long.mp4"
    thumbnail_path = THUMBNAIL_DIR / f"{base_name}_youtube.jpg"

    script_text = read_text_file(script_path)

    return {
        "type": "youtube_long",
        "base_name": base_name,
        "video_path": video_path,
        "thumbnail_path": thumbnail_path,
        "title": build_long_youtube_title(base_name),
        "description": build_long_description(script_text, altered_content=altered_content),
        "tags": [
            "faith",
            "christian",
            "bible",
            "encouragement",
            "prayer",
            "jesus",
            "hope",
            "anxiety",
            "hearing god",
            "biblical truth",
        ],
        "altered_content": altered_content,
    }


def get_short_package(base_name: str, slot: int, altered_content: bool = True) -> dict:
    shorts = load_shorts_json(base_name)
    short = shorts[slot - 1]

    video_path = VIDEO_DIR / f"{base_name}_short_{slot}.mp4"
    thumbnail_path = THUMBNAIL_DIR / f"{base_name}_short_{slot}_youtube.jpg"

    short_title = short.get("title", "")
    short_script = short.get("script", "")

    return {
        "type": "youtube_short",
        "base_name": base_name,
        "slot": slot,
        "video_path": video_path,
        "thumbnail_path": thumbnail_path,
        "title": build_short_youtube_title(short_title, slot),
        "description": build_short_description(short_script, altered_content=altered_content),
        "tags": [
            "shorts",
            "faith",
            "christian",
            "bible",
            "encouragement",
            "prayer",
            "hope",
        ],
        "altered_content": altered_content,
    }


def get_publish_packages_from_schedule(schedule: dict) -> list[dict]:
    base_name = schedule["base_name"]
    packages: list[dict] = []

    youtube_long = schedule.get("youtube_long", {})
    if youtube_long.get("enabled", True):
        long_package = get_long_package(
            base_name=base_name,
            altered_content=youtube_long.get("youtube_altered_content", True),
        )
        long_package["publish_at"] = youtube_long["publish_at"]
        long_package["video_file"] = youtube_long["video_file"]
        packages.append(long_package)

    for short in schedule.get("shorts", []):
        short_package = get_short_package(
            base_name=base_name,
            slot=short["slot"],
            altered_content=short.get("youtube_altered_content", True),
        )
        short_package["publish_at"] = short["publish_at"]
        short_package["video_file"] = short["video_file"]
        short_package["platforms"] = short.get("platforms", [])
        packages.append(short_package)

    return packages
