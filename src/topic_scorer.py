from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

WINNER_SUMMARY_PATH = Path("data/winner_summary.json")


def load_winner_summary() -> dict:
    if not WINNER_SUMMARY_PATH.exists():
        return {
            "video_count": 0,
            "top_topics": [],
            "top_hooks": [],
            "winners": [],
        }

    try:
        return json.loads(WINNER_SUMMARY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {
            "video_count": 0,
            "top_topics": [],
            "top_hooks": [],
            "winners": [],
        }


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


def build_winner_context(summary: dict) -> str:
    if not summary or summary.get("video_count", 0) == 0:
        return "No winner data available yet."

    lines = [f"Winner video count analyzed: {summary.get('video_count', 0)}"]

    top_topics = summary.get("top_topics", [])
    if top_topics:
        lines.append("Top performing topics:")
        for item in top_topics[:5]:
            lines.append(f"- {item.get('topic', '')}: {item.get('count', 0)}")

    top_hooks = summary.get("top_hooks", [])
    if top_hooks:
        lines.append("Top performing hook patterns:")
        for item in top_hooks[:5]:
            lines.append(f"- {item.get('hook_pattern', '')}: {item.get('count', 0)}")

    winners = summary.get("winners", [])
    if winners:
        lines.append("Best recent winners:")
        for item in winners[:10]:
            lines.append(
                f"- Title: {item.get('title', '')} | "
                f"Topic: {item.get('topic', '')} | "
                f"Hook: {item.get('hook_pattern', '')} | "
                f"Views: {item.get('view_count', 0)} | "
                f"Engagement Rate: {item.get('engagement_rate', 0.0)}"
            )

    return "\n".join(lines)


def score_topics(raw_results: list[dict]) -> list[dict]:
    prompt_path = Path("prompts/topic_scoring_prompt.txt")
    system_prompt = prompt_path.read_text(encoding="utf-8")

    research_context = build_research_context(raw_results)
    winner_summary = load_winner_summary()
    winner_context = build_winner_context(winner_summary)

    user_prompt = (
        "Research results:\n\n"
        f"{research_context}\n\n"
        "Historical winner context:\n\n"
        f"{winner_context}\n\n"
        "Generate the best topic opportunities now.\n\n"
        "Important:\n"
        "- Prefer ideas that are closely related to proven winning topics and hook patterns.\n"
        "- Still allow some variation, but bias toward what has already performed well.\n"
        "- Prioritize topics that can work as both long-form videos and shorts.\n"
        "- Return only valid JSON."
    )

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
