from sentence_transformers import SentenceTransformer


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def load_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model.
    """
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str], model: SentenceTransformer):
    """
    Embed multiple texts in a single batch.
    """

    return model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


if __name__ == "__main__":

    import numpy as np
    from config import DATA_DIR
    from src.processing.document_processor import process_document

    raw_data_dir = DATA_DIR / "raw"
    path = raw_data_dir / "quality" / "QUA-INC-001_v3_2026.pdf"

    chunks = process_document(path=path, raw_data_dir=raw_data_dir)

    texts = [ chunk["text"] for chunk in chunks]

    model = load_embedding_model()
    embeddings = embed_texts(texts=texts, model=model)

    print("Chunks:", len(chunks))
    print("Embeddings shape:", embeddings.shape)
    print("Vector dimension:", embeddings.shape[1])
    print("First vector norm:", np.linalg.norm(embeddings[0]))

    print("First chunk ID:", chunks[0]["chunk_id"])