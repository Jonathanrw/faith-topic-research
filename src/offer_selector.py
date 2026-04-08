import json
from pathlib import Path


OFFERS_PATH = Path("data/offers.json")
WINNERS_PATH = Path("data/winner_summary.json")


def load_offers() -> list[dict]:
    if not OFFERS_PATH.exists():
        return []
    return json.loads(OFFERS_PATH.read_text(encoding="utf-8"))


def load_winner_summary() -> dict:
    if not WINNERS_PATH.exists():
        return {
            "video_count": 0,
            "top_topics": [],
            "top_hooks": [],
            "winners": [],
        }

    return json.loads(WINNERS_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return text.lower().strip()


def extract_winner_topics(summary: dict) -> set[str]:
    topics = set()

    for item in summary.get("top_topics", []):
        topic = normalize(item.get("topic", ""))
        if topic:
            topics.add(topic)

    return topics


def extract_winner_hooks(summary: dict) -> set[str]:
    hooks = set()

    for item in summary.get("top_hooks", []):
        hook = normalize(item.get("hook_pattern", ""))
        if hook:
            hooks.add(hook)

    return hooks


def score_offer(
    offer: dict,
    topic: str,
    title: str,
    winner_topics: set[str],
    winner_hooks: set[str],
) -> int:
    topic_text = normalize(topic)
    title_text = normalize(title)

    score = 0

    for offer_topic in offer.get("topics", []):
        offer_topic_text = normalize(offer_topic)

        if offer_topic_text in topic_text or offer_topic_text in title_text:
            score += 3

        if offer_topic_text in winner_topics:
            score += 2

    for hook in offer.get("hooks", []):
        hook_text = normalize(hook)

        if hook_text in title_text:
            score += 2

        if hook_text in winner_hooks:
            score += 2

    if offer.get("type") == "lead_magnet":
        score += 1

    return score


def select_best_offers(topic: str, title: str, max_results: int = 2) -> list[dict]:
    offers = load_offers()
    if not offers:
        return []

    winner_summary = load_winner_summary()
    winner_topics = extract_winner_topics(winner_summary)
    winner_hooks = extract_winner_hooks(winner_summary)

    ranked = sorted(
        offers,
        key=lambda offer: score_offer(
            offer=offer,
            topic=topic,
            title=title,
            winner_topics=winner_topics,
            winner_hooks=winner_hooks,
        ),
        reverse=True,
    )

    ranked = [
        offer
        for offer in ranked
        if score_offer(
            offer=offer,
            topic=topic,
            title=title,
            winner_topics=winner_topics,
            winner_hooks=winner_hooks,
        ) > 0
    ]

    return ranked[:max_results]


def select_primary_offer(topic: str, title: str) -> dict | None:
    matches = select_best_offers(topic=topic, title=title, max_results=1)
    if not matches:
        return None
    return matches[0]
