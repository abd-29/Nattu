import re
from datetime import datetime
from pathlib import Path

from config import DATA_DIR, FRENCH_MONTHS

from src.ingestion.document_loader import load_document
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

def clean_line(line: str) -> str:
    """
    Remove simple formatting characters from a line.
    """

    line = line.strip()
    line = line.replace("**", "")
    line = line.lstrip("#")

    return line.strip()


def extract_field(lines: list[str], labels: list[str]) -> str | None:
    """
    Extract a metadata field from document lines.
    """

    for label in labels:
        pattern = re.compile(rf"^{re.escape(label)}\s*:\s*(.+)$", re.IGNORECASE)

        for line in lines:
            cleaned_line = clean_line(line)
            match = pattern.match(cleaned_line)

            if match:
                return match.group(1).strip()

    return None


def normalize_department(value: str | None) -> str | None:
    """
    Normalize department names.
    """

    if value is None:
        return None

    mapping = {
        "quality": "quality",
        "produits": "products",
        "support": "support",
        "ressources humaines": "hr",
    }

    return mapping.get(value.lower(), value.lower())


def normalize_status(value: str | None) -> str | None:
    """
    Normalize document status.
    """

    if value is None:
        return None

    mapping = {
        "en vigueur": "active",
        "obsolète": "obsolete",
        "brouillon": "draft",
        "archivé": "archived",
    }

    return mapping.get(value.lower(), value.lower())


def normalize_language(value: str | None) -> str | None:
    """
    Normalize document language.
    """

    if value is None:
        return None

    return value.lower()


def extract_header_identity(line: str) -> tuple[str | None, str]:
    """
    Extract document ID and title from the first line.
    """

    cleaned_line = clean_line(line)

    pattern = re.compile(
        r"^([A-Z0-9]+(?:-[A-Z0-9]+)+)"
        r"\s*[—–-]\s*"
        r"(.+)$"
    )

    match = pattern.match(cleaned_line)

    if not match:
        return None, cleaned_line

    document_id = match.group(1)
    title = match.group(2).strip()

    return document_id, title


def normalize_date(value: str | None) -> str | None:
    """
    Normalize document dates to YYYY-MM-DD.
    """

    if value is None:
        return None

    value = value.strip()

    try:
        return datetime.strptime(value, "%Y-%m-%d",).date().isoformat()
    except ValueError:
        pass

    parts = value.lower().split()

    if len(parts) == 3:
        day, month, year = parts
        month_number = FRENCH_MONTHS.get(month)

        if month_number:

            return (
                f"{year}-"
                f"{month_number}-"
                f"{int(day):02d}"
            )

    return value


def normalize_classification(value: str | None) -> str | None:
    """
    Normalize document classification.
    """
    if value is None:
        return None

    return value.lower()

def detect_language(text: str) -> str | None:
    """
    Detect document language from text.
    """

    if not text.strip():
        return None

    try:
        return detect(text)

    except LangDetectException:
        return None


def infer_status_from_text(text: str) -> str | None:
    """
    Infer document status from explicit textual evidence.
    """

    normalized_text = text.lower()

    archived_markers = [
        "archivé",
        "archivée",
        "archivee",
        "ne doit plus être utilisé",
        "ne doit plus etre utilise",
    ]

    for marker in archived_markers:

        if marker in normalized_text:
            return "archived"

    return None

def extract_metadata(
    units: list[dict],
    path: Path | None = None,
    raw_data_dir: Path | None = None,
) -> dict:
    """
    Extract metadata from document content and file path.
    """

    if not units:
        return {}

    text = units[0]["text"]

    lines = [
        line
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return {}

    header_document_id, title = extract_header_identity(lines[0])
    document_id = extract_field(lines,["Référence"])

    if document_id is None:
        document_id = header_document_id

    version = extract_field(lines,["Version"],)
    document_date = extract_field(lines,[ "Date d'application", "Date"])
    department = extract_field(lines, ["Département"])
    classification = extract_field(lines,["Classification"],)
    status = extract_field(lines,["Statut"])

    if status is None:
        status = infer_status_from_text(text)

    language = extract_field(lines,["Langue"])

    if language is None:
        language = detect_language(text)

    source = None
    filename = None
    extension = None

    if path is not None:
        filename = path.name
        extension = path.suffix.lower()

        if raw_data_dir is not None:
            relative_path = path.relative_to(raw_data_dir)

            source = relative_path.as_posix()

            if department is None:
                department = relative_path.parts[0]

    return {
        "document_id": document_id,
        "title": title,
        "version": version,
        "department": normalize_department(department),
        "classification": normalize_classification(classification),
        "status": normalize_status(status),
        "language": normalize_language(language),
        "date": normalize_date(document_date),
        "source": source,
        "filename": filename,
        "extension": extension,
    }

if __name__ == "__main__":

    test_documents = [
        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-INC-001_v3_2026.pdf",

        DATA_DIR
        / "raw"
        / "products"
        / "PRD-ALP-INST_3-1.docx",

        DATA_DIR
        / "raw"
        / "products"
        / "PRD-ALP-MAINT_2-0.md",

        DATA_DIR
        / "raw"
        / "support"
        / "CASE-ACME-001_1-0.txt",

        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-LEGACY-016_scan_2019.pdf",

        DATA_DIR
        / "raw"
        / "quality"
        / "QUA-INC-001_v3.pdf",
    ]

    for path in test_documents:

        units = load_document(
            path
        )

        metadata = extract_metadata(
            units=units,
            path=path,
            raw_data_dir=DATA_DIR / "raw",
        )

        print(
            path.name
        )

        print(
            metadata
        )

        print(
            "-" * 60
        )