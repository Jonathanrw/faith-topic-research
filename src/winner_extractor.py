import json
from collections import Counter
from pathlib import Path


DATA_DIR = Path("data")
LATEST_PATH = DATA_DIR / "performance_latest.json"
WINNERS_PATH = DATA_DIR / "winner_summary.json"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def classify_topic(title: str) -> str:
    text = title.lower()

    if "prayer" in text or "pray" in text:
        return "prayer"
    if "anxiety" in text or "fear" in text or "panic" in text or "worry" in text:
        return "anxiety"
    if "god's voice" in text or "gods voice" in text or "hearing god" in text or "discern" in text:
        return "hearing_gods_voice"
    if "bible" in text or "scripture" in text or "verse" in text or "verses" in text:
        return "scripture"
    if "jesus" in text:
        return "jesus"
    if "faith" in text:
        return "faith"

    return "generic"


def build_hook_pattern(title: str) -> str:
    text = title.lower()

    if "why " in text:
        return "why"
    if "how " in text:
        return "how"
    if "3 " in text or " 3 " in text or text.startswith("3"):
        return "list_3"
    if "?" in title:
        return "question"
    if "stop" in text:
        return "stop"
    if "do this" in text:
        return "do_this"

    return "statement"


def main() -> None:
    latest = load_json(LATEST_PATH, {})
    top_videos = latest.get("top_videos", [])

    if not top_videos:
        summary = {
            "video_count": 0,
            "top_topics": [],
            "top_hooks": [],
            "winners": [],
        }
        save_json(WINNERS_PATH, summary)
        print("No performance data available yet.")
        return

    topic_counter = Counter()
    hook_counter = Counter()
    winners = []

    for video in top_videos:
        title = video.get("youtube_title") or video.get("scheduled_title") or ""
        topic = classify_topic(title)
        hook = build_hook_pattern(title)

        topic_counter[topic] += 1
        hook_counter[hook] += 1

        winners.append(
            {
                "video_id": video.get("video_id", ""),
                "title": title,
                "topic": topic,
                "hook_pattern": hook,
                "view_count": video.get("view_count", 0),
                "engagement_rate": video.get("engagement_rate", 0.0),
                "video_url": video.get("video_url", ""),
            }
        )

    summary = {
        "video_count": len(top_videos),
        "top_topics": [
            {"topic": topic, "count": count}
            for topic, count in topic_counter.most_common(5)
        ],
        "top_hooks": [
            {"hook_pattern": hook, "count": count}
            for hook, count in hook_counter.most_common(5)
        ],
        "winners": winners,
    }

    save_json(WINNERS_PATH, summary)

    print(f"Saved winner summary: {WINNERS_PATH}")
    print("Top topics:")
    for item in summary["top_topics"]:
        print(f"- {item['topic']}: {item['count']}")

    print("Top hooks:")
    for item in summary["top_hooks"]:
        print(f"- {item['hook_pattern']}: {item['count']}")


if __name__ == "__main__":
    main()
