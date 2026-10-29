"""Build the Chroma search index from kb/docs:  python -m kb.build_index  (Stage 4, step 5)

Step 5a: chunk_metadata() makes the label card stored with every chunk.
Step 5b: build_collection() turns chunks into vectors and saves them in Chroma.
Step 5c: build_index() and main() run it for all 20 manuals.
"""

from pathlib import Path

import chromadb
from chromadb.api import ClientAPI
from chromadb.errors import NotFoundError

from kb.chunking import Chunk, chunk_fixed
from kb.documents import DOCS_DIR, Document, load_documents
from kb.retrieval import EMBEDDING_MODEL, INDEX_DIR, get_model

COLLECTION = "fixed_chunks"  # the baseline collection; Stage 5 adds more


def chunk_metadata(doc: Document, chunk: Chunk) -> dict[str, str]:
    """The label card stored next to each chunk in the index.

    It is used to cite sources now, and to filter by robot model and error code in Stage 5.
    """
    return {
        "doc_id": doc.meta["doc_id"],
        "doc_title": doc.title,
        "doc_type": doc.meta["doc_type"],
        "robot_model": doc.meta["robot_model"],
        "firmware": doc.meta["firmware"],
        "error_code": doc.meta.get("error_code", ""),  # "" = this manual is not about one code
        "section_title": chunk.section_title,
        "last_updated": doc.meta["last_updated"],
    }


def build_collection(client: ClientAPI, name: str, docs: list[Document]) -> int:
    """(Re)create one Chroma collection from the documents; returns how many chunks it holds."""
    # Start fresh, so the index always matches the documents exactly.
    try:
        client.delete_collection(name)
    except NotFoundError:
        pass  # nothing to delete on the very first build

    collection = client.create_collection(
        name,
        configuration={"hnsw": {"space": "cosine"}},  # compare vectors by cosine similarity
        embedding_function=None,  # we bring our own vectors from bge
        metadata={"embedding_model": EMBEDDING_MODEL},  # remembered, checked at search time
    )

    ids: list[str] = []
    texts: list[str] = []
    metadatas: list[dict[str, str]] = []
    for doc in docs:
        for i, chunk in enumerate(chunk_fixed(doc)):
            ids.append(f"{doc.meta['doc_id']}#{i}")  # a unique name, e.g. "TG-E42#3"
            texts.append(chunk.text)
            metadatas.append(chunk_metadata(doc, chunk))

    vectors = get_model().encode_document(texts)  # all texts -> fingerprints, in one go
    collection.add(ids=ids, documents=texts, embeddings=vectors, metadatas=metadatas)
    return len(ids)


def build_index(index_dir: Path = INDEX_DIR, docs_dir: Path = DOCS_DIR) -> int:
    """Load all manuals and build the real index on disk; returns how many chunks it holds."""
    docs = load_documents(docs_dir)
    client = chromadb.PersistentClient(path=str(index_dir))  # opens (or creates) the folder
    return build_collection(client, COLLECTION, docs)


def main() -> None:
    count = build_index()
    print(f"{COLLECTION}: {count} chunks")
    print(f"Index written to {INDEX_DIR} (embedding model {EMBEDDING_MODEL})")


if __name__ == "__main__":
    main()  # runs only for "python -m kb.build_index", not when another file imports this one
