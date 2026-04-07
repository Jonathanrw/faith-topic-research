from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from src.ctr_rules import build_thumbnail_subtitle, build_thumbnail_title


THUMBNAIL_DIR = Path("content/thumbnails")


@dataclass
class ThumbnailPreset:
    width: int
    height: int
    max_title_lines: int
    max_subtitle_lines: int
    safe_margin_x: int
    safe_margin_y: int
    title_font_size: int
    subtitle_font_size: int
    badge_font_size: int
    panel_height_ratio: float


YOUTUBE_PRESET = ThumbnailPreset(
    width=1280,
    height=720,
    max_title_lines=3,
    max_subtitle_lines=2,
    safe_margin_x=70,
    safe_margin_y=50,
    title_font_size=96,
    subtitle_font_size=42,
    badge_font_size=30,
    panel_height_ratio=0.48,
)

VERTICAL_PRESET = ThumbnailPreset(
    width=1080,
    height=1920,
    max_title_lines=4,
    max_subtitle_lines=2,
    safe_margin_x=70,
    safe_margin_y=90,
    title_font_size=110,
    subtitle_font_size=54,
    badge_font_size=34,
    panel_height_ratio=0.42,
)


def ensure_thumbnail_dir() -> None:
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


def find_font(preferred: Optional[str] = None) -> str:
    candidates = [
        preferred,
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arialbd.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    raise FileNotFoundError("No usable bold font found. Pass a custom font path if needed.")


def load_font(size: int, font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(find_font(font_path), size=size)


def open_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def resize_and_crop(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    return ImageOps.fit(
        img,
        target_size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def enhance_background(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Contrast(img).enhance(1.10)
    img = ImageEnhance.Color(img).enhance(1.08)
    img = ImageEnhance.Sharpness(img).enhance(1.10)
    return img


def add_soft_text_panel(base: Image.Image, panel_y: int, panel_h: int) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rounded_rectangle(
        [(40, panel_y), (base.width - 40, panel_y + panel_h)],
        radius=36,
        fill=(0, 0, 0, 130),
    )

    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=18))
    return Image.alpha_composite(base.convert("RGBA"), blurred).convert("RGB")


def wrap_text_by_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    max_lines: int,
    stroke_width: int = 5,
) -> str:
    words = text.split()
    if not words:
        return ""

    lines = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=stroke_width)
        if (bbox[2] - bbox[0]) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word

    lines.append(current)

    if len(lines) <= max_lines:
        return "\n".join(lines)

    trimmed = lines[:max_lines]
    last = trimmed[-1]

    while len(last) > 4:
        candidate = last.rstrip(" .,!?:;-") + "..."
        bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=stroke_width)
        if (bbox[2] - bbox[0]) <= max_width:
            trimmed[-1] = candidate
            break
        last = last[:-1]

    if not trimmed[-1].endswith("..."):
        trimmed[-1] = trimmed[-1].rstrip(" .,!?:;-") + "..."

    return "\n".join(trimmed)


def fit_multiline_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    start_size: int,
    min_size: int,
    max_width: int,
    max_height: int,
    max_lines: int,
    font_path: Optional[str] = None,
    spacing: int = 10,
    stroke_width: int = 5,
) -> tuple[ImageFont.FreeTypeFont, str]:
    for size in range(start_size, min_size - 1, -4):
        font = load_font(size, font_path)
        wrapped = wrap_text_by_width(
            draw=draw,
            text=text,
            font=font,
            max_width=max_width,
            max_lines=max_lines,
            stroke_width=stroke_width,
        )
        bbox = draw.multiline_textbbox(
            (0, 0),
            wrapped,
            font=font,
            spacing=spacing,
            stroke_width=stroke_width,
        )
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        if width <= max_width and height <= max_height:
            return font, wrapped

    font = load_font(min_size, font_path)
    wrapped = wrap_text_by_width(
        draw=draw,
        text=text,
        font=font,
        max_width=max_width,
        max_lines=max_lines,
        stroke_width=stroke_width,
    )
    return font, wrapped


def save_optimized_jpeg(img: Image.Image, out_path: Path, quality: int = 88) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    jpg_path = out_path.with_suffix(".jpg")
    img.save(
        jpg_path,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
        subsampling=0,
    )
    return jpg_path


