from sentence_transformers import CrossEncoder


RERANKER_MODEL_NAME = "cross-encoder/" "mmarco-mMiniLMv2-L12-H384-v1"


def load_reranker() -> CrossEncoder:
    """
    Load the multilingual reranking model.
    """

    return CrossEncoder(RERANKER_MODEL_NAME)


def rerank_results(query: str, results: list[dict], model: CrossEncoder, limit: int = 3) -> list[dict]:
    """
    Rerank retrieved chunks against the query.
    """

    if not results:
        return []

    pairs = [
        [
            query,
            result["text"],
        ]
        for result in results
    ]

    scores = model.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):

        reranked.append(
            {
                **result,
                "reranker_score": float(score),
            }
        )

    reranked.sort(
        key=lambda item: item["reranker_score"],
        reverse=True,
    )

    return reranked[:limit]