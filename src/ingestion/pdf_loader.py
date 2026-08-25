from pathlib import Path
from config import DATA_DIR

import pymupdf


def extract_pdf_units(path: Path) -> list[dict]:
    """
    Extract PDF content page by page.
    Use OCR when necessary.
    """

    document = pymupdf.open(path)

    units = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text", sort = True)
        needs_ocr = page_needs_ocr(page, text)

        if needs_ocr:
            text = extract_page_with_ocr(page)

        print(f"Page {page_number} " f"| OCR required: {needs_ocr}")

        units.append(
            {
                "unit": page_number,
                "page": page_number,
                "text": text,
            }
        )

    document.close()

    return units


def page_needs_ocr(page, text: str) -> bool:
    """
    Check whether a PDF page probably requires OCR.
    """

    text_is_empty = len(text.strip()) < 20  #MIN_TEXT_LENGTH


    has_images = bool(
        page.get_images(full=True)
    )

    return text_is_empty and has_images


def extract_page_with_ocr(page) -> str:
    """
    Extract text from a PDF page using OCR.
    """

    text_page = page.get_textpage_ocr(
        language="fra+eng",
        dpi=300,
        full=True,
    )

    return page.get_text(
        "text",
        textpage=text_page,
        sort=True,
    )



if __name__ == "__main__":

    pdf_path = (
        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-INC-001_v3.pdf"
    )

    pages = extract_pdf_units(pdf_path)

    for page in pages:
        print(f"\n--- PAGE {page['page']} ---")
        print(page["text"])