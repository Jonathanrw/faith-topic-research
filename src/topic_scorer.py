from __future__ import annotations

import json
from pathlib import Path
from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def build_research_context(raw_results: list[dict]) -> str:
    lines = []
    for item in raw_results:
        lines.append(
            f"Query: {item['query']}\n"
            f"Title: {item['title']}\n"
            f"Channel: {item['channel_title']}\n"
            f"Published: {item['published_at']}\n"
            f"Views: {item.get('stats', {}).get('view_count', 0)}\n"
            f"Likes: {item.get('stats', {}).get('like_count', 0)}\n"
            f"Comments: {item.get('stats', {}).get('comment_count', 0)}\n"
        )
    return "\n---\n".join(lines[:120])


def score_topics(raw_results: list[dict]) -> list[dict]:
    prompt_path = Path("prompts/topic_scoring_prompt.txt")
    system_prompt = prompt_path.read_text(encoding="utf-8")
    research_context = build_research_context(raw_results)

    user_prompt = f"Research results:\n\n{research_context}\n\nGenerate the best topic opportunities now."

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
