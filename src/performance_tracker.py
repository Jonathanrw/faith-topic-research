import json
import os
from datetime import datetime, timezone
from pathlib import Path

from googleapiclient.discovery import build


MANIFEST_DIR = Path("content/manifests")
DATA_DIR = Path("data")
HISTORY_PATH = DATA_DIR / "performance_history.json"
LATEST_PATH = DATA_DIR / "performance_latest.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_youtube_service():
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY secret.")
    return build("youtube", "v3", developerKey=api_key)


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def get_all_manifests() -> list[Path]:
    if not MANIFEST_DIR.exists():
        return []
    return sorted(MANIFEST_DIR.glob("*_manifest_*.json"))


def collect_uploaded_videos() -> list[dict]:
    manifests = get_all_manifests()
    if not manifests:
        return []

    seen_video_ids = set()
    videos: list[dict] = []

    for manifest_path in manifests:
        manifest = load_json(manifest_path, {})
        base_name = manifest.get("base_name", "")
        uploads = manifest.get("uploads", [])

        for upload in uploads:
            video_id = upload.get("video_id", "").strip()
            if not video_id or video_id in seen_video_ids:
                continue

            seen_video_ids.add(video_id)

            videos.append(
                {
                    "base_name": base_name,
                    "type": upload.get("type", ""),
                    "slot": upload.get("slot"),
                    "video_id": video_id,
                    "title": upload.get("title", ""),
                    "publish_at": upload.get("publish_at", ""),
                    "video_file": upload.get("video_file", ""),
                    "thumbnail_file": upload.get("thumbnail_file", ""),
                }
            )

    return videos


def chunked(items: list[str], size: int) -> list[list[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def fetch_video_stats(service, video_ids: list[str]) -> dict[str, dict]:
    stats_map: dict[str, dict] = {}

    for batch in chunked(video_ids, 50):
        response = service.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch),
        ).execute()

        for item in response.get("items", []):
            video_id = item["id"]
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content_details = item.get("contentDetails", {})

            stats_map[video_id] = {
                "video_id": video_id,
                "youtube_title": snippet.get("title", ""),
                "published_at": snippet.get("publishedAt", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "duration": content_details.get("duration", ""),
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "favorite_count": int(statistics.get("favoriteCount", 0)),
            }

    return stats_map


def build_snapshot_entries(uploaded_videos: list[dict], stats_map: dict[str, dict]) -> list[dict]:
    captured_at = datetime.now(timezone.utc).isoformat()

    snapshot_entries: list[dict] = []

    for video in uploaded_videos:
        video_id = video["video_id"]
        stats = stats_map.get(video_id)

        if not stats:
            continue

        entry = {
            "captured_at": captured_at,
            "base_name": video["base_name"],
            "type": video["type"],
            "slot": video.get("slot"),
            "video_id": video_id,
            "scheduled_title": video.get("title", ""),
            "youtube_title": stats.get("youtube_title", ""),
            "publish_at": video.get("publish_at", ""),
            "published_at": stats.get("published_at", ""),
            "channel_title": stats.get("channel_title", ""),
            "duration": stats.get("duration", ""),
            "view_count": stats.get("view_count", 0),
            "like_count": stats.get("like_count", 0),
            "comment_count": stats.get("comment_count", 0),
            "favorite_count": stats.get("favorite_count", 0),
            "video_file": video.get("video_file", ""),
            "thumbnail_file": video.get("thumbnail_file", ""),
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
        }

        views = entry["view_count"]
        likes = entry["like_count"]
        comments = entry["comment_count"]

        entry["engagement_count"] = likes + comments
        entry["engagement_rate"] = round(((likes + comments) / views), 4) if views > 0 else 0.0

        snapshot_entries.append(entry)

    return snapshot_entries


def merge_history(existing_history: list[dict], latest_entries: list[dict]) -> list[dict]:
    merged = list(existing_history)

    existing_keys = {
        (
            item.get("captured_at", ""),
            item.get("video_id", ""),
        )
        for item in existing_history
    }

    for entry in latest_entries:
        key = (entry.get("captured_at", ""), entry.get("video_id", ""))
        if key not in existing_keys:
            merged.append(entry)

    merged.sort(key=lambda x: (x.get("captured_at", ""), x.get("video_id", "")))
    return merged


def build_latest_summary(entries: list[dict]) -> dict:
    ranked = sorted(
        entries,
        key=lambda x: (
            x.get("view_count", 0),
            x.get("engagement_rate", 0.0),
        ),
        reverse=True,
    )

    top_videos = ranked[:10]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "video_count": len(entries),
        "top_videos": top_videos,
    }


def main() -> None:
    ensure_data_dir()

    uploaded_videos = collect_uploaded_videos()
    if not uploaded_videos:
        print("No manifests found. Nothing to track yet.")
        save_json(LATEST_PATH, {"generated_at": datetime.now(timezone.utc).isoformat(), "video_count": 0, "top_videos": []})
        return

    service = get_youtube_service()
    video_ids = [video["video_id"] for video in uploaded_videos]
    stats_map = fetch_video_stats(service, video_ids)

    latest_entries = build_snapshot_entries(uploaded_videos, stats_map)

    existing_history = load_json(HISTORY_PATH, [])
    merged_history = merge_history(existing_history, latest_entries)

    latest_summary = build_latest_summary(latest_entries)

    save_json(HISTORY_PATH, merged_history)
    save_json(LATEST_PATH, latest_summary)

    print(f"Tracked {len(latest_entries)} videos.")
    print(f"Saved history: {HISTORY_PATH}")
    print(f"Saved latest summary: {LATEST_PATH}")


if __name__ == "__main__":
    main()
