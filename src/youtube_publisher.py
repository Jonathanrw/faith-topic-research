import json
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src.youtube_auth import get_youtube_credentials


VIDEO_DIR = Path("content/videos")
SCHEDULE_DIR = Path("content/schedules")
THUMBNAIL_DIR = Path("content/thumbnails")
SCRIPT_DIR = Path("content/scripts")


def get_youtube_service():
    creds = get_youtube_credentials()
    return build("youtube", "v3", credentials=creds)


def load_latest_schedule() -> dict:
    files = sorted(SCHEDULE_DIR.glob("*_schedule.json"), reverse=True)
    if not files:
        raise FileNotFoundError("No schedule file found in content/schedules")
    return json.loads(files[0].read_text(encoding="utf-8"))


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def find_long_script(base_name: str) -> Path:
    return SCRIPT_DIR / f"{base_name}_long.txt"


def find_shorts_json(base_name: str) -> Path:
    return SCRIPT_DIR / f"{base_name}_shorts.json"


def build_long_metadata(base_name: str, altered_content: bool = True) -> dict:
    script_path = find_long_script(base_name)
    script_text = read_text_file(script_path)

    title = base_name.replace("_", " ").replace("-", " ").strip()
    title = title[:95]

    description = script_text[:4300]

    if altered_content:
        description += "\n\nDisclosure: This video includes AI-generated visuals."

    return {
        "title": title,
        "description": description,
        "tags": ["faith", "encouragement", "christian", "bible", "hope"],
    }


def build_short_metadata(base_name: str, slot: int, altered_content: bool = True) -> dict:
    shorts_path = find_shorts_json(base_name)
    shorts = json.loads(shorts_path.read_text(encoding="utf-8"))

    short = shorts[slot - 1]
    title = short.get("title", f"Short {slot}")[:95]
    description = short.get("script", "")[:4300]

    if altered_content:
        description += "\n\nDisclosure: This short includes AI-generated visuals."

    return {
        "title": title,
        "description": description,
        "tags": ["shorts", "faith", "encouragement", "christian"],
    }


def upload_video(
    service,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    publish_at_iso: str,
) -> str:
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_iso,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)

    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        _, response = request.next_chunk()

    return response["id"]


def set_thumbnail(service, video_id: str, thumbnail_path: Path) -> None:
    if not thumbnail_path.exists():
        print(f"Thumbnail not found: {thumbnail_path}")
        return

    media = MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
    service.thumbnails().set(
        videoId=video_id,
        media_body=media,
    ).execute()
    print(f"Thumbnail set: {thumbnail_path}")


def publish_from_schedule() -> None:
    service = get_youtube_service()
    schedule = load_latest_schedule()
    base_name = schedule["base_name"]

    publish_log_path = SCHEDULE_DIR / f"{base_name}_youtube_publish_log.json"
    results = {
        "base_name": base_name,
        "uploads": [],
    }

    long_altered = schedule["youtube_long"].get("youtube_altered_content", True)
    long_meta = build_long_metadata(base_name, altered_content=long_altered)
    long_video = VIDEO_DIR / schedule["youtube_long"]["video_file"]
    long_publish_at = schedule["youtube_long"]["publish_at"]

    if long_video.exists():
        long_video_id = upload_video(
            service=service,
            video_path=long_video,
            title=long_meta["title"],
            description=long_meta["description"],
            tags=long_meta["tags"],
            publish_at_iso=long_publish_at,
        )

        long_thumb = THUMBNAIL_DIR / f"{base_name}_youtube.jpg"
        set_thumbnail(service, long_video_id, long_thumb)

        results["uploads"].append(
            {
                "type": "youtube_long",
                "video_file": long_video.name,
                "video_id": long_video_id,
                "publish_at": long_publish_at,
                "thumbnail_file": long_thumb.name,
                "youtube_altered_content": long_altered,
            }
        )

    for short in schedule["shorts"]:
        slot = short["slot"]
        short_video = VIDEO_DIR / short["video_file"]
        short_publish_at = short["publish_at"]

        if not short_video.exists():
            continue

        short_altered = short.get("youtube_altered_content", True)
        meta = build_short_metadata(base_name, slot, altered_content=short_altered)

        short_video_id = upload_video(
            service=service,
            video_path=short_video,
            title=meta["title"],
            description=meta["description"],
            tags=meta["tags"],
            publish_at_iso=short_publish_at,
        )

        short_thumb = THUMBNAIL_DIR / f"{base_name}_short_{slot}_youtube.jpg"
        set_thumbnail(service, short_video_id, short_thumb)

        results["uploads"].append(
            {
                "type": "youtube_short",
                "slot": slot,
                "video_file": short_video.name,
                "video_id": short_video_id,
                "publish_at": short_publish_at,
                "thumbnail_file": short_thumb.name,
                "youtube_altered_content": short_altered,
            }
        )

    publish_log_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved publish log: {publish_log_path}")
