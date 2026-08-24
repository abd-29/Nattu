def chunk_text(
    text: str,
    chunk_size: int = 500,
) -> list[str]:
    """
    Split text into chunks while preserving paragraphs.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = []

    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        if (current_chunk
            and current_length + paragraph_length > chunk_size):

            chunks.append("\n\n".join(current_chunk))

            current_chunk = []
            current_length = 0

        current_chunk.append(paragraph)

        current_length += paragraph_length + 2

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks




def chunk_pages(
    pages: list[dict],
    chunk_size: int = 500,
    overlap_paragraphs: int = 1,
) -> list[dict]:
    """
    Split document pages into continuous chunks
    with paragraph overlap.
    """

    paragraphs = []

    for page in pages:
        page_number = page["page"]

        page_paragraphs = [
            paragraph.strip()
            for paragraph in page["text"].split("\n\n")
            if (
                paragraph.strip() and paragraph.strip() != str(page_number)
            )
        ]

        for paragraph in page_paragraphs:
            paragraphs.append(
                {
                    "page": page_number,
                    "text": paragraph,
                }
            )

    chunks = []

    start = 0

    while start < len(paragraphs):
        current = []
        current_length = 0
        end = start

        while end < len(paragraphs):
            text = paragraphs[end]["text"]

            new_length = (
                current_length
                + len(text)
                + 2
            )

            if current and new_length > chunk_size:
                break

            current.append(paragraphs[end])
            current_length = new_length
            end += 1

        chunks.append(
            {
                "chunk": len(chunks) + 1,
                "start_page": current[0]["page"],
                "end_page": current[-1]["page"],
                "text": "\n\n".join(
                    item["text"]
                    for item in current
                ),
            }
        )

        if end == len(paragraphs):
            break

        next_start = end - overlap_paragraphs

        start = max(next_start, start + 1)

    return chunks





if __name__ == "__main__":

    from config import DATA_DIR
    from src.ingestion.pdf_loader import extract_pdf_pages

    pdf_path = (
        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-INC-001_v3.pdf"
    )

    pages = extract_pdf_pages(pdf_path)

    chunks = chunk_pages(pages=pages, chunk_size=500, overlap_paragraphs=1)

    for item in chunks:
        print(
            f"Chunk {item['chunk']} "
            f"| Pages {item['start_page']}-{item['end_page']} "
            f"| {len(item['text'])} chars"
        )

        print(item["text"])
        print("-" * 50)
