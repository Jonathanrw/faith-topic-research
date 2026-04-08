import json
from pathlib import Path


OFFERS_PATH = Path("data/offers.json")


def load_offers() -> list[dict]:
    if not OFFERS_PATH.exists():
        return []

    return json.loads(OFFERS_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return text.lower().strip()


def score_offer(offer: dict, topic: str, title: str) -> int:
    topic_text = normalize(topic)
    title_text = normalize(title)

    score = 0

    for offer_topic in offer.get("topics", []):
        offer_topic_text = normalize(offer_topic)
        if offer_topic_text in topic_text or offer_topic_text in title_text:
            score += 3

    for hook in offer.get("hooks", []):
        hook_text = normalize(hook)
        if hook_text in title_text:
            score += 2

    if offer.get("type") == "lead_magnet":
        score += 1

    return score


def select_best_offers(topic: str, title: str, max_results: int = 2) -> list[dict]:
    offers = load_offers()
    if not offers:
        return []

    ranked = sorted(
        offers,
        key=lambda offer: score_offer(offer, topic, title),
        reverse=True,
    )

    ranked = [offer for offer in ranked if score_offer(offer, topic, title) > 0]

    return ranked[:max_results]


def select_primary_offer(topic: str, title: str) -> dict | None:
    matches = select_best_offers(topic=topic, title=title, max_results=1)
    if not matches:
        return None
    return matches[0]
