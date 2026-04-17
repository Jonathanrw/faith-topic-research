import random
from pathlib import Path

from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
)
from PIL import Image, ImageDraw, ImageFont


VIDEO_DIR = Path("content/videos")
AUDIO_DIR = Path("content/audio")
BACKGROUND_DIR = Path("content/backgrounds")
MUSIC_DIR = Path("content/assets/music")
SCRIPT_DIR = Path("content/scripts")
TEMP_DIR = Path("content/temp")


def ensure_video_dir() -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def pick_music_track(mood: str = "peaceful") -> Path | None:
    mood_dir = MUSIC_DIR / mood

    if not mood_dir.exists():
        print(f"Music folder not found for mood '{mood}': {mood_dir}")
        return None

    tracks = list(mood_dir.glob("*.mp3"))
    if not tracks:
        print(f"No music tracks found for mood '{mood}' in {mood_dir}")
        return None

    return random.choice(tracks)


def build_audio_mix(
    voice_path: Path,
    mood: str = "peaceful",
    music_volume: float = 0.12,
) -> tuple[AudioFileClip, CompositeAudioClip | AudioFileClip]:
    voice_audio = AudioFileClip(str(voice_path))
    music_path = pick_music_track(mood=mood)

    if not music_path:
        print("No background music found. Using voice only.")
        return voice_audio, voice_audio

    print(f"Using background music: {music_path.name}")

    music_audio = AudioFileClip(str(music_path)).volumex(music_volume)
    looped_music = audio_loop(music_audio, duration=voice_audio.duration)

    mixed_audio = CompositeAudioClip([looped_music, voice_audio]).set_duration(
        voice_audio.duration
    )

    music_audio.close()
    return voice_audio, mixed_audio


def read_script_text(script_path: Path) -> str:
    if not script_path.exists():
        return ""

    return script_path.read_text(encoding="utf-8").strip()


def split_caption_lines(text: str, max_words: int = 7) -> list[str]:
    words = text.replace("\n", " ").split()
    lines: list[str] = []

    for i in range(0, len(words), max_words):
        chunk = words[i:i + max_words]
        if chunk:
            lines.append(" ".join(chunk))

    return lines


def make_text_image(
    text: str,
    canvas_size: tuple[int, int],
    font_size: int,
    output_path: Path,
) -> None:
    width, height = canvas_size
    image = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    max_text_width = int(width * 0.82)

    words = text.split()
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font, stroke_width=3)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_text_width:
            current_line = test_line
        else:
            if current_line:
                wrapped_lines.append(current_line)
            current_line = word

    if current_line:
        wrapped_lines.append(current_line)

    line_heights = []
    line_widths = []

    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=3)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + (len(line_heights) - 1) * 18
    y = int(height * 0.72 - total_height / 2)

    for idx, line in enumerate(wrapped_lines):
        line_width = line_widths[idx]
        line_height = line_heights[idx]
        x = int((width - line_width) / 2)

        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=3,
            stroke_fill=(0, 0, 0, 255),
        )
        y += line_height + 18

    image.save(output_path)


def build_caption_overlays(
    text: str,
    duration: float,
    canvas_size: tuple[int, int],
    base_name: str,
    font_size: int,
) -> list[ImageClip]:
    caption_lines = split_caption_lines(text)
    if not caption_lines:
        return []

    clip_duration = max(duration / len(caption_lines), 1.2)
    overlays: list[ImageClip] = []

    for idx, line in enumerate(caption_lines):
        temp_path = TEMP_DIR / f"{base_name}_caption_{idx}.png"
        make_text_image(
            text=line,
            canvas_size=canvas_size,
            font_size=font_size,
            output_path=temp_path,
        )

        overlay = (
            ImageClip(str(temp_path))
            .set_start(idx * clip_duration)
            .set_duration(clip_duration)
            .crossfadein(0.15)
            .crossfadeout(0.15)
        )
        overlays.append(overlay)

    return overlays


def make_clip(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    size: tuple[int, int],
    script_path: Path,
    fps: int = 24,
    mood: str = "peaceful",
    music_volume: float = 0.12,
    font_size: int = 64,
) -> None:
    voice_audio, final_audio = build_audio_mix(
        voice_path=audio_path,
        mood=mood,
        music_volume=music_volume,
    )
    duration = voice_audio.duration

    bg_clip = (
        ImageClip(str(image_path))
        .set_duration(duration)
        .resize(height=size[1])
        .set_position("center")
    )

    bg_clip = bg_clip.resize(lambda t: 1 + 0.02 * (t / max(duration, 1)))

    script_text = read_script_text(script_path)
    caption_overlays = build_caption_overlays(
        text=script_text,
        duration=duration,
        canvas_size=size,
        base_name=output_path.stem,
        font_size=font_size,
    )

    video_layers = [bg_clip] + caption_overlays
    final_video = CompositeVideoClip(video_layers, size=size)
    final_video = final_video.set_audio(final_audio).set_duration(duration).set_fps(fps)

    final_video.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        threads=4,
        logger=None,
    )

    voice_audio.close()
    final_audio.close()
    final_video.close()
    bg_clip.close()

    for overlay in caption_overlays:
        overlay.close()


def render_long_video(base_name: str) -> Path | None:
    audio_path = AUDIO_DIR / f"{base_name}_long_voice.mp3"
    image_path = BACKGROUND_DIR / f"{base_name}_bg.png"
    script_path = SCRIPT_DIR / f"{base_name}_long.txt"
    output_path = VIDEO_DIR / f"{base_name}_long.mp4"

    if not audio_path.exists():
        print(f"Missing long audio: {audio_path}")
        return None

    if not image_path.exists():
        print(f"Missing long background: {image_path}")
        return None

    if not script_path.exists():
        print(f"Missing long script: {script_path}")
        return None

    make_clip(
        image_path=image_path,
        audio_path=audio_path,
        output_path=output_path,
        script_path=script_path,
        size=(1920, 1080),
        mood="peaceful",
        music_volume=0.10,
        font_size=60,
    )
    return output_path


def render_short_video(base_name: str, idx: int) -> Path | None:
    audio_path = AUDIO_DIR / f"{base_name}_short_{idx}_voice.mp3"
    image_path = BACKGROUND_DIR / f"{base_name}_short_{idx}_bg.png"
    script_path = SCRIPT_DIR / f"{base_name}_shorts.json"
    output_path = VIDEO_DIR / f"{base_name}_short_{idx}.mp4"

    if not audio_path.exists():
        print(f"Missing short audio: {audio_path}")
        return None

    if not image_path.exists():
        print(f"Missing short background: {image_path}")
        return None

    if not script_path.exists():
        print(f"Missing shorts file: {script_path}")
        return None

    import json

    try:
        shorts_data = json.loads(script_path.read_text(encoding="utf-8"))
        short_text = shorts_data[idx - 1].get("script", "")
    except Exception as exc:
        print(f"Failed to load short script {idx}: {exc}")
        return None

    temp_script_path = TEMP_DIR / f"{base_name}_short_{idx}_script.txt"
    temp_script_path.write_text(short_text, encoding="utf-8")

    make_clip(
        image_path=image_path,
        audio_path=audio_path,
        output_path=output_path,
        script_path=temp_script_path,
        size=(1080, 1920),
        mood="hopeful",
        music_volume=0.12,
        font_size=58,
    )
    return output_path
