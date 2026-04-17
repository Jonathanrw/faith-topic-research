from pathlib import Path
from typing import Any, Iterable

from src.video_manifest_builder import (
    AUDIO_DIR,
    base_name_from_file,
    find_latest_long_script,
    find_latest_shorts_file,
    load_json,
    load_text,
)
from src.voice_generator import optimize_for_voice, save_voice_manifest


MAX_SHORTS = 3


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def ensure_audio_dir() -> None:
    Path(AUDIO_DIR).mkdir(parents=True, exist_ok=True)


def load_shorts_safely(shorts_file: Path) -> list[dict]:
    try:
        data = load_json(shorts_file)
    except Exception as exc:
        print(f"Failed to load shorts JSON: {shorts_file} | error={exc}")
        return []

    if not isinstance(data, list):
        print(f"Shorts file is not a list: {shorts_file}")
        return []

    cleaned: list[dict] = []
    for item in data:
        if isinstance(item, dict):
            cleaned.append(item)

    return cleaned


def build_voice_manifest(asset_name: str, script_text: str) -> Path | None:
    script_text = safe_text(script_text)
    if not script_text:
        print(f"Skipping {asset_name}: empty script.")
        return None

    try:
        narration = optimize_for_voice(script_text)
        narration = safe_text(narration)

        if not narration:
            print(f"Skipping {asset_name}: optimize_for_voice returned empty text.")
            return None

        manifest_path = save_voice_manifest(asset_name, narration, AUDIO_DIR)
        print(f"Saved voice manifest: {manifest_path}")
        return Path(manifest_path)

    except Exception as exc:
        print(f"Failed to build voice manifest for {asset_name}: {exc}")
        return None


def process_long_video() -> int:
    long_script = find_latest_long_script()

    if not long_script:
        print("No long script found.")
        return 0

    long_base = base_name_from_file(long_script, "_long.txt")
    long_text = load_text(long_script)

    manifest = build_voice_manifest(f"{long_base}_long", long_text)
    return 1 if manifest else 0


def iter_valid_shorts(shorts: Iterable[dict]) -> Iterable[tuple[int, dict]]:
    valid_index = 0

    for raw_index, short in enumerate(shorts, start=1):
        script_text = safe_text(short.get("script"))

        if not script_text:
            print(f"Skipping short #{raw_index}: missing script.")
            continue

        valid_index += 1
        yield valid_index, short

        if valid_index >= MAX_SHORTS:
            break


def process_shorts() -> int:
    shorts_file = find_latest_shorts_file()

    if not shorts_file:
        print("No shorts file found.")
        return 0

    shorts_base = base_name_from_file(shorts_file, "_shorts.json")
    shorts = load_shorts_safely(shorts_file)

    if not shorts:
        print("No valid shorts found in shorts JSON.")
        return 0

    created = 0

    for idx, short in iter_valid_shorts(shorts):
        script_text = safe_text(short.get("script"))
        manifest = build_voice_manifest(f"{shorts_base}_short_{idx}", script_text)
        if manifest:
            created += 1

    return created


def main() -> None:
    ensure_audio_dir()

    long_count = process_long_video()
    short_count = process_shorts()

    total = long_count + short_count
    print(
        f"Audio manifest generation complete | "
        f"long={long_count} | shorts={short_count} | total={total}"
    )

    if total == 0:
        raise SystemExit("No audio manifests were created.")


if __name__ == "__main__":
    main()
