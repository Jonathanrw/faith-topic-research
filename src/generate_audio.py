from pathlib import Path

from src.video_manifest_builder import (
    AUDIO_DIR,
    find_latest_long_script,
    find_latest_shorts_file,
    load_json,
    load_text,
    base_name_from_file,
)
from src.voice_generator import optimize_for_voice, save_voice_manifest


def main() -> None:
    long_script = find_latest_long_script()
    shorts_file = find_latest_shorts_file()

    if not long_script:
        print("No long script found.")
        return

    long_base = base_name_from_file(long_script, "_long.txt")
    long_text = load_text(long_script)
    long_narration = optimize_for_voice(long_text)
    long_manifest = save_voice_manifest(f"{long_base}_long", long_narration, AUDIO_DIR)
    print(f"Saved long voice manifest: {long_manifest}")

    if shorts_file:
        shorts_base = base_name_from_file(shorts_file, "_shorts.json")
        shorts = load_json(shorts_file)

        for idx, short in enumerate(shorts, start=1):
            script_text = short.get("script", "").strip()
            if not script_text:
                continue

            narration = optimize_for_voice(script_text)
            manifest = save_voice_manifest(
                f"{shorts_base}_short_{idx}",
                narration,
                AUDIO_DIR,
            )
            print(f"Saved short voice manifest: {manifest}")


if __name__ == "__main__":
    main()
