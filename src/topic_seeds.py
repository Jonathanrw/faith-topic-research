import json
from pathlib import Path


def load_channel_profile(channel_slug: str = "faith") -> dict:
    channel_path = Path(f"channels/{channel_slug}.json")
    if not channel_path.exists():
        raise FileNotFoundError(f"Channel profile not found: {channel_path}")

    with open(channel_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_seed_patterns(channel_slug: str = "faith") -> list[str]:
    profile = load_channel_profile(channel_slug)
    return profile.get("seed_patterns", [])


def get_short_hook_patterns(channel_slug: str = "faith") -> list[str]:
    profile = load_channel_profile(channel_slug)
    return profile.get("short_hook_patterns", [])
