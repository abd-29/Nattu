import re


def clean_line(
    line: str,
) -> str:
    """
    Remove simple formatting characters from a line.
    """

    line = line.strip()
    line = line.replace("**", "")
    line = line.lstrip("#")

    return line.strip()


def extract_field(
    lines: list[str],
    labels: list[str],
) -> str | None:
    """
    Extract a metadata field from document lines.
    """

    for label in labels:

        pattern = re.compile(
            rf"^{re.escape(label)}\s*:\s*(.+)$",
            re.IGNORECASE,
        )

        for line in lines:

            cleaned_line = clean_line(
                line
            )

            match = pattern.match(
                cleaned_line
            )

            if match:
                return match.group(1).strip()

    return None


def normalize_department(
    value: str | None,
) -> str | None:
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

    return mapping.get(
        value.lower(),
        value.lower(),
    )


def normalize_status(
    value: str | None,
) -> str | None:
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

    return mapping.get(
        value.lower(),
        value.lower(),
    )


def normalize_language(
    value: str | None,
) -> str | None:
    """
    Normalize document language.
    """

    if value is None:
        return None

    return value.lower()


def extract_metadata(
    units: list[dict],
) -> dict:
    """
    Extract metadata from loaded document units.
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

    title = clean_line(
        lines[0]
    )

    document_id = extract_field(
        lines,
        ["Référence"],
    )

    version = extract_field(
        lines,
        ["Version"],
    )

    document_date = extract_field(
        lines,
        [
            "Date d'application",
            "Date",
        ],
    )

    department = extract_field(
        lines,
        ["Département"],
    )

    classification = extract_field(
        lines,
        ["Classification"],
    )

    status = extract_field(
        lines,
        ["Statut"],
    )

    language = extract_field(
        lines,
        ["Langue"],
    )

    return {
        "document_id": document_id,
        "title": title,
        "version": version,
        "date": document_date,
        "department": normalize_department(
            department
        ),
        "classification": (
            classification.lower()
            if classification
            else None
        ),
        "status": normalize_status(
            status
        ),
        "language": normalize_language(
            language
        ),
    }


if __name__ == "__main__":

    from config import DATA_DIR

    from src.ingestion.document_loader import (
        load_document,
    )

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
    ]

    for path in test_documents:

        units = load_document(
            path
        )

        metadata = extract_metadata(
            units
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