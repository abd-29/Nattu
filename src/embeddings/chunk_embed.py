import numpy as np
from sentence_transformers import SentenceTransformer
from src.embeddings.embedding_model import embed_texts


def embed_chunks(chunks: list[dict], model: SentenceTransformer) -> list[dict]:
    """
    Add an embedding vector to each chunk.
    """

    if not chunks:
        return []

    texts = [chunk["text"] for chunk in chunks]

    embeddings = embed_texts(texts=texts, model=model)
    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings,):
        embedded_chunks.append({**chunk, "embedding": embedding})

    return embedded_chunks


if __name__ == "__main__":

    from config import DATA_DIR

    from src.embeddings.embedding_model import load_embedding_model
    from src.processing.document_processor import process_document

    raw_data_dir = DATA_DIR / "raw"

    path = raw_data_dir / "quality" / "QUA-INC-001_v3_2026.pdf"

    chunks = process_document(path=path, raw_data_dir=raw_data_dir)

    model = load_embedding_model()
    embedded_chunks = embed_chunks(chunks=chunks, model=model)

    print(f"Chunks: {len(embedded_chunks)}")

    for chunk in embedded_chunks:

        print(
            chunk["chunk_id"],
            chunk["embedding"].shape,
            round(float(np.linalg.norm(chunk["embedding"])), 4)
        )