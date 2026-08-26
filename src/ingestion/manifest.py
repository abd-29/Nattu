import json
from pathlib import Path

from src.ingestion.document_loader import (
    find_documents,
)
from src.ingestion.file_fingerprint import (
    compute_file_hash,
)


def build_manifest(
    raw_data_dir: Path,
) -> dict:
    """
    Build a manifest containing document fingerprints.
    """

    documents = find_documents(
        raw_data_dir
    )

    manifest = {}

    for path in documents:

        relative_path = path.relative_to(
            raw_data_dir
        ).as_posix()

        manifest[relative_path] = {
            "sha256": compute_file_hash(
                path
            ),
        }

    return manifest


def save_manifest(
    manifest: dict,
    path: Path,
) -> None:
    """
    Save a manifest to a JSON file.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            manifest,
            file,
            indent=2,
            ensure_ascii=False,
        )


def load_manifest(
    path: Path,
) -> dict:
    """
    Load a manifest from a JSON file.
    """

    if not path.exists():
        return {}

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)

if __name__ == "__main__":

    from config import DATA_DIR

    raw_data_dir = (
        DATA_DIR
        / "raw"
    )

    manifest_path = (
        DATA_DIR
        / "processed"
        / "manifest.json"
    )

    manifest = build_manifest(
        raw_data_dir
    )

    save_manifest(
        manifest=manifest,
        path=manifest_path,
    )

    print(
        f"Documents in manifest: "
        f"{len(manifest)}"
    )

    print(
        f"Manifest saved to: "
        f"{manifest_path}"
    )


