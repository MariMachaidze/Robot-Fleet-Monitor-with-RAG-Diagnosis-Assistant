"""Tests for the knowledge base: the validator, the front-matter parser, and the
deliberate "mess" that the retrieval and agent evals rely on."""

import re
from pathlib import Path

import pytest

from erp_mock.db import SEED_SPARE_PARTS
from kb.documents import Document, load_documents, split_front_matter
from kb.validate_docs import check_collection, check_document

DOCS = load_documents()
BY_ID = {doc.meta["doc_id"]: doc for doc in DOCS}
ALL_TEXT = "\n".join(doc.body for doc in DOCS)


# ---------- Validation ----------


def test_every_document_passes_validation():
    problems = {doc.path.name: check_document(doc) for doc in DOCS}
    assert {name: found for name, found in problems.items() if found} == {}
    assert check_collection(DOCS) == []


def test_validator_reports_a_broken_document():
    broken = Document(path=Path("x.md"), meta={"doc_type": "incident_report"}, title="", body="")
    problems = " ".join(check_document(broken))
    for expected in ("doc_id", "robot_model", "last_updated", "error_code", "title", "numbered"):
        assert expected in problems


def test_front_matter_values_stay_strings():
    meta, body = split_front_matter("---\nfirmware: 1.4\nlast_updated: 2025-06-02\n---\n# T\nx")
    assert meta == {"firmware": "1.4", "last_updated": "2025-06-02"}
    assert body == "# T\nx"


def test_missing_front_matter_is_rejected():
    with pytest.raises(ValueError):
        split_front_matter("# No front-matter here")


# ---------- The planned mess (the evals depend on it) ----------


def test_e42_is_spelled_three_ways():
    assert "E42" in ALL_TEXT
    assert "E-42" in ALL_TEXT
    assert "error 42" in ALL_TEXT


def test_e42_has_a_different_fix_per_model():
    guide = BY_ID["TG-E42"].body
    assert "## Fix for AMR-100" in guide and "## Fix for AMR-200" in guide
    assert "SP-1001" in BY_ID["ECR-100"].body  # AMR-100: replace the motor
    assert "encoder cable" in BY_ID["ECR-200"].body  # AMR-200: reseat the encoder cable


def test_outdated_procedure_is_superseded_by_a_newer_document():
    old, new = BY_ID["OP-02"], BY_ID["RN-FW14"]
    assert old.meta["last_updated"] < new.meta["last_updated"]
    assert "OP-02" in new.body and "outdated" in new.body


def test_one_document_has_inconsistent_headings():
    schedule = BY_ID["MS-100"].body
    assert "#### WEEKLY" in schedule  # wrong level, all caps
    assert "**Monthly tasks**" in schedule  # bold text instead of a heading
    assert "Yearly\n------" in schedule  # underline-style heading


def test_unknown_code_e99_is_not_in_the_knowledge_base():
    assert "E99" not in ALL_TEXT and "E-99" not in ALL_TEXT  # agent scenario 5 needs this


def test_part_numbers_exist_in_the_erp_for_the_right_model():
    erp_models = {part_id: model for part_id, _, model, *_ in SEED_SPARE_PARTS}
    for doc in DOCS:
        for part_id in set(re.findall(r"SP-\d{4}", doc.body)):
            assert part_id in erp_models, f"{doc.meta['doc_id']} cites unknown part {part_id}"
            if doc.meta["robot_model"] != "all":
                assert erp_models[part_id] == doc.meta["robot_model"], (
                    f"{doc.meta['doc_id']} cites {part_id}, which fits {erp_models[part_id]}"
                )
