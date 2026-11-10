from src.retrieval.hybrid_search import extract_version_filter

def test_extract_version():
    query = "Que prévoit la version 4.2.3 du produit Alpha ?"
    assert extract_version_filter(query) == "4.2.3"

def test_extract_simple_version():
    query = "Que contient la version 2.0 ?"
    assert extract_version_filter(query) == "2.0"

def test_no_version():
    query = "Comment installer le produit Alpha ?"
    assert extract_version_filter(query) is None