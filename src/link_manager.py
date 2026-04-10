import json
from pathlib import Path


OFFERS_PATH = Path("data/offers.json")
PRODUCTS_PATH = Path("data/products.json")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_offers() -> list[dict]:
    return load_json(OFFERS_PATH, [])


def load_products() -> list[dict]:
    return load_json(PRODUCTS_PATH, [])


def get_offer_link(offer_id: str) -> str:
    for offer in load_offers():
        if offer.get("id") == offer_id:
            return (offer.get("link", "") or "").strip()
    return ""


def get_product_link(product_id: str) -> str:
    for product in load_products():
        if product.get("id") == product_id:
            return (product.get("delivery_link", "") or "").strip()
    return ""


def update_offer_link(offer_id: str, new_link: str) -> bool:
    offers = load_offers()
    updated = False

    for offer in offers:
        if offer.get("id") == offer_id:
            offer["link"] = new_link
            updated = True
            break

    if updated:
        OFFERS_PATH.write_text(json.dumps(offers, indent=2), encoding="utf-8")

    return updated


def update_product_link(product_id: str, new_link: str) -> bool:
    products = load_products()
    updated = False

    for product in products:
        if product.get("id") == product_id:
            product["delivery_link"] = new_link
            updated = True
            break

    if updated:
        PRODUCTS_PATH.write_text(json.dumps(products, indent=2), encoding="utf-8")

    return updated
