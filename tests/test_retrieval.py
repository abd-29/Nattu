from src.retrieval.utils import reciprocal_rank_fusion

def test_rrf_prioritizes_common_result():
    vector_results = [
        {"chunk_id": "chunk_1", "text": "A"},
        {"chunk_id": "chunk_2", "text": "B"},
    ]

    lexical_results = [
        {"chunk_id": "chunk_2", "text": "B"},
        {"chunk_id": "chunk_3", "text": "C"},
    ]

    results = reciprocal_rank_fusion(
        vector_results=vector_results,
        lexical_results=lexical_results,
    )

    assert results[0]["chunk_id"] == "chunk_2"

def test_rrf_removes_duplicate_chunk_ids():
    vector_results = [
        {"chunk_id": "chunk_1", "text": "A"},
    ]

    lexical_results = [
        {"chunk_id": "chunk_1", "text": "A"},
    ]

    results = reciprocal_rank_fusion(
        vector_results=vector_results,
        lexical_results=lexical_results,
    )

    assert len(results) == 1