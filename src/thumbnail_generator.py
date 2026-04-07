from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from src.channel_profile import DEFAULT_CHANNEL_PROFILE
from src.ctr_rules import build_thumbnail_subtitle, build_thumbnail_title
from src.thumbnail_style import DEFAULT_THUMBNAIL_STYLE


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


YOUTUBE_PRESET = ThumbnailPreset(
    width=1280,
    height=720,
    max_title_lines=3,
    max_subtitle_lines=2,
    safe_margin_x=72,
    safe_margin_y=52,
    title_font_size=102,
    subtitle_font_size=44,
    badge_font_size=30,
)

VERTICAL_PRESET = ThumbnailPreset(
    width=1080,
    height=1920,
    max_title_lines=4,
    max_subtitle_lines=2,
    safe_margin_x=72,
    safe_margin_y=96,
    title_font_size=112,
    subtitle_font_size=56,
    badge_font_size=34,
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


def resize_crop_and_zoom(img: Image.Image, target_size: Tuple[int, int], zoom: float) -> Image.Image:
    fitted = ImageOps.fit(
        img,
        target_size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )

    if zoom <= 1.0:
        return fitted

    new_w = int(fitted.width * zoom)
    new_h = int(fitted.height * zoom)

    zoomed = fitted.resize((new_w, new_h), Image.Resampling.LANCZOS)

    left = (new_w - fitted.width) // 2
    top = (new_h - fitted.height) // 2
    right = left + fitted.width
    bottom = top + fitted.height

    return zoomed.crop((left, top, right, bottom))


def enhance_background(img: Image.Image) -> Image.Image:
    style = DEFAULT_THUMBNAIL_STYLE
    img = ImageEnhance.Contrast(img).enhance(style.contrast)
    img = ImageEnhance.Color(img).enhance(style.color)
    img = ImageEnhance.Sharpness(img).enhance(style.sharpness)
    img = ImageEnhance.Brightness(img).enhance(style.brightness)
    return img


def add_vignette_and_panels(base: Image.Image, text_panel_top: int) -> Image.Image:
    style = DEFAULT_THUMBNAIL_STYLE

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle(
        [(0, 0), (base.width, int(base.height * 0.24))],
        fill=(0, 0, 0, style.top_shade_alpha),
    )

    draw.rectangle(
        [(0, text_panel_top - 30), (base.width, base.height)],
        fill=(0, 0, 0, style.bottom_shade_alpha),
    )

    draw.rounded_rectangle(
        [(32, text_panel_top), (base.width - 32, base.height - 28)],
        radius=36,
        fill=(0, 0, 0, style.center_panel_alpha),
    )

    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=style.blur_radius))
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


def draw_badge(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> int:
    style = DEFAULT_THUMBNAIL_STYLE
    badge = text.strip().upper()
    if not badge:
        return y

    bbox = draw.textbbox((0, 0), badge, font=font, stroke_width=1)
    badge_w = bbox[2] - bbox[0]
    badge_h = bbox[3] - bbox[1]

    pad_x = 18
    pad_y = 10

    draw.rounded_rectangle(
        [
            (x, y),
            (x + badge_w + (pad_x * 2), y + badge_h + (pad_y * 2)),
        ],
        radius=18,
        fill=DEFAULT_THUMBNAIL_STYLE.badge_fill,
    )

    draw.text(
        (x + pad_x, y + pad_y - 1),
        badge,
        font=font,
        fill=DEFAULT_THUMBNAIL_STYLE.badge_text_fill,
        stroke_width=1,
        stroke_fill=DEFAULT_THUMBNAIL_STYLE.badge_stroke_fill,
    )

    return y + badge_h + (pad_y * 2)


def create_thumbnail(
    background_path: Path,
    output_path: Path,
    title: str,
    subtitle: str = "",
    badge_text: str = "",
    preset: ThumbnailPreset = YOUTUBE_PRESET,
    font_path: Optional[str] = None,
) -> Path:
    style = DEFAULT_THUMBNAIL_STYLE

    base = open_image(background_path)
    base = resize_crop_and_zoom(base, (preset.width, preset.height), zoom=style.zoom)
    base = enhance_background(base)

    text_panel_top = int(preset.height * 0.50) if preset.height < 1000 else int(preset.height * 0.56)
    image = add_vignette_and_panels(base, text_panel_top=text_panel_top)

    draw = ImageDraw.Draw(image)

    content_x = preset.safe_margin_x
    content_w = preset.width - (preset.safe_margin_x * 2)

    badge_font = load_font(preset.badge_font_size, font_path)
    current_y = preset.safe_margin_y
    current_y = draw_badge(draw, content_x, current_y, badge_text, badge_font) + 26

    title_font, wrapped_title = fit_multiline_text(
        draw=draw,
        text=title,
        start_size=preset.title_font_size,
        min_size=max(46, preset.title_font_size - 44),
        max_width=content_w,
        max_height=int(preset.height * 0.24),
        max_lines=preset.max_title_lines,
        font_path=font_path,
        spacing=10,
        stroke_width=style.title_stroke_width,
    )

    title_y = text_panel_top + 28

    draw.multiline_text(
        (content_x, title_y),
        wrapped_title,
        font=title_font,
        fill=(255, 255, 255),
        spacing=10,
        stroke_width=style.title_stroke_width,
        stroke_fill=(0, 0, 0),
    )

    title_bbox = draw.multiline_textbbox(
        (content_x, title_y),
        wrapped_title,
        font=title_font,
        spacing=10,
        stroke_width=style.title_stroke_width,
    )
    current_y = title_bbox[3] + 18

    if subtitle.strip():
        subtitle_font, wrapped_subtitle = fit_multiline_text(
            draw=draw,
            text=subtitle,
            start_size=preset.subtitle_font_size,
            min_size=max(24, preset.subtitle_font_size - 18),
            max_width=content_w,
            max_height=int(preset.height * 0.10),
            max_lines=preset.max_subtitle_lines,
            font_path=font_path,
            spacing=8,
            stroke_width=style.subtitle_stroke_width,
        )

        draw.multiline_text(
            (content_x, current_y),
            wrapped_subtitle,
            font=subtitle_font,
            fill=style.subtitle_fill,
            spacing=8,
            stroke_width=style.subtitle_stroke_width,
            stroke_fill=(0, 0, 0),
        )

    return save_optimized_jpeg(image, output_path)


def build_thumbnail_set(
    background_path: Path,
    base_name: str,
    title: Optional[str] = None,
    subtitle: str = "",
    badge_text: Optional[str] = None,
    font_path: Optional[str] = None,
) -> tuple[Path, Path]:
    ensure_thumbnail_dir()

    profile = DEFAULT_CHANNEL_PROFILE

    title_text = title or build_thumbnail_title(base_name)
    subtitle_text = subtitle or build_thumbnail_subtitle(base_name)
    badge = badge_text if badge_text is not None else profile.thumbnail_badge_text

    youtube_output = THUMBNAIL_DIR / f"{base_name}_youtube"
    vertical_output = THUMBNAIL_DIR / f"{base_name}_vertical"

    youtube_thumb = create_thumbnail(
        background_path=background_path,
        output_path=youtube_output,
        title=title_text,
        subtitle=subtitle_text,
        badge_text=badge,
        preset=YOUTUBE_PRESET,
        font_path=font_path,
    )

    vertical_thumb = create_thumbnail(
        background_path=background_path,
        output_path=vertical_output,
        title=title_text,
        subtitle=subtitle_text,
        badge_text=badge,
        preset=VERTICAL_PRESET,
        font_path=font_path,
    )

    return youtube_thumb, vertical_thumb
