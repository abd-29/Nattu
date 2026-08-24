def enrich_chunks(chunks: list[dict], metadata: dict) -> list[dict]:
    """
    Add document metadata to chunks.
    """

    enriched_chunks = []

    for chunk in chunks:
        chunk_id = (
            f"{metadata['document_id']}"
            f"_v{metadata['version']}"
            f"_chunk_{chunk['chunk']}"
        )

        enriched_chunk = {
            "chunk_id": chunk_id,
            **metadata,
            **chunk,
        }

        enriched_chunks.append(
            enriched_chunk
        )

    return enriched_chunks



if __name__ == "__main__":

    from pprint import pprint

    from config import DATA_DIR
    from src.ingestion.pdf_loader import extract_pdf_pages
    from src.chunking.text_chunker import chunk_pages

    pdf_path = (
        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-INC-001_v3.pdf"
    )

    metadata = {
        "document_id": "QUA-INC-001",
        "title": "Gestion des incidents produits",
        "version": "3.0",
        "department": "quality",
        "classification": "internal",
        "status": "active",
        "source": "QUA-INC-001_v3.pdf",
    }

    pages = extract_pdf_pages(pdf_path)

    chunks = chunk_pages(
        pages=pages,
        chunk_size=500,
        overlap_paragraphs=1,
    )

    chunks = enrich_chunks(
        chunks=chunks,
        metadata=metadata,
    )

    pprint(chunks[0])

    