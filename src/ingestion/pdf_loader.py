from pathlib import Path

import numpy as np

from config import DATA_DIR

import pymupdf
from rapidocr import RapidOCR


_ocr_engine = None


def get_ocr_engine():
    """
    Load the OCR engine only when needed.
    """

    global _ocr_engine

    if _ocr_engine is None:
        _ocr_engine = RapidOCR()

    return _ocr_engine

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

    pixmap = page.get_pixmap(dpi=300)
    image = np.frombuffer(pixmap.samples, dtype=np.uint8)
    image = image.reshape(pixmap.height, pixmap.width, pixmap.n)

    ocr_engine = get_ocr_engine()
    result = ocr_engine(image)

    if not result.txts:
        return ""

    return "\n".join(result.txts)




if __name__ == "__main__":

    pdf_path = (
        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-LEGACY-016_scan_2019.pdf"
    )

    print(pdf_path)
    pages = extract_pdf_units(pdf_path)

    for page in pages:
        print(f"\n--- PAGE {page['page']} ---")
        print(page["text"])