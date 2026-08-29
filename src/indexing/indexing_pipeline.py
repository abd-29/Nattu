from pathlib import Path

from src.embeddings.embedding_model import embed_chunks, load_embedding_model
from src.indexing.index_state import build_full_index_state, load_index_state, save_index_state

from src.ingestion.manifest import build_manifest, compare_manifests, load_manifest, save_manifest
from src.processing.document_processor import process_document
from src.vectorstore.chunk_repository import delete_document_chunks, replace_document_chunks


def run_indexing_pipeline(raw_data_dir: Path, manifest_path: Path, index_state_path: Path) -> dict:
    """
    Incrementally index documents into the vector store.
    """

    previous_manifest = load_manifest(manifest_path)
    current_manifest = build_manifest(raw_data_dir)

    changes = compare_manifests(previous=previous_manifest, current=current_manifest)
    previous_state = load_index_state(index_state_path)

    has_changes = (
        changes["added"]
        or changes["modified"]
        or changes["deleted"]
    )

    # only when physical files changed.
    if has_changes:
        current_state = build_full_index_state(raw_data_dir)
    else:
        current_state = previous_state

    # Find documents that must be indexed.
    sources_to_process = []

    for source, current_document_state in current_state.items():

        if current_document_state["decision"] != "indexable":
            continue

        previous_document_state = previous_state.get(source)

        file_changed = (
            source in changes["added"]
            or source in changes["modified"]
        )

        became_indexable = (
            previous_document_state is None
            or previous_document_state["decision"]
            != "indexable"
        )

        if file_changed or became_indexable:
            sources_to_process.append(source)

    all_chunks = []
    failed = []

    # Process documents.
    for source in sources_to_process:

        path = raw_data_dir / source

        try:
            chunks = process_document(path=path, raw_data_dir=raw_data_dir)
            all_chunks.extend(chunks)
        except Exception as error:

            failed.append(
                {
                    "source": source,
                    "error": str(error),
                }
            )

    # if document processing failed.
    if failed:

        return {
            "changes": changes,
            "processed_chunks": 0,
            "failed": failed,
            "manifest_updated": False,
        }

    # Embed and store chunks.
    if all_chunks:

        model = load_embedding_model()
        embedded_chunks = embed_chunks(chunks=all_chunks, model=model)

        chunks_by_source = {}

        for chunk in embedded_chunks:
            source = chunk["source"]
            chunks_by_source.setdefault(
                source,
                [],
            ).append(chunk)

        for source, chunks in chunks_by_source.items():
            replace_document_chunks(source=source, chunks=chunks)

    # from the vector store.
    sources_to_delete = set(changes["deleted"])

    for source, previous_document_state in previous_state.items():

        if previous_document_state["decision"] != "indexable":
            continue

        current_document_state = current_state.get(source)

        became_non_indexable = (
            current_document_state is None
            or current_document_state["decision"]
            != "indexable"
        )

        if became_non_indexable:

            sources_to_delete.add(source)

    # or conflicting documents.
    for source in sources_to_delete:
        delete_document_chunks(source=source)

    # only after successful indexing.
    save_manifest(manifest=current_manifest, path=manifest_path)
    save_index_state(state=current_state, path=index_state_path)

    return {
        "changes": changes,
        "processed_chunks": len(all_chunks),
        "failed": [],
        "manifest_updated": True,
    }


if __name__ == "__main__":

    from config import DATA_DIR

    raw_data_dir =DATA_DIR / "raw"

    manifest_path = (
        DATA_DIR
        / "processed"
        / "index_manifest.json"
    )

    index_state_path = (
        DATA_DIR
        / "processed"
        / "index_state.json"
    )

    result = run_indexing_pipeline(
        raw_data_dir=raw_data_dir,
        manifest_path=manifest_path,
        index_state_path=index_state_path,
    )

    changes = result["changes"]

    print(f"Added: {len(changes['added'])}")
    print(f"Modified: {len(changes['modified'])}")
    print(f"Deleted: {len(changes['deleted'])}")
    print(f"Unchanged: {len(changes['unchanged'])}")

    print(
        f"Processed chunks: "
        f"{result['processed_chunks']}"
    )
    print(f"Failed: {len(result['failed'])}")
    print(
        f"Manifest updated: "
        f"{result['manifest_updated']}"
    )