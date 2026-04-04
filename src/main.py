from __future__ import annotations

from datetime import datetime, timezone

from src.channel_loader import load_channel
from src.config import (
    DATA_DIR,
    LAST_RUN_FILE,
    MAX_TOPICS_PER_DAY,
    MIN_TOPIC_SCORE,
    RESEARCH_LOG_FILE,
    TOPIC_QUEUE_FILE,
    USED_TOPICS_FILE,
)
from src.dedupe import is_duplicate
from src.storage import ensure_data_dir, load_json, save_json
from src.topic_scorer import score_topics
from src.topic_seeds import get_seed_patterns, get_short_hook_patterns
from src.youtube_research import search_youtube


def run_research(channel_slug: str = "faith") -> None:
    ensure_data_dir(DATA_DIR)

    channel = load_channel(channel_slug)

    used_topics_payload = load_json(USED_TOPICS_FILE, [])
    queue_payload = load_json(TOPIC_QUEUE_FILE, [])
    research_log = load_json(RESEARCH_LOG_FILE, [])

    used_topics = [item["topic"] if isinstance(item, dict) else str(item) for item in used_topics_payload]
    queued_topics = [item["topic"] for item in queue_payload if isinstance(item, dict) and item.get("topic")]
    existing = used_topics + queued_topics

    raw_results: list[dict] = []

    for query in get_seed_patterns(channel_slug) + get_short_hook_patterns(channel_slug):
        try:
            raw_results.extend(search_youtube(query=query, published_after_days=45))
        except Exception as exc:
            research_log.append(
                {
                    "timestamp": now_iso(),
                    "type": "search_error",
                    "channel": channel_slug,
                    "query": query,
                    "error": str(exc),
                }
            )

    candidates = score_topics(raw_results)
    approved = []

    for item in sorted(candidates, key=lambda x: x.get("overall_score", 0), reverse=True):
        topic = item.get("topic", "").strip()
        score = int(item.get("overall_score", 0))

        if not topic:
            continue
        if score < MIN_TOPIC_SCORE:
            continue
        if is_duplicate(topic, existing):
            continue
        if is_duplicate(topic, [a["topic"] for a in approved]):
            continue

        approved.append(
            {
                "channel": channel_slug,
                "channel_name": channel.get("channel_name", channel_slug),
                "topic": topic,
                "why_it_matters": item.get("why_it_matters", ""),
                "short_hook": item.get("short_hook", ""),
                "long_form_angle": item.get("long_form_angle", ""),
                "pillar": item.get("pillar", ""),
                "searchability_score": item.get("searchability_score", 0),
                "emotional_score": item.get("emotional_score", 0),
                "rewatch_score": item.get("rewatch_score", 0),
                "shorts_score": item.get("shorts_score", 0),
                "long_form_score": item.get("long_form_score", 0),
                "overall_score": score,
                "source": "daily_research",
                "status": "queued",
                "created_at": now_iso(),
            }
        )

        if len(approved) >= MAX_TOPICS_PER_DAY:
            break

    updated_queue = queue_payload + approved
    save_json(TOPIC_QUEUE_FILE, updated_queue)

    research_log.append(
        {
            "timestamp": now_iso(),
            "type": "daily_run_summary",
            "channel": channel_slug,
            "channel_name": channel.get("channel_name", channel_slug),
            "raw_result_count": len(raw_results),
            "candidate_count": len(candidates),
            "approved_count": len(approved),
            "approved_topics": [item["topic"] for item in approved],
        }
    )

    save_json(RESEARCH_LOG_FILE, research_log)
    save_json(
        LAST_RUN_FILE,
        {
            "last_run_at": now_iso(),
            "channel": channel_slug,
            "channel_name": channel.get("channel_name", channel_slug),
            "approved_count": len(approved),
        },
    )

    print(f"Channel: {channel.get('channel_name', channel_slug)}")
    print(f"Approved {len(approved)} new topics.")
    for topic in approved:
        print(f"- {topic['topic']} ({topic['overall_score']})")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    run_research("faith")
