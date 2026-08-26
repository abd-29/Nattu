from statistics import mean

from config import DATA_DIR

from src.chunking.text_chunker import (
    chunk_units,
)
from src.chunking.text_cleaner import clean_units
from src.ingestion.document_loader import (
    find_documents,
    load_document,
)



CHUNK_SIZE = 500
SMALL_CHUNK_THRESHOLD = 100


def audit_chunking():
    """
    Audit chunking on all documents.
    """

    raw_data_dir = DATA_DIR / "raw"

    documents = find_documents(
        raw_data_dir
    )

    total_chunks = 0

    chunk_sizes = []

    empty_chunks = []
    small_chunks = []
    oversized_chunks = []
    duplicate_chunks = []
    failed = []

    for path in documents:

        try:
            units = load_document(
                path
            )

            units = clean_units(
                units
            )

            chunks = chunk_units(
                units=units,
                chunk_size=CHUNK_SIZE,
            )

            seen_texts = set()

            for chunk in chunks:

                text = chunk["text"].strip()

                size = len(text)

                total_chunks += 1
                chunk_sizes.append(size)

                if not text:
                    empty_chunks.append(
                        (
                            path,
                            chunk["chunk"],
                        )
                    )

                if (
                    text
                    and size
                    < SMALL_CHUNK_THRESHOLD
                ):
                    small_chunks.append(
                        (
                            path,
                            chunk["chunk"],
                            size,
                        )
                    )

                if size > CHUNK_SIZE:
                    oversized_chunks.append(
                        (
                            path,
                            chunk["chunk"],
                            size,
                        )
                    )

                if text in seen_texts:
                    duplicate_chunks.append(
                        (
                            path,
                            chunk["chunk"],
                        )
                    )

                seen_texts.add(
                    text
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
        f"Average size: "
        f"{mean(chunk_sizes):.1f}"
    )

    print(
        f"Minimum size: {min(chunk_sizes)}"
    )

    print(
        f"Maximum size: {max(chunk_sizes)}"
    )

    print(
        f"Empty chunks: "
        f"{len(empty_chunks)}"
    )

    print(
        f"Small chunks (<{SMALL_CHUNK_THRESHOLD}): "
        f"{len(small_chunks)}"
    )

    print(
        f"Oversized chunks (>{CHUNK_SIZE}): "
        f"{len(oversized_chunks)}"
    )

    print(
        f"Duplicate chunks: "
        f"{len(duplicate_chunks)}"
    )

    print(
        f"Failed documents: "
        f"{len(failed)}"
    )

    if small_chunks:

        print("\nSMALL CHUNKS")

        for path, chunk, size in small_chunks:

            print(
                path.relative_to(
                    raw_data_dir
                ),
                f"| chunk {chunk}",
                f"| {size} chars",
            )

    if oversized_chunks:

        print("\nOVERSIZED CHUNKS")

        for path, chunk, size in oversized_chunks:

            print(
                path.relative_to(
                    raw_data_dir
                ),
                f"| chunk {chunk}",
                f"| {size} chars",
            )

    if duplicate_chunks:

        print("\nDUPLICATE CHUNKS")

        for path, chunk in duplicate_chunks:

            print(
                path.relative_to(
                    raw_data_dir
                ),
                f"| chunk {chunk}",
            )

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
    audit_chunking()