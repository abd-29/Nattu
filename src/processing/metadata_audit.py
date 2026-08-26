from config import DATA_DIR

from src.ingestion.document_loader import (
    find_documents,
    load_document,
)
from src.processing.metadata_extractor import (
    extract_metadata,
)


REQUIRED_FIELDS = [
    "document_id",
    "title",
    "version",
    "date",
    "department",
    "classification",
    "status",
    "language",
]


def audit_metadata():
    """
    Audit metadata extraction for all documents.
    """

    raw_data_dir = DATA_DIR / "raw"

    documents = find_documents(
        raw_data_dir
    )

    complete = 0
    incomplete = []
    failed = []

    for path in documents:

        try:
            units = load_document(
                path
            )

            metadata = extract_metadata(
                units=units,
                path=path,
                raw_data_dir=raw_data_dir,
            )

            missing_fields = [
                field
                for field in REQUIRED_FIELDS
                if not metadata.get(field)
            ]

            if missing_fields:
                incomplete.append(
                    {
                        "path": path,
                        "missing_fields": missing_fields,
                    }
                )

            else:
                complete += 1

        except Exception as error:
            failed.append(
                {
                    "path": path,
                    "error": str(error),
                }
            )

    print(
        f"Documents: {len(documents)}"
    )

    print(
        f"Complete metadata: {complete}"
    )

    print(
        f"Incomplete metadata: {len(incomplete)}"
    )

    print(
        f"Failed: {len(failed)}"
    )

    if incomplete:

        print("\nINCOMPLETE METADATA")

        for item in incomplete:
            print(
                item["path"].relative_to(
                    raw_data_dir
                )
            )

            print(
                "Missing:",
                item["missing_fields"],
            )

    if failed:

        print("\nFAILED")

        for item in failed:
            print(
                item["path"].relative_to(
                    raw_data_dir
                )
            )

            print(
                item["error"]
            )


if __name__ == "__main__":
    audit_metadata()