"""Checker for kb/build_index.py.

Step 5a:  .venv/bin/pytest tests/test_build_index.py -k step5a -v
Step 5b:  .venv/bin/pytest tests/test_build_index.py -k step5b -v
Step 5c:  .venv/bin/pytest tests/test_build_index.py -k step5c -v
"""

import chromadb

from kb.build_index import COLLECTION, build_collection, build_index, chunk_metadata
from kb.chunking import chunk_fixed
from kb.documents import load_documents

DOCS = {doc.meta["doc_id"]: doc for doc in load_documents()}


def test_step5a_label_card_has_the_eight_fields():
    guide = DOCS["TG-E42"]
    first_chunk = chunk_fixed(guide)[0]
    assert chunk_metadata(guide, first_chunk) == {
        "doc_id": "TG-E42",
        "doc_title": "Troubleshooting Guide: Wheel Motor Stall (E42)",
        "doc_type": "troubleshooting_guide",
        "robot_model": "all",
        "firmware": "all",
        "error_code": "E42",
        "section_title": "Symptoms",
        "last_updated": "2025-12-01",
    }


def test_step5a_manual_without_an_error_code_gets_empty_text():
    reference = DOCS["ECR-100"]  # covers all six codes, so its label card has no error_code
    assert chunk_metadata(reference, chunk_fixed(reference)[0])["error_code"] == ""


def test_step5b_collection_holds_every_chunk_with_its_label_card(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path))  # a throwaway index folder
    expected = sum(len(chunk_fixed(doc)) for doc in DOCS.values())

    assert build_collection(client, "fixed_chunks", list(DOCS.values())) == expected
    collection = client.get_collection("fixed_chunks", embedding_function=None)
    assert collection.count() == expected
    assert collection.metadata["embedding_model"] == "BAAI/bge-small-en-v1.5"

    first = collection.get(ids=["TG-E42#0"], include=["documents", "metadatas"])
    assert first["documents"][0].startswith("# Troubleshooting Guide: Wheel Motor Stall")
    assert first["metadatas"][0]["section_title"] == "Symptoms"


def test_step5b_rebuilding_replaces_instead_of_doubling(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path))
    docs = [DOCS["TG-E42"]]
    build_collection(client, "fixed_chunks", docs)
    build_collection(client, "fixed_chunks", docs)  # second build must not add copies
    assert client.get_collection("fixed_chunks", embedding_function=None).count() == 5


def test_step5c_build_index_writes_all_manuals_to_disk(tmp_path):
    count = build_index(index_dir=tmp_path)
    assert count == sum(len(chunk_fixed(doc)) for doc in DOCS.values())

    # Open the folder again with a brand-new client: the pieces must still be there.
    reopened = chromadb.PersistentClient(path=str(tmp_path))
    assert reopened.get_collection(COLLECTION, embedding_function=None).count() == count
