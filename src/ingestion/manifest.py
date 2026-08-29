import hashlib
import json
from pathlib import Path

from src.ingestion.document_loader import find_documents


def compute_file_hash(path: Path) -> str:
    """
    Compute the SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            block = file.read(1024 * 1024)

            if not block:
                break

            sha256.update(block)

    return sha256.hexdigest()


def build_manifest(raw_data_dir: Path) -> dict:
    """
    Build a manifest containing file hashes.
    """

    documents = find_documents(raw_data_dir)
    manifest = {}

    for path in documents:

        source = path.relative_to(raw_data_dir).as_posix()

        manifest[source] = {
            "sha256": compute_file_hash(path)
        }

    return manifest


def load_manifest(path: Path) -> dict:
    """
    Load a manifest from JSON.
    """

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_manifest(manifest: dict, path: Path) -> None:
    """
    Save a manifest to JSON.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False,)


def compare_manifests(previous: dict, current: dict,) -> dict:
    """
    Detect added, modified, deleted
    and unchanged documents.
    """

    previous_paths = set(previous)
    current_paths = set(current)

    added = current_paths - previous_paths
    deleted = previous_paths - current_paths

    common = previous_paths & current_paths

    modified = set()
    unchanged = set()

    for source in common:

        previous_hash = previous[source]["sha256"]
        current_hash = current[source]["sha256"]

        if previous_hash != current_hash:
            modified.add(source)

        else:
            unchanged.add(source)

    return {
        "added": sorted(added),
        "modified": sorted(modified),
        "deleted": sorted(deleted),
        "unchanged": sorted(unchanged),
    }