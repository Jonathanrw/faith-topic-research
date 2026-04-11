import json
import os
from pathlib import Path


FINAL_READINESS_PATH = Path("data/final_readiness_report.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    pipeline_live = str(os.getenv("PIPELINE_LIVE", "false")).strip().lower() == "true"

    report = load_json(
        FINAL_READINESS_PATH,
        {
            "ready_for_live_mode": False,
            "recommended_mode": "staging",
            "blocker_count": 0,
            "product_count": 0,
            "funnel_count": 0,
            "live_ready_offer_count": 0,
            "live_ready_product_count": 0,
            "blockers": [],
            "go_live_steps": [],
        },
    )

    if not pipeline_live:
        print("PIPELINE_LIVE is false. Live mode guard passed.")
        return

    if not report.get("ready_for_live_mode", False):
        print("Live mode guard failed.")
        print("PIPELINE_LIVE is true, but final_readiness_report says the system is not ready.")
        for blocker in report.get("blockers", []):
            print(f"- {blocker}")
        raise SystemExit(1)

    print("Live mode guard passed. System is ready for live mode.")


if __name__ == "__main__":
    main()
