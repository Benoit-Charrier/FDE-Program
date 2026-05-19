# agent_build/src/specialty_mapper.py
"""
Contract 6 — Specialty mapping (separate from LLM parsing call, per spec).
Algorithm per Shared Glossary + Contract 6:
  EXACT      = case-insensitive string match to any vocabulary label (no embedding needed)
  MAPPED     = cosine similarity score >= SPECIALTY_MAPPING_THRESHOLD
  UNMAPPABLE = score < threshold
Boundary: score == threshold counts as MAPPED (spec: "score = 0.75 exactly counts as MAPPED (>= threshold)").
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np
import openai


@dataclass
class VocabularyEntry:
    code: str            # written to specialty_required CRM field (e.g. "ICU")
    label: str           # embedded for similarity matching (e.g. "Intensive Care Unit")
    embedding: Optional[list[float]] = None  # cached at startup; None = not yet embedded


@dataclass
class MappingResult:
    specialty_required: Optional[str]   # None if UNMAPPABLE
    specialty_confidence: str           # "EXACT" | "MAPPED" | "UNMAPPABLE"
    best_score: Optional[float]         # cosine similarity; None for EXACT (no embedding used)


def map_specialty(
    specialty_text: str,
    vocabulary: list[VocabularyEntry],
    embedding_client: openai.OpenAI,
    embedding_model: str,
    threshold: float,  # SPECIALTY_MAPPING_THRESHOLD default 0.75 per spec
) -> MappingResult:
    """
    Map specialty_text to a CRM specialty vocabulary code.
    vocabulary must have pre-computed embeddings (loaded at startup per Agent Startup Behavior step 1).
    """
    # EXACT: case-insensitive label match (spec: "input already exactly matches a vocabulary label")
    normalized = specialty_text.strip().lower()
    for entry in vocabulary:
        if normalized == entry.label.lower():
            return MappingResult(
                specialty_required=entry.code,
                specialty_confidence="EXACT",
                best_score=None,
            )

    # Embed input text for cosine similarity comparison
    input_emb = _get_embedding(specialty_text, embedding_client, embedding_model)

    best_score = -1.0
    best_entry: Optional[VocabularyEntry] = None
    for entry in vocabulary:
        if entry.embedding is None:
            raise RuntimeError(
                f"Vocabulary entry {entry.code!r} has no cached embedding — "
                "call embed_vocabulary() at startup before mapping"
            )
        score = _cosine_similarity(input_emb, entry.embedding)
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry is not None and best_score >= threshold:  # >= per spec boundary
        return MappingResult(
            specialty_required=best_entry.code,
            specialty_confidence="MAPPED",
            best_score=best_score,
        )

    return MappingResult(
        specialty_required=None,
        specialty_confidence="UNMAPPABLE",
        best_score=best_score if best_score > -1.0 else None,
    )


def embed_vocabulary(
    vocabulary: list[VocabularyEntry],
    embedding_client: openai.OpenAI,
    embedding_model: str,
) -> None:
    """Compute and cache embeddings for all vocabulary labels in-place (startup step 1)."""
    for entry in vocabulary:
        entry.embedding = _get_embedding(entry.label, embedding_client, embedding_model)


def _get_embedding(text: str, client: openai.OpenAI, model: str) -> list[float]:
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)
    norm_a = float(np.linalg.norm(a_arr))
    norm_b = float(np.linalg.norm(b_arr))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a_arr, b_arr)) / (norm_a * norm_b)
