from dataclasses import dataclass


@dataclass(frozen=True)
class ThumbnailStyle:
    zoom: float
    contrast: float
    color: float
    sharpness: float
    brightness: float
    top_shade_alpha: int
    bottom_shade_alpha: int
    center_panel_alpha: int
    blur_radius: int
    badge_fill: tuple[int, int, int]
    badge_text_fill: tuple[int, int, int]
    badge_stroke_fill: tuple[int, int, int]
    subtitle_fill: tuple[int, int, int]
    title_stroke_width: int
    subtitle_stroke_width: int


DEFAULT_THUMBNAIL_STYLE = ThumbnailStyle(
    zoom=1.08,
    contrast=1.16,
    color=1.12,
    sharpness=1.12,
    brightness=1.04,
    top_shade_alpha=78,
    bottom_shade_alpha=125,
    center_panel_alpha=62,
    blur_radius=24,
    badge_fill=(220, 30, 30),
    badge_text_fill=(255, 255, 255),
    badge_stroke_fill=(120, 0, 0),
    subtitle_fill=(255, 235, 140),
    title_stroke_width=7,
    subtitle_stroke_width=4,
)
