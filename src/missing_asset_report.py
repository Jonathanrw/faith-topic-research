import json
from pathlib import Path

from src.content_packager import get_publish_packages_from_schedule


SCHEDULE_DIR = Path("content/schedules")


def load_latest_schedule() -> dict:
    files = sorted(SCHEDULE_DIR.glob("*_schedule.json"), reverse=True)
    if not files:
        raise FileNotFoundError("No schedule file found in content/schedules")
    return json.loads(files[0].read_text(encoding="utf-8"))


def main() -> None:
    schedule = load_latest_schedule()
    packages = get_publish_packages_from_schedule(schedule)

    print("Asset Report\n")

    missing_found = False

    for package in packages:
        print(f"Type: {package['type']}")
        print(f"Title: {package['title']}")
        print(f"Publish At: {package['publish_at']}")

        video_path = Path(package["video_path"])
        thumbnail_path = Path(package["thumbnail_path"])

        video_exists = video_path.exists()
        thumbnail_exists = thumbnail_path.exists()

        print(f"Video Exists: {'YES' if video_exists else 'NO'}")
        print(f"Video Path: {video_path}")

        print(f"Thumbnail Exists: {'YES' if thumbnail_exists else 'NO'}")
        print(f"Thumbnail Path: {thumbnail_path}")

        if not video_exists or not thumbnail_exists:
            missing_found = True

        print("")

    if missing_found:
        raise SystemExit("Missing required publish assets.")
    else:
        print("All required publish assets are present.")


if __name__ == "__main__":
    main()
