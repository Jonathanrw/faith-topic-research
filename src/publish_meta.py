import json
import os
import time
from pathlib import Path
from typing import Any

import requests

from src.content_packager import get_short_package


SCHEDULE_DIR = Path("content/schedules")
LOG_DIR = Path("content/logs")

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "").strip()
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "").strip()
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "").strip()

# For Instagram, Meta needs a public video URL.
# Example if your repo is public:
# https://raw.githubusercontent.com/<owner>/<repo>/main/content/videos
PUBLIC_VIDEO_BASE_URL = os.getenv("PUBLIC_VIDEO_BASE_URL", "").rstrip("/")

GRAPH_API_VERSION = "v19.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_latest_schedule() -> dict[str, Any]:
    files = sorted(SCHEDULE_DIR.glob("*_schedule.json"), reverse=True)
    if not files:
        raise FileNotFoundError("No schedule file found in content/schedules")
    return json.loads(files[0].read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def require_env(name: str, value: str) -> None:
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")


def build_instagram_video_url(video_file: str) -> str:
    if not PUBLIC_VIDEO_BASE_URL:
        raise RuntimeError(
            "Missing PUBLIC_VIDEO_BASE_URL. Instagram publishing needs a public URL "
            "to the video file. Example: "
            "https://raw.githubusercontent.com/<owner>/<repo>/main/content/videos"
        )
    return f"{PUBLIC_VIDEO_BASE_URL}/{video_file}"


def get_meta_caption(base_name: str, slot: int, fallback_title: str = "") -> str:
    """
    Reuses your existing shorts.json content and CTA injection through content_packager.
    """
    package = get_short_package(base_name=base_name, slot=slot, altered_content=True)
    description = package.get("description", "").strip()
    if description:
        return description[:2200]
    return fallback_title[:2200]


def poll_instagram_container_status(creation_id: str, max_attempts: int = 20, sleep_seconds: int = 15) -> dict[str, Any]:
    """
    Waits for the Instagram video container to finish processing.
    """
    status_url = f"{GRAPH_BASE}/{creation_id}"
    params = {
        "fields": "status_code,status",
        "access_token": META_ACCESS_TOKEN,
    }

    last_data: dict[str, Any] = {}

    for attempt in range(1, max_attempts + 1):
        response = requests.get(status_url, params=params, timeout=60)
        data = response.json()
        last_data = data

        status_code = data.get("status_code", "")
        status = data.get("status", "")

        print(f"Instagram container poll {attempt}/{max_attempts}: status_code={status_code} status={status}")

        if status_code == "FINISHED":
            return data

        if status_code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Instagram container failed: {data}")

        time.sleep(sleep_seconds)

    raise RuntimeError(f"Instagram container did not finish in time: {last_data}")


def publish_instagram_reel(video_url: str, caption: str) -> dict[str, Any]:
    require_env("META_ACCESS_TOKEN", META_ACCESS_TOKEN)
    require_env("INSTAGRAM_BUSINESS_ACCOUNT_ID", INSTAGRAM_BUSINESS_ACCOUNT_ID)

    create_url = f"{GRAPH_BASE}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    create_payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN,
    }

    create_resp = requests.post(create_url, data=create_payload, timeout=120)
    create_data = create_resp.json()

    if "id" not in create_data:
        raise RuntimeError(f"Instagram container creation failed: {create_data}")

    creation_id = create_data["id"]

    poll_instagram_container_status(creation_id)

    publish_url = f"{GRAPH_BASE}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN,
    }

    publish_resp = requests.post(publish_url, data=publish_payload, timeout=120)
    publish_data = publish_resp.json()

    if "id" not in publish_data:
        raise RuntimeError(f"Instagram publish failed: {publish_data}")

    return {
        "creation_id": creation_id,
        "instagram_media_id": publish_data["id"],
        "video_url": video_url,
    }


def publish_facebook_reel(video_path: Path, caption: str, title: str) -> dict[str, Any]:
    require_env("META_ACCESS_TOKEN", META_ACCESS_TOKEN)
    require_env("FACEBOOK_PAGE_ID", FACEBOOK_PAGE_ID)

    if not video_path.exists():
        raise FileNotFoundError(f"Facebook video file not found: {video_path}")

    url = f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/videos"

    with video_path.open("rb") as video_file:
        files = {
            "source": (video_path.name, video_file, "video/mp4"),
        }
        data = {
            "description": caption,
            "title": title[:255],
            "access_token": META_ACCESS_TOKEN,
        }

        response = requests.post(url, data=data, files=files, timeout=1800)
        result = response.json()

    if "id" not in result:
        raise RuntimeError(f"Facebook publish failed: {result}")

    return {
        "facebook_video_id": result["id"],
        "video_file": video_path.name,
    }


def publish_from_schedule() -> None:
    ensure_log_dir()
    schedule = load_latest_schedule()
    base_name = schedule["base_name"]

    results: dict[str, Any] = {
        "base_name": base_name,
        "instagram_uploads": [],
        "facebook_uploads": [],
        "errors": [],
    }

    for short in schedule.get("shorts", []):
        slot = short["slot"]
        platforms = short.get("platforms", [])
        video_file = short["video_file"]
        video_path = Path("content/videos") / video_file

        short_package = get_short_package(
            base_name=base_name,
            slot=slot,
            altered_content=short.get("youtube_altered_content", True),
        )

        title = short_package["title"]
        caption = get_meta_caption(base_name=base_name, slot=slot, fallback_title=title)

        if "facebook_reels" in platforms:
            try:
                fb_result = publish_facebook_reel(
                    video_path=video_path,
                    caption=caption,
                    title=title,
                )
                results["facebook_uploads"].append(
                    {
                        "slot": slot,
                        "video_file": video_file,
                        "title": title,
                        "publish_at": short["publish_at"],
                        "status": "published",
                        **fb_result,
                    }
                )
                print(f"Facebook publish succeeded for slot {slot}: {video_file}")
            except Exception as exc:
                results["errors"].append(
                    {
                        "platform": "facebook",
                        "slot": slot,
                        "video_file": video_file,
                        "title": title,
                        "publish_at": short["publish_at"],
                        "status": "failed",
                        "error": str(exc),
                    }
                )
                print(f"Facebook publish failed for slot {slot}: {exc}")

        if "instagram_reels" in platforms:
            try:
                video_url = build_instagram_video_url(video_file)
                ig_result = publish_instagram_reel(
                    video_url=video_url,
                    caption=caption,
                )
                results["instagram_uploads"].append(
                    {
                        "slot": slot,
                        "video_file": video_file,
                        "title": title,
                        "publish_at": short["publish_at"],
                        "status": "published",
                        **ig_result,
                    }
                )
                print(f"Instagram publish succeeded for slot {slot}: {video_file}")
            except Exception as exc:
                results["errors"].append(
                    {
                        "platform": "instagram",
                        "slot": slot,
                        "video_file": video_file,
                        "title": title,
                        "publish_at": short["publish_at"],
                        "status": "failed",
                        "error": str(exc),
                    }
                )
                print(f"Instagram publish failed for slot {slot}: {exc}")

    log_path = LOG_DIR / f"{base_name}_meta_publish_log.json"
    save_json(log_path, results)
    print(f"Saved Meta publish log: {log_path}")

    if results["errors"]:
        print("Meta publishing completed with some errors.")
    else:
        print("Meta publishing completed successfully.")


if __name__ == "__main__":
    publish_from_schedule()
