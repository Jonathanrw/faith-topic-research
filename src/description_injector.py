from src.cta_generator import build_cta_section


def inject_cta_into_description(
    base_description: str,
    title: str,
    include_cta: bool = True,
) -> str:
    description = (base_description or "").strip()

    if not include_cta:
        return description[:4900]

    cta_section = build_cta_section(title)
    if not cta_section:
        return description[:4900]

    if description:
        final_description = f"{description}\n\n{cta_section}"
    else:
        final_description = cta_section

    return final_description[:4900]
