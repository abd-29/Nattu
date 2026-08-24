from pathlib import Path
from config import DATA_DIR

import pymupdf


def extract_pdf_pages(path: Path) -> list[dict]:
    """
    Extract text page by page from a PDF file.
    """

    document = pymupdf.open(path)
    pages = []

    for page_number, page in enumerate(
        document,
        start=1,
    ):
        pages.append(
            {
                "page": page_number,
                "text": page.get_text("text", sort = True),
            }
        )

    document.close()

    return pages


if __name__ == "__main__":

    pdf_path = (
        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-INC-001_v3.pdf"
    )

    pages = extract_pdf_pages(pdf_path)

    for page in pages:
        print(
            f"\n--- PAGE {page['page']} ---"
        )
        print(page["text"])