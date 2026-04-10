import json
from pathlib import Path


BUSINESS_STATUS_PATH = Path("data/business_status_report.json")
PRELAUNCH_CHECK_PATH = Path("data/prelaunch_check.json")
PRODUCT_CATALOG_PATH = Path("data/product_catalog_report.json")
FUNNEL_REPORT_PATH = Path("data/funnel_report.json")
MONETIZATION_SUMMARY_PATH = Path("data/monetization_summary.json")
WINNERS_PATH = Path("data/winner_summary.json")
LIVE_LINK_AUDIT_PATH = Path("data/live_link_audit.json")
OUTPUT_PATH = Path("data/launch_packet.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    business_status = load_json(BUSINESS_STATUS_PATH, {})
    prelaunch_check = load_json(PRELAUNCH_CHECK_PATH, {})
    product_catalog = load_json(PRODUCT_CATALOG_PATH, {"products": []})
    funnel_report = load_json(FUNNEL_REPORT_PATH, {"funnels": []})
    monetization_summary = load_json(MONETIZATION_SUMMARY_PATH, {})
    winners = load_json(WINNERS_PATH, {})
    live_link_audit = load_json(LIVE_LINK_AUDIT_PATH, {})

    payload = {
        "recommended_mode": prelaunch_check.get("recommended_mode", "staging"),
        "blockers": prelaunch_check.get("blockers", []),
        "growth_snapshot": {
            "winner_video_count": winners.get("video_count", 0),
            "top_topics": winners.get("top_topics", []),
            "top_hooks": winners.get("top_hooks", []),
        },
        "monetization_snapshot": {
            "top_offers": monetization_summary.get("top_offers", []),
            "top_topics": monetization_summary.get("top_topics", []),
            "offer_usage_entry_count": monetization_summary.get("entry_count", 0),
        },
        "live_link_snapshot": {
            "offer_count": live_link_audit.get("offer_count", 0),
            "product_count": live_link_audit.get("product_count", 0),
            "ready_offer_count": live_link_audit.get("ready_offer_count", 0),
            "ready_product_count": live_link_audit.get("ready_product_count", 0),
            "all_offers_live_ready": live_link_audit.get("all_offers_live_ready", False),
            "all_products_live_ready": live_link_audit.get("all_products_live_ready", False),
        },
        "products": product_catalog.get("products", []),
        "funnels": funnel_report.get("funnels", []),
        "business_status": business_status,
        "go_live_steps": [],
    }

    go_live_steps = []

    if payload["recommended_mode"] != "live":
        go_live_steps.append("Keep PIPELINE_LIVE set to false.")
    else:
        go_live_steps.append("Set PIPELINE_LIVE to true.")
        go_live_steps.append("Run one manual live workflow.")
        go_live_steps.append("Verify real product links and landing pages.")
        go_live_steps.append("Verify upload + monetization reports after the live run.")

    if not payload["products"]:
        go_live_steps.append("Add products to data/products.json.")

    if not payload["funnels"]:
        go_live_steps.append("Generate landing pages and funnel report.")

    if not payload["monetization_snapshot"]["top_offers"]:
        go_live_steps.append("Confirm offer matching and CTA injection are working.")

    if not payload["live_link_snapshot"]["all_offers_live_ready"]:
        go_live_steps.append("Replace placeholder offer links with real live URLs.")

    if not payload["live_link_snapshot"]["all_products_live_ready"]:
        go_live_steps.append("Replace placeholder product delivery links with real live URLs.")

    payload["go_live_steps"] = go_live_steps

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved launch packet: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
