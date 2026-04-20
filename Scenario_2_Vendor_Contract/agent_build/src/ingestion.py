"""
Ingestion module: PDF and DOCX contract parsing with page tracking.
"""

import os
from pathlib import Path
from typing import Tuple
import PyPDF2
from docx import Document


def ingest_pdf(file_path: str) -> Tuple[str, int]:
    """
    Extract text from PDF with page tracking.
    Returns (full_text_with_markers, page_count).
    """
    text_parts = []
    page_count = 0
    
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page_count = len(reader.pages)
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            text_parts.append(f"[PAGE {page_num}]\n{text}\n")
    
    full_text = "\n".join(text_parts)
    return full_text, page_count


def ingest_docx(file_path: str) -> Tuple[str, int]:
    """
    Extract text from DOCX.
    Estimate page count by heuristic (roughly 500 words per page).
    Returns (full_text, estimated_page_count).
    """
    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs]
    full_text = "\n".join(paragraphs)
    
    word_count = len(full_text.split())
    estimated_page_count = max(1, word_count // 500)
    
    return full_text, estimated_page_count


def ingest_contract(file_path: str) -> Tuple[str, int, str]:
    """
    Ingest a contract file (PDF or DOCX).
    Returns (text, page_count, file_type).
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise FileNotFoundError(f"Contract file not found: {file_path}")
    
    suffix = file_path_obj.suffix.lower()
    
    if suffix == ".pdf":
        text, page_count = ingest_pdf(file_path)
        file_type = "pdf"
    elif suffix == ".docx":
        text, page_count = ingest_docx(file_path)
        file_type = "docx"
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .pdf, .docx")
    
    return text, page_count, file_type
