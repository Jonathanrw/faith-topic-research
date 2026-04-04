from __future__ import annotations

import requests
from datetime import datetime, timedelta, timezone
from typing import Any

from src.config import YOUTUBE_API_KEY, MAX_SEARCH_RESULTS_PER_QUERY

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def iso_days_ago(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def search_youtube(query: str, published_after_days: int = 30) -> list[dict[str, Any]]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "relevance",
        "maxResults": MAX_SEARCH_RESULTS_PER_QUERY,
        "publishedAfter": iso_days_ago(published_after_days),
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()

    items = response.json().get("items", [])

    video_ids = [
        item["id"]["videoId"]
        for item in items
        if item.get("id", {}).get("videoId")
    ]

    stats = get_video_stats(video_ids) if video_ids else {}

    enriched = []

    for item in items:
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})

        enriched.append(
            {
                "video_id": video_id,
                "query": query,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "stats": stats.get(video_id, {}),
            }
        )

    return enriched


def get_video_stats(video_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not video_ids:
        return {}

    params = {
        "part": "statistics,contentDetails",
        "id": ",".join(video_ids[:50]),
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(YOUTUBE_VIDEOS_URL, params=params, timeout=30)
    response.raise_for_status()

    output: dict[str, dict[str, Any]] = {}

    for item in response.json().get("items", []):
        output[item["id"]] = {
            "view_count": int(item.get("statistics", {}).get("viewCount", 0)),
            "like_count": int(item.get("statistics", {}).get("likeCount", 0)),
            "comment_count": int(item.get("statistics", {}).get("commentCount", 0)),
            "duration": item.get("contentDetails", {}).get("duration", ""),
        }

    return output
