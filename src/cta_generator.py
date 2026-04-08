from src.offer_selector import select_best_offers


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


def build_offer_block(offer: dict) -> str:
    offer_type = offer.get("type", "")
    title = offer.get("title", "").strip()
    link = offer.get("link", "").strip()

    if not title or not link:
        return ""

    if offer_type == "lead_magnet":
        return f"Download the free \"{title}\" here:\n👉 {link}"

    if offer_type == "paid":
        return f"Get \"{title}\" here:\n👉 {link}"

    return f"Learn more here:\n👉 {link}"


def build_cta_intro(topic: str) -> str:
    if topic == "anxiety":
        return "🙏 If you're dealing with anxiety or fear, this may help."
    if topic == "prayer":
        return "🙏 If you want to grow deeper in prayer, start here."
    if topic == "hearing_gods_voice":
        return "🙏 If you’re trying to discern God’s voice more clearly, this is for you."
    if topic == "scripture":
        return "📖 Want more Bible-based encouragement and guidance?"
    if topic == "jesus":
        return "✝️ Want to grow closer to Jesus in your daily life?"
    if topic == "faith":
        return "🙏 Want stronger faith and daily encouragement?"
    return "🙏 Want more encouragement and help with this topic?"


def build_cta_section(title: str, max_offers: int = 2) -> str:
    topic = classify_topic(title)
    offers = select_best_offers(topic=topic, title=title, max_results=max_offers)

    if not offers:
        return ""

    lines = [build_cta_intro(topic), ""]

    for offer in offers:
        block = build_offer_block(offer)
        if block:
            lines.append(block)
            lines.append("")

    return "\n".join(line for line in lines).strip()
