import json
from pathlib import Path


LAUNCH_PACKET_PATH = Path("data/launch_packet.json")
OUTPUT_PATH = Path("data/final_readiness_report.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    launch_packet = load_json(
        LAUNCH_PACKET_PATH,
        {
            "recommended_mode": "staging",
            "blockers": [],
            "growth_snapshot": {},
            "monetization_snapshot": {},
            "live_link_snapshot": {},
            "products": [],
            "funnels": [],
            "business_status": {},
            "go_live_steps": [],
        },
    )

    recommended_mode = launch_packet.get("recommended_mode", "staging")
    blockers = launch_packet.get("blockers", [])
    products = launch_packet.get("products", [])
    funnels = launch_packet.get("funnels", [])
    go_live_steps = launch_packet.get("go_live_steps", [])
    live_link_snapshot = launch_packet.get("live_link_snapshot", {})

    payload = {
        "ready_for_live_mode": (
            recommended_mode == "live"
            and len(blockers) == 0
            and live_link_snapshot.get("all_offers_live_ready", False)
            and live_link_snapshot.get("all_products_live_ready", False)
        ),
        "recommended_mode": recommended_mode,
        "blocker_count": len(blockers),
        "product_count": len(products),
        "funnel_count": len(funnels),
        "live_ready_offer_count": live_link_snapshot.get("ready_offer_count", 0),
        "live_ready_product_count": live_link_snapshot.get("ready_product_count", 0),
        "blockers": blockers,
        "go_live_steps": go_live_steps,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved final readiness report: {OUTPUT_PATH}")
    print(f"Ready for live mode: {payload['ready_for_live_mode']}")


if __name__ == "__main__":
    main()
