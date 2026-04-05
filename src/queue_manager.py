import json
from pathlib import Path


TOPIC_QUEUE_PATH = Path("data/topic_queue.json")
USED_TOPICS_PATH = Path("data/used_topics.json")


def load_topic_queue() -> list[dict]:
    if not TOPIC_QUEUE_PATH.exists():
        return []
    with open(TOPIC_QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_topic_queue(queue: list[dict]) -> None:
    with open(TOPIC_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def load_used_topics() -> list:
    if not USED_TOPICS_PATH.exists():
        return []
    with open(USED_TOPICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_used_topics(used_topics: list) -> None:
    with open(USED_TOPICS_PATH, "w", encoding="utf-8") as f:
        json.dump(used_topics, f, indent=2, ensure_ascii=False)


def get_best_queued_topic(channel_slug: str = "faith") -> dict | None:
    queue = load_topic_queue()

    candidates = [
        item for item in queue
        if isinstance(item, dict)
        and item.get("channel") == channel_slug
        and item.get("status") == "queued"
    ]

    if not candidates:
        return None

    candidates.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    return candidates[0]


def mark_topic_as_used(topic_to_mark: dict) -> None:
    queue = load_topic_queue()
    used_topics = load_used_topics()

    updated_queue = []
    for item in queue:
        if (
            item.get("topic") == topic_to_mark.get("topic")
            and item.get("channel") == topic_to_mark.get("channel")
            and item.get("status") == "queued"
        ):
            item["status"] = "used"
            used_topics.append(item)

        updated_queue.append(item)

    save_topic_queue(updated_queue)
    save_used_topics(used_topics)
