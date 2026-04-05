import json
import re
from datetime import datetime, timezone
from pathlib import Path

from src.queue_manager import get_best_queued_topic, mark_topic_as_used
from src.script_generator import generate_long_script, generate_short_scripts


CONTENT_DIR = Path("content/scripts")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text[:80].strip("-")


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def ensure_output_dir() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)


def save_long_script(topic: dict, script_text: str) -> Path:
    filename = f"{now_stamp()}_{slugify(topic['topic'])}_long.txt"
    path = CONTENT_DIR / filename
    path.write_text(script_text, encoding="utf-8")
    return path


def save_short_scripts(topic: dict, shorts: list[dict]) -> Path:
    filename = f"{now_stamp()}_{slugify(topic['topic'])}_shorts.json"
    path = CONTENT_DIR / filename
    path.write_text(json.dumps(shorts, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main(channel_slug: str = "faith") -> None:
    ensure_output_dir()

    topic = get_best_queued_topic(channel_slug)
    if not topic:
        print("No queued topic found.")
        return

    print(f"Generating scripts for: {topic['topic']}")

    long_script = generate_long_script(topic, channel_slug)
    short_scripts = generate_short_scripts(topic, channel_slug)

    if not long_script:
        print("Long script generation failed.")
        return

    if not short_scripts:
        print("Short script generation failed.")
        return

    long_path = save_long_script(topic, long_script)
    short_path = save_short_scripts(topic, short_scripts)

    mark_topic_as_used(topic)

    print(f"Saved long script to: {long_path}")
    print(f"Saved short scripts to: {short_path}")
    print("Topic marked as used.")


if __name__ == "__main__":
    main("faith")
