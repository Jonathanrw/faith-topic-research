import json
from collections import Counter
from pathlib import Path

from src.link_manager import get_offer_link


REPORT_PATH = Path("data/offer_usage_report.json")
SUMMARY_PATH = Path("data/monetization_summary.json")


def load_report() -> dict:
    if not REPORT_PATH.exists():
        return {"entries": []}
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def main() -> None:
    report = load_report()
    entries = report.get("entries", [])

    offer_counter = Counter()
    topic_counter = Counter()
    offer_details = {}

    for entry in entries:
        topic = entry.get("topic", "")
        topic_counter[topic] += 1

        for offer in entry.get("offers", []):
            offer_id = offer.get("id", "")
            if offer_id:
                offer_counter[offer_id] += 1
                offer_details[offer_id] = {
                    "title": offer.get("title", ""),
                    "type": offer.get("type", ""),
                    "link": get_offer_link(offer_id),
                }

    summary = {
        "entry_count": len(entries),
        "top_topics": [
            {"topic": topic, "count": count}
            for topic, count in topic_counter.most_common(5)
        ],
        "top_offers": [
            {
                "offer_id": offer_id,
                "count": count,
                "title": offer_details.get(offer_id, {}).get("title", ""),
                "type": offer_details.get(offer_id, {}).get("type", ""),
                "link": offer_details.get(offer_id, {}).get("link", ""),
            }
            for offer_id, count in offer_counter.most_common(5)
        ],
    }

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Saved monetization summary: {SUMMARY_PATH}")
    print("Top topics:")
    for t in summary["top_topics"]:
        print(f"- {t['topic']}: {t['count']}")

    print("Top offers:")
    for o in summary["top_offers"]:
        print(f"- {o['offer_id']}: {o['count']}")


if __name__ == "__main__":
    main()
