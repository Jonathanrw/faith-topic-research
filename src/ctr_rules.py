import re
from pathlib import Path


def strip_timestamp_prefix(text: str) -> str:
    return re.sub(r"^\d{8}_\d{6}_", "", text).strip()


def strip_suffixes(text: str) -> str:
    text = re.sub(r"_short_\d+$", "", text)
    text = re.sub(r"_long$", "", text)
    return text.strip()


def base_name_to_phrase(base_name: str) -> str:
    text = strip_timestamp_prefix(base_name)
    text = strip_suffixes(text)
    text = text.replace("_", " ").replace("-", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def title_case_phrase(text: str) -> str:
    words = text.split()
    result = []

    for word in words:
        lower = word.lower()
        if lower == "am":
            result.append("AM")
        elif lower == "pm":
            result.append("PM")
        elif lower == "gods":
            result.append("God's")
        elif lower == "dont":
            result.append("Don't")
        elif lower == "cant":
            result.append("Can't")
        elif lower == "wont":
            result.append("Won't")
        elif lower == "youre":
            result.append("You're")
        elif lower == "whats":
            result.append("What's")
        else:
            result.append(word.capitalize())

    return " ".join(result)


def get_topic_key(base_name: str) -> str:
    phrase = base_name_to_phrase(base_name).lower()

    if "prayer" in phrase or "prayers" in phrase or "unanswered" in phrase:
        return "prayer"
    if "anxiety" in phrase or "2 am" in phrase or "panic" in phrase or "fear" in phrase:
        return "anxiety"
    if "hearing gods voice" in phrase or "gods voice" in phrase or "discern" in phrase:
        return "hearing_gods_voice"

    return "generic"


def build_thumbnail_title(base_name: str) -> str:
    key = get_topic_key(base_name)

    if key == "prayer":
        return "Why Prayers Feel Unanswered"
    if key == "anxiety":
        return "Stop The 2 AM Spiral"
    if key == "hearing_gods_voice":
        return "Hearing God's Voice?"

    phrase = title_case_phrase(base_name_to_phrase(base_name))
    words = phrase.split()

    if len(words) <= 5:
        return phrase
    if words and words[0].lower() in {"why", "how", "what", "when"}:
        return " ".join(words[:5])
    return " ".join(words[:5])


def build_thumbnail_subtitle(base_name: str) -> str:
    key = get_topic_key(base_name)

    if key == "prayer":
        return "Watch Before You Quit"
    if key == "anxiety":
        return "Do This Tonight"
    if key == "hearing_gods_voice":
        return "3 Checks To Know"

    return "Watch This"


def build_long_youtube_title(base_name: str) -> str:
    key = get_topic_key(base_name)

    if key == "prayer":
        return "Why Your Prayers Feel Unanswered: 7 Biblical Reasons"
    if key == "anxiety":
        return "3 Scriptures to Stop a 2 AM Anxiety Spiral"
    if key == "hearing_gods_voice":
        return "Hearing God's Voice? 3 Biblical Checks to Discern It"

    phrase = title_case_phrase(base_name_to_phrase(base_name))
    words = phrase.split()

    if len(words) <= 10:
        return phrase[:95]

    return " ".join(words[:10])[:95]


def build_short_youtube_title(short_title: str, slot: int) -> str:
    cleaned = short_title.strip()

    replacements = {
        "60-Second 2 a.m. Reset: 3 Scriptures": "Awake at 2 AM? Do This 60-Second Reset",
        "3 Night Verses to Stop the Spiral": "3 Night Verses to Stop the Anxiety Spiral",
        "How to Pray When Your Mind Won’t Slow Down": "Pray This When Your Mind Won't Slow Down",
    }

    if cleaned in replacements:
        return replacements[cleaned][:95]

    if not cleaned:
        return f"Faith Short #{slot}"

    cleaned = cleaned.replace("2 a.m.", "2 AM").replace("2 A.M.", "2 AM")
    cleaned = cleaned.replace("Won’t", "Won't")
    return cleaned[:95]
