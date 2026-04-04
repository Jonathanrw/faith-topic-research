import json
from pathlib import Path


def load_channel(channel_slug: str = "faith") -> dict:
    channel_path = Path(f"channels/{channel_slug}.json")

    if not channel_path.exists():
        raise FileNotFoundError(f"Channel profile not found: {channel_path}")

    with open(channel_path, "r", encoding="utf-8") as f:
        return json.load(f)
