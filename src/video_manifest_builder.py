import json
from pathlib import Path


SCRIPT_DIR = Path("content/scripts")
AUDIO_DIR = Path("content/audio")


def find_latest_long_script() -> Path | None:
    files = sorted(SCRIPT_DIR.glob("*_long.txt"), reverse=True)
    return files[0] if files else None


def find_latest_shorts_file() -> Path | None:
    files = sorted(SCRIPT_DIR.glob("*_shorts.json"), reverse=True)
    return files[0] if files else None


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def base_name_from_file(path: Path, suffix: str) -> str:
    name = path.name
    if name.endswith(suffix):
        return name[:-len(suffix)]
    return path.stem
