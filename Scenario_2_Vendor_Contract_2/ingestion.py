from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Union
import audit


@dataclass
class Page:
    page_number: int
    text: str


@dataclass
class IngestionError:
    filename: str
    reason: str


IngestionResult = Union[list[Page], IngestionError]

MAX_PAGES = 40
WORDS_PER_PAGE = 350


def ingest(file_path: str) -> IngestionResult:
    path = Path(file_path)
    filename = path.name
    suffix = path.suffix.lower()

    try:
        if suffix == ".pdf":
            result = _ingest_pdf(path)
        elif suffix == ".docx":
            result = _ingest_docx(path)
        else:
            result = IngestionError(filename, "unsupported_format")

        if isinstance(result, IngestionError):
            audit.log_event(filename, "ingestion", {"status": "error", "reason": result.reason})
        else:
            audit.log_event(filename, "ingestion", {"status": "ok", "pages": len(result)})
        return result

    except Exception as e:
        err = IngestionError(filename, f"parse_error: {e}")
        audit.log_event(filename, "ingestion", {"status": "error", "reason": err.reason})
        return err


def _ingest_pdf(path: Path) -> IngestionResult:
    import pdfplumber

    pages: list[Page] = []
    with pdfplumber.open(str(path)) as pdf:
        total = len(pdf.pages)
        if total > MAX_PAGES:
            return IngestionError(path.name, "exceeds_page_limit")
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(Page(page_number=i, text=text))
    return pages


def _ingest_docx(path: Path) -> IngestionResult:
    from docx import Document

    doc = Document(str(path))
    pages: list[Page] = []
    current_page = 1
    word_count = 0
    buffer: list[str] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        words = len(text.split())
        word_count += words
        buffer.append(text)

        if word_count >= WORDS_PER_PAGE:
            pages.append(Page(page_number=current_page, text="\n".join(buffer)))
            current_page += 1
            word_count = 0
            buffer = []

            if current_page > MAX_PAGES:
                return IngestionError(path.name, "exceeds_page_limit")

    if buffer:
        pages.append(Page(page_number=current_page, text="\n".join(buffer)))

    if not pages:
        return IngestionError(path.name, "empty_document")

    return pages
