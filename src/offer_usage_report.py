import json
from pathlib import Path

from src.content_packager import get_publish_packages_from_schedule
from src.offer_selector import select_best_offers


SCHEDULE_DIR = Path("content/schedules")
DATA_DIR = Path("data")
REPORT_PATH = DATA_DIR / "offer_usage_report.json"


def load_latest_schedule() -> dict:
    files = sorted(SCHEDULE_DIR.glob("*_schedule.json"), reverse=True)
    if not files:
        raise FileNotFoundError("No schedule file found in content/schedules")
    return json.loads(files[0].read_text(encoding="utf-8"))


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


def main() -> None:
    schedule = load_latest_schedule()
    packages = get_publish_packages_from_schedule(schedule)

    report_entries = []

    for package in packages:
        title = package.get("title", "")
        topic = classify_topic(title)
        offers = select_best_offers(topic=topic, title=title, max_results=2)

        report_entries.append(
            {
                "type": package.get("type", ""),
                "slot": package.get("slot"),
                "title": title,
                "topic": topic,
                "publish_at": package.get("publish_at", ""),
                "offers": [
                    {
                        "id": offer.get("id", ""),
                        "title": offer.get("title", ""),
                        "type": offer.get("type", ""),
                        "link": offer.get("link", ""),
                    }
                    for offer in offers
                ],
            }
        )

    payload = {
        "base_name": schedule.get("base_name", ""),
        "entry_count": len(report_entries),
        "entries": report_entries,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved offer usage report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
