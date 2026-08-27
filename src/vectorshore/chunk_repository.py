from src.vectorshore.database import get_connection

from pgvector import Vector
def replace_document_chunks(source: str, chunks: list[dict]) -> None:
    """
    Replace all stored chunks for one source document.
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM document_chunks
                WHERE source = %s;
                """,
                (source,),
            )

            for chunk in chunks:
                cursor.execute(
                    """
                    INSERT INTO document_chunks (
                        chunk_id,
                        document_id,
                        title,
                        version,
                        department,
                        classification,
                        status,
                        language,
                        document_date,
                        source,
                        filename,
                        extension,
                        chunk_number,
                        start_unit,
                        end_unit,
                        start_page,
                        end_page,
                        text,
                        embedding
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    );
                    """,
                    (
                        chunk["chunk_id"],
                        chunk["document_id"],
                        chunk["title"],
                        chunk["version"],
                        chunk["department"],
                        chunk["classification"],
                        chunk["status"],
                        chunk["language"],
                        chunk["date"],
                        chunk["source"],
                        chunk["filename"],
                        chunk["extension"],
                        chunk["chunk"],
                        chunk["start_unit"],
                        chunk["end_unit"],
                        chunk["start_page"],
                        chunk["end_page"],
                        chunk["text"],
                        Vector(chunk["embedding"]),
                    ),
                )


if __name__ == "__main__":

    from config import DATA_DIR

    from src.embeddings.chunk_embed import (
        embed_chunks,
    )
    from src.embeddings.embedding_model import (
        load_embedding_model,
    )
    from src.processing.document_processor import (
        process_document,
    )

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

    model = load_embedding_model()

    embedded_chunks = embed_chunks(
        chunks=chunks,
        model=model,
    )

    source = embedded_chunks[0][
        "source"
    ]

    replace_document_chunks(
        source=source,
        chunks=embedded_chunks,
    )

    print(
        f"Stored chunks: "
        f"{len(embedded_chunks)}"
    )