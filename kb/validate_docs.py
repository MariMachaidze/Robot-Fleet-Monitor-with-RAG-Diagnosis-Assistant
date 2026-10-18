"""Validate the knowledge base:  python -m kb.validate_docs

Checks every document in kb/docs/ against the Stage 3 rules (complete front-matter,
length, headings, numbered steps) and the collection as a whole (20 documents in the
planned mix, unique ids). Prints a report and exits with code 1 if any check fails,
so it can also run in CI.
"""

import re
import sys
from collections import Counter
from datetime import date

from kb.documents import Document, load_documents

REQUIRED_FIELDS = ("doc_id", "doc_type", "robot_model", "firmware", "last_updated")
# error_code is required only for documents about one specific fault.
NEEDS_ERROR_CODE = {"troubleshooting_guide", "incident_report"}
EXPECTED_COUNTS = {
    "error_code_reference": 2,
    "troubleshooting_guide": 6,
    "operating_procedure": 4,
    "maintenance_schedule": 2,
    "release_notes": 2,
    "incident_report": 4,
}
ROBOT_MODELS = {"AMR-100", "AMR-200", "all"}
MIN_WORDS, MAX_WORDS = 250, 450
CANONICAL_CODE = re.compile(r"E\d{2}")


def word_count(text: str) -> int:
    """Count words; joined tokens such as SP-1001, E-42 or 0.5 count as one word."""
    return len(re.findall(r"[A-Za-z0-9]+(?:['.-][A-Za-z0-9]+)*", text))


def check_document(doc: Document) -> list[str]:
    """Return the problems found in one document (empty list = valid)."""
    problems = [f"missing front-matter field '{f}'" for f in REQUIRED_FIELDS if not doc.meta.get(f)]

    doc_type = doc.meta.get("doc_type", "")
    if doc_type and doc_type not in EXPECTED_COUNTS:
        problems.append(f"unknown doc_type '{doc_type}'")
    if doc_type in NEEDS_ERROR_CODE and not doc.meta.get("error_code"):
        problems.append(f"a {doc_type} needs an error_code")

    model = doc.meta.get("robot_model", "")
    if model and model not in ROBOT_MODELS:
        problems.append(f"robot_model '{model}' is not one of {sorted(ROBOT_MODELS)}")

    try:
        date.fromisoformat(doc.meta.get("last_updated", ""))
    except ValueError:
        problems.append(f"last_updated '{doc.meta.get('last_updated')}' is not a YYYY-MM-DD date")

    if not doc.title:
        problems.append("no '# ' title heading")
    words = word_count(doc.body)
    if not MIN_WORDS <= words <= MAX_WORDS:
        problems.append(f"{words} words, expected {MIN_WORDS} to {MAX_WORDS}")
    if not re.search(r"^\s*1\. ", doc.body, re.MULTILINE):
        problems.append("no numbered steps")
    return problems


def check_collection(docs: list[Document]) -> list[str]:
    """Return problems with the set of documents as a whole."""
    problems = []
    counts = Counter(doc.meta.get("doc_type") for doc in docs)
    for doc_type, expected in EXPECTED_COUNTS.items():
        if counts[doc_type] != expected:
            problems.append(f"{counts[doc_type]} documents of type {doc_type}, expected {expected}")
    expected_total = sum(EXPECTED_COUNTS.values())
    if len(docs) != expected_total:
        problems.append(f"{len(docs)} documents, expected {expected_total}")
    ids = Counter(doc.meta.get("doc_id") for doc in docs)
    problems += [f"doc_id '{doc_id}' is used {n} times" for doc_id, n in ids.items() if n > 1]
    return problems


def nonstandard_codes(docs: list[Document]) -> list[str]:
    """Error codes in front-matter that are not written as E + two digits.

    These are not failures: the messy spellings are deliberate, and Stage 5 normalizes them.
    """
    return [
        f"{doc.meta['doc_id']}: error_code '{doc.meta['error_code']}'"
        for doc in docs
        if doc.meta.get("error_code") and not CANONICAL_CODE.fullmatch(doc.meta["error_code"])
    ]


def main() -> int:
    docs = load_documents()
    failed = 0
    for doc in docs:
        problems = check_document(doc)
        failed += bool(problems)
        status = "FAIL" if problems else "ok  "
        doc_id, doc_type = doc.meta.get("doc_id", "?"), doc.meta.get("doc_type", "?")
        print(f"{status} {doc_id:<11} {doc_type:<21} {word_count(doc.body):>3} words  {doc.title}")
        for problem in problems:
            print(f"       - {problem}")

    collection_problems = check_collection(docs)
    for problem in collection_problems:
        print(f"FAIL collection: {problem}")
    for note in nonstandard_codes(docs):
        print(f"note {note} (deliberately messy, normalized in Stage 5)")

    if failed or collection_problems:
        print(f"\n{failed} of {len(docs)} documents failed.")
        print(f"{len(collection_problems)} problems with the collection as a whole.")
        return 1
    print(f"\nAll {len(docs)} documents passed: front-matter complete, mix and lengths as planned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
