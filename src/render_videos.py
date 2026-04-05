from pathlib import Path

from src.video_renderer import ensure_video_dir, render_long_video, render_short_video


SCRIPT_DIR = Path("content/scripts")


def find_latest_base_name() -> str | None:
    long_files = sorted(SCRIPT_DIR.glob("*_long.txt"), reverse=True)
    if not long_files:
        return None

    latest = long_files[0].name
    if latest.endswith("_long.txt"):
        return latest[:-9]
    return None


def main() -> None:
    ensure_video_dir()

    base_name = find_latest_base_name()
    if not base_name:
        print("No long script base name found.")
        return

    print(f"Rendering videos for base: {base_name}")

    long_output = render_long_video(base_name)
    if long_output:
        print(f"Created long video: {long_output}")

    for idx in range(1, 4):
        short_output = render_short_video(base_name, idx)
        if short_output:
            print(f"Created short video {idx}: {short_output}")


if __name__ == "__main__":
    main()
