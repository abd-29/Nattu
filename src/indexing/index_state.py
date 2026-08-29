import hashlib
import json

from collections import defaultdict
from pathlib import Path

from src.chunking.text_chunker import clean_units
from src.ingestion.document_loader import find_documents, load_document
from src.ingestion.manifest import compute_file_hash
from src.processing.metadata_extractor import extract_metadata



def compute_document_content_hash(units: list[dict]) -> str:
    """
    Compute a normalized hash from document text.
    """

    normalized_parts = []

    for unit in units:

        normalized_text = " ".join(
            unit["text"].split()
        ).lower()

        if normalized_text:
            normalized_parts.append(normalized_text)

    normalized_document = "\n".join(normalized_parts)

    return hashlib.sha256(
        normalized_document.encode("utf-8")
    ).hexdigest()


def build_document_state(path: Path, raw_data_dir: Path) -> dict:
    """
    Build the indexing state for one document.
    """

    units = load_document(path)

    units = clean_units(units)

    metadata = extract_metadata(
        units=units,
        path=path,
        raw_data_dir=raw_data_dir,
    )

    content_hash = compute_document_content_hash(units)

    return {
        "sha256": compute_file_hash(path),
        "document_id": metadata["document_id"],
        "version": metadata["version"],
        "content_hash": content_hash,
        "status": metadata["status"],
        "decision": None,
    }


def resolve_consistency(states: dict[str, dict]) -> dict[str, dict]:
    """
    Assign an indexing decision to each document.
    """

    resolved_states = {
        source: {
            **state,
        }
        for source, state in states.items()
    }

    identities = defaultdict(list)

    for source, state in resolved_states.items():

        identity = (
            state["document_id"],
            state["version"],
        )

        identities[identity].append(source)

    for sources in identities.values():

        hashes = defaultdict(list)

        for source in sources:

            content_hash = resolved_states[source]["content_hash"]

            hashes[content_hash].append(source)

        # Same identity but different content.
        if len(hashes) > 1:

            for source in sources:
                resolved_states[source]["decision"] = "conflict"
            continue

        # Same identity and same content:
        # keep only one physical copy.
        sorted_sources = sorted(
            sources
        )

        canonical_source = sorted_sources[0]

        for source in sorted_sources:

            if source == canonical_source:
                decision = "indexable"
            else:
                decision = "duplicate"

            resolved_states[source]["decision"] = decision

    return resolved_states


def build_full_index_state(raw_data_dir: Path) -> dict[str, dict]:
    """
    Build indexing state for all documents.
    """

    documents = find_documents(raw_data_dir)

    states = {}

    for path in documents:

        source = path.relative_to(raw_data_dir).as_posix()

        states[source] = (
            build_document_state(
                path=path,
                raw_data_dir=raw_data_dir,
            )
        )

    return resolve_consistency(states)


def save_index_state(state: dict[str, dict], path: Path) -> None:
    """
    Save indexing state to JSON.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:

        json.dump(
            state,
            file,
            indent=2,
            ensure_ascii=False,
        )


def load_index_state(path: Path) -> dict[str, dict]:
    """
    Load indexing state from JSON.
    """

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":

    from config import DATA_DIR

    raw_data_dir = (
        DATA_DIR
        / "raw"
    )

    state_path = (
        DATA_DIR
        / "processed"
        / "index_state.json"
    )

    state = build_full_index_state(
        raw_data_dir
    )

    save_index_state(
        state=state,
        path=state_path,
    )

    counts = {
        "indexable": 0,
        "duplicate": 0,
        "conflict": 0,
    }

    for document_state in state.values():

        decision = document_state[
            "decision"
        ]

        counts[decision] += 1

    print(
        f"Documents: {len(state)}"
    )

    print(
        f"Indexable: {counts['indexable']}"
    )

    print(
        f"Duplicates: {counts['duplicate']}"
    )

    print(
        f"Conflicts: {counts['conflict']}"
    )