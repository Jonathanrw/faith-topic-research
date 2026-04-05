import base64
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.channel_loader import load_channel
from src.config import OPENAI_API_KEY
from src.video_manifest_builder import (
    find_latest_long_script,
    find_latest_shorts_file,
    load_json,
    load_text,
    base_name_from_file,
)
from src.background_prompt_builder import (
    build_long_background_prompt,
    build_short_background_prompt,
)

BACKGROUND_DIR = Path("content/backgrounds")
IMAGES_URL = "https://api.openai.com/v1/images/generations"


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def ensure_output_dir() -> None:
    BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\\s-]", "", text)
    text = re.sub(r"\\s+", "-", text)
    return text[:80].strip("-")


def generate_image_bytes(prompt: str, size: str = "1536x1024") -> bytes:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": size,
        "output_format": "png",
    }

    response = requests.post(IMAGES_URL, headers=headers, json=payload, timeout=120)

    if not response.ok:
        print("Image API error:")
        print(response.status_code)
        print(response.text)
        response.raise_for_status()

    data = response.json()

    if "data" not in data or not data["data"]:
        raise ValueError(f"Unexpected image response: {data}")

    image_b64 = data["data"][0]["b64_json"]
    return base64.b64decode(image_b64)


def save_image(path: Path, image_bytes: bytes) -> None:
    path.write_bytes(image_bytes)


def save_prompt_metadata(path: Path, prompt: str, kind: str) -> None:
    meta = {
        "kind": kind,
        "prompt": prompt,
        "created_at": now_stamp(),
    }
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def main(channel_slug: str = "faith") -> None:
    ensure_output_dir()
    channel = load_channel(channel_slug)

    long_script = find_latest_long_script()
    shorts_file = find_latest_shorts_file()

    if not long_script:
        print("No long script found.")
        return

    long_text = load_text(long_script)
    long_base = base_name_from_file(long_script, "_long.txt")
    long_topic = long_base.replace("_", " ").replace("-", " ")

    long_prompt = build_long_background_prompt(long_topic, long_text, channel)
    long_image = generate_image_bytes(long_prompt, size="1536x1024")

    long_image_path = BACKGROUND_DIR / f"{long_base}_bg.png"
    long_meta_path = BACKGROUND_DIR / f"{long_base}_bg_prompt.json"
    save_image(long_image_path, long_image)
    save_prompt_metadata(long_meta_path, long_prompt, "long")
    print(f"Saved long background: {long_image_path}")

    if shorts_file:
        shorts = load_json(shorts_file)
        shorts_base = base_name_from_file(shorts_file, "_shorts.json")

        for idx, short in enumerate(shorts, start=1):
            title = short.get("title", f"short {idx}")
            script_text = short.get("script", "").strip()
            if not script_text:
                continue

            prompt = build_short_background_prompt(title, script_text, channel)
            image_bytes = generate_image_bytes(prompt, size="1024x1536")

            image_path = BACKGROUND_DIR / f"{shorts_base}_short_{idx}_bg.png"
            meta_path = BACKGROUND_DIR / f"{shorts_base}_short_{idx}_bg_prompt.json"

            save_image(image_path, image_bytes)
            save_prompt_metadata(meta_path, prompt, "short")
            print(f"Saved short background: {image_path}")


if __name__ == "__main__":
    main("faith")
