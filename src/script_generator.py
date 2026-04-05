import json
from pathlib import Path
from openai import OpenAI

from src.channel_loader import load_channel
from src.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def generate_long_script(topic: dict, channel_slug: str = "faith") -> str:
    channel = load_channel(channel_slug)
    system_prompt = load_prompt("prompts/long_script_prompt.txt")

    user_prompt = f"""
Channel profile:
{json.dumps(channel, indent=2)}

Topic data:
{json.dumps(topic, indent=2)}

Write the long-form YouTube script now.
""".strip()

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text.strip()


def generate_short_scripts(topic: dict, channel_slug: str = "faith") -> list[dict]:
    channel = load_channel(channel_slug)
    system_prompt = load_prompt("prompts/short_script_prompt.txt")

    user_prompt = f"""
Channel profile:
{json.dumps(channel, indent=2)}

Topic data:
{json.dumps(topic, indent=2)}

Write the 3 short-form scripts now.
""".strip()

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.output_text.strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    return []
