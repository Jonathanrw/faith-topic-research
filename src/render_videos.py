from pathlib import Path

from src.thumbnail_generator import build_thumbnail_set
from src.video_renderer import ensure_video_dir, render_long_video, render_short_video


SCRIPT_DIR = Path("content/scripts")
AUDIO_DIR = Path("content/audio")
BACKGROUND_DIR = Path("content/backgrounds")
VIDEO_DIR = Path("content/videos")

MUSIC_DIR = Path("content/assets/music")
PEACEFUL_MUSIC_DIR = MUSIC_DIR / "peaceful"
HOPEFUL_MUSIC_DIR = MUSIC_DIR / "hopeful"
EMOTIONAL_MUSIC_DIR = MUSIC_DIR / "emotional"


def log_music_status() -> None:
    music_dirs = {
        "peaceful": PEACEFUL_MUSIC_DIR,
        "hopeful": HOPEFUL_MUSIC_DIR,
        "emotional": EMOTIONAL_MUSIC_DIR,
    }

    for mood, folder in music_dirs.items():
        if not folder.exists():
            print(f"Music folder missing: {folder}")
            continue

        tracks = list(folder.glob("*.mp3"))
        print(f"Music folder '{mood}': {len(tracks)} track(s) found")


def find_latest_ready_base_name() -> str | None:
    long_files = sorted(SCRIPT_DIR.glob("*_long.txt"), reverse=True)

    for path in long_files:
        base_name = path.name[:-9]

        long_audio = AUDIO_DIR / f"{base_name}_long_voice.mp3"
        long_bg = BACKGROUND_DIR / f"{base_name}_bg.png"

        if long_audio.exists() and long_bg.exists():
            return base_name

    return None


def ensure_long_assets(base_name: str) -> None:
    video_path = VIDEO_DIR / f"{base_name}_long.mp4"
    bg_path = BACKGROUND_DIR / f"{base_name}_bg.png"

    if not video_path.exists():
        long_output = render_long_video(base_name)
        if long_output:
            print(f"Created long video: {long_output}")
        else:
            print(f"Failed to create long video for base: {base_name}")
    else:
        print(f"Long video already exists: {video_path}")

    if bg_path.exists():
        yt_thumb, vert_thumb = build_thumbnail_set(
            background_path=bg_path,
            base_name=base_name,
        )
        print(f"Generated long thumbnails: {yt_thumb}, {vert_thumb}")
    else:
        print(f"Background not found for long thumbnail: {bg_path}")


def ensure_short_assets(base_name: str, idx: int) -> None:
    audio_path = AUDIO_DIR / f"{base_name}_short_{idx}_voice.mp3"
    bg_path = BACKGROUND_DIR / f"{base_name}_short_{idx}_bg.png"
    video_path = VIDEO_DIR / f"{base_name}_short_{idx}.mp4"

    if not audio_path.exists() or not bg_path.exists():
        print(f"Skipping short {idx}: missing audio or background")
        return

    if not video_path.exists():
        short_output = render_short_video(base_name, idx)
        if short_output:
            print(f"Created short video {idx}: {short_output}")
        else:
            print(f"Failed to create short video {idx} for base: {base_name}")
    else:
        print(f"Short video {idx} already exists: {video_path}")

    yt_thumb, vert_thumb = build_thumbnail_set(
        background_path=bg_path,
        base_name=f"{base_name}_short_{idx}",
    )
    print(f"Generated short {idx} thumbnails: {yt_thumb}, {vert_thumb}")


def main() -> None:
    ensure_video_dir()
    log_music_status()

    base_name = find_latest_ready_base_name()
    if not base_name:
        print("No ready base name found with both script audio and background.")
        return

    print(f"Rendering assets for ready base: {base_name}")

    ensure_long_assets(base_name)

    for idx in range(1, 4):
        ensure_short_assets(base_name, idx)


if __name__ == "__main__":
    main()
