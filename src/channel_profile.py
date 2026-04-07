from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChannelProfile:
    brand_name: str
    thumbnail_badge_text: str
    long_cta: str
    short_cta: str
    long_tags: list[str] = field(default_factory=list)
    short_tags: list[str] = field(default_factory=list)
    ai_visual_disclosure_long: str = ""
    ai_visual_disclosure_short: str = ""


DEFAULT_CHANNEL_PROFILE = ChannelProfile(
    brand_name="Faith",
    thumbnail_badge_text="Faith",
    long_cta=(
        "If this helped you, subscribe for more Bible-based encouragement, "
        "clarity, and peace."
    ),
    short_cta=(
        "Subscribe for more faith-based shorts and daily encouragement."
    ),
    long_tags=[
        "faith",
        "christian",
        "bible",
        "encouragement",
        "prayer",
        "jesus",
        "hope",
        "anxiety",
        "hearing god",
        "biblical truth",
    ],
    short_tags=[
        "shorts",
        "faith",
        "christian",
        "bible",
        "encouragement",
        "prayer",
        "hope",
    ],
    ai_visual_disclosure_long="Disclosure: This video includes AI-generated visuals.",
    ai_visual_disclosure_short="Disclosure: This short includes AI-generated visuals.",
)
