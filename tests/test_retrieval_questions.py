"""Checker for evals/retrieval_questions.json (Stage 4, step 7).

Step 7:  .venv/bin/pytest tests/test_retrieval_questions.py -v

A wrong answer key would grade the search unfairly, so these tests check the key itself.
"""

import json
from collections import Counter
from pathlib import Path

from kb.chunking import parse_sections
from kb.documents import load_documents

QUESTIONS = json.loads(Path("evals/retrieval_questions.json").read_text(encoding="utf-8"))
DOCS = {doc.meta["doc_id"]: doc for doc in load_documents()}


def test_step7_has_30_questions_in_the_planned_mix():
    assert len(QUESTIONS) == 30
    assert len({q["id"] for q in QUESTIONS}) == 30  # every id is unique
    assert Counter(q["type"] for q in QUESTIONS) == {
        "error_code": 12,
        "symptom": 8,
        "procedure": 5,
        "tricky": 5,
    }


def test_step7_every_question_has_1_to_3_accepted_answers():
    for q in QUESTIONS:
        assert 1 <= len(q["expected"]) <= 3, q["id"]


def test_step7_every_accepted_answer_really_exists_in_the_manuals():
    for q in QUESTIONS:
        for answer in q["expected"]:
            doc = DOCS[answer["doc_id"]]  # KeyError here = a manual that does not exist
            headings = {section.title for section in parse_sections(doc.body, doc.title)}
            if answer["section_title"] in headings:
                continue
            # The only allowed exception: a section the '#' parser cannot see (MS-100's
            # bold heading). Such a question must say so in a "note".
            assert "note" in q and answer["section_title"] in doc.body, (q["id"], answer)
