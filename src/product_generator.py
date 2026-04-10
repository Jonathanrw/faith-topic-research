import json
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.product_loader import load_products


OUTPUT_DIR = Path("content/products")
WINNERS_PATH = Path("data/winner_summary.json")


client = OpenAI(api_key=OPENAI_API_KEY)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_winner_summary() -> dict:
    if not WINNERS_PATH.exists():
        return {
            "video_count": 0,
            "top_topics": [],
            "top_hooks": [],
            "winners": [],
        }

    return json.loads(WINNERS_PATH.read_text(encoding="utf-8"))


def build_winner_context() -> str:
    summary = load_winner_summary()

    if summary.get("video_count", 0) == 0:
        return "No winner data available yet."

    lines = [f"Winner video count analyzed: {summary.get('video_count', 0)}"]

    top_topics = summary.get("top_topics", [])
    if top_topics:
        lines.append("Top performing topics:")
        for item in top_topics[:5]:
            lines.append(f"- {item.get('topic', '')}: {item.get('count', 0)}")

    top_hooks = summary.get("top_hooks", [])
    if top_hooks:
        lines.append("Top performing hook patterns:")
        for item in top_hooks[:5]:
            lines.append(f"- {item.get('hook_pattern', '')}: {item.get('count', 0)}")

    winners = summary.get("winners", [])
    if winners:
        lines.append("Recent winning titles:")
        for item in winners[:10]:
            lines.append(f"- {item.get('title', '')}")

    return "\n".join(lines)


def build_prompt(product: dict) -> str:
    winner_context = build_winner_context()

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

Topic:
{product.get("topic")}

Winner Context:
{winner_context}

Requirements:
- Write in a warm, encouraging tone
- Use simple, clear language
- Include headings and sections
- Include actionable steps or reflections
- Include scripture where appropriate
- Keep it practical and helpful
- No fluff
- Make the product feel highly relevant to the topic and likely viewer intent
- Use strong clarity and usefulness so this feels worth downloading or buying

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
