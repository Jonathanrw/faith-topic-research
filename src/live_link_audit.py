import json
from pathlib import Path


OFFERS_PATH = Path("data/offers.json")
PRODUCTS_PATH = Path("data/products.json")
OUTPUT_PATH = Path("data/live_link_audit.json")


PLACEHOLDER_PATTERNS = [
    "example.com",
    "yourlink.com",
    "gumroad.com/your",
    "stan.store/your",
]


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def is_placeholder(link: str) -> bool:
    text = (link or "").strip().lower()
    if not text:
        return True
    return any(pattern in text for pattern in PLACEHOLDER_PATTERNS)


def main() -> None:
    offers = load_json(OFFERS_PATH, [])
    products = load_json(PRODUCTS_PATH, [])

    offer_checks = []
    for offer in offers:
        link = offer.get("link", "")
        offer_checks.append(
            {
                "id": offer.get("id", ""),
                "title": offer.get("title", ""),
                "link": link,
                "has_live_link": not is_placeholder(link),
            }
        )

    product_checks = []
    for product in products:
        link = product.get("delivery_link", "")
        product_checks.append(
            {
                "id": product.get("id", ""),
                "title": product.get("title", ""),
                "delivery_link": link,
                "has_live_link": not is_placeholder(link),
            }
        )

    ready_offer_count = sum(1 for item in offer_checks if item["has_live_link"])
    ready_product_count = sum(1 for item in product_checks if item["has_live_link"])

    payload = {
        "offer_count": len(offer_checks),
        "product_count": len(product_checks),
        "ready_offer_count": ready_offer_count,
        "ready_product_count": ready_product_count,
        "all_offers_live_ready": ready_offer_count == len(offer_checks) and len(offer_checks) > 0,
        "all_products_live_ready": ready_product_count == len(product_checks) and len(product_checks) > 0,
        "offers": offer_checks,
        "products": product_checks,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved live link audit: {OUTPUT_PATH}")
    print(f"Live-ready offers: {ready_offer_count}/{len(offer_checks)}")
    print(f"Live-ready products: {ready_product_count}/{len(product_checks)}")


if __name__ == "__main__":
    main()
