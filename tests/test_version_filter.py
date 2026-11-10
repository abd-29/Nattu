from src.retrieval.utils import extract_version_filter

def test_extract_version():
    assert extract_version_filter(
        "Que prévoit la version 4.2.3 du produit Alpha ?"
    ) == "4.2.3"

def test_extract_simple_version():
    assert extract_version_filter(
        "Que contient la version 2.0 ?"
    ) == "2.0"

def test_no_version():
    assert extract_version_filter(
        "Comment installer le produit Alpha ?"
    ) is None