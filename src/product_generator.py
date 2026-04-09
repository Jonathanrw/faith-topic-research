import json
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.product_loader import load_products


OUTPUT_DIR = Path("content/products")


client = OpenAI(api_key=OPENAI_API_KEY)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_prompt(product: dict) -> str:
    return f"""
Create a clean, well-structured digital product in plain text format.

Product Title:
{product.get("title")}

Audience:
{product.get("audience")}

Promise:
{product.get("promise")}

Description:
{product.get("description")}

Requirements:
- Write in a warm, encouraging tone
- Use simple, clear language
- Include headings and sections
- Include actionable steps or reflections
- Include scripture where appropriate
- Keep it practical and helpful
- No fluff

Output:
Return the full product content as formatted text.
"""


def generate_product_content(product: dict) -> str:
    prompt = build_prompt(product)

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
    )

    return response.output_text.strip()


def save_product(product: dict, content: str) -> Path:
    ensure_output_dir()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{product['id']}.txt"

    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")

    return path


def main() -> None:
    products = load_products()

    if not products:
        print("No products found.")
        return

    for product in products:
        print(f"Generating product: {product['title']}")
        content = generate_product_content(product)
        path = save_product(product, content)
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
