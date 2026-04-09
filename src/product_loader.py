import json
from pathlib import Path


PRODUCTS_PATH = Path("data/products.json")


def load_products() -> list[dict]:
    if not PRODUCTS_PATH.exists():
        return []
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def get_product_by_id(product_id: str) -> dict | None:
    for product in load_products():
        if product.get("id") == product_id:
            return product
    return None


def get_products_by_topic(topic: str) -> list[dict]:
    topic = (topic or "").strip().lower()
    return [
        product
        for product in load_products()
        if (product.get("topic", "") or "").strip().lower() == topic
    ]
