"""Load the knowledge-base documents: markdown files with a small front-matter header.

The front-matter is flat "key: value" lines between two '---' lines. A tiny parser is
enough for that, and it avoids YAML surprises: YAML would read `firmware: 1.4` as the
number 1.4 and `last_updated: 2025-06-02` as a date object. Here every value is a string.
"""

from dataclasses import dataclass
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"


@dataclass
class Document:
    path: Path
    meta: dict[str, str]  # the front-matter fields
    title: str  # text of the first "# " heading
    body: str  # the markdown after the front-matter


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Split a file into (front-matter fields, markdown body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file does not start with a '---' front-matter block")
    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError("front-matter block is not closed with '---'")

    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"front-matter line has no ':': {line!r}")
        meta[key.strip()] = value.strip().strip("\"'")
    return meta, "\n".join(lines[end + 1 :]).strip()


def find_title(body: str) -> str:
    """The first level-1 heading, or "" if there is none."""
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def load_document(path: Path) -> Document:
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    return Document(path=path, meta=meta, title=find_title(body), body=body)


def load_documents(docs_dir: Path = DOCS_DIR) -> list[Document]:
    """All documents in docs_dir, sorted by file name so the order is stable."""
    return [load_document(path) for path in sorted(docs_dir.glob("*.md"))]
