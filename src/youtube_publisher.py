import json
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src.content_packager import get_publish_packages_from_schedule
from src.preflight_validator import validate_publish_packages
from src.publish_manifest import build_manifest, save_manifest
from src.youtube_auth import get_youtube_credentials


SCHEDULE_DIR = Path("content/schedules")


def get_youtube_service():
    creds = get_youtube_credentials()
    return build("youtube", "v3", credentials=creds)


def load_latest_schedule() -> dict:
    files = sorted(SCHEDULE_DIR.glob("*_schedule.json"), reverse=True)
    if not files:
        raise FileNotFoundError("No schedule file found in content/schedules")
    return json.loads(files[0].read_text(encoding="utf-8"))


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
    schedule = load_latest_schedule()
    base_name = schedule["base_name"]

    publish_log_path = SCHEDULE_DIR / f"{base_name}_youtube_publish_log.json"
    results = {
        "base_name": base_name,
        "uploads": [],
    }

    packages = get_publish_packages_from_schedule(schedule)
    validation_errors = validate_publish_packages(packages)

    if validation_errors:
        print("Preflight validation failed:")
        for error in validation_errors:
            print(f" - {error}")
        raise RuntimeError("Publish stopped because preflight validation failed.")

    service = get_youtube_service()

    for package in packages:
        video_path = package["video_path"]

        video_id = upload_video(
            service=service,
            video_path=video_path,
            title=package["title"],
            description=package["description"],
            tags=package["tags"],
            publish_at_iso=package["publish_at"],
        )

        set_thumbnail(service, video_id, package["thumbnail_path"])

        log_entry = {
            "type": package["type"],
            "video_file": package["video_file"],
            "video_id": video_id,
            "publish_at": package["publish_at"],
            "thumbnail_file": package["thumbnail_path"].name,
            "title": package["title"],
            "youtube_altered_content": package["altered_content"],
        }

        if "slot" in package:
            log_entry["slot"] = package["slot"]

        results["uploads"].append(log_entry)

    publish_log_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    manifest = build_manifest(base_name, results["uploads"])
    manifest_path = save_manifest(base_name, manifest)

    print(f"Saved publish log: {publish_log_path}")
    print(f"Saved manifest: {manifest_path}")


if __name__ == "__main__":
    publish_from_schedule()