def create_thumbnail(
    background_path: Path,
    output_path: Path,
    title: str,
    subtitle: str = "",
    badge_text: str = "Faith",
    preset: ThumbnailPreset = YOUTUBE_PRESET,
    font_path: Optional[str] = None,
) -> Path:
    base = open_image(background_path)
    base = resize_and_crop(base, (preset.width, preset.height))
    base = enhance_background(base)

    panel_h = int(preset.height * preset.panel_height_ratio)
    panel_y = preset.height - panel_h - preset.safe_margin_y
    image = add_soft_text_panel(base, panel_y=panel_y, panel_h=panel_h)

    draw = ImageDraw.Draw(image)

    content_x = preset.safe_margin_x
    content_w = preset.width - (preset.safe_margin_x * 2)
    current_y = panel_y + 34

    badge_font = load_font(preset.badge_font_size, font_path)
    badge = badge_text.strip().upper()

    if badge:
        badge_bbox = draw.textbbox((0, 0), badge, font=badge_font, stroke_width=1)
        badge_w = badge_bbox[2] - badge_bbox[0]
        badge_h = badge_bbox[3] - badge_bbox[1]

        pad_x = 16
        pad_y = 10

        draw.rounded_rectangle(
            [
                (content_x, current_y),
                (content_x + badge_w + (pad_x * 2), current_y + badge_h + (pad_y * 2)),
            ],
            radius=16,
            fill=(200, 20, 20),
        )
        draw.text(
            (content_x + pad_x, current_y + pad_y - 1),
            badge,
            font=badge_font,
            fill=(255, 255, 255),
            stroke_width=1,
            stroke_fill=(120, 0, 0),
        )
        current_y += badge_h + (pad_y * 2) + 24

    title_font, wrapped_title = fit_multiline_text(
        draw=draw,
        text=title,
        start_size=preset.title_font_size,
        min_size=max(44, preset.title_font_size - 42),
        max_width=content_w,
        max_height=int(panel_h * 0.58),
        max_lines=preset.max_title_lines,
        font_path=font_path,
        spacing=10,
        stroke_width=6,
    )

    draw.multiline_text(
        (content_x, current_y),
        wrapped_title,
        font=title_font,
        fill=(255, 255, 255),
        spacing=10,
        stroke_width=6,
        stroke_fill=(0, 0, 0),
    )

    title_bbox = draw.multiline_textbbox(
        (content_x, current_y),
        wrapped_title,
        font=title_font,
        spacing=10,
        stroke_width=6,
    )
    current_y = title_bbox[3] + 18

    if subtitle.strip():
        subtitle_font, wrapped_subtitle = fit_multiline_text(
            draw=draw,
            text=subtitle,
            start_size=preset.subtitle_font_size,
            min_size=max(24, preset.subtitle_font_size - 18),
            max_width=content_w,
            max_height=int(panel_h * 0.22),
            max_lines=preset.max_subtitle_lines,
            font_path=font_path,
            spacing=8,
            stroke_width=4,
        )

        draw.multiline_text(
            (content_x, current_y),
            wrapped_subtitle,
            font=subtitle_font,
            fill=(245, 245, 245),
            spacing=8,
            stroke_width=4,
            stroke_fill=(0, 0, 0),
        )

    return save_optimized_jpeg(image, output_path)


def build_thumbnail_set(
    background_path: Path,
    base_name: str,
    title: Optional[str] = None,
    subtitle: str = "",
    badge_text: str = "Faith",
    font_path: Optional[str] = None,
) -> tuple[Path, Path]:
    ensure_thumbnail_dir()

    title_text = title or build_thumbnail_title(base_name)
    subtitle_text = subtitle or build_thumbnail_subtitle(base_name)

    youtube_output = THUMBNAIL_DIR / f"{base_name}_youtube"
    vertical_output = THUMBNAIL_DIR / f"{base_name}_vertical"

    youtube_thumb = create_thumbnail(
        background_path=background_path,
        output_path=youtube_output,
        title=title_text,
        subtitle=subtitle_text,
        badge_text=badge_text,
        preset=YOUTUBE_PRESET,
        font_path=font_path,
    )

    vertical_thumb = create_thumbnail(
        background_path=background_path,
        output_path=vertical_output,
        title=title_text,
        subtitle=subtitle_text,
        badge_text=badge_text,
        preset=VERTICAL_PRESET,
        font_path=font_path,
    )

    return youtube_thumb, vertical_thumb
