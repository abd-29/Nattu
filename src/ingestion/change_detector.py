from pathlib import Path


def compare_manifests(
    previous: dict,
    current: dict,
) -> dict:
    """
    Compare two document manifests.
    """

    previous_paths = set(
        previous.keys()
    )

    current_paths = set(
        current.keys()
    )

    added = (
        current_paths
        - previous_paths
    )

    deleted = (
        previous_paths
        - current_paths
    )

    common = (
        previous_paths
        & current_paths
    )

    modified = set()
    unchanged = set()

    for path in common:

        previous_hash = (
            previous[path]["sha256"]
        )

        current_hash = (
            current[path]["sha256"]
        )

        if previous_hash != current_hash:
            modified.add(path)

        else:
            unchanged.add(path)

    return {
        "added": sorted(added),
        "modified": sorted(modified),
        "deleted": sorted(deleted),
        "unchanged": sorted(unchanged),
    }


if __name__ == "__main__":

    from config import DATA_DIR

    from src.ingestion.manifest import (
        build_manifest,
        load_manifest,
    )

    raw_data_dir = (
        DATA_DIR
        / "raw"
    )

    manifest_path = (
        DATA_DIR
        / "processed"
        / "manifest.json"
    )

    previous_manifest = load_manifest(
        manifest_path
    )

    current_manifest = build_manifest(
        raw_data_dir
    )

    changes = compare_manifests(
        previous=previous_manifest,
        current=current_manifest,
    )

    print(
        f"Added: "
        f"{len(changes['added'])}"
    )

    print(
        f"Modified: "
        f"{len(changes['modified'])}"
    )

    print(
        f"Deleted: "
        f"{len(changes['deleted'])}"
    )

    print(
        f"Unchanged: "
        f"{len(changes['unchanged'])}"
    )

