from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

def extract_table_text(table: Table) -> str:
    """
    Convert a DOCX table into text.
    """

    rows = []

    for row in table.rows:
        cells = [
            cell.text.strip()
            for cell in row.cells
        ]

        rows.append(" | ".join(cells)
        )

    return "\n".join(rows)


def extract_docx_units(path: Path) -> list[dict]:
    """
    Extract text from a DOCX file.
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
            "text": "\n\n".join(texts)
        }
    ]