from datetime import datetime
from pathlib import Path

from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.link_manager import get_product_link
from src.product_loader import load_products


OUTPUT_DIR = Path("content/landing_pages")


client = OpenAI(api_key=OPENAI_API_KEY)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_prompt(product: dict) -> str:
    product_id = product.get("id", "")
    delivery_link = get_product_link(product_id)

    return f"""
Create a simple high-converting landing page in markdown format for this digital product.

Product Title:
{product.get("title")}

Product Type:
{product.get("type")}

Format:
{product.get("format")}

Price:
{product.get("price")}

Audience:
{product.get("audience")}

Promise:
{product.get("promise")}

Description:
{product.get("description")}

CTA:
{product.get("cta")}

Requirements:
- Use a clean markdown structure
- Include a headline
- Include a short emotional hook
- Include 3 to 5 benefits
- Include a short section explaining who this is for
- Include a simple call to action at the end
- Keep it persuasive but not hypey
- Write in a warm, clear tone
- Do not include HTML
- Do not include fake testimonials
- Mention the delivery link placeholder exactly like this:
  DELIVERY LINK: {delivery_link}

Return only the finished markdown page.
"""


def generate_landing_page(product: dict) -> str:
    prompt = build_prompt(product)

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
    )

    return response.output_text.strip()


def save_landing_page(product: dict, content: str) -> Path:
    ensure_output_dir()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{product['id']}_landing_page.md"

    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")

    return path


def main() -> None:
    products = load_products()

    if not products:
        print("No products found.")
        return

    for product in products:
        print(f"Generating landing page: {product['title']}")
        content = generate_landing_page(product)
        path = save_landing_page(product, content)
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
