import json
from datetime import datetime
from pathlib import Path

from src.scheduler import build_daily_schedule


VIDEO_DIR = Path("content/videos")
SCHEDULE_DIR = Path("content/schedules")


def ensure_schedule_dir() -> None:
    SCHEDULE_DIR.mkdir(parents=True, exist_ok=True)


def find_latest_base_name() -> str | None:
    long_files = sorted(VIDEO_DIR.glob("*_long.mp4"), reverse=True)
    if not long_files:
        return None

    latest = long_files[0].name
    if latest.endswith("_long.mp4"):
        return latest[:-9]
    return None


def main() -> None:
    ensure_schedule_dir()

    base_name = find_latest_base_name()
    if not base_name:
        print("No rendered long video found.")
        return

    schedule = build_daily_schedule(base_name)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = SCHEDULE_DIR / f"{stamp}_{base_name}_schedule.json"

    output_path.write_text(
        json.dumps(schedule, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved schedule: {output_path}")


if __name__ == "__main__":
    main()
