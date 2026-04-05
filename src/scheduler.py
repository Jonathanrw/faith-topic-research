import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SCHEDULE_CONFIG_PATH = Path("config/publishing_schedule.json")


def load_schedule_config() -> dict:
    if not SCHEDULE_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing schedule config: {SCHEDULE_CONFIG_PATH}")

    with open(SCHEDULE_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_local_datetime(date_str: str, time_str: str, timezone_name: str) -> str:
    tz = ZoneInfo(timezone_name)
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=tz)
    return dt.isoformat()


def build_daily_schedule(base_name: str, date_str: str | None = None) -> dict:
    config = load_schedule_config()
    timezone_name = config["timezone"]

    local_now = datetime.now(ZoneInfo(timezone_name))
    if date_str is None:
        date_str = local_now.strftime("%Y-%m-%d")

    long_time = config["youtube_long"]
    short_1_time = config["short_1"]
    short_2_time = config["short_2"]
    short_3_time = config["short_3"]

    return {
        "base_name": base_name,
        "timezone": timezone_name,
        "schedule_date": date_str,
        "youtube_long": {
            "video_file": f"{base_name}_long.mp4",
            "publish_at": parse_local_datetime(date_str, long_time, timezone_name),
            "enabled": config["platforms"]["youtube"]["long_enabled"]
        },
        "shorts": [
            {
                "slot": 1,
                "video_file": f"{base_name}_short_1.mp4",
                "publish_at": parse_local_datetime(date_str, short_1_time, timezone_name),
                "platforms": ["youtube_shorts", "instagram_reels", "facebook_reels", "tiktok"]
            },
            {
                "slot": 2,
                "video_file": f"{base_name}_short_2.mp4",
                "publish_at": parse_local_datetime(date_str, short_2_time, timezone_name),
                "platforms": ["youtube_shorts", "instagram_reels", "facebook_reels", "tiktok"]
            },
            {
                "slot": 3,
                "video_file": f"{base_name}_short_3.mp4",
                "publish_at": parse_local_datetime(date_str, short_3_time, timezone_name),
                "platforms": ["youtube_shorts", "instagram_reels", "facebook_reels", "tiktok"]
            }
        ]
    }
