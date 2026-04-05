import json
from pathlib import Path
from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def optimize_for_voice(script_text: str) -> str:
    system_prompt = load_prompt("prompts/voice_style_prompt.txt")

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": script_text},
        ],
    )

    return response.output_text.strip()


def save_voice_manifest(base_name: str, narration_text: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{base_name}_voice.json"
    payload = {
        "base_name": base_name,
        "narration_text": narration_text,
        "status": "ready_for_tts"
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
