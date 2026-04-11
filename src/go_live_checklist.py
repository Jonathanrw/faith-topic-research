import json
from pathlib import Path


FINAL_READINESS_PATH = Path("data/final_readiness_report.json")
LIVE_LINK_AUDIT_PATH = Path("data/live_link_audit.json")
OUTPUT_PATH = Path("data/go_live_checklist.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    final_readiness = load_json(
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

    live_link_audit = load_json(
        LIVE_LINK_AUDIT_PATH,
        {
            "offer_count": 0,
            "product_count": 0,
            "ready_offer_count": 0,
            "ready_product_count": 0,
            "all_offers_live_ready": False,
            "all_products_live_ready": False,
            "offers": [],
            "products": [],
        },
    )

    checklist = {
        "ready_for_live_mode": final_readiness.get("ready_for_live_mode", False),
        "steps": [
            {
                "step": "Replace placeholder offer links with real URLs",
                "complete": live_link_audit.get("all_offers_live_ready", False),
            },
            {
                "step": "Replace placeholder product delivery links with real URLs",
                "complete": live_link_audit.get("all_products_live_ready", False),
            },
            {
                "step": "Confirm no blockers remain in final readiness report",
                "complete": final_readiness.get("blocker_count", 0) == 0,
            },
            {
                "step": "Switch PIPELINE_LIVE from false to true when ready",
                "complete": False,
            },
            {
                "step": "Run one manual live workflow and verify upload results",
                "complete": False,
            },
        ],
        "blockers": final_readiness.get("blockers", []),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(checklist, indent=2), encoding="utf-8")

    print(f"Saved go-live checklist: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
