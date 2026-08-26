from config import DATA_DIR

from src.ingestion.document_loader import (
    find_documents,
)
from src.processing.document_processor import (
    process_document,
)


def audit_document_processor():
    """
    Audit the complete document processing pipeline.
    """

    raw_data_dir = DATA_DIR / "raw"

    documents = find_documents(
        raw_data_dir
    )

    total_chunks = 0
    chunk_ids = set()

    duplicate_chunk_ids = []
    empty_chunks = []
    failed = []

    for path in documents:

        try:
            chunks = process_document(
                path=path,
                raw_data_dir=raw_data_dir,
            )

            total_chunks += len(chunks)

            for chunk in chunks:

                chunk_id = chunk["chunk_id"]

                if chunk_id in chunk_ids:
                    duplicate_chunk_ids.append(
                        chunk_id
                    )

                chunk_ids.add(
                    chunk_id
                )

                if not chunk["text"].strip():
                    empty_chunks.append(
                        chunk_id
                    )

        except Exception as error:
            failed.append(
                (
                    path,
                    str(error),
                )
            )

    print(
        f"Documents: {len(documents)}"
    )

    print(
        f"Total chunks: {total_chunks}"
    )

    print(
        f"Unique chunk IDs: {len(chunk_ids)}"
    )

    print(
        f"Duplicate chunk IDs: "
        f"{len(duplicate_chunk_ids)}"
    )

    print(
        f"Empty chunks: "
        f"{len(empty_chunks)}"
    )

    print(
        f"Failed documents: "
        f"{len(failed)}"
    )

    if duplicate_chunk_ids:

        print("\nDUPLICATE CHUNK IDS")

        for chunk_id in duplicate_chunk_ids:
            print(chunk_id)

    if failed:

        print("\nFAILED")

        for path, error in failed:

            print(
                path.relative_to(
                    raw_data_dir
                )
            )

            print(error)


if __name__ == "__main__":
    audit_document_processor()