import json
from pathlib import Path

from src.product_loader import load_products


OFFERS_PATH = Path("data/offers.json")
FUNNEL_REPORT_PATH = Path("data/funnel_report.json")
OUTPUT_PATH = Path("data/revenue_readiness_report.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    products = load_products()
    offers = load_json(OFFERS_PATH, [])
    funnel_report = load_json(FUNNEL_REPORT_PATH, {"funnels": []})

    product_ids = {product.get("id", "") for product in products}
    offer_ids = {offer.get("id", "") for offer in offers}

    readiness_checks = []

    for product in products:
        source_offer_id = product.get("source_offer_id", "")
        delivery_link = product.get("delivery_link", "")
        landing_page_exists = any(
            funnel.get("product_id", "") == product.get("id", "")
            and bool(funnel.get("landing_page_path", ""))
            for funnel in funnel_report.get("funnels", [])
        )

        readiness_checks.append(
            {
                "product_id": product.get("id", ""),
                "title": product.get("title", ""),
                "has_source_offer": source_offer_id in offer_ids if source_offer_id else False,
                "has_delivery_link": bool(delivery_link.strip()),
                "has_landing_page": landing_page_exists,
                "ready_for_live_sales": (
                    (source_offer_id in offer_ids if source_offer_id else False)
                    and bool(delivery_link.strip())
                    and landing_page_exists
                ),
            }
        )

    ready_count = sum(1 for item in readiness_checks if item["ready_for_live_sales"])

    payload = {
        "product_count": len(products),
        "offer_count": len(offers),
        "funnel_count": len(funnel_report.get("funnels", [])),
        "ready_product_count": ready_count,
        "all_products_ready": ready_count == len(products) and len(products) > 0,
        "checks": readiness_checks,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved revenue readiness report: {OUTPUT_PATH}")
    print(f"Ready products: {ready_count}/{len(products)}")


if __name__ == "__main__":
    main()
