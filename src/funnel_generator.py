import json
from pathlib import Path

from src.link_manager import get_product_link
from src.product_loader import load_products


LANDING_PAGES_DIR = Path("content/landing_pages")
OUTPUT_PATH = Path("data/funnel_report.json")


def find_latest_landing_page(product_id: str) -> str:
    if not LANDING_PAGES_DIR.exists():
        return ""

    matches = sorted(LANDING_PAGES_DIR.glob(f"*_{product_id}_landing_page.md"))
    if not matches:
        return ""

    return str(matches[-1])


def build_funnel_entry(product: dict) -> dict:
    product_id = product.get("id", "")
    price = product.get("price", 0)
    funnel_type = "lead_capture" if price == 0 else "direct_offer"
    delivery_link = get_product_link(product_id)

    return {
        "product_id": product_id,
        "title": product.get("title", ""),
        "topic": product.get("topic", ""),
        "type": product.get("type", ""),
        "price": price,
        "cta": product.get("cta", ""),
        "delivery_link": delivery_link,
        "landing_page_path": find_latest_landing_page(product_id),
        "funnel_type": funnel_type,
        "entry_point": "youtube_description",
        "flow": [
            "video",
            "description_cta",
            "landing_page",
            "delivery_link",
        ] if funnel_type == "lead_capture" else [
            "video",
            "description_cta",
            "landing_page",
            "checkout_or_delivery_link",
        ],
    }


def main() -> None:
    products = load_products()

    payload = {
        "product_count": len(products),
        "funnels": [build_funnel_entry(product) for product in products],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved funnel report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
