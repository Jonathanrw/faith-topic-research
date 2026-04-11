import json
from pathlib import Path


WINNERS_PATH = Path("data/winner_summary.json")
MONETIZATION_SUMMARY_PATH = Path("data/monetization_summary.json")
REVENUE_READINESS_PATH = Path("data/revenue_readiness_report.json")
PRODUCT_CATALOG_PATH = Path("data/product_catalog_report.json")
FUNNEL_REPORT_PATH = Path("data/funnel_report.json")
LIVE_LINK_AUDIT_PATH = Path("data/live_link_audit.json")
OUTPUT_PATH = Path("data/business_status_report.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    winners = load_json(
        WINNERS_PATH,
        {"video_count": 0, "top_topics": [], "top_hooks": [], "winners": []},
    )
    monetization = load_json(
        MONETIZATION_SUMMARY_PATH,
        {"entry_count": 0, "top_topics": [], "top_offers": []},
    )
    readiness = load_json(
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
    product_catalog = load_json(
        PRODUCT_CATALOG_PATH,
        {"product_count": 0, "products": []},
    )
    funnel_report = load_json(
        FUNNEL_REPORT_PATH,
        {"product_count": 0, "funnels": []},
    )
    live_links = load_json(
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

    payload = {
        "growth": {
            "winner_video_count": winners.get("video_count", 0),
            "top_topics": winners.get("top_topics", []),
            "top_hooks": winners.get("top_hooks", []),
        },
        "monetization": {
            "offer_usage_entry_count": monetization.get("entry_count", 0),
            "top_offers": monetization.get("top_offers", []),
            "top_topics": monetization.get("top_topics", []),
        },
        "revenue_readiness": {
            "product_count": readiness.get("product_count", 0),
            "offer_count": readiness.get("offer_count", 0),
            "funnel_count": readiness.get("funnel_count", 0),
            "ready_product_count": readiness.get("ready_product_count", 0),
            "all_products_ready": readiness.get("all_products_ready", False),
        },
        "live_links": {
            "offer_count": live_links.get("offer_count", 0),
            "product_count": live_links.get("product_count", 0),
            "ready_offer_count": live_links.get("ready_offer_count", 0),
            "ready_product_count": live_links.get("ready_product_count", 0),
            "all_offers_live_ready": live_links.get("all_offers_live_ready", False),
            "all_products_live_ready": live_links.get("all_products_live_ready", False),
        },
        "catalog": {
            "product_count": product_catalog.get("product_count", 0),
            "funnel_count": len(funnel_report.get("funnels", [])),
        },
        "next_actions": [],
    }

    next_actions = []

    if payload["revenue_readiness"]["product_count"] == 0:
        next_actions.append("Add products to data/products.json.")

    if payload["revenue_readiness"]["offer_count"] == 0:
        next_actions.append("Add offers to data/offers.json.")

    if payload["revenue_readiness"]["ready_product_count"] < payload["revenue_readiness"]["product_count"]:
        next_actions.append("Update missing offer links, delivery links, or landing pages before going live.")

    if payload["growth"]["winner_video_count"] == 0:
        next_actions.append("Run the pipeline more to collect winner data before optimizing aggressively.")

    if not payload["monetization"]["top_offers"]:
        next_actions.append("Verify offer matching so videos are paired with monetization offers.")

    if not payload["live_links"]["all_offers_live_ready"]:
        next_actions.append("Replace placeholder offer links with real live URLs.")

    if not payload["live_links"]["all_products_live_ready"]:
        next_actions.append("Replace placeholder product delivery links with real live URLs.")

    if not next_actions:
        next_actions.append("System looks healthy. Finalize live links and switch PIPELINE_LIVE to true when ready.")

    payload["next_actions"] = next_actions

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved business status report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
