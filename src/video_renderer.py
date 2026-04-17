import random
from pathlib import Path

from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.editor import AudioFileClip, CompositeAudioClip, ImageClip


VIDEO_DIR = Path("content/videos")
AUDIO_DIR = Path("content/audio")
BACKGROUND_DIR = Path("content/backgrounds")
MUSIC_DIR = Path("content/assets/music")


def ensure_video_dir() -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def pick_music_track(
    mood: str = "peaceful",
) -> Path | None:
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


def make_clip(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    size: tuple[int, int],
    fps: int = 24,
    mood: str = "peaceful",
    music_volume: float = 0.12,
) -> None:
    voice_audio, final_audio = build_audio_mix(
        voice_path=audio_path,
        mood=mood,
        music_volume=music_volume,
    )
    duration = voice_audio.duration

    clip = (
        ImageClip(str(image_path))
        .set_duration(duration)
        .resize(height=size[1])
        .set_position("center")
    )

    clip = clip.resize(lambda t: 1 + 0.02 * (t / max(duration, 1)))
    clip = clip.set_audio(final_audio)
    final = clip.set_duration(duration).set_fps(fps)

    final.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        threads=4,
        logger=None,
    )

    voice_audio.close()
    final_audio.close()
    final.close()
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
        mood="peaceful",
        music_volume=0.10,
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
        mood="hopeful",
        music_volume=0.12,
    )
    return output_path
