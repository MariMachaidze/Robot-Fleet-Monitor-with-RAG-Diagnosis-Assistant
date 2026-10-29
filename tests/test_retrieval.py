"""Checker for kb/retrieval.py.

Step 4:   .venv/bin/pytest tests/test_retrieval.py -k step4 -v
Step 6a:  .venv/bin/pytest tests/test_retrieval.py -k step6a -v
Step 6b:  .venv/bin/pytest tests/test_retrieval.py -k step6b -v
Step 6c:  .venv/bin/pytest tests/test_retrieval.py -k step6c -v
"""

import chromadb
import pytest

from kb import retrieval
from kb.build_index import build_index
from kb.retrieval import get_collection, get_model, search, to_hit


def test_step4_model_is_loaded_only_once():
    assert get_model() is get_model()  # "is" = the very same object, not a second copy


def test_step4_model_makes_384_number_fingerprints():
    vector = get_model().encode_query(["wheel motor stalled"])[0]
    assert len(vector) == 384


def make_empty_collection(folder, built_with: str) -> None:
    """A tiny fake index: one empty collection with a sticky note naming its model."""
    client = chromadb.PersistentClient(path=str(folder))
    client.create_collection(
        "fixed_chunks", embedding_function=None, metadata={"embedding_model": built_with}
    )


def test_step6a_opens_an_index_built_with_our_model(tmp_path):
    make_empty_collection(tmp_path, built_with=retrieval.EMBEDDING_MODEL)
    assert get_collection("fixed_chunks", index_dir=tmp_path).name == "fixed_chunks"


def test_step6a_missing_index_says_how_to_build_it(tmp_path):
    # pytest.raises = "this line MUST fail with this error, or the test fails"
    with pytest.raises(RuntimeError, match="python -m kb.build_index"):
        get_collection("fixed_chunks", index_dir=tmp_path / "empty")


def test_step6a_index_from_another_model_is_refused(tmp_path):
    make_empty_collection(tmp_path, built_with="some/other-model")
    with pytest.raises(RuntimeError, match="Rebuild"):
        get_collection("fixed_chunks", index_dir=tmp_path)


def test_step6b_hit_has_the_five_fields_and_a_similarity_score():
    meta = {
        "doc_id": "TG-E42",
        "doc_title": "Troubleshooting Guide: Wheel Motor Stall (E42)",
        "section_title": "Fix for AMR-100",
        "robot_model": "all",  # extra label-card fields are left out of the hit
    }
    assert to_hit("Reset the motor controller...", meta, distance=0.25) == {
        "doc_id": "TG-E42",
        "doc_title": "Troubleshooting Guide: Wheel Motor Stall (E42)",
        "section_title": "Fix for AMR-100",
        "text": "Reset the motor controller...",
        "score": 0.75,  # distance 0.25 -> similarity 0.75
    }


def test_step6b_score_is_rounded_to_4_decimals():
    meta = {"doc_id": "x", "doc_title": "x", "section_title": "x"}
    assert to_hit("x", meta, distance=0.123456789)["score"] == 0.8765


@pytest.fixture(scope="module")
def index_dir(tmp_path_factory):
    """Build one real index of all 20 manuals in a throwaway folder, shared by the 6c tests."""
    folder = tmp_path_factory.mktemp("chroma")
    build_index(index_dir=folder)
    return folder


def test_step6c_returns_k_hits_best_first(index_dir):
    hits = search("wheel motor stalled", k=3, index_dir=index_dir)
    assert len(hits) == 3
    scores = [hit["score"] for hit in hits]
    assert scores == sorted(scores, reverse=True)  # best first
    assert all(0 < score <= 1 for score in scores)


def test_step6c_k_controls_how_many_come_back(index_dir):
    assert len(search("battery", k=1, index_dir=index_dir)) == 1


def test_step6c_finds_the_obvious_manual(index_dir):
    hits = search("How do I restart a robot after the emergency stop?", index_dir=index_dir)
    assert "OP-01" in [hit["doc_id"] for hit in hits]


def test_step6c_unknown_strategy_is_rejected(index_dir):
    with pytest.raises(ValueError, match="Unknown strategy"):
        search("anything", strategy="magic", index_dir=index_dir)
