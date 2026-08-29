from src.vectorshore.database import get_connection

from pgvector import Vector


def delete_document_chunks_by_sources(sources: list[str]) -> int:
    """
    Delete chunks belonging to multiple source documents.
    """

    if not sources:
        return 0

    deleted_chunks = 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for source in sources:

                cursor.execute(
                    """
                    DELETE FROM document_chunks
                    WHERE source = %s;
                    """,
                    (source,),
                )

                deleted_chunks += (
                    cursor.rowcount
                )

    return deleted_chunks


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


def delete_document_chunks(source: str) -> None:
    """
    Delete all chunks belonging to one source document.
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

