from pathlib import Path


def validate_publish_package(package: dict) -> list[str]:
    errors: list[str] = []

    video_path = package.get("video_path")
    thumbnail_path = package.get("thumbnail_path")
    title = package.get("title", "")
    description = package.get("description", "")
    tags = package.get("tags", [])
    publish_at = package.get("publish_at", "")

    if not video_path:
        errors.append("Missing video_path in package.")
    elif not Path(video_path).exists():
        errors.append(f"Video file not found: {video_path}")

    if not thumbnail_path:
        errors.append("Missing thumbnail_path in package.")
    elif not Path(thumbnail_path).exists():
        errors.append(f"Thumbnail file not found: {thumbnail_path}")

    if not title or not str(title).strip():
        errors.append("Missing title.")

    if len(str(title)) > 100:
        errors.append(f"Title too long ({len(str(title))} chars). Max is 100.")

    if not description or not str(description).strip():
        errors.append("Missing description.")

    if len(str(description)) > 5000:
        errors.append(f"Description too long ({len(str(description))} chars).")

    if not isinstance(tags, list):
        errors.append("Tags must be a list.")

    if not publish_at or not str(publish_at).strip():
        errors.append("Missing publish_at timestamp.")

    return errors


def validate_publish_packages(packages: list[dict]) -> list[str]:
    all_errors: list[str] = []

    for idx, package in enumerate(packages, start=1):
        package_type = package.get("type", f"package_{idx}")
        errors = validate_publish_package(package)

        for error in errors:
            all_errors.append(f"[{package_type}] {error}")

    return all_errors
