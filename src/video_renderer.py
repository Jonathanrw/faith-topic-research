from pathlib import Path

from moviepy import AudioFileClip, ImageClip


VIDEO_DIR = Path("content/videos")
AUDIO_DIR = Path("content/audio")
BACKGROUND_DIR = Path("content/backgrounds")


def ensure_video_dir() -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def make_clip(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    size: tuple[int, int],
    fps: int = 24,
) -> None:
    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    clip = (
        ImageClip(str(image_path))
        .with_duration(duration)
        .resized(height=size[1])
        .with_audio(audio)
        .with_fps(fps)
    )

    clip.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        threads=4,
        logger=None,
    )

    audio.close()
    clip.close()


def render_long_video(base_name: str) -> Path | None:
    audio_path = AUDIO_DIR / f"{base_name}_long_voice.mp3"
    image_path = BACKGROUND_DIR / f"{base_name}_bg.png"
    output_path = VIDEO_DIR / f"{base_name}_long.mp4"

    if not audio_path.exists():
        print(f"Missing long audio: {audio_path}")
        return None

    if not image_path.exists():
        print(f"Missing long background: {image_path}")
        return None

    make_clip(
        image_path=image_path,
        audio_path=audio_path,
        output_path=output_path,
        size=(1920, 1080),
    )
    return output_path


def render_short_video(base_name: str, idx: int) -> Path | None:
    audio_path = AUDIO_DIR / f"{base_name}_short_{idx}_voice.mp3"
    image_path = BACKGROUND_DIR / f"{base_name}_short_{idx}_bg.png"
    output_path = VIDEO_DIR / f"{base_name}_short_{idx}.mp4"

    if not audio_path.exists():
        print(f"Missing short audio: {audio_path}")
        return None

    if not image_path.exists():
        print(f"Missing short background: {image_path}")
        return None

    make_clip(
        image_path=image_path,
        audio_path=audio_path,
        output_path=output_path,
        size=(1080, 1920),
    )
    return output_path
