import json
from pathlib import Path

from src.content_packager import get_publish_packages_from_schedule
from src.preflight_validator import validate_publish_packages


SCHEDULE_DIR = Path("content/schedules")


def load_latest_schedule() -> dict:
    files = sorted(SCHEDULE_DIR.glob("*_schedule.json"), reverse=True)
    if not files:
        raise FileNotFoundError("No schedule file found in content/schedules")
    return json.loads(files[0].read_text(encoding="utf-8"))


def main() -> None:
    schedule = load_latest_schedule()
    packages = get_publish_packages_from_schedule(schedule)
    errors = validate_publish_packages(packages)

    if errors:
        print("Publish readiness check failed:\n")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Publish readiness check passed.\n")

    for package in packages:
        print(f"Type: {package['type']}")
        print(f"Title: {package['title']}")
        print(f"Video: {package['video_path']}")
        print(f"Thumbnail: {package['thumbnail_path']}")
        print(f"Publish At: {package['publish_at']}")
        print("")


if __name__ == "__main__":
    main()
