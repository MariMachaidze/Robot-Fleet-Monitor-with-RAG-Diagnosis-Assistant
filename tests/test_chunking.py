"""Checker for kb/chunking.py.

Step 1:  .venv/bin/pytest tests/test_chunking.py -k step1 -v
Step 2:  .venv/bin/pytest tests/test_chunking.py -k step2 -v
"""

from pathlib import Path

from kb.chunking import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    Section,
    chunk_fixed,
    fixed_windows,
    majority_section,
    parse_sections,
)
from kb.documents import Document, load_documents

DOCS = {doc.meta["doc_id"]: doc for doc in load_documents()}

BODY = """# Guide

Intro text.

## Symptoms

Robot stops.

### Details

More.
**Bold line**
Underlined
----------
Tail."""


# ---------- Step 1: parse_sections ----------


def test_step1_example_from_the_docstring():
    body = "# Guide\nIntro.\n## Steps\n1. Go"
    assert parse_sections(body, "Guide") == [Section("Guide", 0, 15), Section("Steps", 15, 29)]


def test_step1_every_hash_heading_starts_a_section():
    sections = parse_sections(BODY, "Guide")
    assert [s.title for s in sections] == ["Guide", "Symptoms", "Details"]


def test_step1_sections_cover_the_whole_body_without_gaps():
    sections = parse_sections(BODY, "Guide")
    assert sections[0].start == 0
    assert sections[-1].end == len(BODY)
    for before, after in zip(sections, sections[1:], strict=False):
        assert before.end == after.start


def test_step1_text_before_the_first_heading_is_named_after_the_document():
    sections = parse_sections("Preface.\n\n## Steps\n1. Go", "My Doc")
    assert [s.title for s in sections] == ["My Doc", "Steps"]


def test_step1_bold_and_underlined_lines_are_not_headings():
    details = parse_sections(BODY, "Guide")[-1]
    assert "**Bold line**" in BODY[details.start : details.end]
    assert "Underlined" in BODY[details.start : details.end]


def test_step1_real_documents():
    tg = DOCS["TG-E42"]
    assert [s.title for s in parse_sections(tg.body, tg.title)] == [
        "Troubleshooting Guide: Wheel Motor Stall (E42)",
        "Symptoms",
        "First steps (both models)",
        "Fix for AMR-100",
        "Fix for AMR-200",
        "Lessons from past incidents",
    ]
    ms = DOCS["MS-100"]  # the messy one: bold and underlined headings are invisible
    assert [s.title for s in parse_sections(ms.body, ms.title)] == [
        "AMR-100 Maintenance Schedule",
        "Daily checks",
        "WEEKLY",
        "Every 6 months:",
    ]


# ---------- Step 2: fixed windows and labels ----------


def test_step2_fixed_windows_overlap_and_cover_the_text():
    starts = fixed_windows("x" * 1200)
    assert starts == [0, 450, 900]
    assert all(
        b - a == CHUNK_SIZE - CHUNK_OVERLAP for a, b in zip(starts, starts[1:], strict=False)
    )


def test_step2_short_text_is_one_window():
    assert fixed_windows("short") == [0]


def test_step2_majority_section_picks_the_biggest_share():
    sections = [Section("A", 0, 100), Section("B", 100, 1000)]
    assert majority_section(sections, 0, 500) == "B"  # 100 chars of A, 400 of B
    assert majority_section(sections, 0, 150) == "A"  # 100 chars of A, 50 of B


def test_step2_chunks_are_labeled_with_their_majority_section():
    body = "## A\n" + "a" * 600 + "\n## B\n" + "b" * 300
    doc = Document(path=Path("x.md"), meta={}, title="X", body=body)
    labels = [chunk.section_title for chunk in chunk_fixed(doc)]
    assert labels[0] == "A" and labels[-1] == "B"


def test_step2_every_real_document_chunks_into_labeled_pieces():
    for doc in DOCS.values():
        titles = {s.title for s in parse_sections(doc.body, doc.title)}
        chunks = chunk_fixed(doc)
        assert chunks, doc.meta["doc_id"]
        assert all(len(c.text) <= CHUNK_SIZE for c in chunks)
        assert all(c.section_title in titles for c in chunks)
