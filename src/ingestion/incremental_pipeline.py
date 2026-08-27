from pathlib import Path

from src.ingestion.change_detector import compare_manifests
from src.ingestion.manifest import build_manifest, load_manifest
from src.processing.document_processor import process_document


def run_incremental_processing(raw_data_dir: Path, manifest_path: Path) -> dict:
    """
    Detect changes and process added or modified documents.
    """

    previous_manifest = load_manifest(manifest_path)
    current_manifest = build_manifest(raw_data_dir)

    changes = compare_manifests(
        previous=previous_manifest,
        current=current_manifest,
    )

    paths_to_process = changes["added"] + changes["modified"]

    processed = {}
    failed = []

    for relative_path in paths_to_process:
        path = raw_data_dir / relative_path

        try:
            chunks = process_document(path=path, raw_data_dir=raw_data_dir)
            processed[relative_path] = chunks
        except Exception as error:

            failed.append(
                {
                    "source": relative_path,
                    "error": str(error),
                }
            )

    return {
        "changes": changes,
        "processed": processed,
        "failed": failed,
        "current_manifest": current_manifest,
    }


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

    result = run_incremental_processing(
        raw_data_dir=raw_data_dir,
        manifest_path=manifest_path,
    )

    changes = result["changes"]

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

    print(
        f"Processed documents: "
        f"{len(result['processed'])}"
    )

    print(
        f"Failed documents: "
        f"{len(result['failed'])}"
    )