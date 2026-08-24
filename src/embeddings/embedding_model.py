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


def embed_text(
    text: str,
    model: SentenceTransformer,
):
    """
    Convert text into an embedding vector.
    """

    return model.encode(text)





def cosine_similarity(
    vector_a,
    vector_b,
) -> float:
    """
    Compute cosine similarity between two vectors.
    """

    return np.dot(vector_a, vector_b) / (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )



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
    
    question = (
    "Quel est le délai pour informer "
    "le responsable Quality lors "
    "d'un incident critique ?"
    )

    question_embedding = embed_text(
        text=question,
        model=model,
    )

    for chunk in chunks:
        chunk_embedding = embed_text(
            text=chunk["text"],
            model=model,
        )

        score = cosine_similarity(
            question_embedding,
            chunk_embedding,
        )

        print(
            f"Chunk {chunk['chunk']} "
            f"| score = {score:.4f}"
        )

