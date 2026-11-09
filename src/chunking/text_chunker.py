from config import DATA_DIR
from src.ingestion.document_loader import load_document


import re


def clean_text(text: str) -> str:
    """
    Remove common extraction noise from text.
    """

    cleaned_lines = []

    for line in text.splitlines():

        normalized_line = " ".join(line.split())

        if not normalized_line:
            cleaned_lines.append("")
            continue

        if re.fullmatch(r"\d+", normalized_line):
            continue

        if normalized_line.startswith("NovaTech Industries - Document interne"):
            continue

        cleaned_lines.append(line.strip())

    return "\n".join(cleaned_lines).strip()


def clean_units(units: list[dict]) -> list[dict]:
    """
    Clean document units while preserving metadata.
    """

    return [
        {
            **unit,
            "text": clean_text(unit["text"]),
        }
        for unit in units
    ]



def chunk_units(units: list[dict], chunk_size: int = 500, overlap_paragraphs: int = 1) -> list[dict]:
    """
    Split document units into continuous chunks
    with paragraph overlap.
    """

    paragraphs = []

    for unit in units:

        unit_number = unit["unit"]
        page_number = unit["page"]

        unit_paragraphs = [
            paragraph.strip()
            for paragraph in unit["text"].split("\n\n")
            if paragraph.strip()
        ]

        for paragraph in unit_paragraphs:

            paragraphs.append(
                {
                    "unit": unit_number,
                    "page": page_number,
                    "text": paragraph,
                }
            )

    chunks = []

    start = 0
    covered_until = 0

    while start < len(paragraphs):

        current = []
        current_length = 0
        end = start

        while end < len(paragraphs):

            text = paragraphs[end]["text"]
            new_length = current_length + len(text) + 2

            if (current and new_length > chunk_size):
                break

            current.append(paragraphs[end])
            current_length = new_length
            end += 1

        if not current:
            break

        # Skip chunks containing only overlap
        if end <= covered_until:
            start = covered_until
            continue

        pages = [
            item["page"]
            for item in current
            if item["page"] is not None
        ]

        chunks.append(
            {
                "chunk": len(chunks) + 1,
                "start_unit": current[0]["unit"],
                "end_unit": current[-1]["unit"],
                "start_page": pages[0] if pages else None,
                "end_page": pages[-1] if pages else None,
                "text": "\n\n".join(item["text"] for item in current),
            }
        )

        covered_until = end

        if end == len(paragraphs):
            break

        next_start = end - overlap_paragraphs
        start = max(next_start, start + 1)

    return chunks


if __name__ == "__main__":

    path =  DATA_DIR  / "raw" / "quality" / "QUA-INC-001_v3_2026.pdf"

    units = load_document(path)
    units = clean_units(units)
    chunks = chunk_units(units)

    for chunk in chunks:
        print("=" * 70)
        print(
            f"Chunk {chunk['chunk']} "
            f"| pages "
            f"{chunk['start_page']}-"
            f"{chunk['end_page']} "
            f"| chars "
            f"{len(chunk['text'])}"
        )
        print()
        print(chunk["text"])