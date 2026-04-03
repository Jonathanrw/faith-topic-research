import re
from difflib import SequenceMatcher


def normalize_topic(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def topic_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_topic(a), normalize_topic(b)).ratio()


def is_duplicate(candidate: str, existing_topics: list[str], threshold: float = 0.82) -> bool:
    for topic in existing_topics:
        if topic_similarity(candidate, topic) >= threshold:
            return True
    return False
