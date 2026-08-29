import re

from pgvector import Vector
from sentence_transformers import SentenceTransformer

from config import DATA_DIR
from src.embeddings.embedding_model import embed_texts
from src.indexing.index_state import load_index_state
from src.vectorstore.database import get_connection
from src.retrieval.reranker import load_reranker, rerank_results


def build_lexical_query(query: str) -> str:
    """
    Convert a natural language query into
    an OR-based lexical query.
    """

    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", query)

    return " OR ".join(words)


def vector_search(query: str, model: SentenceTransformer, limit: int = 10) -> list[dict]:
    """
    Retrieve chunks using cosine similarity.
    """

    query_embedding = embed_texts(texts=[query], model=model)[0]

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    version,
                    text,
                    source,
                    start_page,
                    end_page,
                    1 - (
                        embedding <=> %s
                    ) AS score
                FROM document_chunks
                ORDER BY embedding <=> %s
                LIMIT %s;
                """,
                (
                    Vector(query_embedding),
                    Vector(query_embedding),
                    limit,
                ),
            )

            rows = cursor.fetchall()

    return [
        {
            "chunk_id": row[0],
            "document_id": row[1],
            "version": row[2],
            "text": row[3],
            "source": row[4],
            "start_page": row[5],
            "end_page": row[6],
            "score": float(row[7]),
        }
        for row in rows
    ]


def lexical_search(query: str, limit: int = 10) -> list[dict]:
    """
    Retrieve chunks using PostgreSQL full-text search.
    """

    lexical_query = build_lexical_query(query)

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    version,
                    text,
                    source,
                    start_page,
                    end_page,
                    ts_rank_cd(
                        to_tsvector(
                            'french',
                            text
                        ),
                        websearch_to_tsquery(
                            'french',
                            %s
                        )
                    ) AS score
                FROM document_chunks
                WHERE
                    to_tsvector(
                        'french',
                        text
                    )
                    @@
                    websearch_to_tsquery(
                        'french',
                        %s
                    )
                ORDER BY score DESC
                LIMIT %s;
                """,
                (
                    lexical_query,
                    lexical_query,
                    limit,
                ),
            )

            rows = cursor.fetchall()

    return [
        {
            "chunk_id": row[0],
            "document_id": row[1],
            "version": row[2],
            "text": row[3],
            "source": row[4],
            "start_page": row[5],
            "end_page": row[6],
            "score": float(row[7]),
        }
        for row in rows
    ]



def reciprocal_rank_fusion(vector_results: list[dict], lexical_results: list[dict], k: int = 60,) -> list[dict]:
    """
    Fuse vector and lexical rankings using RRF.
    """

    fused = {}

    for rank, result in enumerate(vector_results, start=1):

        chunk_id = result["chunk_id"]

        if chunk_id not in fused:
            fused[chunk_id] = {
                **result,
                "rrf_score": 0.0,
            }

        fused[chunk_id]["rrf_score"] += (
            1 / (k + rank)
        )

    for rank, result in enumerate(lexical_results, start=1,):

        chunk_id = result["chunk_id"]

        if chunk_id not in fused:
            fused[chunk_id] = {
                **result,
                "rrf_score": 0.0,
            }

        fused[chunk_id]["rrf_score"] += (
            1 / (k + rank)
        )

    return sorted(
        fused.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )



def deduplicate_results(results: list[dict]) -> list[dict]:
    """
    Remove results containing identical text.
    """

    unique_results = []

    seen_texts = set()

    for result in results:

        normalized_text = " ".join(result["text"].split())

        if normalized_text in seen_texts:
            continue

        seen_texts.add(normalized_text)
        unique_results.append(result)

    return unique_results


def hybrid_search(query: str, model: SentenceTransformer, limit: int = 10) -> list[dict]:
    """
    Run vector and lexical retrieval,
    then fuse their rankings using RRF.
    """

    vector_results = vector_search(
        query=query,
        model=model,
        limit=10,
    )

    lexical_results = lexical_search(
        query=query,
        limit=10,
    )

    fused_results = reciprocal_rank_fusion(
        vector_results=vector_results,
        lexical_results=lexical_results,
    )

    fused_results = deduplicate_results(
        fused_results
    )

    return fused_results[:limit]



def version_key(version: str) -> tuple:
    """
    Convert a version string into a sortable tuple.
    """
    try:
        return tuple(
            int(part)
            for part in version.split(".")
        )

    except (AttributeError, ValueError):
        return (0,)


def find_blocking_conflict(results: list[dict], index_state: dict) -> dict | None:
    """
    Detect whether a newer conflicting version
    exists for a retrieved document.
    """

    retrieved_document_ids = {
        result["document_id"]
        for result in results
    }

    for document_id in retrieved_document_ids:

        document_states = [
            state
            for state in index_state.values()
            if state["document_id"] == document_id
        ]

        if not document_states:
            continue

        latest_version = max(
            (
                state["version"]
                for state in document_states
            ),
            key=version_key,
        )

        latest_states = [
            state
            for state in document_states
            if state["version"] == latest_version
        ]

        has_conflict = any(
            state["decision"] == "conflict"
            for state in latest_states
        )

        if not has_conflict:
            continue

        retrieved_versions = sorted(
            {
                result["version"]
                for result in results
                if result["document_id"]
                == document_id
            },
            key=version_key,
        )

        return {
            "document_id": document_id,
            "latest_version": latest_version,
            "retrieved_versions": retrieved_versions,
        }

    return None


if __name__ == "__main__":

    from src.embeddings.embedding_model import (
        load_embedding_model,
    )

    query = (
        "Que faut-il faire lorsqu'un "
        "incident sécurité client est qualifié ?"
    )

    # Load embedding model.
    embedding_model = load_embedding_model()

    # Retrieve candidate chunks.
    results = hybrid_search(
        query=query,
        model=embedding_model,
        limit=10,
    )

    # Rerank retrieved chunks.
    reranker = load_reranker()

    results = rerank_results(
        query=query,
        results=results,
        model=reranker,
        limit=3,
    )

    # Load document indexing state.
    index_state_path = (
        DATA_DIR
        / "processed"
        / "index_state.json"
    )

    index_state = load_index_state(
        index_state_path
    )

    # Check whether a newer conflicting
    # document version exists.
    conflict = find_blocking_conflict(
        results=results,
        index_state=index_state,
    )

    if conflict:

        retrieved_versions = ", ".join(
            conflict["retrieved_versions"]
        )

        print("=" * 70)

        print(
            f"Conflict detected for "
            f"{conflict['document_id']}"
        )

        print(
            f"Latest version: "
            f"{conflict['latest_version']}"
        )

        print()

        print(
            f"La version "
            f"{conflict['latest_version']} "
            f"présente un conflit documentaire, "
            f"donc je ne peux pas garantir "
            f"la règle actuelle."
        )

        print(
            f"Des informations provenant "
            f"des anciennes versions "
            f"({retrieved_versions}) "
            f"ont été trouvées, "
            f"mais elles peuvent être obsolètes."
        )

    else:

        for rank, result in enumerate(
            results,
            start=1,
        ):

            print("=" * 70)

            print(
                f"Rank: {rank}"
            )

            print(
                f"Chunk: "
                f"{result['chunk_id']}"
            )

            print(
                f"Document: "
                f"{result['document_id']}"
            )

            print(
                f"Version: "
                f"{result['version']}"
            )

            print(
                f"RRF score: "
                f"{result['rrf_score']:.6f}"
            )

            print(
                f"Reranker score: "
                f"{result['reranker_score']:.4f}"
            )

            print()

            print(
                result["text"]
            )