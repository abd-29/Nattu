from pathlib import Path

from src.ingestion.docx_loader import extract_docx_units
from src.ingestion.pdf_loader import extract_pdf_units
from src.ingestion.text_loader import extract_text_units

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".md",
    ".txt",
}


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


def load_document(path: Path) -> list[dict]:
    """
    Load a document according to its file type.
    """

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_units(path)

    if suffix == ".docx":
        return extract_docx_units(path)

    if suffix in {".md", ".txt"}:
        return extract_text_units(path)

    raise ValueError(
        f"Unsupported file type: {suffix}"
    )


if __name__ == "__main__":

    from config import DATA_DIR

    raw_data_dir = DATA_DIR / "raw"

    test_documents = [
        raw_data_dir / "quality" / "QUA-INC-001_v3_2026.pdf",
        raw_data_dir / "products" / "PRD-ALP-INST_3-1.docx",
        raw_data_dir / "products" / "PRD-ALP-MAINT_2-0.md",
        raw_data_dir / "support"  / "CASE-ACME-001_1-0.txt",
        raw_data_dir / "quality" / "QUA-LEGACY-016_scan_2019.pdf",
    ]

    for path in test_documents:

        units = load_document(path)

        print("=" * 70)
        print(f"Document: {path.name}")
        print(f"Number of units: {len(units)}")

        for unit in units:
            print(
                f"Unit: {unit['unit']} "
                f"| Page: {unit['page']}"
            )

            print(unit["text"][:500])

        print()