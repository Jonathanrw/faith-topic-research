import json
from pathlib import Path
from datetime import datetime


MANIFEST_DIR = Path("content/manifests")


def ensure_manifest_dir() -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)


def build_manifest(base_name: str, uploads: list[dict]) -> dict:
    return {
        "base_name": base_name,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "upload_count": len(uploads),
        "uploads": uploads,
    }


def save_manifest(base_name: str, manifest: dict) -> Path:
    ensure_manifest_dir()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_manifest_{timestamp}.json"

    path = MANIFEST_DIR / filename
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return path
