import shutil

from config import DATA_DIR

from src.ingestion.change_detector import (
    compare_manifests,
)
from src.ingestion.manifest import (
    build_manifest,
)


def run_test():
    """
    Test added, modified, deleted and unchanged files.
    """

    test_dir = (
        DATA_DIR
        / "change_test"
    )

    if test_dir.exists():
        shutil.rmtree(
            test_dir
        )

    test_dir.mkdir(
        parents=True
    )

    # Initial state
    file_a = test_dir / "a.txt"
    file_b = test_dir / "b.txt"
    file_c = test_dir / "c.txt"

    file_a.write_text(
        "Document A",
        encoding="utf-8",
    )

    file_b.write_text(
        "Document B",
        encoding="utf-8",
    )

    file_c.write_text(
        "Document C",
        encoding="utf-8",
    )

    previous_manifest = build_manifest(
        test_dir
    )

    # Modify B
    file_b.write_text(
        "Document B modified",
        encoding="utf-8",
    )

    # Delete C
    file_c.unlink()

    # Add D
    file_d = test_dir / "d.txt"

    file_d.write_text(
        "Document D",
        encoding="utf-8",
    )

    current_manifest = build_manifest(
        test_dir
    )

    changes = compare_manifests(
        previous=previous_manifest,
        current=current_manifest,
    )

    print("Added:", changes["added"])
    print("Modified:", changes["modified"])
    print("Deleted:", changes["deleted"])
    print("Unchanged:", changes["unchanged"])


if __name__ == "__main__":
    run_test()