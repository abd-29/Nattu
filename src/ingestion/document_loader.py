from pathlib import Path

import numpy as np
import pymupdf

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from rapidocr import RapidOCR

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}

MIN_TEXT_LENGTH = 20

_ocr_engine = None


def find_documents(directory: Path) -> list[Path]:
    """
    Find all supported documents recursively.
    """

    documents = []

    for path in directory.rglob("*"):

        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        documents.append(path)

    return sorted(documents)


def get_ocr_engine():
    """
    Load the OCR engine only when needed.
    """

    global _ocr_engine

    if _ocr_engine is None:
        _ocr_engine = RapidOCR()

    return _ocr_engine


def page_needs_ocr(page, text: str) -> bool:
    """
    Check whether a PDF page requires OCR.
    """

    text_is_empty = len(text.strip()) < MIN_TEXT_LENGTH

    has_images = bool(page.get_images(full=True))

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


def extract_pdf_units(path: Path) -> list[dict]:
    """
    Extract text units from a PDF document.
    """

    document = pymupdf.open(path)

    units = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text( "text", sort=True)

        if page_needs_ocr(page, text):
            text = extract_page_with_ocr(page)

        units.append(
            {
                "unit": page_number,
                "page": page_number,
                "text": text,
            }
        )

    document.close()

    return units


def extract_table_text(table: Table) -> str:
    """
    Extract text from a DOCX table.
    """

    rows = []

    for row in table.rows:

        cells = [
            cell.text.strip()
            for cell in row.cells
        ]

        rows.append(" | ".join(cells))

    return "\n".join(rows)


def extract_docx_units(path: Path) -> list[dict]:
    """
    Extract text units from a DOCX document.
    """

    document = Document(path)
    texts = []

    for element in document.iter_inner_content():

        if isinstance(element, Paragraph):

            text = element.text.strip()

            if text:
                texts.append(text)

        elif isinstance(element, Table):

            table_text = extract_table_text(element)

            if table_text:
                texts.append(table_text)

    return [
        {
            "unit": 1,
            "page": None,
            "text": "\n\n".join(texts),
        }
    ]


def extract_text_units(path: Path) -> list[dict]:
    """
    Extract text units from TXT or Markdown.
    """

    text = path.read_text(encoding="utf-8")

    return [
        {
            "unit": 1,
            "page": None,
            "text": text,
        }
    ]


def load_document(path: Path) -> list[dict]:
    """
    Load a document according to its format.
    """

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_units(path)

    if suffix == ".docx":
        return extract_docx_units(path)

    if suffix in {
        ".md",
        ".txt",
    }:
        return extract_text_units(path)

    raise ValueError(f"Unsupported file type: {suffix}")