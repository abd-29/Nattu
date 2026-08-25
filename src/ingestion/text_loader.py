from pathlib import Path


def extract_text_units(path: Path) -> list[dict]:
    """
    Extract content from a text-based file.
    """

    text = path.read_text(encoding="utf-8")

    return [
        {
            "unit": 1,
            "page": None,
            "text": text
        }
    ]