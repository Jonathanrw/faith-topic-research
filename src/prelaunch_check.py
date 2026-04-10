import json
from pathlib import Path


BUSINESS_STATUS_PATH = Path("data/business_status_report.json")
REVENUE_READINESS_PATH = Path("data/revenue_readiness_report.json")
MONETIZATION_SUMMARY_PATH = Path("data/monetization_summary.json")
WINNERS_PATH = Path("data/winner_summary.json")
OUTPUT_PATH = Path("data/prelaunch_check.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    business_status = load_json(
        BUSINESS_STATUS_PATH,
        {
            "growth": {"winner_video_count": 0, "top_topics": [], "top_hooks": []},
            "monetization": {"offer_usage_entry_count": 0, "top_offers": [], "top_topics": []},
            "revenue_readiness": {
                "product_count": 0,
                "offer_count": 0,
                "funnel_count": 0,
                "ready_product_count": 0,
                "all_products_ready": False,
            },
            "catalog": {"product_count": 0, "funnel_count": 0},
            "next_actions": [],
        },
    )

    revenue_readiness = load_json(
        REVENUE_READINESS_PATH,
        {
            "product_count": 0,
            "offer_count": 0,
            "funnel_count": 0,
            "ready_product_count": 0,
            "all_products_ready": False,
            "checks": [],
        },
    )

    monetization_summary = load_json(
        MONETIZATION_SUMMARY_PATH,
        {"entry_count": 0, "top_topics": [], "top_offers": []},
    )

    winners = load_json(
        WINNERS_PATH,
        {"video_count": 0, "top_topics": [], "top_hooks": [], "winners": []},
    )

    checks = {
        "has_winner_data": winners.get("video_count", 0) > 0,
        "has_offer_usage_data": monetization_summary.get("entry_count", 0) > 0,
        "has_top_offers": len(monetization_summary.get("top_offers", [])) > 0,
        "has_products": revenue_readiness.get("product_count", 0) > 0,
        "has_offers": revenue_readiness.get("offer_count", 0) > 0,
        "has_funnels": revenue_readiness.get("funnel_count", 0) > 0,
        "all_products_ready": revenue_readiness.get("all_products_ready", False),
    }

    recommended_mode = "live" if all(checks.values()) else "staging"

    blockers = []
    if not checks["has_winner_data"]:
        blockers.append("Not enough winner data yet.")
    if not checks["has_offer_usage_data"]:
        blockers.append("Offer usage report is empty.")
    if not checks["has_top_offers"]:
        blockers.append("No top offers identified yet.")
    if not checks["has_products"]:
        blockers.append("No products found.")
    if not checks["has_offers"]:
        blockers.append("No offers found.")
    if not checks["has_funnels"]:
        blockers.append("No funnels found.")
    if not checks["all_products_ready"]:
        blockers.append("Not all products are ready for live sales.")

    payload = {
        "recommended_mode": recommended_mode,
        "checks": checks,
        "blockers": blockers,
        "summary": {
            "winner_video_count": business_status.get("growth", {}).get("winner_video_count", 0),
            "offer_usage_entry_count": business_status.get("monetization", {}).get("offer_usage_entry_count", 0),
            "ready_product_count": business_status.get("revenue_readiness", {}).get("ready_product_count", 0),
            "product_count": business_status.get("revenue_readiness", {}).get("product_count", 0),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved prelaunch check: {OUTPUT_PATH}")
    print(f"Recommended mode: {recommended_mode}")

    if blockers:
        print("Blockers:")
        for blocker in blockers:
            print(f"- {blocker}")


if __name__ == "__main__":
    main()
