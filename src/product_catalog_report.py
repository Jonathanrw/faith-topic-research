import json
from pathlib import Path

from src.product_loader import load_products


REPORT_PATH = Path("data/product_catalog_report.json")


def main() -> None:
    products = load_products()

    payload = {
        "product_count": len(products),
        "products": [
            {
                "id": product.get("id", ""),
                "title": product.get("title", ""),
                "type": product.get("type", ""),
                "format": product.get("format", ""),
                "price": product.get("price", 0),
                "topic": product.get("topic", ""),
                "cta": product.get("cta", ""),
                "delivery_link": product.get("delivery_link", ""),
                "source_offer_id": product.get("source_offer_id", ""),
            }
            for product in products
        ],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved product catalog report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
