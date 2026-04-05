from pathlib import Path
from openai import OpenAI

from src.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


AUDIO_DIR = Path("content/audio")


def generate_speech(text: str, output_path: Path) -> None:
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )

    output_path.write_bytes(response.content)


def process_voice_manifest(json_path: Path) -> None:
    import json

    data = json.loads(json_path.read_text(encoding="utf-8"))
    narration = data.get("narration_text", "").strip()

    if not narration:
        print(f"Skipping empty narration: {json_path.name}")
        return

    mp3_path = json_path.with_suffix(".mp3")

    if mp3_path.exists():
        print(f"Audio already exists: {mp3_path.name}")
        return

    print(f"Generating audio for: {json_path.name}")
    generate_speech(narration, mp3_path)


def main() -> None:
    if not AUDIO_DIR.exists():
        print("No audio directory found.")
        return

    files = list(AUDIO_DIR.glob("*_voice.json"))

    if not files:
        print("No voice manifests found.")
        return

    for file in files:
        process_voice_manifest(file)


if __name__ == "__main__":
    main()
