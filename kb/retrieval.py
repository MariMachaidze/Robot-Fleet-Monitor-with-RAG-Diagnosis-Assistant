"""Search the knowledge base (Stage 4, built step by step).

Step 4: get_model() loads the local embedding model once.
Step 5: INDEX_DIR says where the search index lives on disk.
Step 6a: get_collection() opens the index and checks it matches our model.
Step 6b: to_hit() shapes one search result.
Step 6c: search() finds the k pieces closest in meaning to a question.
"""

import os
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

# Which embedding model to use. An environment variable can swap it without code changes.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# Folder of the Chroma index (git-ignored). Docker can point it elsewhere with KB_INDEX_DIR.
INDEX_DIR = Path(os.getenv("KB_INDEX_DIR", str(Path(__file__).parent / "chroma_db")))

# Strategy name -> the Chroma collection it searches. Stage 5 adds more strategies.
STRATEGIES: dict[str, str] = {"baseline": "fixed_chunks"}


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the embedding model the first time; later calls get the same loaded model."""
    return SentenceTransformer(EMBEDDING_MODEL, device="cpu")


def get_collection(name: str, index_dir: Path = INDEX_DIR) -> Collection:
    """Open one collection of the index, with a clear message if it is missing or outdated."""
    client = chromadb.PersistentClient(path=str(index_dir))
    try:
        collection = client.get_collection(name, embedding_function=None)
    except NotFoundError:
        # "from None" hides Chroma's long error, so the reader sees only the fix.
        raise RuntimeError(
            f"Search index '{name}' not found in {index_dir}. Run: python -m kb.build_index"
        ) from None

    # Read the sticky note from build time. Fingerprints from two different models
    # cannot be compared, so searching would quietly return nonsense.
    built_with = (collection.metadata or {}).get("embedding_model")
    if built_with != EMBEDDING_MODEL:
        raise RuntimeError(
            f"Index was built with '{built_with}' but EMBEDDING_MODEL is '{EMBEDDING_MODEL}'. "
            "Rebuild it: python -m kb.build_index"
        )
    return collection


def to_hit(text: str, meta: dict, distance: float) -> dict:
    """Turn one Chroma result into the shape the rest of the project uses."""
    return {
        "doc_id": meta["doc_id"],
        "doc_title": meta["doc_title"],
        "section_title": meta["section_title"],
        "text": text,
        # Chroma gives cosine DISTANCE (0 = identical). We want similarity: higher = closer.
        "score": round(1.0 - distance, 4),
    }


def search(
    query: str,
    k: int = 3,
    robot_model: str | None = None,
    error_code: str | None = None,
    strategy: str = "baseline",
    index_dir: Path = INDEX_DIR,
) -> list[dict]:
    """Return the k pieces closest in meaning to the query, best first.

    The baseline ignores robot_model and error_code on purpose (meaning only);
    the Stage 5 strategies use them as filters.
    """
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy '{strategy}'. Choose one of: {', '.join(STRATEGIES)}")
    collection = get_collection(STRATEGIES[strategy], index_dir)

    query_vector = get_model().encode_query([query])  # the question gets a fingerprint too
    result = collection.query(
        query_embeddings=query_vector,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    # Chroma can answer many questions at once, so every field is a list per question.
    # We asked one question, so we take item [0] of each.
    hits: list[dict] = []
    for text, meta, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0], strict=True
    ):
        hits.append(to_hit(text, meta, distance))
    return hits
