import hashlib
from pathlib import Path

from src.chunking.text_chunker import (
    chunk_units,
)
from src.chunking.text_cleaner import clean_units
from src.ingestion.document_loader import (
    load_document,
)
from src.processing.metadata_extractor import (
    extract_metadata,
)

def build_chunk_id(
    metadata: dict,
    chunk_number: int,
) -> str:
    """
    Build a deterministic and unique chunk identifier.
    """

    source = metadata["source"]

    source_hash = hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()[:8]

    return (
        f"{metadata['document_id']}"
        f"_v{metadata['version']}"
        f"_{source_hash}"
        f"_chunk_{chunk_number}"
    )


def enrich_chunks(
    chunks: list[dict],
    metadata: dict,
) -> list[dict]:
    """
    Add document metadata to each chunk.
    """

    enriched_chunks = []

    for chunk in chunks:
        chunk_id = build_chunk_id(
            metadata=metadata,
            chunk_number=chunk["chunk"],
        )

        enriched_chunks.append(
            {
                "chunk_id": chunk_id,
                **metadata,
                **chunk,
            }
        )

    return enriched_chunks


def process_document(
    path: Path,
    raw_data_dir: Path,
) -> list[dict]:
    """
    Process one document from loading to enriched chunks.
    """

    units = load_document(
        path
    )

    units = clean_units(
        units
    )

    metadata = extract_metadata(
        units=units,
        path=path,
        raw_data_dir=raw_data_dir,
    )

    chunks = chunk_units(
        units=units,
    )

    return enrich_chunks(
        chunks=chunks,
        metadata=metadata,
    )


if __name__ == "__main__":

    from config import DATA_DIR

    raw_data_dir = (
        DATA_DIR
        / "raw"
    )

    path = (
        raw_data_dir
        / "quality"
        / "QUA-INC-001_v3_2026.pdf"
    )

    chunks = process_document(
        path=path,
        raw_data_dir=raw_data_dir,
    )

    for chunk in chunks:

        print("=" * 70)

        print(
            chunk["chunk_id"]
        )

        print(
            chunk["document_id"],
            chunk["version"],
            chunk["department"],
            chunk["status"],
            chunk["language"],
        )

        print(
            f"pages: "
            f"{chunk['start_page']}-"
            f"{chunk['end_page']}"
        )

        print(
            chunk["text"][:150]
        )