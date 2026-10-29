"""Split a knowledge-base document into chunks for the search index.

Why chunks? The embedding model turns a piece of text into ONE list of numbers (a
vector). A whole manual would become one blurry vector about many things at once, so
search could not point at the right part. Small pieces give sharp vectors, and each
piece can be cited on its own.

Why section titles? The assistant must cite "document title + section" for every fix,
so every chunk carries the title of the section it comes from.

This file does two jobs:
- parse_sections(): find where each section starts and ends.          (step 1)
- chunk_fixed(): the baseline chunker. It cuts fixed windows of about
  500 characters with 50 characters of overlap, without looking at
  the document's structure.                                            (step 2)
Stage 5 will add a smarter, section-aware chunker next to it.
"""

import re
from dataclasses import dataclass

from kb.documents import Document

CHUNK_SIZE = 500  # characters per baseline chunk
CHUNK_OVERLAP = 50  # characters shared by neighbouring chunks

# A markdown heading line: 1 to 6 '#' characters, at least one space, then the title.
# The part in brackets, (.+?), "captures" the title, so match.group(1) returns it.
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")


@dataclass
class Section:
    """One section of a document, stored as character positions in the body.

    We keep positions instead of a copy of the text, because in step 2 we need to work
    out how many characters of a chunk fall inside each section.
    """

    title: str
    start: int  # position of the section's first character in the body
    end: int  # position just after its last character, like a slice: body[start:end]


@dataclass
class Chunk:
    text: str  # what gets embedded and later shown to the assistant
    section_title: str  # used for citations, and to score the retrieval eval


# ---------- Step 1 ----------


def parse_sections(body: str, doc_title: str) -> list[Section]:
    """Split the body at every '#'-style heading line.

    Rules:
    - Every line that matches HEADING starts a new section, titled with the heading text.
    - A section ends where the next one starts; the last one ends at len(body).
      Together the sections cover the whole body, with no gaps.
    - If the body does not start with a heading, the text before the first heading
      becomes a section named doc_title.
    - Bold lines (**Monthly tasks**) and underlined headings (Yearly / ------) are NOT
      headings for this parser. MS-100 uses them on purpose, and the eval will show
      what that costs.

    Example, for the body "# Guide\\nIntro.\\n## Steps\\n1. Go":
        [Section("Guide", 0, 15), Section("Steps", 15, 29)]
    """
    # Part 1: find every heading and remember (where it starts, what it says).
    starts: list[tuple[int, str]] = []
    offset = 0  # position of the current line's first character in the body
    for line in body.splitlines(keepends=True):  # keepends: each line keeps its "\n"
        match = HEADING.match(line.strip())
        if match:  # None for normal lines, a match object for heading lines
            starts.append((offset, match.group(1)))
        offset += len(line)

    # Part 2: text before the first heading gets a section named after the document.
    if not starts or starts[0][0] != 0:
        starts.insert(0, (0, doc_title))

    # Part 3: each section ends where the next one starts; the last one ends at the end.
    sections: list[Section] = []
    for i, (start, title) in enumerate(starts):
        if i + 1 < len(starts):
            end = starts[i + 1][0]  # where the next section starts
        else:
            end = len(body)  # the last section runs to the end of the text
        sections.append(Section(title, start, end))
    return sections


# ---------- Step 2 (we do this one together next) ----------


def fixed_windows(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[int]:
    """Start positions of the baseline windows over `text`.

    Each window is `size` characters long. The next window starts `size - overlap`
    characters later, so two neighbours share `overlap` characters. We stop as soon as
    a window reaches the end of the text.

    Example: a text of 1200 characters gives [0, 450, 900], meaning the windows
    0-500, 450-950 and 900-1200 (the last one is shorter).
    """
    step = size - overlap  # how far each window moves forward: 500 - 50 = 450
    starts: list[int] = []
    for start in range(0, len(text), step):
        starts.append(start)
        if start + size >= len(text):  # this window already reaches the end of the text
            break
    return starts


def majority_section(sections: list[Section], start: int, end: int) -> str:
    """Title of the section that covers the most characters of body[start:end].

    A fixed window can cross a heading, but a chunk can carry only one label, so it
    gets the title of the section that fills most of it.

    Example: sections A = 0-100 and B = 100-1000, window 0-500. A covers 100
    characters of the window and B covers 400, so the answer is "B".
    """
    best_title = ""
    best_covered = -1
    for section in sections:
        # The shared part of two ranges starts at the later start and ends at the
        # earlier end. A negative result means they do not touch, so count it as 0.
        covered = max(0, min(end, section.end) - max(start, section.start))
        if covered > best_covered:  # ">" keeps the earlier section when two are equal
            best_title = section.title
            best_covered = covered
    return best_title


def chunk_fixed(doc: Document) -> list[Chunk]:
    """Baseline chunking for one document: fixed windows, each labeled with a section.

    It puts the three helpers together:
    1. parse_sections() finds where each section starts and ends.
    2. fixed_windows() says where each 500-character window starts.
    3. majority_section() names each window after the section that fills most of it.

    A window can cross a heading, so its label may not describe all of its text. That
    is the known weakness of this baseline; Stage 5 measures section-aware chunks
    against it.
    """
    sections = parse_sections(doc.body, doc.title)
    chunks: list[Chunk] = []
    for start in fixed_windows(doc.body):
        end = min(start + CHUNK_SIZE, len(doc.body))  # the last window may be shorter
        text = doc.body[start:end].strip()  # cleaning: drop spaces and newlines at the edges
        label = majority_section(sections, start, end)
        chunks.append(Chunk(text=text, section_title=label))
    return chunks
