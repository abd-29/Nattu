def build_local_index(
    chunks: list[dict],
    model,
) -> list[dict]:
    """
    Compute and attach embeddings to chunks.
    """

    indexed_chunks = []

    for chunk in chunks:
        embedding = model.encode(chunk["text"])

        indexed_chunk = {
            **chunk,
            "embedding": embedding,
        }

        indexed_chunks.append(indexed_chunk)

    return indexed_chunks


def cosine_similarity(vector_a, vector_b) -> float:
    """
    Compute cosine similarity.
    """

    return float(
        np.dot(vector_a, vector_b)
        / (
            np.linalg.norm(vector_a)
            * np.linalg.norm(vector_b)
        )
    )



def search(
    query: str,
    indexed_chunks: list[dict],
    model,
    top_k: int = 3,
) -> list[dict]:
    """
    Return the most similar chunks.
    """

    query_embedding = model.encode(
        query
    )

    results = []

    for chunk in indexed_chunks:
        score = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        results.append(
            {
                "score": score,
                **chunk,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]




if __name__ == "__main__":

    from pprint import pprint

    from config import DATA_DIR
    from src.ingestion.pdf_loader import extract_pdf_pages
    from src.chunking.text_chunker import chunk_pages
    from src.processing.document_processor import enrich_chunks
    import numpy as np

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

    chunks = chunk_pages(pages=pages, chunk_size=500, overlap_paragraphs=1)

    chunks = enrich_chunks(chunks=chunks, metadata=metadata)

    model = load_embedding_model()
    
    query = (
    "Quel est le délai pour informer "
    "le responsable Quality lors "
    "d'un incident critique ?"
    )

    results = search(
    query=query,
    indexed_chunks=indexed_chunks,
    model=model,
    top_k=3,
    )

    for result in results:
        print(
            result["chunk_id"],
            result["score"],
        )