from config import DATA_DIR

from src.ingestion.document_loader import find_documents, load_document


def audit_documents():
    """
    Check that all supported documents
    can be extracted successfully.
    """

    raw_data_dir = DATA_DIR / "raw"
    documents = find_documents(raw_data_dir)

    successful = 0
    failed = []
    empty = []

    for path in documents:

        try:
            units = load_document(path)
            text = "\n".join(unit["text"] for unit in units).strip()

            if not text:
                empty.append(path)
            else:
                successful += 1

        except Exception as error:

            failed.append(
                {
                    "path": path,
                    "error": str(error),
                }
            )

    print(f"Documents found: {len(documents)}")
    print(f"Successful: {successful}")
    print(f"Empty: {len(empty)}")
    print(f"Failed: {len(failed)}")

    if empty:

        print("\nEMPTY DOCUMENTS")

        for path in empty:
            print(path.relative_to(raw_data_dir))

    if failed:
        print("\nFAILED DOCUMENTS")

        for item in failed:
            print(item["path"].relative_to(raw_data_dir))
            print(item["error"])


if __name__ == "__main__":
    audit_documents()