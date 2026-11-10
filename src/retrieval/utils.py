import re

def reciprocal_rank_fusion(vector_results: list[dict], lexical_results: list[dict], k: int = 60) -> list[dict]:
    """Fuse vector and lexical rankings using RRF."""
    fused = {}

    for rank, result in enumerate(vector_results, start=1):
        chunk_id = result["chunk_id"]
        if chunk_id not in fused:
            fused[chunk_id] = {**result, "rrf_score": 0.0}
        fused[chunk_id]["rrf_score"] += 1 / (k + rank)

    for rank, result in enumerate(lexical_results, start=1):
        chunk_id = result["chunk_id"]
        if chunk_id not in fused:
            fused[chunk_id] = {**result, "rrf_score": 0.0}
        fused[chunk_id]["rrf_score"] += 1 / (k + rank)

    return sorted(
        fused.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

def extract_version_filter(query: str) -> str | None:
    """Extract an explicit document version from the query."""
    match = re.search(
        r"\bversion\s+(\d+(?:\.\d+){1,3})\b",
        query,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    return match.group(1)